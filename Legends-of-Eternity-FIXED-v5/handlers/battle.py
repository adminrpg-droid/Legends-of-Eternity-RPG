import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, level_up, is_admin
from monster import get_random_monster
from ui import hp_bar
from handlers.enhance import get_enhance_level, enhance_stat_bonus
from items import GOD_SSSR_BOSS_DROPS, GOD_SSSR_WEAPONS, GOD_SSSR_ARMORS, GOD_SSSR_SKILLS, GOD_SSSR_PETS, RARITY_STARS as _RARITY_STARS


def _bs(ctx, uid):  return ctx.user_data.get(f"b_{uid}", {})

def _get_enhance_atk(player: dict) -> int:
    """Get total ATK including weapon base stat + enhance bonus from weapon."""
    base_atk = player.get("atk", 0)
    wpn_id   = player.get("equipment", {}).get("weapon")
    if wpn_id:
        from items import get_item
        item = get_item(wpn_id)
        if item:
            wpn_atk    = item.get("stats", {}).get("atk", 0)
            enhance_lv = get_enhance_level(player, "weapon")
            # BUG FIX: tambahkan weapon base ATK + enhance bonus
            base_atk += wpn_atk + enhance_stat_bonus(wpn_atk, enhance_lv)
    # Skill enhance bonus (dihitung dari total ATK setelah weapon)
    skill_lv = get_enhance_level(player, "skill")
    if skill_lv > 0:
        base_atk += enhance_stat_bonus(base_atk // 5, skill_lv)
    return base_atk
def _sbs(ctx, uid, s): ctx.user_data[f"b_{uid}"] = s
def _cbs(ctx, uid): ctx.user_data.pop(f"b_{uid}", None)


async def battle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    from database import is_banned
    if is_banned(user.id):
        await update.message.reply_text("🚫 Akunmu di-ban! Hubungi admin.")
        return
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    if player["hp"] <= 0:
        await update.message.reply_text("💀 HP 0! Pulihkan dulu di /equipment (Rest)")
        return
    if player.get("is_resting"):
        await update.message.reply_text("😴 Kamu sedang istirahat! Ketik /rest untuk berhenti istirahat dulu.")
        return

    # ── Cooldown 5 detik mencari monster ──────────────────────────
    admin = is_admin(user.id)
    # BUG FIX: state init lengkap dengan semua key yang dipakai di battle_action_handler
    def _make_state(monster):
        return {
            "monster": monster, "turn": 1, "log": [],
            "death_marked": False, "dot": 0, "dot_turns": 0,
            "monster_status": {}, "status_effects": {},
            "attack_count": 0, "souls": 0,
        }
    if admin:
        # Admin langsung dapat monster
        monster = get_random_monster(player["level"])
        state   = _make_state(monster)
        _sbs(context, user.id, state)
        await _show_battle(update.message, player, state, first=True)
    else:
        # Tampilkan pesan cooldown
        msg = await update.message.reply_text(
            "🔍 *Mencari monster...*\n"
            "⏳ Cooldown 5 detik...",
            parse_mode="Markdown"
        )
        await asyncio.sleep(5)
        monster = get_random_monster(player["level"])
        state   = _make_state(monster)
        _sbs(context, user.id, state)
        try:
            await msg.edit_text(
                f"✅ *Monster ditemukan!*\n"
                f"{monster['emoji']} *{monster['name']}* muncul di hadapanmu!\n\n"
                f"⚔️ Persiapkan dirimu...",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await asyncio.sleep(1)
        await _show_battle(update.message, player, state, first=True)


async def _show_battle(target, player: dict, state: dict, first=False):
    m   = state["monster"]
    log = "\n".join(state["log"][-3:]) if state["log"] else "⚡ Pertempuran dimulai!"

    p_bar = hp_bar(player["hp"], player["max_hp"], 9)
    m_bar = hp_bar(m["current_hp"], m["hp"], 9)

    vip_tag = ""
    if player.get("vip", {}).get("active"):
        vip_tag = " 💎"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║      ⚔️  *PERTEMPURAN!*  ⚔️      ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"🟢 *{player['name']}*{vip_tag} Lv.{player['level']}\n"
        f"❤️ {p_bar}\n"
        f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
        f"⚔️ VS ⚔️\n\n"
        f"{m['emoji']} *{m['name']}*\n"
        f"❤️ {m_bar}\n\n"
        f"📜 *Log:*\n{log}\n\n"
        f"🎮 Giliran #{state['turn']} — Pilih aksi:"
    )

    cd     = player.get("skill_cooldown", 0)
    # Cek skill dari equipment atau bought_skills
    active_skill = _get_active_skill(player)
    s_lbl  = active_skill["name"] if cd == 0 else f"{active_skill['name']} ⏳{cd}"

    # Hitung total consumable yang dimiliki
    inv = player.get("inventory", {})
    _CONS_IDS = ("health_potion", "mana_potion", "elixir", "revive_crystal", "mega_potion")
    total_cons = sum(inv.get(cid, 0) for cid in _CONS_IDS)

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Serang", callback_data="battle_attack"),
            InlineKeyboardButton(s_lbl,       callback_data="battle_skill"),
        ],
        [
            InlineKeyboardButton(f"🎒 Item ({total_cons})", callback_data="battle_item_menu"),
            InlineKeyboardButton("🏃 Kabur",                callback_data="battle_flee"),
        ],
    ]

    markup = InlineKeyboardMarkup(keyboard)
    if first:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


