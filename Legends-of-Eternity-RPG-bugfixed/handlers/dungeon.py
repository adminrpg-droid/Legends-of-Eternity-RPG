import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, level_up, is_admin, is_banned
from handlers.enhance import get_enhance_level, enhance_stat_bonus
from monster import DUNGEONS, get_dungeon_monsters, get_boss
from items import BOSS_DROPS, get_item
from ui import hp_bar


def _ds(ctx, uid):  return ctx.bot_data.get(f"dg_{uid}", {})
def _sds(ctx, uid, s): ctx.bot_data[f"dg_{uid}"] = s
def _cds(ctx, uid): ctx.bot_data.pop(f"dg_{uid}", None)


async def dungeon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    if is_banned(user.id):
        await update.message.reply_text("🚫 Akunmu di-ban! Hubungi admin.")
        return
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    if player["hp"] <= 0:
        await update.message.reply_text("💀 HP 0! Pulihkan di /inventory")
        return
    if player.get("is_resting"):
        await update.message.reply_text("😴 Kamu sedang istirahat! Ketik /rest untuk berhenti dulu.")
        return
    await _show_dungeon_list(update.message, player, is_msg=True)


async def _show_dungeon_list(target, player: dict, is_msg=False):
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║    🏰  *PILIH DUNGEON*            ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ {player['hp']}/{player['max_hp']}  Lv.{player['level']}\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih dungeon yang ingin dijelajahi:\n"
        f"_(Min. level tercantum di setiap dungeon)_"
    )
    buttons = []
    player_is_admin = is_admin(player.get("user_id", 0))
    for did, dg in DUNGEONS.items():
        min_lv = dg["min_level"]
        unlocked = player["level"] >= min_lv or player_is_admin
        lock = "🔓" if unlocked else f"🔒 (Lv.{min_lv}+)"
        label = f"{dg['emoji']} {dg['name']} {lock}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"dungeon_enter_{did}")])

    markup = InlineKeyboardMarkup(buttons)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def dungeon_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data.replace("dungeon_", "")
    user   = query.from_user
    player = get_player(user.id)

    if not player:
        await query.edit_message_text("❌ Ketik /start dulu!")
        return

    # ── Enter dungeon ────────────────────────────────────────────
    if action.startswith("enter_"):
        did = int(action.replace("enter_", ""))
        dg  = DUNGEONS.get(did)
        if not dg:
            await query.answer("Dungeon tidak ada!", show_alert=True)
            return
        if player["level"] < dg["min_level"] and not is_admin(user.id):
            await query.answer(
                f"❌ Perlu Lv.{dg['min_level']}! Kamu Lv.{player['level']}",
                show_alert=True
            )
            return

        _sds(context, user.id, {
            "dungeon_id": did,
            "floor": 1,
            "total_floors": dg["floor_count"],
            "monster": None,
            "turn": 1,
            "log": [],
            "is_boss": False,
        })
        await _show_dungeon_room(query, player, _ds(context, user.id))
        return

    if action == "exit":
        _cds(context, user.id)
        await query.edit_message_text(
            "🚪 *Kamu keluar dari dungeon.*\nSampai jumpa petualang!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Menu", callback_data="menu")
            ]])
        )
        return

    if action == "dungeonlist":
        await _show_dungeon_list(query, player)
        return

    if action == "room":
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Masuk dungeon dulu!")
            return
        # Refresh player dari DB agar HP/data terkini
        player = get_player(user.id) or player
        await _show_dungeon_room(query, player, dstate)
        return

    if action == "explore":
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Masuk dungeon dulu!")
            return
        # FIX: refresh player dari DB agar data HP/coin terkini sebelum explore
        player = get_player(user.id) or player
        await _dungeon_explore(query, player, dstate, context, user.id)
        return

    if action == "boss":
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Masuk dungeon dulu!")
            return
        # FIX: refresh player dari DB agar data HP/stats terkini saat masuk boss
        player = get_player(user.id) or player
        did  = dstate["dungeon_id"]
        dg   = DUNGEONS[did]
        boss = get_boss(dg["boss"], player["level"], floor=dstate.get("total_floors", 1))
        # BUG FIX: sertakan semua key state agar tidak KeyError saat battle berlangsung
        dstate.update({
            "monster": boss, "is_boss": True, "turn": 1, "log": [],
            "death_marked": False, "dot": 0, "dot_turns": 0,
            "monster_status": {}, "status_effects": {},
            "attack_count": 0, "souls": 0, "berserk_active": False,
        })
        _sds(context, user.id, dstate)
        await _show_dg_battle(query, player, dstate, is_boss=True)
        return

    if action == "item_menu":
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Tidak ada battle aktif.")
            return
        await _show_dg_item_menu(query, player, dstate)
        return

    if action.startswith("use_item_"):
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Tidak ada battle aktif.")
            return
        item_id = action.replace("use_item_", "")
        # FIX: refresh player sebelum pakai item agar inventory terkini
        player = get_player(user.id) or player
        await _use_dg_consumable(query, user.id, player, dstate, item_id)
        _sds(context, user.id, dstate)  # simpan state SEBELUM render
        await _show_dg_battle(query, player, dstate, is_boss=dstate.get("is_boss", False))
        return

    if action == "item_back":
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Tidak ada battle aktif.")
            return
        await _show_dg_battle(query, player, dstate, is_boss=dstate.get("is_boss", False))
        return

    if action in ("attack", "skill", "potion", "dflee"):
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Tidak ada battle aktif.")
            return
        # FIX: selalu refresh player dari DB sebelum proses battle
        # agar gold/XP/HP yang disave adalah data terkini, bukan data stale
        player = get_player(user.id) or player
        await _process_dg_action(query, player, dstate, action, context, user.id)
        return


