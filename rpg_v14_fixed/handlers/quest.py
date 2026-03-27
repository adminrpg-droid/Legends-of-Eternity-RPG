"""
Quest System — Legends of Eternity RPG
Quests reset daily/weekly. Rewards: EXP, Gold, Diamond.
"""
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, save_player

# ─── QUEST DEFINITIONS ───────────────────────────────────────────
DAILY_QUESTS = {
    "daily_kill_5": {
        "name": "🗡️ Pemburu Harian",
        "desc": "Bunuh 5 monster biasa",
        "type": "kills",
        "target": 5,
        "reward": {"exp": 80, "gold": 200, "diamond": 0},
        "reset": "daily",
    },
    "daily_kill_15": {
        "name": "⚔️ Petarung Tangguh",
        "desc": "Bunuh 15 monster biasa",
        "type": "kills",
        "target": 15,
        "reward": {"exp": 200, "gold": 500, "diamond": 1},
        "reset": "daily",
    },
    "daily_dungeon_1": {
        "name": "🕳️ Penjelajah Dungeon",
        "desc": "Selesaikan 1 dungeon",
        "type": "dungeon_clears",
        "target": 1,
        "reward": {"exp": 150, "gold": 300, "diamond": 1},
        "reset": "daily",
    },
    "daily_boss_1": {
        "name": "💀 Pembunuh Boss",
        "desc": "Kalahkan 1 boss",
        "type": "boss_kills",
        "target": 1,
        "reward": {"exp": 300, "gold": 600, "diamond": 2},
        "reset": "daily",
    },
    "daily_login": {
        "name": "🌅 Login Harian",
        "desc": "Masuk ke game hari ini",
        "type": "login",
        "target": 1,
        "reward": {"exp": 50, "gold": 100, "diamond": 0},
        "reset": "daily",
    },
}

WEEKLY_QUESTS = {
    "weekly_kill_50": {
        "name": "⚔️ Pembantai Mingguan",
        "desc": "Bunuh 50 monster dalam seminggu",
        "type": "weekly_kills",
        "target": 50,
        "reward": {"exp": 800, "gold": 2000, "diamond": 5},
        "reset": "weekly",
    },
    "weekly_boss_5": {
        "name": "👹 Pemburu Boss Sejati",
        "desc": "Kalahkan 5 boss dalam seminggu",
        "type": "weekly_boss_kills",
        "target": 5,
        "reward": {"exp": 1200, "gold": 3000, "diamond": 8},
        "reset": "weekly",
    },
    "weekly_dungeon_3": {
        "name": "🗺️ Penjelajah Abadi",
        "desc": "Selesaikan 3 dungeon dalam seminggu",
        "type": "dungeon_clears_weekly",
        "target": 3,
        "reward": {"exp": 600, "gold": 1500, "diamond": 4},
        "reset": "weekly",
    },
    "weekly_earn_5000": {
        "name": "💰 Kolektor Kekayaan",
        "desc": "Kumpulkan 5000 Gold dari pertempuran minggu ini",
        "type": "weekly_coin_earned",
        "target": 5000,
        "reward": {"exp": 500, "gold": 1000, "diamond": 3},
        "reset": "weekly",
    },
}

ALL_QUESTS = {**DAILY_QUESTS, **WEEKLY_QUESTS}

# ─── HELPERS ─────────────────────────────────────────────────────
def _day_start() -> float:
    t = time.gmtime()
    import calendar
    return float(calendar.timegm((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, 0)))

def _week_start() -> float:
    # BUG FIX: gunakan datetime.timedelta agar tidak crash saat mday - wday <= 0 (awal bulan)
    import datetime
    today  = datetime.datetime.utcnow().date()
    monday = today - datetime.timedelta(days=today.weekday())
    return float(datetime.datetime(monday.year, monday.month, monday.day, 0, 0, 0).timestamp())

def init_quests(player: dict) -> dict:
    """Initialize or reset quest progress for player."""
    now = time.time()
    day  = _day_start()
    week = _week_start()

    if "quest_data" not in player:
        player["quest_data"] = {
            "daily_reset": 0.0,
            "weekly_reset": 0.0,
            "progress": {},
            "claimed": [],
        }

    qd = player["quest_data"]

    # Reset daily
    if qd.get("daily_reset", 0) < day:
        for qid, q in DAILY_QUESTS.items():
            qd["progress"][qid] = 0
        # Remove daily from claimed
        qd["claimed"] = [c for c in qd.get("claimed", []) if c not in DAILY_QUESTS]
        qd["daily_reset"] = day

    # Reset weekly
    if qd.get("weekly_reset", 0) < week:
        for qid, q in WEEKLY_QUESTS.items():
            qd["progress"][qid] = 0
        qd["claimed"] = [c for c in qd.get("claimed", []) if c not in WEEKLY_QUESTS]
        qd["weekly_reset"] = week

    # Auto-set login quest progress
    if "daily_login" in DAILY_QUESTS:
        qd["progress"]["daily_login"] = 1

    return player


def update_quest_progress(player: dict, quest_type: str, amount: int = 1) -> dict:
    """Update quest progress when player does something."""
    player = init_quests(player)
    qd = player["quest_data"]
    for qid, q in ALL_QUESTS.items():
        if q["type"] == quest_type and qid not in qd.get("claimed", []):
            qd["progress"][qid] = qd["progress"].get(qid, 0) + amount
    return player