def _get_active_skill(player: dict) -> dict:
    """Dapatkan skill aktif dari equipment atau class default."""
    equipped_skill_id = player.get("equipment", {}).get("skill")
    if equipped_skill_id:
        from items import SHOP_SKILLS, PREMIUM_SKILLS, GOD_SSSR_SKILLS
        sk = SHOP_SKILLS.get(equipped_skill_id)
        if sk:
            return sk
        sk = PREMIUM_SKILLS.get(equipped_skill_id)
        if sk:
            return sk
        sk = GOD_SSSR_SKILLS.get(equipped_skill_id)
        if sk:
            return sk
        # Cek juga dari bought_skills (data lengkap tersimpan di player)
        for entry in player.get("bought_skills", []):
            if isinstance(entry, dict) and entry.get("id") == equipped_skill_id:
                return entry

    # Default: class skill
    return {"name": player.get("skill", "Skill"), "effect": {"dmg_mult": 2.0, "mp_cost": 25}}


async def battle_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    user   = query.from_user
    player = get_player(user.id)
    state  = _bs(context, user.id)

    if not state or not player:
        await query.edit_message_text("❌ Tidak ada pertempuran aktif. /battle")
        return

    action  = query.data.replace("battle_", "")
    monster = state["monster"]
    log     = state["log"]
    admin   = is_admin(user.id)

    # ── Item menu: tampilkan daftar consumable (tanpa cooldown) ───
    if action == "item_menu":
        await _show_item_menu(query, player)
        return

    # ── Use item: pakai consumable tertentu ───────────────────────
    if action.startswith("use_item_"):
        item_id = action.replace("use_item_", "")
        await _use_consumable_in_battle(query, user.id, player, state, item_id)
        _sbs(context, user.id, state)
        return

    # ── Kembali ke battle dari item menu ─────────────────────────
    if action == "item_back":
        await _show_battle(query, player, state)
        return

    # ── Cooldown 3 detik setelah memilih aksi (kecuali admin) ─────
    if not admin and action not in ("flee", "item_menu", "item_back"):
        try:
            base_text = query.message.text or "⚔️ Battle berlangsung..."
            await query.edit_message_text(
                base_text + "\n\n⏳ *Battle sedang dimulai... (3 detik)*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([])
            )
        except Exception:
            pass
        await asyncio.sleep(3)
        # Refresh player setelah sleep
        player = get_player(user.id)
        state  = _bs(context, user.id)
        if not state:
            return
        monster = state["monster"]
        log     = state["log"]

    # Apply pet bonus sebelum kalkulasi damage (salinan sementara)
    player_with_pet = apply_pet_bonus({**player})
    player["atk"]  = player_with_pet.get("atk", player["atk"])
    player["crit"] = player_with_pet.get("crit", player["crit"])

    if action == "flee":
        if random.randint(1, 100) <= 40:
            _cbs(context, user.id)
            await query.edit_message_text(
                "🏃 *Kamu berhasil kabur!*\nLain kali hadapi mereka!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⚔️ Battle Lagi", callback_data="menu")
                ]])
            )
        else:
            log.append("🏃 Gagal kabur! Monster menyerang!")
            _do_monster_attack(player, monster, log, admin)
            state["turn"] += 1
            save_player(user.id, player)
            _sbs(context, user.id, state)
            await _show_battle(query, player, state)
        return

    if action == "potion":
        # Legacy fallback (tidak dipakai lagi, dialihkan ke item_menu)
        await _show_item_menu(query, player)
        return

    elif action == "skill":
        cd = player.get("skill_cooldown", 0)
        if cd > 0 and not admin:
            await query.answer(f"⏳ Skill cooldown {cd} giliran!", show_alert=True)
            return

        active_skill = _get_active_skill(player)
        effect = active_skill.get("effect", {})
        mp_cost = effect.get("mp_cost", 25)
        
        if player["mp"] < mp_cost and not admin:
            await query.answer(f"❌ MP tidak cukup (butuh {mp_cost})!", show_alert=True)
            return

        if not admin:
            player["mp"] -= mp_cost
        
        mult = effect.get("dmg_mult", 2.0)
        if mult == 0:
            mult = random.uniform(1.9, 2.8)
        else:
            mult *= random.uniform(0.9, 1.1)

        # Death Scythe: life steal
        if player["class"] == "reaper":
            dmg = max(1, int(player["atk"] * mult - monster["def"] * 0.4))
            heal_val = dmg // 3
            if not admin:
                player["hp"] = min(player["max_hp"], player["hp"] + heal_val)
            log.append(f"💜 {active_skill['name']}! -{dmg} HP, +{heal_val} HP!")
        # Assassin: death mark
        elif player["class"] == "assassin":
            state["death_marked"] = True
            dmg = max(1, int(player["atk"] * mult * 1.5 - monster["def"] * 0.3))
            log.append(f"💀 {active_skill['name']}! 💥INSTANT! -{dmg} HP!")
        else:
            dmg = max(1, int(player["atk"] * mult - monster["def"] * 0.4))
            log.append(f"✨ {active_skill['name']}! -{dmg} HP 💥")

        monster["current_hp"] -= dmg
        state["last_dmg"] = dmg
        if not admin:
            player["skill_cooldown"] = effect.get("cooldown", 3)

    else:  # attack
        crit_chance = player.get("crit", 10)
        if player.get("vip", {}).get("active"):
            crit_chance += player["vip"].get("effects", {}).get("crit_bonus", 0)

        crit = random.randint(1, 100) <= crit_chance
        mult = 1.6 if crit else 1.0
        if state.get("death_marked"):
            mult *= 2.0
            state["death_marked"] = False

        # Apply berserker ATK boost (Warrior low-hp special)
        berserker = state.get("status_effects", {}).get("berserker")
        berserker_active = berserker and berserker.get("turns", 0) > 0
        if berserker_active:
            mult *= (1.0 + berserker.get("atk_boost", 0.5))
            berserker["turns"] -= 1

        e_atk = _get_enhance_atk(player)
        dmg = max(1, int(e_atk * mult - monster["def"] * 0.7))
        tag = " 💥CRITICAL!" if crit else ""
        if mult >= 3:
            tag += " 🔥DEATH MARK!"
        # BUG FIX #2: cek berserker_active (sebelum turns dikurangi) bukan sesudah
        if berserker_active:
            tag += " 🔥BERSERK!"
        log.append(f"⚔️ Serang! -{dmg} HP{tag}")
        monster["current_hp"] -= dmg
        state["last_dmg"] = dmg

        # Assassin: CRIT procs Bleed
        if crit and player.get("class") == "assassin":
            bleed_dmg = 15
            bleed_turns = 3
            equip = player.get("equipment", {})
            wpn = equip.get("weapon", "")
            if wpn in ("nightshade_sickle", "death_scythe"):
                bleed_dmg = 18
            state.setdefault("monster_status", {})["bleed"] = {"dmg_per_turn": bleed_dmg, "turns": bleed_turns}
            log.append(f"🩸 *BLEED!* Musuh berdarah -{bleed_dmg}/ronde selama {bleed_turns} ronde!")

        # Apply weapon special effect on attack — kirim dmg giliran ini untuk lifesteal
        apply_weapon_special_on_attack(player, state, monster, log, crit, current_dmg=dmg)

        # Apply class special on_attack trigger (misal: Mage Arcane Overload)
        sp_log = get_class_special_effect(player, state, "on_attack")
        if sp_log:
            log.append(sp_log)

        # Consume pending_arcane jika sudah terkumpul (Mage: every 3 attacks)
        if state.get("pending_arcane"):
            state["pending_arcane"] = False
            arcane_dmg = max(1, int(player.get("atk", 10) * 2.5 - monster["def"] * 0.3))
            monster["current_hp"] -= arcane_dmg
            log.append(f"⚡ *ARCANE BURST!* Sihir otomatis meledak! -{arcane_dmg} HP!")

    # DoT damage tick (legacy dot field)
    if state.get("dot_turns", 0) > 0 and action not in ("item_menu", "item_back"):
        dot = state.get("dot", 0)
        monster["current_hp"] -= dot
        state["dot_turns"] -= 1
        log.append(f"☠️ Racun! -{dot} HP pada monster!")

    # ── Tick semua status effect (burn, bleed, poison, dll) ─────
    if action not in ("potion", "item_menu", "item_back"):
        apply_status_effects_to_monster(state, monster, log)

    # Reduce skill cooldown
    if action not in ("skill", "potion", "item_menu", "item_back") and player.get("skill_cooldown", 0) > 0 and not admin:
        player["skill_cooldown"] -= 1

    # ── Monster dies ────────────────────────────────────────────
    if monster["current_hp"] <= 0:
        gold_range = monster.get("gold", (5, 15))
        gold  = random.randint(*gold_range)
        exp   = monster["exp"]

        # Naikkan reward lebih banyak — gold x5, xp x4
        gold  = int(gold * 5.0)
        exp   = int(exp  * 4.0)

        player["coin"]  = player.get("coin", 0) + gold
        player["exp"]   = player.get("exp", 0) + exp
        player["kills"] = player.get("kills", 0) + 1
        # Quest progress
        # Update player stats (untuk leaderboard)
        player["weekly_kills"]        = player.get("weekly_kills", 0) + 1
        player["monthly_kills"]       = player.get("monthly_kills", 0) + 1
        player["weekly_coin_earned"]  = player.get("weekly_coin_earned", 0) + gold
        player["monthly_coin_earned"] = player.get("monthly_coin_earned", 0) + gold
        # Update quest progress (untuk quest_data.progress — terpisah dari stats di atas)
        from handlers.quest import update_quest_progress
        player = update_quest_progress(player, "kills", 1)
        player = update_quest_progress(player, "weekly_kills", 1)
        player = update_quest_progress(player, "weekly_coin_earned", gold)
        # Titles
        from handlers.title import check_and_award_titles
        player, _new_titles = check_and_award_titles(player)

        # ── GOD SSSR Drop (0.1% rate dari boss tier monster) ────────
        god_sssr_txt = ""
        if monster.get("tier", 0) >= 3:  # Hanya monster tier 3+ (boss-like)
            roll = random.randint(1, 1000)  # 0.1% = 1/1000
            if roll == 1:
                char_class = player.get("class", "warrior")
                sssr_pool  = GOD_SSSR_BOSS_DROPS.get(char_class, [])
                if sssr_pool:
                    sssr_id = random.choice(sssr_pool)
                    # Determine item type to store correctly
                    if sssr_id in GOD_SSSR_WEAPONS:
                        sssr_item = GOD_SSSR_WEAPONS[sssr_id]
                        inv = player.setdefault("inventory", {})
                        inv[sssr_id] = inv.get(sssr_id, 0) + 1
                        god_sssr_txt = f"\n\n🔱✨ *[GOD SSSR DROP!]* 🔱✨\n🎁 *{sssr_item['name']}* masuk inventory!\n_(Rate 0.1% — Kamu sangat beruntung! Equip via menu inventory)_"
                    elif sssr_id in GOD_SSSR_ARMORS:
                        sssr_item = GOD_SSSR_ARMORS[sssr_id]
                        inv = player.setdefault("inventory", {})
                        inv[sssr_id] = inv.get(sssr_id, 0) + 1
                        god_sssr_txt = f"\n\n🔱✨ *[GOD SSSR DROP!]* 🔱✨\n🎁 *{sssr_item['name']}* masuk inventory!\n_(Rate 0.1% — Kamu sangat beruntung! Equip via menu inventory)_"
                    elif sssr_id in GOD_SSSR_SKILLS:
                        sssr_item = GOD_SSSR_SKILLS[sssr_id]
                        inv = player.setdefault("inventory", {})
                        inv[sssr_id] = 1
                        player.setdefault("bought_skills", [])
                        if sssr_id not in [s if isinstance(s, str) else s.get("id","") for s in player["bought_skills"]]:
                            player["bought_skills"].append({"id": sssr_id, "name": sssr_item["name"]})
                        god_sssr_txt = f"\n\n🔱✨ *[GOD SSSR DROP!]* 🔱✨\n🎁 Skill *{sssr_item['name']}* ditambahkan!\n_(Rate 0.1% — Kamu sangat beruntung!)_"
                    elif sssr_id in GOD_SSSR_PETS:
                        sssr_item = GOD_SSSR_PETS[sssr_id]
                        player["pet"] = sssr_id
                        player["pet_tier"] = 10
                        god_sssr_txt = f"\n\n🔱✨ *[GOD SSSR DROP!]* 🔱✨\n🎁 Pet *{sssr_item['name']}* didapatkan!\n_(Rate 0.1% — Kamu sangat beruntung!)_"

        # ── Class Special: on_kill triggers ─────────────────────
        kill_special_txt = ""
        char_class = player.get("class", "warrior")

        # Reaper: Soul Reap on kill
        # BUG FIX #1: Soul hanya di-increment SATU kali di sini.
        # get_class_special_effect("on_kill") tidak dipanggil agar tidak double-increment.
        if char_class == "reaper":
            state["souls"] = state.get("souls", 0) + 1
            heal_soul = int(player["max_hp"] * 0.15)
            player["hp"] = min(player["max_hp"], player["hp"] + heal_soul)
            kill_special_txt = f"\n☠️ *SOUL REAP!* +1 Soul ({state['souls']}/5) | +{heal_soul} HP!"
            if state["souls"] >= 5:
                state["souls"] = 0
                kill_special_txt += "\n💀 *HARVEST!* Musuh menerima pukulan maut!"

        # Assassin: first_kill Shadow Execution
        elif char_class == "assassin" and not state.get("first_kill_used"):
            state["first_kill_used"] = True
            heal_exe = int(player["max_hp"] * 0.25)
            player["hp"] = min(player["max_hp"], player["hp"] + heal_exe)
            state["death_marked"] = True
            kill_special_txt = f"\n🩸 *SHADOW EXECUTION!* +{heal_exe} HP | Next attack x3 DMG!"

        player, leveled, levels_up = level_up(player)
        _cbs(context, user.id)
        save_player(user.id, player)

        lv_txt = f"\n🎊 *LEVEL UP!* Lv.{player['level']} (+{levels_up})" if leveled else ""
        await query.edit_message_text(
            f"🏆 *MENANG!*\n\n"
            f"💀 *{monster['name']}* dikalahkan!\n"
            f"🪙 +{gold} Gold\n"
            f"✨ +{exp} EXP{lv_txt}{kill_special_txt}{god_sssr_txt}\n\n"
            f"❤️ HP: {player['hp']}/{player['max_hp']}\n"
            f"🪙 Total Gold: {player.get('coin',0):,}\n\n"
            f"☠️ *Monster telah mati!*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⚔️ Battle Lagi", callback_data="menu"),
                    InlineKeyboardButton("📜 Profile", callback_data="profile"),
                ]
            ])
        )
        return

    # ── Monster attacks back ─────────────────────────────────────
    # Cek stun: jika monster terstun, skip serangan & kurangi turn stun
    monster_status = state.get("monster_status", {})
    stun_data = monster_status.get("stun")
    if stun_data and stun_data.get("turns", 0) > 0:
        log.append(f"⚡ {monster['emoji']} TERSTUN! Serangan dilewati!")
        stun_data["turns"] -= 1
        if stun_data["turns"] <= 0:
            del monster_status["stun"]
        state["monster_status"] = monster_status
    else:
        _do_monster_attack(player, monster, log, admin)
    state["turn"] += 1

    if player["hp"] <= 0 and not admin:
        await _handle_player_death(query, player, monster, context, user.id)
        return

    # Apply low_hp class special trigger (e.g. Warrior Berserker Rage)
    low_hp_log = get_class_special_effect(player, state, "low_hp")
    if low_hp_log:
        log.append(low_hp_log)

    save_player(user.id, player)
    _sbs(context, user.id, state)
    await _show_battle(query, player, state)