async def _show_dungeon_room(target, player: dict, dstate: dict):
    did  = dstate["dungeon_id"]
    dg   = DUNGEONS[did]
    fl   = dstate["floor"]
    total = dstate["total_floors"]

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {dg['emoji']} *{dg['name']}*               ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  📍 Lantai {fl}/{total}\n"
        f"║  ❤️ {player['hp']}/{player['max_hp']}\n"
        f"║  💰 {player.get('coin',0)} Gold\n"
        f"╚══════════════════════════════════╝\n\n"
        f"_{dg['desc']}_\n\n"
        f"Apa yang akan kamu lakukan?"
    )
    keyboard = [
        [InlineKeyboardButton("⚔️ Jelajahi Lantai",  callback_data="dungeon_explore")],
        [InlineKeyboardButton("👹 Tantang Boss",       callback_data="dungeon_boss")],
        [InlineKeyboardButton("🚪 Keluar Dungeon",    callback_data="dungeon_exit")],
    ]
    await target.edit_message_text(text, parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(keyboard))


async def _dungeon_explore(query, player: dict, dstate: dict, context, user_id: int):
    events = ["monster"] * 5 + ["treasure", "trap", "rest", "monster"]
    event  = random.choice(events)
    did    = dstate["dungeon_id"]

    if event == "treasure":
        gold = random.randint(500, 2000)
        player["coin"] = player.get("coin", 0) + gold
        # BUG FIX: treasure harus update weekly/monthly coin tracking dan quest progress
        player["weekly_coin_earned"]  = player.get("weekly_coin_earned", 0) + gold
        player["monthly_coin_earned"] = player.get("monthly_coin_earned", 0) + gold
        from handlers.quest import update_quest_progress
        player = update_quest_progress(player, "weekly_coin_earned", gold)
        save_player(user_id, player)
        await query.edit_message_text(
            f"🪙 *HARTA KARUN!*\n\nKamu menemukan peti berisi *{gold} Gold*!\n"
            f"Total Gold: {player.get('coin',0)}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚔️ Lanjut", callback_data="dungeon_explore"),
                 InlineKeyboardButton("👹 Boss",    callback_data="dungeon_boss")],
                [InlineKeyboardButton("🚪 Keluar", callback_data="dungeon_exit")],
            ])
        )
        return

    if event == "trap":
        dmg = random.randint(15, 35)
        player["hp"] = max(1, player["hp"] - dmg)
        save_player(user_id, player)
        await query.edit_message_text(
            f"🪤 *JEBAKAN!*\n\nKamu terkena jebakan! -{dmg} HP\n"
            f"HP tersisa: {player['hp']}/{player['max_hp']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚔️ Lanjut", callback_data="dungeon_explore"),
                 InlineKeyboardButton("🚪 Keluar", callback_data="dungeon_exit")],
            ])
        )
        return

    if event == "rest":
        heal = random.randint(25, 50)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        save_player(user_id, player)
        await query.edit_message_text(
            f"🛖 *TEMPAT ISTIRAHAT*\n\nKamu menemukan api unggun!\n"
            f"+{heal} HP | HP: {player['hp']}/{player['max_hp']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚔️ Lanjut", callback_data="dungeon_explore"),
                 InlineKeyboardButton("👹 Boss",    callback_data="dungeon_boss")],
            ])
        )
        return

    # Monster encounter
    monster = get_dungeon_monsters(did, player["level"], floor=dstate.get("floor", 1))
    # BUG FIX: sertakan semua key state yang dibutuhkan selama battle
    dstate.update({
        "monster": monster, "is_boss": False, "turn": 1, "log": [],
        "death_marked": False, "dot": 0, "dot_turns": 0,
        "monster_status": {}, "status_effects": {},
        "attack_count": 0, "souls": 0, "berserk_active": False,
    })
    _sds(context, user_id, dstate)
    await _show_dg_battle(query, player, dstate)


