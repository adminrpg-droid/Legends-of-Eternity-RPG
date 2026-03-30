import random
import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, is_admin, is_banned

# ── PVP Sessions per grup {chat_id: session} ────────────────────
_PVP_SESSIONS = {}

CHALLENGE_TIMEOUT = 60   # detik untuk menerima tantangan
BATTLE_DELAY      = 2    # detik antar ronde


def _get_pvp(chat_id: int) -> dict:
    return _PVP_SESSIONS.get(chat_id, {})

def _set_pvp(chat_id: int, s: dict):
    _PVP_SESSIONS[chat_id] = s

def _del_pvp(chat_id: int):
    _PVP_SESSIONS.pop(chat_id, None)


# ════════════════════════════════════════════════════════════════
#  HELPER: HP BAR & STATUS BADGE
# ════════════════════════════════════════════════════════════════
def _hp_bar(current: int, max_val: int, length: int = 10) -> str:
    if max_val <= 0:
        return "░" * length
    ratio  = max(0.0, min(1.0, current / max_val))
    filled = int(ratio * length)
    bar    = "█" * filled + "░" * (length - filled)
    pct    = int(ratio * 100)
    if pct > 60:
        color = "🟢"
    elif pct > 30:
        color = "🟡"
    else:
        color = "🔴"
    return f"{color} `{bar}` {max(0,current):,}/{max_val:,} ({pct}%)"


def _mp_bar(current: int, max_val: int, length: int = 8) -> str:
    if max_val <= 0:
        return "░" * length
    ratio  = max(0.0, min(1.0, current / max_val))
    filled = int(ratio * length)
    bar    = "▓" * filled + "░" * (length - filled)
    return f"💙 `{bar}` {current}/{max_val}"


def _status_icon(hp: int) -> str:
    if hp <= 0:
        return "💀"
    return "⚔️"


# ════════════════════════════════════════════════════════════════
#  HELPER: BANGUN TEKS PERTARUNGAN LIVE
# ════════════════════════════════════════════════════════════════
def _build_pvp_battle_text(
    attacker: dict, defender: dict,
    a_hp: int, d_hp: int,
    a_mp: int, d_mp: int,
    a_max: int, d_max: int,
    a_max_mp: int, d_max_mp: int,
    round_num: int,
    log_lines: list,
    status: str = "running"
) -> str:
    a_hp_bar = _hp_bar(a_hp, a_max)
    d_hp_bar = _hp_bar(d_hp, d_max)
    a_mp_bar = _mp_bar(a_mp, a_max_mp)
    d_mp_bar = _mp_bar(d_mp, d_max_mp)
    a_icon = _status_icon(a_hp)
    d_icon = _status_icon(d_hp)
    recent_log = "\n".join(log_lines[-8:]) if log_lines else "⚔️ Pertempuran segera dimulai..."
    if status == "running":
        title_line = "║  ⚔️  *PVP BERLANGSUNG!*  ⚔️"
    else:
        title_line = "║  🏁  *PVP SELESAI!*  🏁"

    return (
        f"╔══════════════════════════════════╗\n"
        f"{title_line}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🔢 *Ronde: {round_num}*  |  Mode: 1v1 Grup\n"
        f"╚══════════════════════════════════╝\n\n"
        f"🗡️ *{attacker['name']}*  Lv.{attacker.get('level', 1)}"
        f"  [{attacker.get('class', 'warrior').replace('_',' ').title()}]\n"
        f"  {a_icon} HP: {a_hp_bar}\n"
        f"  {a_mp_bar}  |  ⚔️ATK: `{attacker.get('atk',10)}`  🛡️DEF: `{attacker.get('def',5)}`  💨SPD: `{attacker.get('spd',10)}`\n\n"
        f"      ╔════════════╗\n"
        f"      ║    ⚔️ VS ⚔️    ║\n"
        f"      ╚════════════╝\n\n"
        f"🛡️ *{defender['name']}*  Lv.{defender.get('level', 1)}"
        f"  [{defender.get('class', 'warrior').replace('_',' ').title()}]\n"
        f"  {d_icon} HP: {d_hp_bar}\n"
        f"  {d_mp_bar}  |  ⚔️ATK: `{defender.get('atk',10)}`  🛡️DEF: `{defender.get('def',5)}`  💨SPD: `{defender.get('spd',10)}`\n\n"
        f"╔══════════════════════════════════╗\n"
        f"║  📜  *LOG PERTARUNGAN*\n"
        f"╚══════════════════════════════════╝\n"
        f"{recent_log}"
    )