def _do_monster_attack(player: dict, monster: dict, log: list, admin: bool = False):
    if admin:
        log.append(f"{monster['emoji']} Serang! (Admin tidak terkena damage)")
        return
    dodge = min(50, player.get("spd", 10) * 2)
    if random.randint(1, 100) <= dodge:
        log.append("💨 Kamu menghindar!")
        return
    mdmg = max(1, monster["atk"] - int(player["def"] * 0.75))
    player["hp"] = max(0, player["hp"] - mdmg)
    log.append(f"{monster['emoji']} Serang! -{mdmg} HP")


async def _handle_player_death(query, player, monster, context, user_id):
    revives = player.get("inventory", {}).get("revive_crystal", 0)
    if revives > 0:
        player["hp"] = player["max_hp"] // 2
        player["inventory"]["revive_crystal"] -= 1
        save_player(user_id, player)
        state = _bs(context, user_id)
        state["log"].append("💠 Revive Crystal aktif! HP dipulihkan!")
        _sbs(context, user_id, state)
        await _show_battle(query, player, state)
        return

    gold_lost = player.get("coin", 0) // 15
    player["coin"]   = max(0, player.get("coin", 0) - gold_lost)
    player["hp"]     = player["max_hp"] // 3
    player["losses"] = player.get("losses", 0) + 1
    _cbs(context, user_id)
    save_player(user_id, player)

    await query.edit_message_text(
        f"💀 *GAME OVER*\n\n"
        f"Kamu dikalahkan oleh {monster['emoji']} *{monster['name']}*!\n"
        f"🪙 Kehilangan {gold_lost} Gold\n"
        f"❤️ HP dipulihkan ke {player['hp']}/{player['max_hp']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Coba Lagi", callback_data="menu")]
        ])
    )


