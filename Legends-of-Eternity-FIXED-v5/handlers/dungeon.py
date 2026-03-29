import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, level_up, is_admin, is_banned
from handlers.enhance import get_enhance_level, enhance_stat_bonus
from monster import DUNGEONS, get_dungeon_monsters, get_boss
from items import BOSS_DROPS, get_item
from ui import hp_bar


def _ds(ctx, uid):  return ctx.user_data.get(f"dg_{uid}", {})
def _sds(ctx, uid, s): ctx.user_data[f"dg_{uid}"] = s
def _cds(ctx, uid): ctx.user_data.pop(f"dg_{uid}", None)


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

    if action == "explore":
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Masuk dungeon dulu!")
            return
        await _dungeon_explore(query, player, dstate, context, user.id)
        return

    if action == "boss":
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Masuk dungeon dulu!")
            return
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

    elif action == "skill":
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
        if player["class"] == "reaper":
            player["hp"] = min(player["max_hp"], player["hp"] + player_dmg // 3)
        if not admin:
            player["skill_cooldown"] = effect.get("cooldown", 3)
        log.append(f"✨ {active_skill['name']}! -{player_dmg} HP 💥")

    else:  # attack
        crit_chance = player.get("crit", 10)
        crit = random.randint(1, 100) <= crit_chance
        mult = 1.6 if crit else 1.0
        # BUG FIX #3: gunakan _get_enhance_atk agar skill enhance bonus ikut dihitung,
        # konsisten dengan battle.py dan blok skill di atas
        from handlers.battle import _get_enhance_atk
        e_atk = _get_enhance_atk(player)
        player_dmg = max(1, int(e_atk * mult - monster["def"] * 0.7))
        log.append(f"⚔️ Serang! -{player_dmg} HP{'  💥CRIT!' if crit else ''}")

    if action not in ("item_menu", "item_back", "potion"):
        monster["current_hp"] -= player_dmg
    # Kurangi cooldown skill setiap turn kecuali saat pakai skill atau item
    if action not in ("skill", "potion", "item_menu", "item_back") and player.get("skill_cooldown", 0) > 0:
        player["skill_cooldown"] -= 1

    # ── Monster dies — cek SEBELUM boss regen agar boss tidak regen saat hp <= 0 ─
    if monster["current_hp"] <= 0:
        gold  = int(random.randint(*monster.get("gold", (20, 50))) * 6.0)
        exp   = int(monster.get("exp", 50) * 5.0)

        player["coin"]  = player.get("coin", 0) + (gold * 3 if is_boss else gold)
        player["exp"]   = player.get("exp", 0) + exp
        player["kills"] = player.get("kills", 0) + 1
        earned = gold * 3 if is_boss else gold
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

        player, leveled, lv_gained = level_up(player)
        # Check titles
        from handlers.title import check_and_award_titles
        player, new_titles = check_and_award_titles(player)
        lv_txt = f"\n🎊 *LEVEL UP!* → Lv.{player['level']}" if leveled else ""

        # Boss drops rare item
        drop_txt = ""
        if is_boss:
            char_class = player.get("class", "warrior")
            drops = BOSS_DROPS.get(char_class, [])
            if drops and random.randint(1, 100) <= 60:
                drop_id   = random.choice(drops)
                drop_item = get_item(drop_id)
                if drop_item:
                    equip = player.setdefault("equipment", {})
                    old   = equip.get(drop_item["type"])
                    from items import ALL_ITEMS
                    if old:
                        old_i = ALL_ITEMS.get(old, {})
                        for s, v in old_i.get("stats", {}).items():
                            player[s] = max(1, player.get(s, 0) - v)
                    # Keep old item in inventory
                    if old:
                        inv = player.setdefault("inventory", {})
                        inv[old] = inv.get(old, 0) + 1
                    equip[drop_item["type"]] = drop_id
                    for s, v in drop_item.get("stats", {}).items():
                        player[s] = player.get(s, 0) + v
                        if s == "max_hp":
                            player["hp"] = min(player.get("hp", 1) + v, player["max_hp"])
                        if s == "max_mp":
                            player["mp"] = min(player.get("mp", 0) + v, player["max_mp"])
                    drop_txt = f"\n🎁 *DROP ITEM!* {drop_item['name']} ✅ Disimpan & Terpasang!"

        # Evolution Stone drop — 0.1% rate dari boss
        evo_stone_txt = ""
        if is_boss:
            roll = random.randint(1, 1000)
            if roll == 1:  # 0.1% = 1/1000
                inv = player.setdefault("inventory", {})
                inv["evolution_stone"] = inv.get("evolution_stone", 0) + 1
                evo_stone_txt = "\n\n💠 *LUAR BIASA! EVOLUTION STONE DIDAPAT!*\n_(Drop 0.1% — sangat langka!)_"

        _cds(context, user_id)
        save_player(user_id, player)

        boss_txt = "🎊 *BOSS DIKALAHKAN!* Floor naik!\n" if is_boss else ""
        await query.edit_message_text(
            f"🏆 *MENANG!*\n\n"
            f"{boss_txt}"
            f"💀 *{monster['name']}* dikalahkan!\n"
            f"💰 +{gold * (3 if is_boss else 1)} Gold\n"
            f"✨ +{exp} EXP{lv_txt}{drop_txt}{evo_stone_txt}\n\n"
            f"❤️ HP: {player['hp']}/{player['max_hp']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏰 Lanjut Dungeon", callback_data="dungeon_explore"),
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
    if action in ("item_menu", "item_back"):
        # Pakai item tidak memicu serangan balik monster
        pass
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
            mdmg = max(1, base_atk - int(player["def"] * 0.75))
            player["hp"] = max(0, player["hp"] - mdmg)
            berserk_tag = " 🔥BERSERK!" if dstate.get("berserk_active") and is_boss else ""
            log.append(f"{monster['emoji']} -{mdmg} HP{berserk_tag}")

    # ── Boss counter attack ──────────────────────────────────────
    if is_boss and action not in ("potion", "item_menu", "item_back"):
        counter_pct = int(monster.get("counter_pct", 0) * 100)
        if counter_pct > 0 and random.randint(1, 100) <= counter_pct:
            c_dmg = max(1, int(monster["atk"] * 0.5) - int(player["def"] * 0.3))
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
            gold_lost = player.get("coin", 0) // 15
            player["coin"]   = max(0, player.get("coin", 0) - gold_lost)
            player["hp"]     = player["max_hp"] // 3
            player["losses"] = player.get("losses", 0) + 1
            _cds(context, user_id)
            save_player(user_id, player)
            await query.edit_message_text(
                f"💀 *GAME OVER*\n\n"
                f"Dikalahkan oleh {monster['emoji']} *{monster['name']}*!\n"
                f"Kehilangan {gold_lost} Gold",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Kembali", callback_data="dungeon_exit")
                ]])
            )
            return

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
