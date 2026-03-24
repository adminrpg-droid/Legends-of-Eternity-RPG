"""leaderboard.py — Papan peringkat dengan filter admin, weekly & monthly"""
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, get_all_players, is_admin, refresh_periods, save_player


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

    # Reset period stats lazily & save
    for uid, p in list(all_p.items()):
        updated = refresh_periods(p)
        if updated is not p:
            all_p[uid] = updated
            save_player(int(uid), updated)

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

    my_rank = None
    for i, p in enumerate(sorted_p):
        rank = i + 1
        pid  = p.get("user_id", 0)
        if str(pid) == str(user_id) or pid == user_id:
            my_rank = rank
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

        text += f"{medal} {p['emoji']} *{p['name']}* {g_ico}{vip_ico} — {val}\n"

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
