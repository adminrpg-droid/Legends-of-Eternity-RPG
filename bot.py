import logging
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from keep_alive import keep_alive

# ── Handlers ────────────────────────────────────────────────────
from handlers.start     import (start_handler, gender_handler,
                                 class_selection_handler,
                                 name_input_handler, show_main_menu)
from handlers.profile   import profile_handler
from handlers.battle    import battle_handler, battle_action_handler
from handlers.dungeon   import dungeon_handler, dungeon_action_handler
from handlers.shop      import shop_handler, shop_action_handler
from handlers.inventory import inventory_handler, inventory_action_handler
from handlers.market    import market_handler, market_action_handler
from handlers.transfer  import transfer_handler, transfer_action_handler
from handlers.book      import book_handler, book_action_handler
from handlers.daily     import daily_handler
from handlers.leaderboard import leaderboard_handler, lb_action_handler
from handlers.admin     import (admin_handler, admin_action_handler,
                                 addcoin_handler, adddiamond_handler,
                                 setvip_handler, setmedia_handler)
from handlers.rest      import rest_handler, rest_action_handler
from handlers.group_boss import group_boss_handler, group_boss_action_handler

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN","8656505461:AAGwzpxBdkzpquDA3Pz4aRExxVpOu9vBNYo")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN belum diset! Tambahkan ke environment variable.")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "╔══════════════════════════════════╗\n"
        "║      📖  *PANDUAN LENGKAP*       ║\n"
        "╚══════════════════════════════════╝\n\n"
        "⚔️ *PERINTAH UTAMA*\n"
        "/start       — Mulai & Menu Utama\n"
        "/profile     — Profil & Stats\n"
        "/profile @user — Lihat profil pemain lain di grup\n"
        "/battle      — Lawan monster acak\n"
        "/dungeon     — Masuki dungeon\n"
        "/shop        — Beli item, skill & equipment\n"
        "/inventory   — Kelola item & potion\n"
        "/market      — Jual & beli antar pemain\n"
        "/transfer    — Kirim item ke pemain lain\n"
        "/book        — Ensiklopedia monster & boss\n"
        "/daily       — Login bonus harian\n"
        "/leaderboard — Papan peringkat\n"
        "/rest        — Istirahat untuk regen HP & MP\n"
        "/help        — Panduan ini\n\n"
        "👥 *PERINTAH GRUP (Admin)*\n"
        "/groupboss   — Spawn boss untuk dilawan bersama\n"
        "_(Maks 5 pemain, auto-battle, hadiah khusus pembunuh boss)_\n\n"
        "😴 *SISTEM ISTIRAHAT*\n"
        "• /rest — Mulai istirahat, regen HP+15 & MP+12 per 10 detik\n"
        "• Tekan ❌ Batal untuk lanjut bermain kapan saja\n"
        "• Cooldown 60 detik setelah berhenti istirahat\n"
        "• Maks durasi istirahat: 5 menit\n\n"
        "🔮 *SKILL SHOP*\n"
        "• Beli skill ekstra di /shop → Skill\n"
        "• Skill sesuai kelas masing-masing\n"
        "• Harga mulai 3.500 hingga 9.000 Coin\n\n"
        "🎯 *TIPS BERMAIN*\n"
        "• Klaim /daily setiap hari untuk streak bonus\n"
        "• Senjata & armor harus sesuai kelasmu\n"
        "• Boss dungeon drop item langka acak\n"
        "• Transfer item maks 2x per minggu\n"
        "• VIP memberi Crit, HP, MP, ATK bonus\n"
        "• /rest saat HP/MP rendah sebelum masuk dungeon\n\n"
        "💡 *ALUR PROGRESSION*\n"
        "Battle → EXP → Level Up → Dungeon → Boss\n"
        "→ Item Langka → Skill Shop → Group Boss → Market"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def menu_cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)


async def menu_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_main_menu(query, context)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ── Commands ─────────────────────────────────────────────────
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
    app.add_handler(CommandHandler("help",        help_handler))
    app.add_handler(CommandHandler("menu",        menu_cmd_handler))
    app.add_handler(CommandHandler("rest",        rest_handler))
    app.add_handler(CommandHandler("groupboss",   group_boss_handler))

    # ── Admin Commands ────────────────────────────────────────────
    app.add_handler(CommandHandler("admin",      admin_handler))
    app.add_handler(CommandHandler("addcoin",    addcoin_handler))
    app.add_handler(CommandHandler("adddiamond", adddiamond_handler))
    app.add_handler(CommandHandler("setvip",     setvip_handler))
    app.add_handler(CommandHandler("setmedia",   setmedia_handler))

    # ── Callbacks ─────────────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(gender_handler,              pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(class_selection_handler,     pattern="^class_"))
    app.add_handler(CallbackQueryHandler(battle_action_handler,       pattern="^battle_"))
    app.add_handler(CallbackQueryHandler(shop_action_handler,         pattern="^shop_"))
    app.add_handler(CallbackQueryHandler(dungeon_action_handler,      pattern="^dungeon_"))
    app.add_handler(CallbackQueryHandler(inventory_action_handler,    pattern="^inv_"))
    app.add_handler(CallbackQueryHandler(market_action_handler,       pattern="^market_"))
    app.add_handler(CallbackQueryHandler(transfer_action_handler,     pattern="^transfer_"))
    app.add_handler(CallbackQueryHandler(book_action_handler,         pattern="^book_"))
    app.add_handler(CallbackQueryHandler(lb_action_handler,           pattern="^lb_"))
    app.add_handler(CallbackQueryHandler(admin_action_handler,        pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(rest_action_handler,         pattern="^rest_"))
    app.add_handler(CallbackQueryHandler(group_boss_action_handler,   pattern="^gb_"))
    app.add_handler(CallbackQueryHandler(profile_handler,             pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(menu_cb_handler,             pattern="^menu$"))

    # ── Text input (for character name) ──────────────────────────
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        name_input_handler
    ))

    logger.info("⚔️  Legends of Eternity v4.0 is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    keep_alive()
    main()
