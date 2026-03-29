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

    # Tentukan target
    target_user = None
    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
    elif context.args and msg.entities:
        # Cari entity bertipe text_mention atau mention di pesan
        mention_used = False
        for entity in msg.entities:
            if entity.type == "text_mention" and entity.user:
                target_user = entity.user
                break
            elif entity.type == "mention":
                # Username mention tidak bisa di-resolve ke User object tanpa API call
                # Minta user reply pesan target sebagai gantinya
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

    # Simpan sesi challenge
    _set_pvp(chat.id, {
        "status":      "waiting",
        "attacker_id": user.id,
        "defender_id": target_user.id,
        "chat_id":     chat.id,
        "created_at":  time.time(),
        "msg_id":      None,
    })

    text = (
        f"⚔️ *TANTANGAN PVP!* ⚔️\n\n"
        f"🗡️ *{attacker['name']}* (Lv.{attacker['level']}) menantang\n"
        f"🛡️ *{defender['name']}* (Lv.{defender['level']})!\n\n"
        f"💬 {target_user.mention_markdown()}, apakah kamu menerima?\n\n"
        f"⏳ Tantangan berakhir dalam *{CHALLENGE_TIMEOUT}s*"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Terima Tantangan", callback_data=f"pvp_accept_{chat.id}"),
            InlineKeyboardButton("❌ Tolak",            callback_data=f"pvp_decline_{chat.id}"),
        ]
    ])
    sent = await msg.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

    # Update msg_id di sesi
    sess = _get_pvp(chat.id)
    sess["msg_id"] = sent.message_id
    _set_pvp(chat.id, sess)

    # Auto-expire setelah timeout
    asyncio.create_task(_expire_pvp(context, chat.id, sent.message_id))


async def _expire_pvp(context, chat_id: int, msg_id: int):
    await asyncio.sleep(CHALLENGE_TIMEOUT)
    sess = _get_pvp(chat_id)
    if sess and sess.get("status") == "waiting":
        _del_pvp(chat_id)
        try:
            await context.bot.edit_message_text(
                "⏳ *Tantangan PVP kedaluwarsa!*",
                chat_id=chat_id, message_id=msg_id, parse_mode="Markdown"
            )
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════
#  CALLBACK: pvp_accept / pvp_decline
# ════════════════════════════════════════════════════════════════
async def pvp_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
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
            f"❌ *Tantangan PVP ditolak!*",
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

        await query.edit_message_text(
            f"⚔️ *PVP DIMULAI!*\n\n"
            f"🗡️ {attacker['name']} vs 🛡️ {defender['name']}\n\n"
            f"⏳ Pertarungan sedang berjalan...",
            parse_mode="Markdown"
        )

        await asyncio.sleep(1)
        await _run_pvp_battle(context, chat_id, query.message, attacker, defender, sess)


# ════════════════════════════════════════════════════════════════
#  BATTLE ENGINE
# ════════════════════════════════════════════════════════════════
def _calc_damage(attacker: dict, defender: dict) -> tuple:
    """Returns (damage, is_crit, skill_used)"""
    base_atk = attacker.get("atk", 10)
    defense  = defender.get("def", 5)
    crit_pct = attacker.get("crit", 10)

    # VIP bonus — flat ATK bonus
    vip = attacker.get("vip", {})
    if vip.get("active"):
        effects = vip.get("effects", {})
        base_atk += effects.get("atk_bonus", 0)

    damage   = max(1, base_atk - int(defense * 0.6) + random.randint(-5, 10))
    is_crit  = random.randint(1, 100) <= crit_pct

    if is_crit:
        damage = int(damage * 1.5)

    skill_used = False
    # 30% chance to use active skill
    if random.random() < 0.30:
        skill_bonus = int(base_atk * 0.4)
        damage += skill_bonus
        skill_used = True

    return max(1, damage), is_crit, skill_used


