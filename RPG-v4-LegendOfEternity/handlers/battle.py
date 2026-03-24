import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, level_up
from monster import get_random_monster
from ui import hp_bar


def _bs(ctx, uid):  return ctx.user_data.get(f"b_{uid}", {})
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
        await update.message.reply_text("💀 HP 0! Pulihkan di /inventory")
        return

    monster = get_random_monster(player["level"])
    state   = {"monster": monster, "turn": 1, "log": [], "death_marked": False}
    _sbs(context, user.id, state)
    await _show_battle(update.message, player, state, first=True)


async def _show_battle(target, player: dict, state: dict, first=False):
    m   = state["monster"]
    log = "\n".join(state["log"][-3:]) if state["log"] else "⚡ Pertempuran dimulai!"

    p_bar = hp_bar(player["hp"], player["max_hp"], 9)
    m_bar = hp_bar(m["current_hp"], m["hp"], 9)

    crit   = player.get("crit", 10)
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
    s_lbl  = player["skill"] if cd == 0 else f"{player['skill']} ⏳{cd}"
    pot    = player.get("inventory", {}).get("health_potion", 0)

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Serang", callback_data="battle_attack"),
            InlineKeyboardButton(s_lbl,       callback_data="battle_skill"),
        ],
        [
            InlineKeyboardButton(f"🧪 Potion ({pot})", callback_data="battle_potion"),
            InlineKeyboardButton("🏃 Kabur",            callback_data="battle_flee"),
        ],
    ]

    markup = InlineKeyboardMarkup(keyboard)
    if first:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


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
            _do_monster_attack(player, monster, log)
            state["turn"] += 1
            save_player(user.id, player)
            _sbs(context, user.id, state)
            await _show_battle(query, player, state)
        return

    if action == "potion":
        pot = player.get("inventory", {}).get("health_potion", 0)
        if pot <= 0:
            await query.answer("❌ Potion habis!", show_alert=True)
            return
        heal = 60
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        player["inventory"]["health_potion"] -= 1
        log.append(f"🧪 Minum potion +{heal} HP!")

    elif action == "skill":
        cd = player.get("skill_cooldown", 0)
        if cd > 0:
            await query.answer(f"⏳ Skill cooldown {cd} giliran!", show_alert=True)
            return
        if player["mp"] < 25:
            await query.answer("❌ MP tidak cukup (butuh 25)!", show_alert=True)
            return

        player["mp"] -= 25
        mult = random.uniform(1.9, 2.8)
        # Necromancer: life steal
        if player["class"] == "necromancer":
            dmg = max(1, int(player["atk"] * mult - monster["def"] * 0.4))
            heal_val = dmg // 3
            player["hp"] = min(player["max_hp"], player["hp"] + heal_val)
            log.append(f"💜 {player['skill']}! -{dmg} HP, +{heal_val} HP!")
        # Assassin: death mark
        elif player["class"] == "assassin":
            state["death_marked"] = True
            dmg = max(1, int(player["atk"] * mult * 1.5 - monster["def"] * 0.3))
            log.append(f"💀 {player['skill']}! 💥INSTANT! -{dmg} HP!")
        else:
            dmg = max(1, int(player["atk"] * mult - monster["def"] * 0.4))
            log.append(f"✨ {player['skill']}! -{dmg} HP 💥")

        monster["current_hp"] -= dmg
        player["skill_cooldown"] = 3

    else:  # attack
        crit_chance = player.get("crit", 10)
        if player.get("vip", {}).get("active"):
            crit_chance += player["vip"].get("effects", {}).get("crit_bonus", 0)

        crit = random.randint(1, 100) <= crit_chance
        mult = 1.6 if crit else 1.0
        # Death mark doubles next attack
        if state.get("death_marked"):
            mult *= 2.0
            state["death_marked"] = False
        dmg = max(1, int(player["atk"] * mult - monster["def"] * 0.7))
        tag = " 💥CRITICAL!" if crit else ""
        if mult >= 3:
            tag += " 🔥DEATH MARK!"
        log.append(f"⚔️ Serang! -{dmg} HP{tag}")
        monster["current_hp"] -= dmg

    # Reduce skill cooldown
    if action != "skill" and player.get("skill_cooldown", 0) > 0:
        player["skill_cooldown"] -= 1

    # ── Monster dies ────────────────────────────────────────────
    if monster["current_hp"] <= 0:
        gold_range = monster.get("gold", (5, 15))
        gold  = random.randint(*gold_range)
        exp   = monster["exp"]

        # Reduced income per request
        gold  = int(gold * 0.7)
        exp   = int(exp  * 0.8)

        player["coin"]  = player.get("coin", 0) + gold
        player["exp"]   += exp
        player["kills"] += 1

        player, leveled, levels_up = level_up(player)
        _cbs(context, user.id)
        save_player(user.id, player)

        lv_txt = f"\n🎊 *LEVEL UP!* Lv.{player['level']} (+{levels_up})" if leveled else ""
        await query.edit_message_text(
            f"🏆 *MENANG!*\n\n"
            f"💀 *{monster['name']}* dikalahkan!\n"
            f"💰 +{gold} Coin\n"
            f"✨ +{exp} EXP{lv_txt}\n\n"
            f"❤️ HP: {player['hp']}/{player['max_hp']}\n"
            f"💰 Total Coin: {player.get('coin',0)}",
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
    _do_monster_attack(player, monster, log)
    state["turn"] += 1

    if player["hp"] <= 0:
        await _handle_player_death(query, player, monster, context, user.id)
        return

    save_player(user.id, player)
    _sbs(context, user.id, state)
    await _show_battle(query, player, state)


def _do_monster_attack(player: dict, monster: dict, log: list):
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
    player["losses"] += 1
    _cbs(context, user_id)
    save_player(user_id, player)

    await query.edit_message_text(
        f"💀 *GAME OVER*\n\n"
        f"Kamu dikalahkan oleh {monster['emoji']} *{monster['name']}*!\n"
        f"💰 Kehilangan {gold_lost} Coin\n"
        f"❤️ HP dipulihkan ke {player['hp']}/{player['max_hp']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Coba Lagi", callback_data="menu")]
        ])
    )