# ════════════════════════════════════════════════════════════════
#  ENTRY: /pvp [@username|reply]
# ════════════════════════════════════════════════════════════════
async def pvp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    msg  = update.message

    if chat.type not in ("group", "supergroup"):
        await msg.reply_text("⚔️ PVP hanya bisa dilakukan di *grup*!", parse_mode="Markdown")
        return

    if is_banned(user.id):
        await msg.reply_text("🚫 Akunmu di-ban!")
        return

    attacker = get_player(user.id)
    if not attacker:
        await msg.reply_text("❌ Ketik /start dulu untuk membuat karakter!")
        return

    if attacker.get("is_resting"):
        await msg.reply_text("😴 Kamu sedang istirahat! Gunakan /rest untuk bangun.")
        return

    sess = _get_pvp(chat.id)
    if sess and sess.get("status") in ("waiting", "running"):
        await msg.reply_text("⚠️ Sudah ada pertarungan PVP aktif di grup ini!")
        return

    target_user = None
    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
    elif context.args and msg.entities:
        mention_used = False
        for entity in msg.entities:
            if entity.type == "text_mention" and entity.user:
                target_user = entity.user
                break
            elif entity.type == "mention":
                mention_used = True
                break
        if mention_used and not target_user:
            await msg.reply_text(
                "⚠️ *Mention @username tidak bisa diproses langsung.*\n\n"
                "Gunakan cara ini:\n"
                "➡️ *Reply* pesan pemain target, lalu ketik `/pvp`",
                parse_mode="Markdown"
            )
            return

    if not target_user or target_user.id == user.id:
        await msg.reply_text(
            "⚔️ *CARA MENANTANG PVP:*\n\n"
            "Reply pesan pemain lain dengan `/pvp`\n"
            "atau: `/pvp @username`\n\n"
            "_Contoh: reply pesan lawan lalu ketik /pvp_",
            parse_mode="Markdown"
        )
        return

    if target_user.is_bot:
        await msg.reply_text("❌ Tidak bisa menantang bot!")
        return

    if is_banned(target_user.id):
        await msg.reply_text("❌ Pemain tersebut di-ban!")
        return

    defender = get_player(target_user.id)
    if not defender:
        await msg.reply_text(f"❌ *{target_user.first_name}* belum punya karakter!", parse_mode="Markdown")
        return

    if defender.get("is_resting"):
        await msg.reply_text(f"😴 *{defender['name']}* sedang istirahat!", parse_mode="Markdown")
        return

    if attacker.get("hp", 1) <= 0:
        await msg.reply_text("❌ HP kamu 0! Pulihkan dulu sebelum PVP.", parse_mode="Markdown")
        return
    if defender.get("hp", 1) <= 0:
        await msg.reply_text(f"❌ *{defender['name']}* HP-nya 0! Tidak bisa ditantang.", parse_mode="Markdown")
        return

    _set_pvp(chat.id, {
        "status":      "waiting",
        "attacker_id": user.id,
        "defender_id": target_user.id,
        "chat_id":     chat.id,
        "created_at":  time.time(),
        "msg_id":      None,
    })

    a_hp_bar = _hp_bar(attacker.get("hp", attacker.get("max_hp", 100)), attacker.get("max_hp", 100), 8)
    d_hp_bar = _hp_bar(defender.get("hp", defender.get("max_hp", 100)), defender.get("max_hp", 100), 8)

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   ⚔️  *TANTANGAN PVP!*  ⚔️        ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  Mode: *1v1 Pertarungan Grup*\n"
        f"╚══════════════════════════════════╝\n\n"
        f"🗡️ *PENANTANG*\n"
        f"  {attacker['emoji']} *{attacker['name']}*  Lv.{attacker['level']}\n"
        f"  [{attacker.get('class','warrior').replace('_',' ').title()}]\n"
        f"  HP: {a_hp_bar}\n"
        f"  ⚔️ATK: `{attacker.get('atk',10)}`  🛡️DEF: `{attacker.get('def',5)}`"
        f"  💨SPD: `{attacker.get('spd',10)}`  🎯CRIT: `{attacker.get('crit',10)}%`\n\n"
        f"      ╔═══════╗\n"
        f"      ║ ⚔️ VS ⚔️ ║\n"
        f"      ╚═══════╝\n\n"
        f"🛡️ *YANG DITANTANG*\n"
        f"  {defender['emoji']} *{defender['name']}*  Lv.{defender['level']}\n"
        f"  [{defender.get('class','warrior').replace('_',' ').title()}]\n"
        f"  HP: {d_hp_bar}\n"
        f"  ⚔️ATK: `{defender.get('atk',10)}`  🛡️DEF: `{defender.get('def',5)}`"
        f"  💨SPD: `{defender.get('spd',10)}`  🎯CRIT: `{defender.get('crit',10)}%`\n\n"
        f"💬 {target_user.mention_markdown()}, apakah kamu menerima tantangan ini?\n\n"
        f"⏳ Tantangan berakhir dalam *{CHALLENGE_TIMEOUT} detik*"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Terima Tantangan", callback_data=f"pvp_accept_{chat.id}"),
            InlineKeyboardButton("❌ Tolak",            callback_data=f"pvp_decline_{chat.id}"),
        ]
    ])
    sent = await msg.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

    sess = _get_pvp(chat.id)
    sess["msg_id"] = sent.message_id
    _set_pvp(chat.id, sess)

    asyncio.create_task(_expire_pvp(context, chat.id, sent.message_id))


