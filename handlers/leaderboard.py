import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, get_all_players, is_admin, refresh_periods, save_player

# ─── HADIAH LEADERBOARD ──────────────────────────────────────────
LB_REWARDS = {
    1: {"diamond": 100, "gold": 0,        "label": "🥇 Juara 1: +100 💎 Diamond"},
    2: {"diamond": 50,  "gold": 0,        "label": "🥈 Juara 2: +50 💎 Diamond"},
    3: {"diamond": 0,   "gold": 10000000, "label": "🥉 Juara 3: +10.000.000 🪙 Gold"},
}
LB_REWARD_PERIOD_KEY = "lb_reward_last_period"  # key di player data


async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    await _show_lb(update.message, player, user.id, "level", "all", is_msg=True)


async def lb_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    parts  = query.data.replace("lb_", "").split("_")
    sort   = parts[0] if parts else "level"
    period = parts[1] if len(parts) > 1 else "all"
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        return
    await _show_lb(query, player, user.id, sort, period)


async def _show_lb(target, player: dict, user_id: int,
                   sort_by: str = "level", period: str = "all", is_msg: bool = False):
    all_p = get_all_players()

    # Reset period stats lazily & save if any period was reset
    for uid, p in list(all_p.items()):
        before_weekly  = p.get("weekly_reset", 0)
        before_monthly = p.get("monthly_reset", 0)
        refresh_periods(p)
        if p.get("weekly_reset", 0) != before_weekly or p.get("monthly_reset", 0) != before_monthly:
            all_p[uid] = p
            save_player(int(uid), p)

    # ── Admin dikeluarkan dari leaderboard ───────────────────────
    visible = {uid: p for uid, p in all_p.items() if not is_admin(int(uid))}

    prefix = {"weekly": "weekly_", "monthly": "monthly_"}.get(period, "")

    def sort_fn(p):
        if sort_by == "level":
            return (p.get("level", 1), p.get("exp", 0))
        elif sort_by == "kills":
            return p.get(f"{prefix}kills" if prefix else "kills", 0)
        elif sort_by == "boss":
            return p.get(f"{prefix}boss_kills" if prefix else "boss_kills", 0)
        else:  # coin
            return p.get(f"{prefix}coin_earned" if prefix else "coin", 0)

    sorted_p = sorted(visible.values(), key=sort_fn, reverse=True)

    medals       = ["🥇", "🥈", "🥉"]
    sort_labels  = {"level": "LEVEL", "kills": "KILLS", "boss": "BOSS KILLS", "coin": "COIN"}
    period_label = {"all": "🏆 SEMUA WAKTU", "weekly": "📅 MINGGUAN", "monthly": "📆 BULANAN"}

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  🏆 *LEADERBOARD {sort_labels.get(sort_by,'LEVEL')}*\n"
        f"║  {period_label.get(period,'')}\n"
        f"╚══════════════════════════════════╝\n\n"
    )

    # Find user's rank first (full scan)
    my_rank = None
    for i, p in enumerate(sorted_p):
        pid = p.get("user_id", 0)
        if str(pid) == str(user_id) or pid == user_id:
            my_rank = i + 1
            break

    for i, p in enumerate(sorted_p):
        rank = i + 1
        if rank > 10:
            break

        medal    = medals[i] if i < 3 else f"#{rank}"
        vip_ico  = "💎" if p.get("vip", {}).get("active") else ""
        g_ico    = "♀️" if p.get("gender") == "female" else "♂️"

        if sort_by == "level":
            val = f"Lv.{p.get('level',1)}"
        elif sort_by == "kills":
            val = f"{p.get(f'{prefix}kills' if prefix else 'kills', 0):,} kills"
        elif sort_by == "boss":
            val = f"{p.get(f'{prefix}boss_kills' if prefix else 'boss_kills', 0):,} boss kills"
        else:
            val = f"{p.get(f'{prefix}coin_earned' if prefix else 'coin', 0):,} coin"

        # Tampilkan reward di samping nama untuk top 3
        reward_tag = ""
        if rank <= 3:
            r = LB_REWARDS[rank]
            if r["diamond"]:
                reward_tag = f" 💎{r['diamond']}"
            elif r["gold"]:
                reward_tag = f" 🪙{r['gold']//1000000}jt"

        text += f"{medal} {p['emoji']} *{p['name']}* {g_ico}{vip_ico}{reward_tag} — {val}\n"

    # ── Distribusi reward (hanya saat sort=level, period=weekly, auto tiap minggu) ──
    reward_msg = ""
    if sort_by == "level" and period == "weekly" and len(sorted_p) >= 3:
        # BUG FIX: use Monday-aligned ISO week number (year*100 + week) instead of
        # int(time.time()) // (7*86400) which is Thursday-aligned (Unix epoch = Thu).
        # This matches database.py's refresh_periods() which resets on Monday 00:00 UTC.
        import datetime as _dt
        # BUG FIX: gunakan date.today() (lokal) konsisten dengan refresh_periods di database
        _today       = _dt.date.today()
        _iso         = _today.isocalendar()
        current_week = _iso[0] * 100 + _iso[1]  # e.g. 202615 = year 2026, week 15
        for rank_idx in range(min(3, len(sorted_p))):
            winner = sorted_p[rank_idx]
            rank = rank_idx + 1
            reward = LB_REWARDS[rank]
            winner_id = winner.get("user_id", 0)
            last_rewarded_week = winner.get("lb_reward_last_week", -1)
            if last_rewarded_week != current_week:
                winner["lb_reward_last_week"] = current_week
                if reward["diamond"]:
                    winner["diamond"] = winner.get("diamond", 0) + reward["diamond"]
                if reward["gold"]:
                    winner["coin"] = winner.get("coin", 0) + reward["gold"]
                save_player(int(winner_id), winner)
        reward_msg = (
            "\n\n🎁 *HADIAH MINGGUAN LEADERBOARD:*\n"
            "🥇 Juara 1: +100 💎 Diamond\n"
            "🥈 Juara 2: +50 💎 Diamond\n"
            "🥉 Juara 3: +10.000.000 🪙 Gold\n"
            "_(Diberikan otomatis setiap reset mingguan)_"
        )

    text += reward_msg

    if not sorted_p:
        text += "_Belum ada data._\n"

    if my_rank and my_rank > 10:
        text += f"\n...\n🔹 Rankmu: #{my_rank}"
    elif my_rank:
        text += f"\n🔹 *Kamu di posisi #{my_rank}*"
    elif is_admin(user_id):
        text += "\n\n👑 _Admin tidak tampil di leaderboard_"

    keyboard = [
        [
            InlineKeyboardButton("🏅 Level",      callback_data=f"lb_level_{period}"),
            InlineKeyboardButton("⚔️ Kills",      callback_data=f"lb_kills_{period}"),
            InlineKeyboardButton("👹 Boss",        callback_data=f"lb_boss_{period}"),
        ],
        [
            # FIX BUG #8: tambahkan tombol sort Coin yang sebelumnya hilang
            InlineKeyboardButton("🪙 Coin",        callback_data=f"lb_coin_{period}"),
        ],
        [
            InlineKeyboardButton("📅 Mingguan",   callback_data=f"lb_{sort_by}_weekly"),
            InlineKeyboardButton("📆 Bulanan",    callback_data=f"lb_{sort_by}_monthly"),
            InlineKeyboardButton("🏆 All Time",    callback_data=f"lb_{sort_by}_all"),
        ],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]

    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