def get_quest_status(player: dict, qid: str) -> dict:
    """Get quest progress info."""
    player = init_quests(player)
    q = ALL_QUESTS.get(qid, {})
    progress = player["quest_data"]["progress"].get(qid, 0)
    target   = q.get("target", 1)
    claimed  = qid in player["quest_data"].get("claimed", [])
    done     = progress >= target
    return {
        "q": q,
        "progress": progress,
        "target": target,
        "done": done,
        "claimed": claimed,
    }


# ─── HANDLERS ────────────────────────────────────────────────────
async def quest_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    player = init_quests(player)
    save_player(user.id, player)
    await _show_quests(update.message, player, user.id)


async def quest_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        await query.answer("❌ Ketik /start!", show_alert=True)
        return

    player = init_quests(player)

    if action == "quest_daily":
        await _show_quest_list(query, player, user.id, "daily")
        return
    if action == "quest_weekly":
        await _show_quest_list(query, player, user.id, "weekly")
        return
    if action == "quest_main":
        save_player(user.id, player)
        await _show_quests(query, player, user.id, edit=True)
        return
    if action.startswith("quest_claim_"):
        qid = action.replace("quest_claim_", "")
        await _claim_quest(query, player, user.id, qid)
        return


async def _show_quests(target, player: dict, user_id: int, edit: bool = False):
    player = init_quests(player)

    daily_done  = sum(1 for qid in DAILY_QUESTS  if get_quest_status(player, qid)["done"] and not get_quest_status(player, qid)["claimed"])
    weekly_done = sum(1 for qid in WEEKLY_QUESTS if get_quest_status(player, qid)["done"] and not get_quest_status(player, qid)["claimed"])

    text = (
        "╔══════════════════════════════════╗\n"
        "║       📜  *SISTEM QUEST*         ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  🌅 Quest Harian  — {daily_done} bisa diklaim\n"
        f"║  📅 Quest Mingguan — {weekly_done} bisa diklaim\n"
        "╠══════════════════════════════════╣\n"
        "║  Selesaikan quest untuk reward!\n"
        "║  EXP, Gold & Diamond menantimu!\n"
        "╚══════════════════════════════════╝"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌅 Quest Harian",   callback_data="quest_daily"),
         InlineKeyboardButton("📅 Quest Mingguan", callback_data="quest_weekly")],
        [InlineKeyboardButton("🏠 Menu",           callback_data="menu")],
    ])
    if edit and hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        msg_fn = target.reply_text if hasattr(target, "reply_text") else target.edit_message_text
        await msg_fn(text, parse_mode="Markdown", reply_markup=keyboard)


async def _show_quest_list(query, player: dict, user_id: int, qtype: str):
    quests = DAILY_QUESTS if qtype == "daily" else WEEKLY_QUESTS
    label  = "🌅 QUEST HARIAN" if qtype == "daily" else "📅 QUEST MINGGUAN"

    lines   = [f"╔══════════════════════════════════╗\n║  {label}\n╠══════════════════════════════════╣\n"]
    buttons = []

    for qid, q in quests.items():
        st  = get_quest_status(player, qid)
        bar = f"{st['progress']}/{st['target']}"
        if st["claimed"]:
            status = "✅ Diklaim"
            emoji  = "✅"
        elif st["done"]:
            status = "🎁 Klaim!"
            emoji  = "🎁"
        else:
            status = f"⏳ {bar}"
            emoji  = "⏳"

        r = q["reward"]
        reward_str = []
        if r.get("exp"):     reward_str.append(f"{r['exp']} EXP")
        if r.get("gold"):    reward_str.append(f"{r['gold']} Gold")
        if r.get("diamond"): reward_str.append(f"💎{r['diamond']}")

        lines.append(
            f"║ {emoji} *{q['name']}*\n"
            f"║   _{q['desc']}_\n"
            f"║   Progress: {bar} | {status}\n"
            f"║   🎁 {' | '.join(reward_str)}\n"
            f"╠══════════════════════════════════╣\n"
        )
        if st["done"] and not st["claimed"]:
            buttons.append([InlineKeyboardButton(f"🎁 Klaim: {q['name']}", callback_data=f"quest_claim_{qid}")])

    lines.append("╚══════════════════════════════════╝")
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="quest_main")])

    await query.edit_message_text(
        "".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def _claim_quest(query, player: dict, user_id: int, qid: str):
    st = get_quest_status(player, qid)
    if st["claimed"]:
        await query.answer("❌ Quest sudah diklaim!", show_alert=True)
        return
    if not st["done"]:
        await query.answer("❌ Quest belum selesai!", show_alert=True)
        return

    q = st["q"]
    r = q["reward"]

    from database import level_up
    player["exp"]    = player.get("exp", 0) + r.get("exp", 0)
    player["coin"]   = player.get("coin", 0) + r.get("gold", 0)
    player["diamond"]= player.get("diamond", 0) + r.get("diamond", 0)
    player, leveled, levels = level_up(player)

    player["quest_data"]["claimed"].append(qid)
    save_player(user_id, player)

    reward_lines = []
    if r.get("exp"):     reward_lines.append(f"✨ +{r['exp']} EXP")
    if r.get("gold"):    reward_lines.append(f"🪙 +{r['gold']} Gold")
    if r.get("diamond"): reward_lines.append(f"💎 +{r['diamond']} Diamond")

    level_up_text = f"\n🎉 *LEVEL UP! Sekarang Lv.{player['level']}!*" if leveled else ""

    await query.edit_message_text(
        f"🎁 *Quest Berhasil Diklaim!*\n\n"
        f"📜 *{q['name']}*\n\n"
        f"*Reward:*\n" + "\n".join(reward_lines) +
        level_up_text + "\n\n"
        f"_Terus selesaikan quest untuk reward lebih besar!_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Quest Lainnya", callback_data="quest_main")],
            [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
        ])
    )