async def _expire_pvp(context, chat_id: int, msg_id: int):
    await asyncio.sleep(CHALLENGE_TIMEOUT)
    sess = _get_pvp(chat_id)
    if sess and sess.get("status") == "waiting":
        _del_pvp(chat_id)
        try:
            await context.bot.edit_message_text(
                "⏳ *Tantangan PVP kedaluwarsa!* Tidak ada yang merespons.",
                chat_id=chat_id, message_id=msg_id, parse_mode="Markdown"
            )
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════
#  CALLBACK: pvp_accept / pvp_decline
# ════════════════════════════════════════════════════════════════
async def pvp_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    action = query.data
    user   = query.from_user
    chat   = query.message.chat

    if action.startswith("pvp_decline_"):
        chat_id = int(action.replace("pvp_decline_", ""))
        sess    = _get_pvp(chat_id)
        if not sess:
            await query.edit_message_text("⚠️ Sesi PVP tidak ditemukan.")
            return
        if user.id not in (sess["attacker_id"], sess["defender_id"]):
            await query.answer("❌ Bukan urusanmu!", show_alert=True)
            return
        _del_pvp(chat_id)
        await query.edit_message_text(
            "╔══════════════════════════════════╗\n"
            "║   ❌  *TANTANGAN DITOLAK!*         ║\n"
            "╚══════════════════════════════════╝\n\n"
            "Tantangan PVP telah ditolak. Tidak ada pertarungan.",
            parse_mode="Markdown"
        )
        return

    if action.startswith("pvp_accept_"):
        chat_id  = int(action.replace("pvp_accept_", ""))
        sess     = _get_pvp(chat_id)
        if not sess or sess.get("status") != "waiting":
            await query.edit_message_text("⚠️ Sesi PVP tidak valid atau sudah berakhir.")
            return

        if user.id != sess["defender_id"]:
            await query.answer("❌ Hanya yang ditantang yang bisa menerima!", show_alert=True)
            return

        sess["status"] = "running"
        _set_pvp(chat_id, sess)

        attacker = get_player(sess["attacker_id"])
        defender = get_player(sess["defender_id"])

        if not attacker or not defender:
            _del_pvp(chat_id)
            await query.edit_message_text("❌ Data pemain tidak valid.")
            return

        a_hp = attacker.get("hp", attacker.get("max_hp", 100))
        d_hp = defender.get("hp", defender.get("max_hp", 100))
        a_max = attacker.get("max_hp", 100)
        d_max = defender.get("max_hp", 100)
        a_mp = attacker.get("mp", attacker.get("max_mp", 50))
        d_mp = defender.get("mp", defender.get("max_mp", 50))
        a_max_mp = attacker.get("max_mp", 50)
        d_max_mp = defender.get("max_mp", 50)

        init_text = _build_pvp_battle_text(
            attacker, defender,
            a_hp, d_hp, a_mp, d_mp,
            a_max, d_max, a_max_mp, d_max_mp,
            round_num=0,
            log_lines=["⚔️ Tantangan diterima! Memuat data petarung..."],
            status="running"
        )
        await query.edit_message_text(init_text, parse_mode="Markdown")
        await asyncio.sleep(1)
        await _run_pvp_battle(context, chat_id, query.message, attacker, defender, sess)


