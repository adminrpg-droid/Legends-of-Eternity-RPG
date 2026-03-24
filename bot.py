import logging
import os
import sys

from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes,
)
from keep_alive import keep_alive

# ── Handlers ────────────────────────────────────────────────────
from handlers.start      import (start_handler, gender_handler,
                                  class_selection_handler,
                                  name_input_handler, show_main_menu)
from handlers.profile    import profile_handler
from handlers.battle     import battle_handler, battle_action_handler
from handlers.dungeon    import dungeon_handler, dungeon_action_handler
from handlers.shop       import shop_handler, shop_action_handler
from handlers.inventory  import inventory_handler, inventory_action_handler
from handlers.market     import market_handler, market_action_handler
from handlers.transfer   import transfer_handler, transfer_action_handler
from handlers.book       import book_handler, book_action_handler
from handlers.daily      import daily_handler
from handlers.leaderboard import leaderboard_handler, lb_action_handler
from handlers.rest       import rest_handler, rest_action_handler
from handlers.group_boss import group_boss_handler, group_boss_action_handler
from handlers.admin      import (
    admin_handler, admin_action_handler,
    addcoin_handler, adddiamond_handler,
    setvip_handler, setmedia_handler,
    addadmin_handler, removeadmin_handler,
    ban_handler, unban_handler,
    adminhelp_handler,
)

# ── Buat folder data sebelum logging ────────────────────────────
os.makedirs("data", exist_ok=True)

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# FIX: Token dibaca dari env var saja; jangan hardcode di kode
BOT_TOKEN = os.environ.get("BOT_TOKEN","8656505461:AAGwzpxBdkzpquDA3Pz4aRExxVpOu9vBNYo")
if not BOT_TOKEN:
    logger.critical("❌ BOT_TOKEN belum diset! Set environment variable BOT_TOKEN.")
    sys.exit(1)


# ════════════════════════════════════════════════════════════════
#  /help
# ════════════════════════════════════════════════════════════════
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "╔══════════════════════════════════╗\n"
        "║      📖  *PANDUAN LENGKAP*       ║\n"
        "╚══════════════════════════════════╝\n\n"
        "⚔️ *PERINTAH UTAMA*\n"
        "/start       — Mulai & Menu Utama\n"
        "/profile     — Profil & Stats karakter\n"
        "/battle      — Lawan monster acak\n"
        "/dungeon     — Masuki dungeon\n"
        "/shop        — Beli item, skill & equipment\n"
        "/inventory   — Kelola item & potion\n"
        "/market      — Jual & beli antar pemain\n"
        "/transfer    — Kirim item ke pemain lain\n"
        "/book        — Ensiklopedia monster & boss\n"
        "/daily       — Login bonus harian\n"
        "/leaderboard — Papan peringkat\n"
        "/rest        — Istirahat & regen HP/MP\n"
        "/help        — Panduan ini\n"
        "/menu        — Tampilkan menu utama\n\n"
        "😴 *SISTEM ISTIRAHAT (/rest)*\n"
        "• Regen +15 HP & +12 MP setiap 10 detik\n"
        "• Tekan ❌ Batal untuk lanjut bermain\n"
        "• Cooldown 60 detik setelah berhenti\n"
        "• Maks durasi: 5 menit per sesi\n\n"
        "🔮 *SKILL SHOP (/shop → Skill)*\n"
        "• 5 skill eksklusif per kelas (2 baru!)\n"
        "• Skill tersimpan permanen di karakter\n"
        "• Gunakan saat battle dengan tombol Skill\n\n"
        "🏆 *LEADERBOARD (/leaderboard)*\n"
        "• Tab 🏆 Semua Waktu | 📅 Mingguan | 📆 Bulanan\n"
        "• Diurutkan: Level, Kills, Boss Kills\n\n"
        "💎 *SISTEM VIP*\n"
        "• 🥈 Silver — Bonus stat ringan, 30 hari\n"
        "• 🥇 Gold — Bonus stat sedang, 30 hari\n"
        "• 💎 Diamond — Bonus stat tinggi, 30 hari\n\n"
        "🎯 *TIPS BERMAIN*\n"
        "• Klaim /daily setiap hari untuk streak bonus\n"
        "• Senjata & armor harus sesuai kelasmu\n"
        "• Boss dungeon drop item langka acak\n"
        "• Gunakan /rest saat HP/MP rendah\n"
        "• Transfer item maks 2x per minggu\n\n"
        "💡 *ALUR PROGRESSION*\n"
        "Battle → EXP → Level Up → Dungeon\n"
        "→ Boss → Item Langka → Skill Shop → Market"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ════════════════════════════════════════════════════════════════
#  /menu command
# ════════════════════════════════════════════════════════════════
async def menu_cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

async def menu_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_main_menu(query, context)


# ════════════════════════════════════════════════════════════════
#  BOT COMMANDS (menu Telegram)
# ════════════════════════════════════════════════════════════════
PLAYER_COMMANDS = [
    BotCommand("start",       "🏠 Mulai & Menu Utama"),
    BotCommand("profile",     "📜 Profil karakter"),
    BotCommand("battle",      "⚔️ Lawan monster"),
    BotCommand("dungeon",     "🏰 Masuki dungeon"),
    BotCommand("shop",        "🛒 Toko item & equipment"),
    BotCommand("inventory",   "🎒 Inventori"),
    BotCommand("market",      "🏪 Pasar antar pemain"),
    BotCommand("transfer",    "📦 Kirim item"),
    BotCommand("daily",       "📅 Login bonus harian"),
    BotCommand("leaderboard", "🏆 Papan peringkat"),
    BotCommand("rest",        "😴 Istirahat & regen HP/MP"),
    BotCommand("book",        "📖 Ensiklopedia monster"),
    BotCommand("menu",        "📌 Tampilkan menu"),
    BotCommand("help",        "❓ Panduan bermain"),
]