# ════════════════════════════════════════════════════════════════
#  STATUS EFFECT & CLASS SPECIAL INTEGRATION
# ════════════════════════════════════════════════════════════════
def apply_pet_bonus(player: dict) -> dict:
    """Apply pet passive stats to battle player copy."""
    from items import PET_SHOP, PET_EVOLUTION_TIERS
    pet_id = player.get("pet")
    if not pet_id:
        return player
    pet = PET_SHOP.get(pet_id)
    if not pet:
        return player

    pet_tier = player.get("pet_tier", 1)
    tier_info = PET_EVOLUTION_TIERS.get(pet_tier, PET_EVOLUTION_TIERS[1])
    mult = tier_info["stat_mult"]

    effect = pet.get("effect", {})
    player["atk"] += int(effect.get("atk_bonus", 0) * mult)
    player["def"] += int(effect.get("def_bonus", 0) * mult)
    player["spd"] += int(effect.get("spd_bonus", 0) * mult)
    player["crit"] = player.get("crit", 10) + int(effect.get("crit_bonus", 0) * mult)
    if effect.get("hp_bonus"):
        bonus_hp = int(effect["hp_bonus"] * mult)
        player["max_hp"] += bonus_hp
        player["hp"] = min(player["hp"] + bonus_hp, player["max_hp"])
    return player