# ════════════════════════════════════════════════════════════════
#  BATTLE ENGINE
# ════════════════════════════════════════════════════════════════
def _calc_damage(attacker: dict, defender: dict, a_mp: int) -> tuple:
    base_atk  = attacker.get("atk", 10)
    defense   = defender.get("def", 5)
    crit_pct  = attacker.get("crit", 10)

    vip = attacker.get("vip", {})
    if vip.get("active"):
        effects = vip.get("effects", {})
        base_atk += effects.get("atk_bonus", 0)

    damage   = max(1, base_atk - int(defense * 0.6) + random.randint(-5, 10))
    is_crit  = random.randint(1, 100) <= crit_pct
    if is_crit:
        damage = int(damage * 1.5)

    skill_used  = False
    skill_name  = ""
    mp_used     = 0
    if a_mp >= 25 and random.random() < 0.30:
        skill_bonus = int(base_atk * 0.4)
        damage += skill_bonus
        skill_used = True
        mp_used    = 25
        equip = attacker.get("equipment", {})
        skill_id = equip.get("skill", "")
        if skill_id:
            try:
                from items import SHOP_SKILLS, PREMIUM_SKILLS, GOD_SSSR_SKILLS
                sk = (SHOP_SKILLS.get(skill_id)
                      or PREMIUM_SKILLS.get(skill_id)
                      or GOD_SSSR_SKILLS.get(skill_id))
                skill_name = sk.get("name", "Skill") if sk else "Skill"
            except Exception:
                skill_name = "Skill"
        if not skill_name:
            skill_name = attacker.get("skill", "Skill Aktif")

    return max(1, damage), is_crit, skill_used, skill_name, mp_used


