from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, save_player, check_vip_expiry, is_admin
from ui import format_profile


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ── Callback (profil sendiri via inline button) ───────────────
    if hasattr(update, "callback_query") and update.callback_query:
        query  = update.callback_query
        await query.answer()
        user   = query.from_user
        player = get_player(user.id)
        if not player:
            await query.edit_message_text("❌ Belum ada karakter. /start")
            return
        player = check_vip_expiry(player)
        save_player(user.id, player)
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="profile")],
            [InlineKeyboardButton("🏠 Menu",    callback_data="menu")],
        ]
        await query.edit_message_text(format_profile(player, user.id),
                                      parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ── /profile command ─────────────────────────────────────────
    msg  = update.message
    user = update.effective_user

    target_user   = None
    target_player = None

    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
    elif context.args:
        try:
            uid           = int(context.args[0])
            target_player = get_player(uid)
            if target_player:
                target_user = type("U", (), {"id": uid})()
        except ValueError:
            pass

    if target_user and target_user.id != user.id:
        # ── Blokir lihat profil admin dari grup ──────────────────
        if is_admin(target_user.id):
            await msg.reply_text(
                "🚫 *Profil admin tidak dapat dilihat.*\n"
                "_Privasi admin dilindungi oleh sistem._",
                parse_mode="Markdown"
            )
            return

        tp = target_player or get_player(target_user.id)
        if not tp:
            await msg.reply_text("❌ Pemain tersebut belum punya karakter.")
            return
        tp = check_vip_expiry(tp)
        save_player(target_user.id, tp)
        await msg.reply_text(
            format_profile(tp, target_user.id, viewer_id=user.id),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="menu")]])
        )
        return

    # ── Profil sendiri ───────────────────────────────────────────
    player = get_player(user.id)
    if not player:
        await msg.reply_text("❌ Belum ada karakter. Ketik /start")
        return
    player = check_vip_expiry(player)
    save_player(user.id, player)
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="profile")],
        [InlineKeyboardButton("🏠 Menu",    callback_data="menu")],
    ]
    await msg.reply_text(format_profile(player, user.id),
                         parse_mode="Markdown",
                         reply_markup=InlineKeyboardMarkup(keyboard))
