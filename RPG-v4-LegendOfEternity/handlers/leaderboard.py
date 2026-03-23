# ═══════════════════════════════════════════════════════════════
#  LEGENDS OF ETERNITY — Leaderboard Handler
#  FIX: Admin masuk leaderboard (is_admin tidak difilter)
# ═══════════════════════════════════════════════════════════════
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models.database import get_player, get_all_players, is_admin


async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    await _show_leaderboard(update.message, player, user.id, "level", is_msg=True)


async def lb_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data.replace("lb_", "")
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        return
    await _show_leaderboard(query, player, user.id, action)


async def _show_leaderboard(target, player: dict, user_id: int, sort_by: str, is_msg=False):
    all_players = get_all_players()

    sort_keys = {
        "level":  lambda p: (p.get("level", 1), p.get("exp", 0)),
        "kills":  lambda p: p.get("kills", 0),
        "boss":   lambda p: p.get("boss_kills", 0),
        "coin":   lambda p: p.get("coin", 0),
    }
    sort_fn = sort_keys.get(sort_by, sort_keys["level"])
    # FIX: Admin ikut leaderboard — tidak ada filter is_admin
    sorted_players = sorted(all_players.values(), key=sort_fn, reverse=True)

    medals = ["🥇", "🥈", "🥉"]
    labels = {"level": "LEVEL", "kills": "KILLS", "boss": "BOSS KILLS", "coin": "COIN"}

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   🏆  *LEADERBOARD {labels.get(sort_by,'LEVEL')}*    ║\n"
        f"╚══════════════════════════════════╝\n\n"
    )

    my_rank = None
    for i, p in enumerate(sorted_players):
        rank = i + 1
        if str(p.get("user_id", "")) == str(user_id) or p.get("user_id") == user_id:
            my_rank = rank

        if rank > 10:
            break

        medal     = medals[i] if i < 3 else f"#{rank}"
        vip_icon  = "💎" if p.get("vip", {}).get("active") else ""
        g_icon    = "♀️" if p.get("gender") == "female" else "♂️"
        # Tampilkan badge admin di leaderboard
        adm_icon  = " 👑" if is_admin(p.get("user_id", 0)) else ""

        if sort_by == "level":
            stat_val = f"Lv.{p.get('level',1)}"
        elif sort_by == "kills":
            stat_val = f"{p.get('kills',0)} kills"
        elif sort_by == "boss":
            stat_val = f"{p.get('boss_kills',0)} boss kills"
        else:
            stat_val = f"{p.get('coin',0)} coin"

        text += f"{medal} {p['emoji']} *{p['name']}* {g_icon}{vip_icon}{adm_icon} — {stat_val}\n"

    if my_rank and my_rank > 10:
        text += f"\n...\n🔹 Rankmu: #{my_rank}"
    elif my_rank:
        text += f"\n🔹 *Kamu di posisi #{my_rank}*"

    keyboard = [
        [
            InlineKeyboardButton("🏅 Level",      callback_data="lb_level"),
            InlineKeyboardButton("⚔️ Kills",      callback_data="lb_kills"),
        ],
        [
            InlineKeyboardButton("👹 Boss Kills", callback_data="lb_boss"),
            InlineKeyboardButton("💰 Coin",       callback_data="lb_coin"),
        ],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