# ════════════════════════════════════════════════════════════════
#  Menu action callbacks
# ════════════════════════════════════════════════════════════════
async def menu_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    instructions = {
        "menu_battle":    "⚔️ Ketik /battle untuk mulai bertarung!",
        "menu_dungeon":   "🏰 Ketik /dungeon untuk masuki dungeon!",
        "menu_shop":      "🛒 Ketik /shop untuk buka toko!",
        "menu_inventory": "🎒 Ketik /inventory untuk buka inventori!",
        "menu_market":    "🏪 Ketik /market untuk buka pasar!",
        "menu_transfer":  "📦 Ketik /transfer untuk kirim item!",
        "menu_rest":      "😴 Ketik /rest untuk mulai istirahat!",
        "menu_daily":     "📅 Ketik /daily untuk klaim bonus harian!",
        "menu_book":      "📖 Ketik /book untuk buka ensiklopedia!",
        "menu_help":      "❓ Ketik /help untuk panduan bermain!",
    }
    msg = instructions.get(action, "Gunakan command yang sesuai.")
    await query.message.reply_text(msg)


def main():
    os.makedirs("data", exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()

    # ── Player Commands ───────────────────────────────────────────
    app.add_handler(CommandHandler("start",       start_handler))
    app.add_handler(CommandHandler("profile",     profile_handler))
    app.add_handler(CommandHandler("battle",      battle_handler))
    app.add_handler(CommandHandler("dungeon",     dungeon_handler))
    app.add_handler(CommandHandler("shop",        shop_handler))
    app.add_handler(CommandHandler("inventory",   inventory_handler))
    app.add_handler(CommandHandler("market",      market_handler))
    app.add_handler(CommandHandler("transfer",    transfer_handler))
    app.add_handler(CommandHandler("book",        book_handler))
    app.add_handler(CommandHandler("daily",       daily_handler))
    app.add_handler(CommandHandler("leaderboard", leaderboard_handler))
    app.add_handler(CommandHandler("rest",        rest_handler))
    app.add_handler(CommandHandler("help",        help_handler))
    app.add_handler(CommandHandler("menu",        menu_cmd_handler))
    app.add_handler(CommandHandler("groupboss",   group_boss_handler))

    # ── Admin Commands ────────────────────────────────────────────
    app.add_handler(CommandHandler("admin",        admin_handler))
    app.add_handler(CommandHandler("adminhelp",    adminhelp_handler))
    app.add_handler(CommandHandler("addcoin",      addcoin_handler))
    app.add_handler(CommandHandler("adddiamond",   adddiamond_handler))
    app.add_handler(CommandHandler("setvip",       setvip_handler))
    app.add_handler(CommandHandler("setmedia",     setmedia_handler))
    app.add_handler(CommandHandler("addadmin",     addadmin_handler))
    app.add_handler(CommandHandler("removeadmin",  removeadmin_handler))
    app.add_handler(CommandHandler("ban",          ban_handler))
    app.add_handler(CommandHandler("unban",        unban_handler))

    # ── Callbacks ─────────────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(gender_handler,            pattern=r"^gender_"))
    app.add_handler(CallbackQueryHandler(class_selection_handler,   pattern=r"^class_"))
    app.add_handler(CallbackQueryHandler(battle_action_handler,     pattern=r"^battle_"))
    app.add_handler(CallbackQueryHandler(shop_action_handler,       pattern=r"^shop_"))
    app.add_handler(CallbackQueryHandler(dungeon_action_handler,    pattern=r"^dungeon_"))
    app.add_handler(CallbackQueryHandler(inventory_action_handler,  pattern=r"^inv_"))
    app.add_handler(CallbackQueryHandler(market_action_handler,     pattern=r"^market_"))
    app.add_handler(CallbackQueryHandler(transfer_action_handler,   pattern=r"^transfer_"))
    app.add_handler(CallbackQueryHandler(book_action_handler,       pattern=r"^book_"))
    app.add_handler(CallbackQueryHandler(lb_action_handler,         pattern=r"^lb_"))
    app.add_handler(CallbackQueryHandler(admin_action_handler,      pattern=r"^admin_"))
    app.add_handler(CallbackQueryHandler(rest_action_handler,       pattern=r"^rest_"))
    app.add_handler(CallbackQueryHandler(group_boss_action_handler, pattern=r"^gb_"))
    app.add_handler(CallbackQueryHandler(profile_handler,           pattern=r"^profile$"))
    app.add_handler(CallbackQueryHandler(menu_cb_handler,           pattern=r"^menu$"))
    app.add_handler(CallbackQueryHandler(menu_action_handler,       pattern=r"^menu_"))

    # ── Text input (nama karakter) ────────────────────────────────
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, name_input_handler))

    # ── Set bot commands ──────────────────────────────────────────
    async def post_init(application):
        await application.bot.set_my_commands(PLAYER_COMMANDS)
        logger.info("✅ Bot commands registered.")

    app.post_init = post_init

    logger.info("⚔️  Legends of Eternity v5.0 — READY!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    keep_alive()
    main()