async def _run_pvp_battle(context, chat_id: int, message, attacker: dict, defender: dict, sess: dict):
    """Simulate PVP rounds and determine winner."""
    # Work on copies with current HP
    a_hp  = attacker.get("hp", attacker.get("max_hp", 100))
    d_hp  = defender.get("hp", defender.get("max_hp", 100))
    a_max = attacker.get("max_hp", 100)
    d_max = defender.get("max_hp", 100)

    log_lines = []
    round_num = 0
    MAX_ROUNDS = 20

    # Speed determines who goes first
    a_spd = attacker.get("spd", 10)
    d_spd = defender.get("spd", 10)
    a_first = a_spd >= d_spd

    while a_hp > 0 and d_hp > 0 and round_num < MAX_ROUNDS:
        round_num += 1

        if a_first:
            # Attacker hits first
            dmg, crit, skill = _calc_damage(attacker, defender)
            d_hp -= dmg
            crit_txt  = " ⚡CRIT!" if crit else ""
            skill_txt = " 🔮Skill!" if skill else ""
            log_lines.append(f"Ronde {round_num}: 🗡️ {attacker['name']} → {dmg} DMG{crit_txt}{skill_txt}")
            if d_hp <= 0:
                break

            dmg2, crit2, skill2 = _calc_damage(defender, attacker)
            a_hp -= dmg2
            crit_txt2  = " ⚡CRIT!" if crit2 else ""
            skill_txt2 = " 🔮Skill!" if skill2 else ""
            log_lines.append(f"         🛡️ {defender['name']} → {dmg2} DMG{crit_txt2}{skill_txt2}")
        else:
            dmg2, crit2, skill2 = _calc_damage(defender, attacker)
            a_hp -= dmg2
            crit_txt2  = " ⚡CRIT!" if crit2 else ""
            skill_txt2 = " 🔮Skill!" if skill2 else ""
            log_lines.append(f"Ronde {round_num}: 🛡️ {defender['name']} → {dmg2} DMG{crit_txt2}{skill_txt2}")
            if a_hp <= 0:
                break

            dmg, crit, skill = _calc_damage(attacker, defender)
            d_hp -= dmg
            crit_txt  = " ⚡CRIT!" if crit else ""
            skill_txt = " 🔮Skill!" if skill else ""
            log_lines.append(f"         🗡️ {attacker['name']} → {dmg} DMG{crit_txt}{skill_txt}")

    # Determine winner
    is_draw = False
    if a_hp > 0 and d_hp <= 0:
        winner_id = sess["attacker_id"]
        loser_id  = sess["defender_id"]
        winner    = attacker
        loser     = defender
    elif d_hp > 0 and a_hp <= 0:
        winner_id = sess["defender_id"]
        loser_id  = sess["attacker_id"]
        winner    = defender
        loser     = attacker
    else:
        # FIX BUG #9: tandai sebagai draw dan tentukan "pemenang" berdasarkan HP tersisa
        is_draw = True
        if a_hp >= d_hp:
            winner_id, loser_id = sess["attacker_id"], sess["defender_id"]
            winner, loser = attacker, defender
        else:
            winner_id, loser_id = sess["defender_id"], sess["attacker_id"]
            winner, loser = defender, attacker

    # ── Update stats di database (PERMANEN) ─────────────────────
    w_player = get_player(winner_id)
    l_player = get_player(loser_id)

    # Default reward (dipakai di result_text di bawah)
    reward_exp  = max(10, loser.get("level", 1) * 8)
    reward_gold = max(20, loser.get("level", 1) * 15)

    if w_player:
        w_player["wins"]   = w_player.get("wins", 0) + 1
        pvp_stats = w_player.get("pvp_stats", {"wins": 0, "losses": 0, "streak": 0, "best_streak": 0})
        pvp_stats["wins"]   += 1
        pvp_stats["streak"] = pvp_stats.get("streak", 0) + 1
        if pvp_stats["streak"] > pvp_stats.get("best_streak", 0):
            pvp_stats["best_streak"] = pvp_stats["streak"]
        w_player["pvp_stats"] = pvp_stats
        w_player["exp"]  = w_player.get("exp", 0) + reward_exp
        w_player["coin"] = w_player.get("coin", 0) + reward_gold
        # BUG FIX: update weekly/monthly coin tracking dan quest progress saat menang PVP
        w_player["weekly_coin_earned"]  = w_player.get("weekly_coin_earned", 0) + reward_gold
        w_player["monthly_coin_earned"] = w_player.get("monthly_coin_earned", 0) + reward_gold
        from handlers.quest import update_quest_progress
        w_player = update_quest_progress(w_player, "weekly_coin_earned", reward_gold)
        from database import level_up
        w_player, _leveled, _lv = level_up(w_player)
        save_player(winner_id, w_player)

    if l_player:
        l_player["losses"] = l_player.get("losses", 0) + 1
        pvp_stats = l_player.get("pvp_stats", {"wins": 0, "losses": 0, "streak": 0, "best_streak": 0})
        pvp_stats["losses"]  += 1
        pvp_stats["streak"]   = 0  # reset streak
        l_player["pvp_stats"] = pvp_stats
        save_player(loser_id, l_player)

    _del_pvp(chat_id)

    # ── Tampilkan log & hasil ────────────────────────────────────
    # Ambil log 8 ronde terakhir agar tidak terlalu panjang
    show_log = log_lines[-8:] if len(log_lines) > 8 else log_lines
    log_text = "\n".join(show_log)

    w_pvp = (w_player or {}).get("pvp_stats", {})
    l_pvp = (l_player or {}).get("pvp_stats", {})

    # FIX BUG #9: tampilkan keterangan draw jika skor sama
    if is_draw:
        outcome_txt = (
            f"🤝 *DRAW!* HP keduanya habis bersamaan!\n"
            f"🏆 *{winner['name']}* menang tipis (HP lebih banyak)!\n"
            f"💀 *{loser['name']}* kalah tipis\n\n"
        )
    else:
        outcome_txt = (
            f"🏆 *PEMENANG: {winner['name']}!* 🎉\n"
            f"💀 *Kalah: {loser['name']}*\n\n"
        )

    result_text = (
        f"╔══════════════════════════════════╗\n"
        f"║     ⚔️  *HASIL PVP*  ⚔️          ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"📋 *Log Pertarungan:*\n"
        f"`{log_text}`\n\n"
        f"{outcome_txt}"
        f"📊 *Statistik PVP:*\n"
        f"🗡️ {winner['name']}: {w_pvp.get('wins',0)}W / {w_pvp.get('losses',0)}L "
        f"(Streak: {w_pvp.get('streak',0)} 🔥)\n"
        f"🛡️ {loser['name']}: {l_pvp.get('wins',0)}W / {l_pvp.get('losses',0)}L\n\n"
        f"🎁 {winner['name']} mendapat:\n"
        f"   ✨ +{reward_exp} EXP  🪙 +{reward_gold} Gold"
    )

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=result_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📜 Profil Saya", url=f"https://t.me/{context.bot.username}?start=pvp")]
            ])
        )
    except Exception as e:
        try:
            await message.reply_text(result_text, parse_mode="Markdown")
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

    pvp = player.get("pvp_stats", {"wins": 0, "losses": 0, "streak": 0, "best_streak": 0})
    total = pvp.get("wins", 0) + pvp.get("losses", 0)
    winrate = f"{int(pvp['wins']/total*100)}%" if total > 0 else "N/A"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   ⚔️  *STATISTIK PVP*  ⚔️         ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  {player['emoji']} *{player['name']}* Lv.{player['level']}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🏆 Menang  : *{pvp.get('wins', 0)}*\n"
        f"║  💔 Kalah   : *{pvp.get('losses', 0)}*\n"
        f"║  📊 Total   : *{total}*\n"
        f"║  📈 Win Rate: *{winrate}*\n"
        f"║  🔥 Streak  : *{pvp.get('streak', 0)}*\n"
        f"║  🌟 Best    : *{pvp.get('best_streak', 0)}*\n"
        f"╚══════════════════════════════════╝"
    )
    await update.message.reply_text(text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="menu")]]))