async def _show_dg_battle(query, player: dict, dstate: dict, is_boss=False):
    monster = dstate["monster"]
    log_txt = "\n".join(dstate["log"][-3:]) if dstate["log"] else "⚔️ Pertempuran dimulai!"
    p_bar   = hp_bar(player["hp"], player["max_hp"], 9)
    m_bar   = hp_bar(monster["current_hp"], monster["hp"], 9)
    boss_tag = "👹 *BOSS BATTLE!*\n" if is_boss else ""
    boss_special = f"\n💥 _{monster.get('special', '')}_" if is_boss else ""

    floor     = dstate.get("floor", 1)
    total_fl  = dstate.get("total_floors", 1)
    # Floor difficulty label
    if floor <= total_fl // 3:
        diff_icon = "🟢"
    elif floor <= (total_fl * 2) // 3:
        diff_icon = "🟡"
    else:
        diff_icon = "🔴"
    floor_info = f"📍 Lantai {floor}/{total_fl} {diff_icon}" if not is_boss else f"📍 LANTAI BOSS {total_fl}/{total_fl} 💀"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║    🏰  *DUNGEON BATTLE*  🏰      ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  {floor_info}\n"
        f"╚══════════════════════════════════╝\n\n"
        f"{boss_tag}"
        f"🟢 *{player['name']}* Lv.{player['level']}\n"
        f"❤️ {p_bar}\n"
        f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
        f"{monster['emoji']} *{monster['name']}*{boss_special}\n"
        f"❤️ {m_bar}\n\n"
        f"📜 {log_txt}\n\n"
        f"🎮 Giliran #{dstate['turn']}:"
    )

    cd     = player.get("skill_cooldown", 0)
    from handlers.battle import _get_active_skill
    _active_sk = _get_active_skill(player)
    s_lbl  = _active_sk["name"] if cd == 0 else f"{_active_sk['name']} ⏳{cd}"
    flee_txt = "🚫 Boss" if is_boss else "🏃 Kabur"

    # Hitung total consumable yang dimiliki
    inv = player.get("inventory", {})
    _CONS_IDS = ("health_potion", "mana_potion", "elixir", "revive_crystal", "mega_potion")
    total_cons = sum(inv.get(cid, 0) for cid in _CONS_IDS)

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Serang", callback_data="dungeon_attack"),
            InlineKeyboardButton(s_lbl,       callback_data="dungeon_skill"),
        ],
        [
            InlineKeyboardButton(f"🎒 Item ({total_cons})", callback_data="dungeon_item_menu"),
            InlineKeyboardButton(flee_txt,                   callback_data="dungeon_dflee"),
        ],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def _process_dg_action(query, player: dict, dstate: dict, action: str, context, user_id: int):
    monster  = dstate["monster"]
    log      = dstate["log"]
    is_boss  = dstate.get("is_boss", False)
    admin    = is_admin(user_id)  # FIX BUG #2: admin check untuk bypass cooldown/MP

    if action == "dflee":
        if is_boss:
            await query.answer("⛔ Tidak bisa kabur dari Boss!", show_alert=True)
            return
        log.append("🏃 Kamu kabur dari dungeon!")
        _cds(context, user_id)
        save_player(user_id, player)
        await query.edit_message_text("🏃 *Kamu kabur!*", parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup([[
                                          InlineKeyboardButton("🏠 Menu", callback_data="menu")
                                      ]]))
        return

    player_dmg = 0  # default aman agar tidak UnboundLocalError

    # action potion (legacy fallback) — redirect ke item_menu
    if action == "potion":
        await _show_dg_item_menu(query, player, dstate)
        return

    # BUG FIX: Apply pet bonus ke player copy sebelum kalkulasi damage
    # (konsisten dengan battle.py yang juga terapkan ini)
    if action in ("attack", "skill"):
        from handlers.battle import apply_pet_bonus
        player_with_pet = apply_pet_bonus({**player})
        player["atk"]  = player_with_pet.get("atk", player["atk"])
        player["crit"] = player_with_pet.get("crit", player["crit"])

    if action == "skill":
        if player.get("skill_cooldown", 0) > 0 and not admin:
            await query.answer(f"⏳ Cooldown!", show_alert=True)
            return
        # Gunakan skill yang di-equip (sama seperti battle.py)
        from handlers.battle import _get_active_skill, _get_enhance_atk
        active_skill = _get_active_skill(player)
        effect = active_skill.get("effect", {})
        mp_cost = effect.get("mp_cost", 25)
        if player["mp"] < mp_cost and not admin:
            await query.answer(f"❌ MP kurang (butuh {mp_cost})!", show_alert=True)
            return
        if not admin:
            player["mp"] -= mp_cost
        mult = effect.get("dmg_mult", 0)
        if mult == 0:
            mult = random.uniform(2.0, 3.0)
        else:
            mult *= random.uniform(0.9, 1.1)
        # BUG FIX: pakai _get_enhance_atk agar weapon base ATK ikut dihitung
        player_dmg = max(1, int(_get_enhance_atk(player) * mult - monster["def"] * 0.4))

        # [FIX] Reaper skill — semua effect ditangani dengan benar
        if player["class"] == "reaper":
            skill_log = f"☠️ {active_skill['name']}! -{player_dmg} HP"

            if effect.get("heal"):
                h = min(effect["heal"], player["max_hp"] - player["hp"])
                player["hp"] = min(player["max_hp"], player["hp"] + h)
                skill_log += f" | +{h} HP"
            if effect.get("drain_pct"):
                drain = int(monster["current_hp"] * effect["drain_pct"])
                player["hp"] = min(player["max_hp"], player["hp"] + drain)
                skill_log += f" | Drain +{drain} HP"
            elif effect.get("lifesteal"):
                steal = int(player_dmg * effect["lifesteal"])
                player["hp"] = min(player["max_hp"], player["hp"] + steal)
                skill_log += f" | Lifesteal +{steal} HP"
            if effect.get("stat_boost"):
                boost = effect["stat_boost"]
                dur = effect.get("duration", 3)
                dstate.setdefault("status_effects", {})["lich_awakening"] = {"turns": dur, "atk_boost": boost}
                skill_log += f" | 🌑 Lich Awakening! All stat +{int(boost*100)}% ({dur} ronde)"
            if effect.get("shield_pct"):
                dstate.setdefault("status_effects", {})["shield"] = {"turns": effect.get("duration", 3), "dmg_reduce": effect["shield_pct"]}
                skill_log += f" | 🦴 Bone Shield aktif!"
            if effect.get("def_debuff"):
                dstate.setdefault("monster_status", {})["curse"] = {"turns": 3, "def_reduce": effect["def_debuff"]}
                skill_log += f" | 💜 DEF musuh -{int(effect['def_debuff']*100)}%!"
            if effect.get("soul_bonus"):
                dstate["souls"] = min(5, dstate.get("souls", 0) + effect["soul_bonus"])
                skill_log += f" | ☠️ +{effect['soul_bonus']} Soul ({dstate['souls']}/5)"
            if effect.get("instant_harvest") or effect.get("mass_harvest"):
                harvest_dmg = int(monster["current_hp"] * 0.5)
                player_dmg += harvest_dmg
                dstate["souls"] = 0
                skill_log += f" | 💀 HARVEST! -{harvest_dmg} bonus DMG!"
            if effect.get("heal_pct"):
                h2 = int(player["max_hp"] * effect["heal_pct"])
                player["hp"] = min(player["max_hp"], player["hp"] + h2)
                skill_log += f" | +{h2} HP"
            if effect.get("immortal_turns"):
                dstate["immortal"] = effect["immortal_turns"]
                skill_log += f" | 🌟 Immortal {effect['immortal_turns']} ronde!"
            if effect.get("dmg_buff_mult"):
                dstate["dmg_buff_next"] = effect["dmg_buff_mult"]
                skill_log += f" | Next atk x{effect['dmg_buff_mult']} DMG"

            log.append(skill_log)

        # BUG FIX: Assassin skill di dungeon sekarang konsisten dengan battle.py
        # — mendapat bonus 1.5x DMG dan mentrigger death_marked untuk serangan berikutnya
        elif player["class"] == "assassin":
            e_atk_assassin = _get_enhance_atk(player)
            player_dmg = max(1, int(e_atk_assassin * mult * 1.5 - monster["def"] * 0.3))
            dstate["death_marked"] = True
            log.append(f"💀 {active_skill['name']}! 💥INSTANT! -{player_dmg} HP!")

        else:
            log.append(f"✨ {active_skill['name']}! -{player_dmg} HP 💥")

        if not admin:
            player["skill_cooldown"] = effect.get("cooldown", 3)

    else:  # attack
        crit_chance = player.get("crit", 10)
        crit = random.randint(1, 100) <= crit_chance
        mult = 1.6 if crit else 1.0

        # BUG FIX: terapkan death_marked (Assassin) seperti di battle.py
        if dstate.get("death_marked"):
            mult *= 2.0
            dstate["death_marked"] = False

        # [FIX] Apply Lich Awakening stat boost in dungeon attack
        lich_dg = dstate.get("status_effects", {}).get("lich_awakening")
        if lich_dg and lich_dg.get("turns", 0) > 0:
            mult *= (1.0 + lich_dg.get("atk_boost", 0.5))
        # [FIX] Apply dmg_buff_next (Dark Ritual) in dungeon
        if dstate.get("dmg_buff_next"):
            mult *= dstate.pop("dmg_buff_next")

        # BUG FIX: terapkan Berserker ATK boost (Warrior low-hp special) di dungeon attack
        berserker_dg = dstate.get("status_effects", {}).get("berserker")
        berserker_dg_active = berserker_dg and berserker_dg.get("turns", 0) > 0
        if berserker_dg_active:
            mult *= (1.0 + berserker_dg.get("atk_boost", 0.5))

        from handlers.battle import _get_enhance_atk
        e_atk = _get_enhance_atk(player)
        player_dmg = max(1, int(e_atk * mult - monster["def"] * 0.7))
        crit_tag = "  💥CRIT!" if crit else ""
        berserk_tag = " 🔥BERSERK!" if berserker_dg_active else ""
        log.append(f"⚔️ Serang! -{player_dmg} HP{crit_tag}{berserk_tag}")

        # BUG FIX: Assassin Bleed on CRIT (konsisten dengan battle.py)
        if crit and player.get("class") == "assassin":
            bleed_dmg = 15
            bleed_turns = 3
            eq_wpn = player.get("equipment", {}).get("weapon", "")
            if eq_wpn in ("nightshade_sickle", "death_scythe"):
                bleed_dmg = 18
            dstate.setdefault("monster_status", {})["bleed"] = {"dmg_per_turn": bleed_dmg, "turns": bleed_turns}
            log.append(f"🩸 *BLEED!* Musuh berdarah -{bleed_dmg}/ronde selama {bleed_turns} ronde!")

        # BUG FIX: Apply weapon special effect on attack (burn/lifesteal/on_crit)
        from handlers.battle import apply_weapon_special_on_attack
        apply_weapon_special_on_attack(player, dstate, monster, log, crit, current_dmg=player_dmg)

        # BUG FIX: Apply class special — every_3_attacks (Mage Arcane Overload) + on_attack
        from handlers.battle import get_class_special_effect
        sp_log = get_class_special_effect(player, dstate, "on_attack")
        if sp_log:
            log.append(sp_log)

        # Consume pending_arcane jika sudah terkumpul (Mage: every 3 attacks)
        if dstate.get("pending_arcane"):
            dstate["pending_arcane"] = False
            arcane_dmg = max(1, int(player.get("atk", 10) * 2.5 - monster["def"] * 0.3))
            monster["current_hp"] -= arcane_dmg
            log.append(f"⚡ *ARCANE BURST!* Sihir otomatis meledak! -{arcane_dmg} HP!")

    if action not in ("item_menu", "item_back", "potion"):
        monster["current_hp"] -= player_dmg

    # BUG FIX: Apply DoT status effects ke monster per turn (burn, bleed, poison)
    if action not in ("potion", "item_menu", "item_back"):
        from handlers.battle import apply_status_effects_to_monster
        apply_status_effects_to_monster(dstate, monster, log)

    # Kurangi cooldown skill setiap turn kecuali saat pakai skill atau item
    if action not in ("skill", "potion", "item_menu", "item_back") and player.get("skill_cooldown", 0) > 0:
        player["skill_cooldown"] -= 1

    # BUG FIX: Trigger low_hp class special (Warrior Berserker Rage) di dungeon
    if action not in ("potion", "item_menu", "item_back"):
        from handlers.battle import get_class_special_effect
        low_hp_log = get_class_special_effect(player, dstate, "low_hp")
        if low_hp_log:
            log.append(low_hp_log)

    # ── Monster dies — cek SEBELUM boss regen agar boss tidak regen saat hp <= 0 ─
    if monster["current_hp"] <= 0:
        gold  = int(random.randint(*monster.get("gold", (20, 50))) * 12.0)
        exp   = int(monster.get("exp", 50) * 5.0)

        player["coin"]  = player.get("coin", 0) + (gold * 6 if is_boss else gold)
        player["exp"]   = player.get("exp", 0) + exp
        player["kills"] = player.get("kills", 0) + 1
        # War point
        try:
            from handlers.war import add_war_point
            add_war_point(user_id, 2 if is_boss else 1)
        except Exception:
            pass
        earned = gold * 6 if is_boss else gold
        player["weekly_coin_earned"]  = player.get("weekly_coin_earned", 0) + earned
        player["monthly_coin_earned"] = player.get("monthly_coin_earned", 0) + earned
        if is_boss:
            player["boss_kills"] = player.get("boss_kills", 0) + 1
            player["dungeon_clears"] = player.get("dungeon_clears", 0) + 1
            player["dungeon_clears_weekly"] = player.get("dungeon_clears_weekly", 0) + 1
            # Weekly/monthly boss kills tracking
            player["weekly_boss_kills"]  = player.get("weekly_boss_kills", 0) + 1
            player["monthly_boss_kills"] = player.get("monthly_boss_kills", 0) + 1
            # Quest progress — boss kill juga menambah weekly kills untuk leaderboard
            player["weekly_kills"]  = player.get("weekly_kills", 0) + 1
            player["monthly_kills"] = player.get("monthly_kills", 0) + 1
            from handlers.quest import update_quest_progress
            player = update_quest_progress(player, "boss_kills", 1)
            player = update_quest_progress(player, "weekly_boss_kills", 1)
            player = update_quest_progress(player, "dungeon_clears", 1)
            player = update_quest_progress(player, "dungeon_clears_weekly", 1)
            # BUG FIX: boss dungeon kill juga harus menambah daily_kill & weekly_kill quest progress
            player = update_quest_progress(player, "kills", 1)
            player = update_quest_progress(player, "weekly_kills", 1)
            # BUG FIX: update quest weekly_coin_earned dari dungeon boss kill
            player = update_quest_progress(player, "weekly_coin_earned", earned)
        else:
            # Hanya monster biasa yang naikkan floor
            player["weekly_kills"]  = player.get("weekly_kills", 0) + 1
            player["monthly_kills"] = player.get("monthly_kills", 0) + 1
            from handlers.quest import update_quest_progress
            player = update_quest_progress(player, "kills", 1)
            # BUG FIX: weekly_kill_50 quest harus diupdate dari dungeon monster kill juga
            player = update_quest_progress(player, "weekly_kills", 1)
            # BUG FIX: update quest weekly_coin_earned dari dungeon monster kill
            player = update_quest_progress(player, "weekly_coin_earned", earned)
            dstate["floor"] = dstate.get("floor", 1) + 1

        # BUG FIX: Reaper Soul Reap on kill (konsisten dengan battle.py)
        kill_special_txt = ""
        char_class = player.get("class", "warrior")
        if char_class == "reaper":
            dstate["souls"] = dstate.get("souls", 0) + 1
            heal_soul = int(player["max_hp"] * 0.15)
            player["hp"] = min(player["max_hp"], player["hp"] + heal_soul)
            kill_special_txt = f"\n☠️ *SOUL REAP!* +1 Soul ({dstate['souls']}/5) | +{heal_soul} HP!"
            if dstate["souls"] >= 5:
                dstate["souls"] = 0
                kill_special_txt += "\n💀 *HARVEST!* Musuh menerima pukulan maut!"
        elif char_class == "assassin" and not dstate.get("first_kill_used"):
            dstate["first_kill_used"] = True
            heal_exe = int(player["max_hp"] * 0.25)
            player["hp"] = min(player["max_hp"], player["hp"] + heal_exe)
            dstate["death_marked"] = True
            kill_special_txt = f"\n🩸 *SHADOW EXECUTION!* +{heal_exe} HP | Next attack x2 DMG!"

        player, leveled, lv_gained = level_up(player)
        # Check titles
        from handlers.title import check_and_award_titles
        player, new_titles = check_and_award_titles(player)
        lv_txt = f"\n🎊 *LEVEL UP!* → Lv.{player['level']}" if leveled else ""

        # Boss drops: Evolution Stone (0.1%) + GOD SSSR (0.1%)
        drop_txt = ""
        evo_stone_txt = ""
        if is_boss:
            # Evolution Stone drop — 0.1% rate dari boss
            if random.randint(1, 1000) == 1:
                inv = player.setdefault("inventory", {})
                inv["evolution_stone"] = inv.get("evolution_stone", 0) + 1
                evo_stone_txt = "\n\n💠 *LUAR BIASA! EVOLUTION STONE DIDAPAT!*\n_(Drop 0.1% — sangat langka!)_"
            # GOD SSSR drop — 0.1% rate dari boss dungeon
            from items import GOD_SSSR_BOSS_DROPS, GOD_SSSR_WEAPONS, GOD_SSSR_ARMORS, GOD_SSSR_SKILLS, GOD_SSSR_PETS
            if random.randint(1, 1000) == 1:
                char_class = player.get("class", "warrior")
                sssr_pool  = GOD_SSSR_BOSS_DROPS.get(char_class, [])
                if sssr_pool:
                    sssr_id = random.choice(sssr_pool)
                    inv = player.setdefault("inventory", {})
                    if sssr_id in GOD_SSSR_WEAPONS:
                        sssr_item = GOD_SSSR_WEAPONS[sssr_id]
                        inv[sssr_id] = inv.get(sssr_id, 0) + 1
                        drop_txt = f"\n\n🔱✨ *[GOD SSSR DROP!]* 🔱✨\n🎁 *{sssr_item['name']}* masuk inventory!\n_(Rate 0.1% — Equip via menu inventory)_"
                    elif sssr_id in GOD_SSSR_ARMORS:
                        sssr_item = GOD_SSSR_ARMORS[sssr_id]
                        inv[sssr_id] = inv.get(sssr_id, 0) + 1
                        drop_txt = f"\n\n🔱✨ *[GOD SSSR DROP!]* 🔱✨\n🎁 *{sssr_item['name']}* masuk inventory!\n_(Rate 0.1% — Equip via menu inventory)_"
                    elif sssr_id in GOD_SSSR_SKILLS:
                        sssr_item = GOD_SSSR_SKILLS[sssr_id]
                        inv[sssr_id] = 1
                        player.setdefault("bought_skills", [])
                        if sssr_id not in [s if isinstance(s, str) else s.get("id", "") for s in player["bought_skills"]]:
                            player["bought_skills"].append({"id": sssr_id, "name": sssr_item["name"]})
                        drop_txt = f"\n\n🔱✨ *[GOD SSSR DROP!]* 🔱✨\n🎁 Skill *{sssr_item['name']}* ditambahkan!\n_(Rate 0.1% — sangat beruntung!)_"
                    elif sssr_id in GOD_SSSR_PETS:
                        sssr_item = GOD_SSSR_PETS[sssr_id]
                        inv[sssr_id] = inv.get(sssr_id, 0) + 1
                        # BUG FIX: tambahkan ke owned_pets dan pet_tiers agar bisa diequip
                        owned_pets = player.setdefault("owned_pets", [])
                        if sssr_id not in owned_pets:
                            owned_pets.append(sssr_id)
                        pet_tiers_d = player.setdefault("pet_tiers", {})
                        if sssr_id not in pet_tiers_d:
                            pet_tiers_d[sssr_id] = sssr_item.get("tier", 1)
                        # Set sebagai pet aktif jika belum punya pet
                        if not player.get("pet"):
                            player["pet"] = sssr_id
                            player["pet_tier"] = sssr_item.get("tier", 1)
                            pet_tiers_d[sssr_id] = sssr_item.get("tier", 1)
                        drop_txt = f"\n\n🔱✨ *[GOD SSSR DROP!]* 🔱✨\n🎁 Pet *{sssr_item['name']}* masuk inventory!\n_(Rate 0.1% — sangat beruntung!)_"

        _cds(context, user_id)
        save_player(user_id, player)

        if is_boss:
            # Dungeon selesai — simpan state minimal untuk dungeonlist
            boss_txt = "🎊 *BOSS DIKALAHKAN!* Dungeon Selesai!\n"
            await query.edit_message_text(
                f"🏆 *MENANG!*\n\n"
                f"{boss_txt}"
                f"💀 *{monster['name']}* dikalahkan!\n"
                f"💰 +{gold * 6} Gold\n"
                f"✨ +{exp} EXP{lv_txt}{kill_special_txt}{drop_txt}{evo_stone_txt}\n\n"
                f"❤️ HP: {player['hp']}/{player['max_hp']}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏰 Pilih Dungeon Lain", callback_data="dungeon_dungeonlist"),
                     InlineKeyboardButton("🚪 Keluar",             callback_data="dungeon_exit")],
                ])
            )
        else:
            # Monster biasa — simpan state agar room bisa ditampilkan
            _sds(context, user_id, dstate)
            await query.edit_message_text(
                f"🏆 *MENANG!*\n\n"
                f"💀 *{monster['name']}* dikalahkan!\n"
                f"💰 +{gold} Gold\n"
                f"✨ +{exp} EXP{lv_txt}{kill_special_txt}\n\n"
                f"❤️ HP: {player['hp']}/{player['max_hp']}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏰 Lanjut Dungeon", callback_data="dungeon_room"),
                     InlineKeyboardButton("🚪 Keluar",         callback_data="dungeon_exit")],
                ])
            )
        return

    # ── Boss REGEN — hanya jika boss masih hidup setelah serangan ─
    if is_boss and monster["current_hp"] > 0 and action not in ("potion", "item_menu", "item_back"):
        regen_pct = monster.get("regen_pct", 0.03)
        regen_hp  = int(monster.get("hp", 1) * regen_pct)
        if regen_hp > 0:
            monster["current_hp"] = min(monster["hp"], monster["current_hp"] + regen_hp)
            log.append(f"💚 {monster['name']} regenerasi +{regen_hp} HP!")
        # Boss berserk saat HP rendah
        berserk_th = monster.get("berserk_threshold", 0)
        if berserk_th > 0 and monster["current_hp"] / monster["hp"] <= berserk_th:
            if not dstate.get("berserk_active"):
                dstate["berserk_active"] = True
                log.append(f"🔥 {monster['name']} BERSERK! ATK x2!")

    # ── Monster attacks ─────────────────────────────────────────
    if action in ("item_menu", "item_back", "potion"):
        # Pakai item / redirect potion tidak memicu serangan balik monster
        p_def = 0  # BUG FIX: definisikan p_def agar counter attack tidak UnboundLocalError
    else:
        from handlers.battle import _get_enhance_def
        p_def = _get_enhance_def(player)  # BUG FIX #2 + #5: hitung sekali di luar cabang dodge

        # BUG FIX: Admin tidak kena damage di dungeon (konsisten dengan battle.py)
        if admin:
            log.append(f"{monster['emoji']} Serang! (Admin tidak terkena damage)")
        else:
            # BUG FIX: cek Immortal — skip damage dan kurangi turn
            immortal = dstate.get("immortal", 0)
            if immortal > 0:
                dstate["immortal"] = immortal - 1
                log.append(f"🌟 *IMMORTAL!* Serangan diblokir! ({immortal - 1} ronde tersisa)")
            else:
                dodge = min(50, player.get("spd", 10) * 2)
                if random.randint(1, 100) <= dodge:
                    log.append("💨 Menghindar!")
                else:
                    base_atk = monster["atk"]
                    # Terapkan berserk multiplier jika aktif
                    if dstate.get("berserk_active") and is_boss:
                        berserk_mult = monster.get("berserk_atk_mult", 2.0)
                        base_atk = int(base_atk * berserk_mult)
                    mdmg = max(1, base_atk - int(p_def * 0.75))
                    # BUG FIX: cek Shield (Bone Shield) — kurangi damage dan decrement turns
                    shield = dstate.get("status_effects", {}).get("shield")
                    if shield and shield.get("turns", 0) > 0:
                        reduce_pct = shield.get("dmg_reduce", 0.3)
                        mdmg = max(1, int(mdmg * (1.0 - reduce_pct)))
                        shield["turns"] -= 1
                        berserk_tag = " 🔥BERSERK!" if dstate.get("berserk_active") and is_boss else ""
                        if shield["turns"] <= 0:
                            dstate.get("status_effects", {}).pop("shield", None)
                            log.append(f"{monster['emoji']} -{mdmg} HP 🦴 *(Shield habis!)*{berserk_tag}")
                        else:
                            log.append(f"{monster['emoji']} -{mdmg} HP 🦴 *(Shield -{int(reduce_pct*100)}%)*{berserk_tag}")
                    else:
                        berserk_tag = " 🔥BERSERK!" if dstate.get("berserk_active") and is_boss else ""
                        log.append(f"{monster['emoji']} -{mdmg} HP{berserk_tag}")
                    player["hp"] = max(0, player["hp"] - mdmg)

    # ── Boss counter attack ──────────────────────────────────────
    if is_boss and action not in ("potion", "item_menu", "item_back") and not admin:
        counter_pct = int(monster.get("counter_pct", 0) * 100)
        if counter_pct > 0 and random.randint(1, 100) <= counter_pct:
            # BUG FIX: cek Immortal untuk counter attack juga
            if dstate.get("immortal", 0) > 0:
                log.append(f"🌟 *IMMORTAL!* Counter diblokir!")
            else:
                c_dmg = max(1, int(monster["atk"] * 0.5) - int(p_def * 0.3))
                # BUG FIX: cek Shield untuk counter attack juga
                shield_c = dstate.get("status_effects", {}).get("shield")
                if shield_c and shield_c.get("turns", 0) > 0:
                    c_dmg = max(1, int(c_dmg * (1.0 - shield_c.get("dmg_reduce", 0.3))))
                player["hp"] = max(0, player["hp"] - c_dmg)
                log.append(f"⚡ *COUNTER!* {monster['emoji']} balas serang! -{c_dmg} HP!")

    dstate["turn"] += 1

    if player["hp"] <= 0:
        revives = player.get("inventory", {}).get("revive_crystal", 0)
        if revives > 0:
            player["hp"] = player["max_hp"] // 2
            player["inventory"]["revive_crystal"] -= 1
            log.append("💠 Revive Crystal aktif!")
            # FIX BUG #3: simpan dstate setelah revive agar perubahan tidak hilang
            save_player(user_id, player)
            _sds(context, user_id, dstate)
            await _show_dg_battle(query, player, dstate, is_boss=is_boss)
            return
        else:
            # [FIX] Kalah tidak mengurangi gold
            player["hp"]     = player["max_hp"] // 3
            player["losses"] = player.get("losses", 0) + 1
            _cds(context, user_id)
            save_player(user_id, player)
            await query.edit_message_text(
                f"💀 *GAME OVER*\n\n"
                f"Dikalahkan oleh {monster['emoji']} *{monster['name']}*!\n"
                f"HP dipulihkan ke {player['hp']}/{player['max_hp']}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Kembali", callback_data="dungeon_exit")
                ]])
            )
            return

    # [FIX] Tick lich_awakening per round in dungeon
    lich_tick = dstate.get("status_effects", {}).get("lich_awakening")
    if lich_tick and lich_tick.get("turns", 0) > 0:
        lich_tick["turns"] -= 1
        if lich_tick["turns"] <= 0:
            dstate.get("status_effects", {}).pop("lich_awakening", None)

    # BUG FIX: Tick berserker turns per round in dungeon (Warrior low-hp special)
    # Sebelumnya turns tidak pernah dikurangi → buff berlangsung selamanya
    if action not in ("potion", "item_menu", "item_back"):
        berserker_tick = dstate.get("status_effects", {}).get("berserker")
        if berserker_tick and berserker_tick.get("turns", 0) > 0:
            berserker_tick["turns"] -= 1
            if berserker_tick["turns"] <= 0:
                dstate.get("status_effects", {}).pop("berserker", None)
                log.append("🔥 Berserker Rage habis.")

    save_player(user_id, player)
    _sds(context, user_id, dstate)
    await _show_dg_battle(query, player, dstate, is_boss=is_boss)