def get_class_special_effect(player: dict, state: dict, trigger: str) -> str:
    """Check and apply class special effects. Returns log message or empty string."""
    from items import CLASS_SPECIALS
    char_class = player.get("class", "warrior")
    special = CLASS_SPECIALS.get(char_class)
    if not special:
        return ""

    effect = special.get("effect", {})
    log = ""

    if trigger == "low_hp" and special.get("trigger") == "low_hp":
        if player["hp"] < player["max_hp"] * 0.30:
            if not state.get("special_triggered"):
                state["special_triggered"] = True
                state["status_effects"] = state.get("status_effects", {})
                state["status_effects"]["berserker"] = {"turns": 3, "atk_boost": effect.get("atk_bonus_pct", 0.5)}
                log = f"🔥 *BERSERKER RAGE!* ATK +50% selama 3 ronde!"

    elif trigger == "on_attack" and special.get("trigger") == "every_3_attacks":
        state["attack_count"] = state.get("attack_count", 0) + 1
        if state["attack_count"] % 3 == 0:
            state["pending_arcane"] = True
            log = f"⚡ *ARCANE OVERLOAD!* Sihir otomatis siap!"

    elif trigger == "on_kill" and special.get("trigger") == "on_kill":
        if char_class == "reaper":
            state["souls"] = state.get("souls", 0) + 1
            heal = int(player["max_hp"] * effect.get("heal_pct", 0.15))
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            log = f"☠️ *SOUL REAP!* +1 Soul ({state['souls']}/5) | Heal +{heal} HP!"
            if state["souls"] >= 5:
                state["souls"] = 0
                log += f"\n💀 *HARVEST!* Semua musuh menerima pukulan maut!"

    return log


