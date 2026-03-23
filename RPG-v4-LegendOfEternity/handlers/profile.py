# ═══════════════════════════════════════════════════════════════
#  LEGENDS OF ETERNITY — Profile Handler
#  FIX: Pemain bisa cek profil admin di grup
# ═══════════════════════════════════════════════════════════════
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.database import get_player, save_player, check_vip_expiry, is_admin
from utils.ui import format_profile


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if hasattr(update, "callback_query") and update.callback_query:
        query = update.callback_query
        await query.answer()
        user   = query.from_user
        player = get_player(user.id)
        if not player:
            await query.edit_message_text("❌ Belum ada karakter. /start")
            return
        player = check_vip_expiry(player)
        save_player(user.id, player)
        text = format_profile(player, user.id)
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="profile")],
            [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
        ]
        await query.edit_message_text(text, parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        msg  = update.message
        user = update.effective_user

        # Cek apakah ada mention/reply — untuk melihat profil orang lain di grup
        target_user  = None
        target_player = None

        # Jika ada reply ke pesan orang lain
        if msg.reply_to_message:
            target_user = msg.reply_to_message.from_user
        # Jika ada argumen (mention by username or ID)
        elif context.args:
            arg = context.args[0]
            # Support @username atau user_id
            try:
                uid = int(arg)
                target_player = get_player(uid)
                if target_player:
                    target_user = type("U", (), {"id": uid, "first_name": target_player.get("name", "?")})()
            except ValueError:
                # Username mention — kita tidak bisa resolve tanpa cache, skip
                pass

        if target_user and target_user.id != user.id:
            # Pemain melihat profil orang lain
            tp = target_player or get_player(target_user.id)
            if not tp:
                await msg.reply_text("❌ Pemain tersebut belum punya karakter.")
                return
            tp = check_vip_expiry(tp)
            save_player(target_user.id, tp)
            text = format_profile(tp, target_user.id, viewer_id=user.id)
            keyboard = [
                [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
            ]
            await msg.reply_text(text, parse_mode="Markdown",
                                 reply_markup=InlineKeyboardMarkup(keyboard))
            return

        # Profil sendiri
        player = get_player(user.id)
        if not player:
            await msg.reply_text("❌ Belum ada karakter. Ketik /start")
            return
        player = check_vip_expiry(player)
        save_player(user.id, player)
        text = format_profile(player, user.id)
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="profile")],
            [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
        ]
        await msg.reply_text(text, parse_mode="Markdown",
                             reply_markup=InlineKeyboardMarkup(keyboard))