async def _run_pvp_battle(context, chat_id: int, message, attacker: dict, defender: dict, sess: dict):
    a_hp     = attacker.get("hp", attacker.get("max_hp", 100))
    d_hp     = defender.get("hp", defender.get("max_hp", 100))
    a_max    = attacker.get("max_hp", 100)
    d_max    = defender.get("max_hp", 100)
    a_mp     = attacker.get("mp", attacker.get("max_mp", 50))
    d_mp     = defender.get("mp", defender.get("max_mp", 50))
    a_max_mp = attacker.get("max_mp", 50)
    d_max_mp = defender.get("max_mp", 50)

    log_lines = []
    round_num = 0
    MAX_ROUNDS = 20

    a_spd   = attacker.get("spd", 10)
    d_spd   = defender.get("spd", 10)
    a_first = a_spd >= d_spd

    if a_first:
        log_lines.append(f"⚡ *{attacker['name']}* lebih cepat! (SPD {a_spd} vs {d_spd}) — Menyerang duluan!")
    else:
        log_lines.append(f"⚡ *{defender['name']}* lebih cepat! (SPD {d_spd} vs {a_spd}) — Menyerang duluan!")

    msg_id = message.message_id

    while a_hp > 0 and d_hp > 0 and round_num < MAX_ROUNDS:
        round_num += 1
        log_lines.append(f"\n🔔 *── Ronde {round_num} ──*")

        if a_first:
            dmg, crit, skill, sname, mp_cost = _calc_damage(attacker, defender, a_mp)
            d_hp   -= dmg
            a_mp    = max(0, a_mp - mp_cost)
            tags    = []
            if crit:  tags.append("⚡CRIT!")
            if skill: tags.append(f"🔮{sname}!")
            tag_str = "  " + "  ".join(tags) if tags else ""
            log_lines.append(
                f"  🗡️ *{attacker['name']}* menyerang *{defender['name']}*\n"
                f"      💥 `-{dmg}` HP{tag_str}\n"
                f"      ❤️ HP tersisa: `{max(0,d_hp):,}/{d_max:,}`"
            )
            if d_hp <= 0:
                d_hp = 0
                break

            dmg2, crit2, skill2, sname2, mp_cost2 = _calc_damage(defender, attacker, d_mp)
            a_hp   -= dmg2
            d_mp    = max(0, d_mp - mp_cost2)
            tags2   = []
            if crit2:  tags2.append("⚡CRIT!")
            if skill2: tags2.append(f"🔮{sname2}!")
            tag_str2 = "  " + "  ".join(tags2) if tags2 else ""
            log_lines.append(
                f"  🛡️ *{defender['name']}* membalas *{attacker['name']}*\n"
                f"      💥 `-{dmg2}` HP{tag_str2}\n"
                f"      ❤️ HP tersisa: `{max(0,a_hp):,}/{a_max:,}`"
            )
        else:
            dmg2, crit2, skill2, sname2, mp_cost2 = _calc_damage(defender, attacker, d_mp)
            a_hp   -= dmg2
            d_mp    = max(0, d_mp - mp_cost2)
            tags2   = []
            if crit2:  tags2.append("⚡CRIT!")
            if skill2: tags2.append(f"🔮{sname2}!")
            tag_str2 = "  " + "  ".join(tags2) if tags2 else ""
            log_lines.append(
                f"  🛡️ *{defender['name']}* menyerang *{attacker['name']}*\n"
                f"      💥 `-{dmg2}` HP{tag_str2}\n"
                f"      ❤️ HP tersisa: `{max(0,a_hp):,}/{a_max:,}`"
            )
            if a_hp <= 0:
                a_hp = 0
                break

            dmg, crit, skill, sname, mp_cost = _calc_damage(attacker, defender, a_mp)
            d_hp   -= dmg
            a_mp    = max(0, a_mp - mp_cost)
            tags    = []
            if crit:  tags.append("⚡CRIT!")
            if skill: tags.append(f"🔮{sname}!")
            tag_str = "  " + "  ".join(tags) if tags else ""
            log_lines.append(
                f"  🗡️ *{attacker['name']}* membalas *{defender['name']}*\n"
                f"      💥 `-{dmg}` HP{tag_str}\n"
                f"      ❤️ HP tersisa: `{max(0,d_hp):,}/{d_max:,}`"
            )

        a_mp = min(a_max_mp, a_mp + 5)
        d_mp = min(d_max_mp, d_mp + 5)

        battle_text = _build_pvp_battle_text(
            attacker, defender,
            a_hp, d_hp, a_mp, d_mp,
            a_max, d_max, a_max_mp, d_max_mp,
            round_num=round_num,
            log_lines=log_lines,
            status="running"
        )
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=battle_text,
                parse_mode="Markdown"
            )
        except Exception:
            pass

        await asyncio.sleep(BATTLE_DELAY)

    # ── Tentukan pemenang ──
    is_draw = False
    if a_hp > 0 and d_hp <= 0:
        winner_id = sess["attacker_id"]
        loser_id  = sess["defender_id"]
        winner    = attacker
        loser     = defender
        winner_hp = a_hp
    elif d_hp > 0 and a_hp <= 0:
        winner_id = sess["defender_id"]
        loser_id  = sess["attacker_id"]
        winner    = defender
        loser     = attacker
        winner_hp = d_hp
    else:
        is_draw = True
        if a_hp >= d_hp:
            winner_id, loser_id = sess["attacker_id"], sess["defender_id"]
            winner, loser = attacker, defender
            winner_hp = a_hp
        else:
            winner_id, loser_id = sess["defender_id"], sess["attacker_id"]
            winner, loser = defender, attacker
            winner_hp = d_hp

    w_player = get_player(winner_id)
    l_player = get_player(loser_id)

    reward_exp  = max(10, loser.get("level", 1) * 8)
    reward_gold = max(20, loser.get("level", 1) * 15)

    if w_player:
        w_player["wins"]    = w_player.get("wins", 0) + 1
        pvp_stats           = w_player.get("pvp_stats", {"wins": 0, "losses": 0, "streak": 0, "best_streak": 0})
        pvp_stats["wins"]  += 1
        pvp_stats["streak"] = pvp_stats.get("streak", 0) + 1
        if pvp_stats["streak"] > pvp_stats.get("best_streak", 0):
            pvp_stats["best_streak"] = pvp_stats["streak"]
        w_player["pvp_stats"] = pvp_stats
        w_player["exp"]   = w_player.get("exp", 0) + reward_exp
        w_player["coin"]  = w_player.get("coin", 0) + reward_gold
        w_player["weekly_coin_earned"]  = w_player.get("weekly_coin_earned", 0) + reward_gold
        w_player["monthly_coin_earned"] = w_player.get("monthly_coin_earned", 0) + reward_gold
        from handlers.quest import update_quest_progress
        w_player = update_quest_progress(w_player, "weekly_coin_earned", reward_gold)
        from database import level_up
        w_player, leveled, new_lv = level_up(w_player)
        save_player(winner_id, w_player)

    if l_player:
        l_player["losses"]  = l_player.get("losses", 0) + 1
        pvp_stats           = l_player.get("pvp_stats", {"wins": 0, "losses": 0, "streak": 0, "best_streak": 0})
        pvp_stats["losses"] += 1
        pvp_stats["streak"]  = 0
        l_player["pvp_stats"] = pvp_stats
        save_player(loser_id, l_player)

    _del_pvp(chat_id)

    w_pvp = (w_player or {}).get("pvp_stats", {})
    l_pvp = (l_player or {}).get("pvp_stats", {})
    w_total = w_pvp.get("wins", 0) + w_pvp.get("losses", 0)
    l_total = l_pvp.get("wins", 0) + l_pvp.get("losses", 0)
    w_wr    = f"{int(w_pvp['wins']/w_total*100)}%" if w_total > 0 else "N/A"
    l_wr    = f"{int(l_pvp['wins']/l_total*100)}%" if l_total > 0 else "N/A"

    leveled_txt = ""
    if w_player and w_player.get("level", 1) > winner.get("level", 1):
        leveled_txt = f"\n  🎊 *LEVEL UP!* → Lv.{w_player['level']}"

    if is_draw:
        outcome_header = (
            f"╔══════════════════════════════════╗\n"
            f"║  🤝  *HASIL: DRAW (SERI)!*  🤝    ║\n"
            f"╚══════════════════════════════════╝\n\n"
            f"⚔️ HP keduanya hampir habis!\n"
            f"🏆 *{winner['name']}* unggul tipis (HP tersisa lebih banyak)\n"
        )
    else:
        outcome_header = (
            f"╔══════════════════════════════════╗\n"
            f"║  🏆  *HASIL PVP — ADA PEMENANG!*   ║\n"
            f"╚══════════════════════════════════╝\n\n"
        )

    w_max_final = winner.get("max_hp", 100)
    l_max_final = loser.get("max_hp", 100)

    result_text = (
        f"{outcome_header}\n"
        f"🏆 *PEMENANG:*\n"
        f"  {winner['emoji']} *{winner['name']}*  Lv.{winner.get('level',1)}\n"
        f"  HP Tersisa: {_hp_bar(winner_hp, w_max_final, 8)}\n"
        f"  🏅 W/L: *{w_pvp.get('wins',0)}W / {w_pvp.get('losses',0)}L*"
        f"  📈 WR: *{w_wr}*\n"
        f"  🔥 Streak: *{w_pvp.get('streak',0)}*"
        f"  🌟 Best: *{w_pvp.get('best_streak',0)}*\n\n"
        f"💀 *KALAH:*\n"
        f"  {loser['emoji']} *{loser['name']}*  Lv.{loser.get('level',1)}\n"
        f"  HP Tersisa: {_hp_bar(0, l_max_final, 8)}\n"
        f"  🏅 W/L: *{l_pvp.get('wins',0)}W / {l_pvp.get('losses',0)}L*"
        f"  📈 WR: *{l_wr}*\n"
        f"  💔 Streak direset ke 0\n\n"
        f"╔══════════════════════════════════╗\n"
        f"║  🎁  *HADIAH KEMENANGAN*\n"
        f"╚══════════════════════════════════╝\n"
        f"  ✨ +{reward_exp} EXP\n"
        f"  🪙 +{reward_gold} Gold\n"
        f"{leveled_txt}\n\n"
        f"🔢 Total Ronde: *{round_num}*  |  Max: {MAX_ROUNDS}\n"
        f"_Gunakan /pvpstats untuk lihat statistik lengkap!_"
    )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=result_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⚔️ Tantang Lagi", callback_data="pvp_rechallenge"),
                    InlineKeyboardButton("📊 PVP Stats", callback_data="pvp_stats_menu"),
                ],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu")]
            ])
        )
    except Exception:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=result_text,
                parse_mode="Markdown"
            )
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════
#  /pvpstats — Lihat statistik PVP sendiri
# ════════════════════════════════════════════════════════════════
async def pvpstats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return

    pvp   = player.get("pvp_stats", {"wins": 0, "losses": 0, "streak": 0, "best_streak": 0})
    total = pvp.get("wins", 0) + pvp.get("losses", 0)
    winrate = f"{int(pvp['wins']/total*100)}%" if total > 0 else "N/A"

    hp_bar_txt = _hp_bar(player.get("hp", player.get("max_hp", 100)), player.get("max_hp", 100), 10)
    mp_bar_txt = _mp_bar(player.get("mp", player.get("max_mp", 50)), player.get("max_mp", 50), 8)

    wr_num = int(pvp["wins"] / total * 100) if total > 0 else 0
    if wr_num >= 80:
        grade = "🔱 GRANDMASTER"
    elif wr_num >= 65:
        grade = "💎 MASTER"
    elif wr_num >= 50:
        grade = "🥇 GOLD"
    elif wr_num >= 35:
        grade = "🥈 SILVER"
    else:
        grade = "🥉 BRONZE"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   ⚔️  *STATISTIK PVP*  ⚔️         ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  {player['emoji']} *{player['name']}*  Lv.{player['level']}\n"
        f"║  [{player.get('class','warrior').replace('_',' ').title()}]\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ HP : {hp_bar_txt}\n"
        f"║  {mp_bar_txt}\n"
        f"║  ⚔️ ATK: `{player.get('atk',10)}`  🛡️ DEF: `{player.get('def',5)}`\n"
        f"║  💨 SPD: `{player.get('spd',10)}`  🎯 CRIT: `{player.get('crit',10)}%`\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🏆 Menang     : *{pvp.get('wins', 0)}*\n"
        f"║  💔 Kalah      : *{pvp.get('losses', 0)}*\n"
        f"║  📊 Total      : *{total}*\n"
        f"║  📈 Win Rate   : *{winrate}*\n"
        f"║  🔥 Streak     : *{pvp.get('streak', 0)}*\n"
        f"║  🌟 Best Streak: *{pvp.get('best_streak', 0)}*\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🏅 Grade      : *{grade}*\n"
        f"╚══════════════════════════════════╝"
    )
    await update.message.reply_text(text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Menu", callback_data="menu")]
        ]))