def apply_status_effects_to_monster(state: dict, monster: dict, log: list):
    """Tick DoT effects on monster each turn."""
    effects = state.get("monster_status", {})
    to_remove = []
    for eff_name, eff_data in effects.items():
        turns = eff_data.get("turns", 0)
        if turns <= 0:
            to_remove.append(eff_name)
            continue
        dot = eff_data.get("dmg_per_turn", 0)
        if dot > 0:
            monster["current_hp"] -= dot
            log.append(f"⚗️ {eff_name.title()}: -{dot} HP pada monster!")
        eff_data["turns"] -= 1
    for e in to_remove:
        del effects[e]


def apply_weapon_special_on_attack(player: dict, state: dict, monster: dict, log: list, is_crit: bool, current_dmg: int = 0):
    """Check equipped weapon's special_effect on attack."""
    from items import ALL_ITEMS
    eq_weapon = player.get("equipment", {}).get("weapon")
    if not eq_weapon:
        return
    item = ALL_ITEMS.get(eq_weapon, {})
    special = item.get("special_effect", {})
    if not special:
        return

    monster_status = state.get("monster_status", {})

    # Burn on attack
    if "on_attack" in special and special["on_attack"] == "burn":
        turns = special.get("burn_turns", 2)
        dmg = special.get("burn_dmg", 8)
        monster_status["burn"] = {"dmg_per_turn": dmg, "turns": turns}
        log.append(f"🔥 *Weapon Special!* Burn aktif! -{dmg} HP/ronde selama {turns} ronde")

    # Lifesteal — BUG FIX: gunakan current_dmg (damage giliran ini), bukan last_dmg (giliran lalu)
    if "lifesteal_pct" in special:
        steal = int(current_dmg * special["lifesteal_pct"])
        if steal > 0:
            player["hp"] = min(player["max_hp"], player["hp"] + steal)
            log.append(f"🩸 *Life Steal!* +{steal} HP")

    # On crit effects
    if is_crit and "on_crit" in special:
        eff = special["on_crit"]
        if eff == "bleed":
            monster_status["bleed"] = {"dmg_per_turn": 15, "turns": 3}
            log.append("🩸 *CRIT — Bleed!* -15 HP/ronde selama 3 ronde")
        elif eff == "stun":
            monster_status["stun"] = {"turns": 1, "skip_turn": True}
            log.append("⚡ *CRIT — STUN!* Monster terstun 1 ronde!")
        elif eff == "poison":
            dmg = special.get("poison_dmg", 12)
            turns = special.get("poison_turns", 3)
            monster_status["poison"] = {"dmg_per_turn": dmg, "turns": turns}
            log.append(f"☠️ *CRIT — Poison!* -{dmg} HP/ronde selama {turns} ronde")

    state["monster_status"] = monster_status