# ════════════════════════════════════════════════════════════════
#  ITEM MENU IN DUNGEON BATTLE
# ════════════════════════════════════════════════════════════════
_DG_BATTLE_CONSUMABLES = {
    "health_potion": {"name": "⚕️ Health Potion",  "effect": {"hp": 60}},
    "mana_potion":   {"name": "🔵 Mana Potion",    "effect": {"mp": 50}},
    "elixir":        {"name": "⚗️ Grand Elixir",   "effect": {"hp": 150, "mp": 120}},
    "mega_potion":   {"name": "🌟 Mega Potion",    "effect": {"hp": 9999}},
    "revive_crystal":{"name": "💠 Revive Crystal", "effect": {}},
}


async def _show_dg_item_menu(query, player: dict, dstate: dict):
    """Tampilkan daftar consumable yang dimiliki player saat dungeon battle."""
    inv     = player.get("inventory", {})
    is_boss = dstate.get("is_boss", False)
    buttons = []
    lines   = ["🎒 *PILIH ITEM YANG INGIN DIPAKAI*\n_(Item tidak memicu serangan balik monster)_\n"]

    for item_id, item_info in _DG_BATTLE_CONSUMABLES.items():
        qty = inv.get(item_id, 0)
        if qty <= 0:
            continue
        eff = item_info["effect"]
        desc_parts = []
        if eff.get("hp"):
            hp_val = eff["hp"]
            desc_parts.append(f"+{hp_val if hp_val < 9999 else 'FULL'} HP")
        if eff.get("mp"):
            desc_parts.append(f"+{eff['mp']} MP")
        if item_id == "revive_crystal":
            desc_parts.append("Bangkit otomatis saat mati")
        desc = ", ".join(desc_parts) if desc_parts else ""
        lines.append(f"• {item_info['name']} ×{qty} — _{desc}_")
        buttons.append([InlineKeyboardButton(
            f"{item_info['name']} ×{qty}",
            callback_data=f"dungeon_use_item_{item_id}"
        )])

    if not buttons:
        lines.append("\n❌ *Tidak ada item yang bisa dipakai!*")
    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Battle", callback_data="dungeon_item_back")])

    await query.edit_message_text(
        "\n".join(lines), parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def _use_dg_consumable(query, user_id: int, player: dict, dstate: dict, item_id: str):
    """Proses pemakaian consumable saat dungeon battle — tidak memicu serangan balik."""
    item_info = _DG_BATTLE_CONSUMABLES.get(item_id)
    if not item_info:
        await query.answer("❌ Item tidak dikenal!", show_alert=True)
        return

    inv = player.get("inventory", {})
    qty = inv.get(item_id, 0)
    if qty <= 0:
        await query.answer(f"❌ {item_info['name']} habis!", show_alert=True)
        await _show_dg_item_menu(query, player, dstate)
        return

    eff          = item_info["effect"]
    log          = dstate["log"]
    result_parts = []

    if eff.get("hp"):
        heal       = eff["hp"]
        before_hp  = player["hp"]
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        actual_heal = player["hp"] - before_hp
        if player["hp"] >= player["max_hp"]:
            result_parts.append("❤️ HP pulih penuh!")
        else:
            result_parts.append(f"❤️ +{actual_heal} HP")

    if eff.get("mp"):
        before_mp  = player["mp"]
        player["mp"] = min(player["max_mp"], player["mp"] + eff["mp"])
        actual_mp   = player["mp"] - before_mp
        result_parts.append(f"💙 +{actual_mp} MP")

    if item_id == "revive_crystal":
        result_parts.append("💠 Revive Crystal siap — akan aktif saat HP 0!")

    inv[item_id]  -= 1
    result_str     = ", ".join(result_parts) if result_parts else "Digunakan"
    log.append(f"🎒 {item_info['name']} dipakai! {result_str}")

    dstate["turn"] += 1
    save_player(user_id, player)
    # Catatan: _show_dg_battle dipanggil oleh caller (dungeon_action_handler)
    # setelah _sds menyimpan dstate, agar state tidak hilang jika ada race condition