# ════════════════════════════════════════════════════════════════
#  ITEM MENU IN BATTLE
# ════════════════════════════════════════════════════════════════
_BATTLE_CONSUMABLES = {
    "health_potion": {"name": "⚕️ Health Potion",  "effect": {"hp": 60}},
    "mana_potion":   {"name": "🔵 Mana Potion",    "effect": {"mp": 50}},
    "elixir":        {"name": "⚗️ Grand Elixir",   "effect": {"hp": 150, "mp": 120}},
    "mega_potion":   {"name": "🌟 Mega Potion",    "effect": {"hp": 9999}},
    "revive_crystal":{"name": "💠 Revive Crystal", "effect": {}},
}


async def _show_item_menu(query, player: dict):
    """Tampilkan daftar consumable yang dimiliki player saat battle."""
    inv = player.get("inventory", {})
    buttons = []
    lines = ["🎒 *PILIH ITEM YANG INGIN DIPAKAI*\n_(Item tidak memicu serangan balik monster)_\n"]

    for item_id, item_info in _BATTLE_CONSUMABLES.items():
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
            callback_data=f"battle_use_item_{item_id}"
        )])

    if not buttons:
        lines.append("\n❌ *Tidak ada item yang bisa dipakai!*")
        buttons.append([InlineKeyboardButton("⬅️ Kembali ke Battle", callback_data="battle_item_back")])
    else:
        buttons.append([InlineKeyboardButton("⬅️ Kembali ke Battle", callback_data="battle_item_back")])

    text = "\n".join(lines)
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def _use_consumable_in_battle(query, user_id: int, player: dict, state: dict, item_id: str):
    """Proses pemakaian consumable saat battle."""
    item_info = _BATTLE_CONSUMABLES.get(item_id)
    if not item_info:
        await query.answer("❌ Item tidak dikenal!", show_alert=True)
        return

    inv = player.get("inventory", {})
    qty = inv.get(item_id, 0)
    if qty <= 0:
        await query.answer(f"❌ {item_info['name']} habis!", show_alert=True)
        await _show_item_menu(query, player)
        return

    eff = item_info["effect"]
    log = state["log"]
    result_parts = []

    # Heal HP
    if eff.get("hp"):
        heal = eff["hp"]
        before_hp = player["hp"]
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        actual_heal = player["hp"] - before_hp
        if player["hp"] >= player["max_hp"]:
            result_parts.append(f"❤️ HP pulih penuh!")
        else:
            result_parts.append(f"❤️ +{actual_heal} HP")

    # Restore MP
    if eff.get("mp"):
        before_mp = player["mp"]
        player["mp"] = min(player["max_mp"], player["mp"] + eff["mp"])
        actual_mp = player["mp"] - before_mp
        result_parts.append(f"💙 +{actual_mp} MP")

    # Revive crystal: pasif saat mati, tidak langsung efek
    if item_id == "revive_crystal":
        result_parts.append("💠 Revive Crystal siap — akan aktif saat HP 0!")

    inv[item_id] -= 1
    result_str = ", ".join(result_parts) if result_parts else "Digunakan"
    log.append(f"🎒 {item_info['name']} dipakai! {result_str}")

    state["turn"] += 1
    save_player(user_id, player)
    # state dimodifikasi in-place, caller sudah menyimpannya via _sbs sebelumnya

    await _show_battle(query, player, state)
