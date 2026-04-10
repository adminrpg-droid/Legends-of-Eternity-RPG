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
from handlers.shop       import shop_handler, shop_action_handler, premium_shop_handler, premium_shop_action_handler
from handlers.inventory  import inventory_handler, inventory_action_handler
from handlers.market     import market_handler, market_action_handler
from handlers.transfer   import transfer_handler, transfer_action_handler
from handlers.book       import book_handler, book_action_handler
from handlers.daily      import daily_handler
from handlers.leaderboard import leaderboard_handler, lb_action_handler
from handlers.rest       import rest_handler, rest_action_handler
from handlers.group_boss import group_boss_handler, group_boss_action_handler, reset_group_boss_handler
from handlers.pvp       import pvp_handler, pvp_action_handler, pvpstats_handler
from handlers.quest   import quest_handler, quest_action_handler
from handlers.enhance import enhance_handler, enhance_action_handler
from handlers.battle  import reset_battle_handler
from handlers.market_channel import setchannel_handler
from handlers.title   import title_handler, title_action_handler
from handlers.war     import (
    war_handler, war_menu_handler, war_declare_handler,
    war_vote_handler, war_vote_status_handler,
    war_info_handler, war_history_handler, war_status_handler,
    warstats_handler, setkerajaan_handler,
)
from handlers.admin      import (
    admin_handler, admin_action_handler,
    addcoin_handler, adddiamond_handler,
    setvip_handler,
    addadmin_handler, removeadmin_handler,
    ban_handler, unban_handler,
    adminhelp_handler,
    resetplayer_handler, resetall_handler, addgold_handler,
    addstone_handler, setlevel_handler,
    broadcast_handler, setmedia_reply_handler,
    infofoto_handler, infofoto_action_handler,
    giveallgold_handler, givealldiamond_handler,
    giveitem_handler,
)
from handlers.profile import profile_media_handler, profile_rename_handler, profile_rename_cancel_handler, rename_input_handler
from handlers.market  import market_price_input_handler

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

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")  # Set via environment variable, jangan hardcode!
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
        "📌 *MENU UTAMA*\n"
        "Semua fitur tersedia melalui tombol menu.\n"
        "Gunakan /start atau /menu untuk membuka menu utama.\n\n"
        "📌 *SISTEM ISTIRAHAT*\n"
        "Regen +15 HP & +12 MP setiap 10 detik.\n"
        "Tekan Batal untuk lanjut bermain.\n"
        "Cooldown 30 detik setelah berhenti.\n"
        "Maks durasi: 5 menit per sesi.\n\n"
        "📌 *SKILL SHOP*\n"
        "5 skill eksklusif per kelas.\n"
        "Skill tersimpan permanen di karakter.\n"
        "Equip skill di Equipment, aktif saat battle.\n\n"
        "📌 *SISTEM BATTLE*\n"
        "Cooldown 5 detik mencari monster.\n"
        "Cooldown 3 detik setiap aksi battle.\n"
        "Membunuh monster/boss mendapat Gold & EXP.\n"
        "⚠️ Kalah tidak mengurangi Gold!\n"
        "🔄 Battle stuck? Ketik /resetbattle untuk reset.\n\n"
        "📌 *GROUP BOSS RAID*\n"
        "Ketik /groupboss atau /grub di grup untuk mulai Boss Raid.\n"
        "Ajak teman join raid dan kalahkan boss bersama!\n"
        "Stat boss otomatis scale sesuai jumlah pemain.\n"
        "Drop: 💠 Evolution Stone (0.1%) & 🔱 GOD SSSR (0.1%) untuk semua peserta!\n"
        "Killer mendapat bonus Gold x2.\n\n"
        "📌 *MARKET P2P*\n"
        "Jual & beli item antar pemain via /market.\n"
        "Listing baru otomatis dipost ke channel market.\n"
        "Penjual tampil sebagai ID yang bisa diklik.\n\n"
        "📌 *LEADERBOARD*\n"
        "Tab Semua Waktu, Mingguan, Bulanan.\n"
        "Diurutkan: Level, Kills, Boss Kills.\n\n"
        "📌 *SISTEM VIP*\n"
        "Silver — Bonus stat ringan, 30 hari.\n"
        "Gold — Bonus stat sedang, 30 hari.\n"
        "Diamond — Bonus stat tinggi, 30 hari.\n\n"
        "📌 *TIPS BERMAIN*\n"
        "Klaim Daily setiap hari untuk streak bonus.\n"
        "Weapon, Armor & Skill butuh level tertentu.\n"
        "Boss dungeon drop: 💠 Evolution Stone & 🔱 GOD SSSR item.\n"
        "Item drop masuk inventory otomatis, tidak langsung dipakai.\n"
        "Istirahat saat HP/MP rendah.\n\n"
        "📌 *EVOLUTION SYSTEM*\n"
        "Class & Pet punya 10 Tier evolusi.\n"
        "Naik tier butuh Evolution Stone (sangat langka!).\n"
        "Evolution Stone drop dari Boss/Dungeon Boss/Group Boss rate 0.1%.\n"
        "Tier GOD = multiplier stat x3.0!\n\n"
        "📌 *CLASS SPECIAL & STATUS EFFECTS*\n"
        "Tiap class punya Special ability unik.\n"
        "Status: Burn, Poison, Stun, Freeze, Bleed.\n"
        "Item SSR/UR/GOD punya special effect di battle.\n\n"
        "📌 *PET SYSTEM*\n"
        "Pet memberikan bonus stat & passive skill.\n"
        "Rarity: Common → Uncommon → Rare → Epic → SSR → UR → GOD.\n"
        "Pet bisa dievolution hingga Tier 10 LEGENDARY.\n\n"
        "📌 *ALUR PROGRESSION*\n"
        "Battle → EXP → Level Up → Beli Equipment\n"
        "→ Dungeon → Boss → Evolution Stone (0.1%!)\n"
        "→ Evolution → GOD TIER → Premium Shop SSR/UR/GOD"
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

async def noop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk tombol header/label yang tidak melakukan apa-apa."""
    await update.callback_query.answer()


# ════════════════════════════════════════════════════════════════
#  Menu action callbacks — langsung trigger handler
# ════════════════════════════════════════════════════════════════
async def menu_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    user = query.from_user

    from database import get_player
    from handlers.war import war_menu_handler
    player = get_player(user.id)
    if not player:
        await query.message.reply_text("❌ Ketik /start dulu!")
        return

    if action == "menu_battle":
        await battle_handler_from_menu(query, context, player)
        return

    if action == "menu_dungeon":
        from handlers.dungeon import _show_dungeon_list
        await _show_dungeon_list(query.message, player, is_msg=True)
        return

    if action == "menu_shop":
        from handlers.shop import _shop_main_keyboard
        def _gold_line(p): return f"🪙 Gold: *{p.get('coin',0):,}*  💎 Diamond: *{p.get('diamond',0)}*"
        text = (
            "╔══════════════════════════════════╗\n"
            "║       🛒  *TOKO ETERNITY*        ║\n"
            "╠══════════════════════════════════╣\n"
            f"║  {_gold_line(player)}\n"
            "╚══════════════════════════════════╝\n\n"
            "🛍️ Pilih kategori item:"
        )
        await query.message.reply_text(text, parse_mode="Markdown",
                                       reply_markup=_shop_main_keyboard(player))
        return

    if action == "menu_inventory":
        from handlers.inventory import _show_equipment
        await _show_equipment(query.message, player, is_msg=True)
        return

    if action == "menu_market":
        from handlers.market import _show_market
        await _show_market(query.message, player, is_msg=True)
        return

    if action == "menu_transfer":
        from handlers.transfer import _show_transfer_menu
        await _show_transfer_menu(query.message, player, user.id, is_msg=True)
        return

    if action == "menu_rest":
        from handlers.rest import _show_rest_status, _build_rest_message, _rest_loop, REST_COOLDOWN
        import asyncio, time as _time
        now = _time.time()
        rest_cd_until = player.get("rest_cooldown_until", 0)
        if now < rest_cd_until:
            sisa = int(rest_cd_until - now)
            await query.message.reply_text(
                f"⏳ *Kamu masih lelah!*\nCooldown: `{sisa}` detik lagi.",
                parse_mode="Markdown"
            )
            return
        if player["hp"] >= player["max_hp"] and player["mp"] >= player["max_mp"]:
            await query.message.reply_text(
                f"✅ *HP dan MP kamu sudah penuh!*\n❤️ {player['hp']}/{player['max_hp']}  💙 {player['mp']}/{player['max_mp']}",
                parse_mode="Markdown"
            )
            return
        if player.get("is_resting"):
            await _show_rest_status(query.message, player, user.id, is_msg=True)
            return
        player["is_resting"]   = True
        player["rest_start"]   = now
        player["rest_msg_id"]  = None
        player["rest_chat_id"] = query.message.chat_id
        from database import save_player
        save_player(user.id, player)
        text, markup = _build_rest_message(player, now)
        msg = await query.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)
        player["rest_msg_id"] = msg.message_id
        save_player(user.id, player)
        asyncio.create_task(_rest_loop(context, user.id, query.message.chat_id, msg.message_id))
        return

    if action == "menu_daily":
        from handlers.daily import daily_handler
        # BUG FIX: gunakan instance attributes (bukan class-level) agar tidak
        # terjadi shared state antar user yang memanggil menu_daily bersamaan
        class _FakeUpdate:
            def __init__(self, _user, _msg, _chat):
                self.effective_user = _user
                self.message        = _msg
                self.effective_chat = _chat
        await daily_handler(_FakeUpdate(user, query.message, query.message.chat), context)
        return

    if action == "menu_book":
        from handlers.book import _show_book_menu
        await _show_book_menu(query.message, player, is_msg=True)
        return

    if action == "menu_help":
        # help_handler menggunakan update.message — tidak bisa dipanggil langsung dari callback
        # Gunakan query.message.reply_text sebagai gantinya
        await query.message.reply_text(
            "❓ Ketik /help untuk panduan bermain lengkap!", parse_mode="Markdown"
        )
        return

    if action == "menu_premiumshop":
        from handlers.shop import _show_premium_main
        await _show_premium_main(query.message, player, edit=False)
        return

    if action == "menu_evolution":
        from handlers.shop import _show_evolution_info
        class _FakeQuery:
            async def edit_message_text(self, *a, **kw):
                await query.message.reply_text(*a, **kw)
        await _show_evolution_info(_FakeQuery(), player)
        return

    if action == "menu_war":
        # BUG FIX #3: war_menu_handler memerlukan update dengan callback_query valid
        # Langsung tampilkan war menu tanpa melewati war_menu_handler
        from handlers.war import _show_war_menu
        await _show_war_menu(query.message, player, user.id, is_msg=True)
        return

    await query.message.reply_text("Gunakan command yang sesuai.")


async def battle_handler_from_menu(query, context, player):
    """Trigger battle dari menu button — sinkron dengan battle_handler."""
    import asyncio
    from database import is_admin, is_banned
    from monster import get_random_monster
    from handlers.battle import _show_battle, _sbs

    user = query.from_user
    if is_banned(user.id):
        await query.message.reply_text("🚫 Akunmu di-ban! Hubungi admin.")
        return
    if player["hp"] <= 0:
        await query.message.reply_text("💀 HP 0! Pulihkan dulu di /equipment (Rest)")
        return
    if player.get("is_resting"):
        await query.message.reply_text("😴 Kamu sedang istirahat! Ketik /rest untuk berhenti dulu.")
        return

    # BUG FIX: state init sekarang identik dengan battle_handler (tambah monster_status, status_effects, attack_count)
    def _make_state(monster):
        return {
            "monster": monster, "turn": 1, "log": [],
            "death_marked": False, "dot": 0, "dot_turns": 0,
            "monster_status": {}, "status_effects": {},
            "attack_count": 0, "souls": 0,
        }

    admin = is_admin(user.id)
    if admin:
        monster = get_random_monster(player["level"])
        state   = _make_state(monster)
        _sbs(context, user.id, state)
        await _show_battle(query.message, player, state, first=True)
    else:
        msg = await query.message.reply_text(
            "🔍 *Mencari monster...*\n⏳ Cooldown 5 detik...",
            parse_mode="Markdown"
        )
        await asyncio.sleep(5)
        monster = get_random_monster(player["level"])
        state   = _make_state(monster)
        _sbs(context, user.id, state)
        try:
            await msg.edit_text(
                f"✅ *Monster ditemukan!*\n"
                f"{monster['emoji']} *{monster['name']}* muncul!\n\n"
                f"⚔️ Persiapkan dirimu...",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await asyncio.sleep(1)
        await _show_battle(query.message, player, state, first=True)


# ════════════════════════════════════════════════════════════════
#  BOT COMMANDS
# ════════════════════════════════════════════════════════════════
PLAYER_COMMANDS = [
    BotCommand("start",       "🏠 Mulai & Menu Utama"),
    BotCommand("profile",     "📜 Profil karakter"),
    BotCommand("battle",      "⚔️ Lawan monster"),
    BotCommand("dungeon",     "🏰 Masuki dungeon"),
    BotCommand("shop",        "🛒 Toko item & equipment"),
    BotCommand("premiumshop", "💎 Toko SSR/UR/GOD & Pet & Evolution"),
    BotCommand("equipment",   "⚔️ Equipment & Skill"),
    BotCommand("market",      "🏪 Pasar antar pemain"),
    BotCommand("transfer",    "📦 Kirim item"),
    BotCommand("daily",       "📅 Login bonus harian"),
    BotCommand("leaderboard", "🏆 Papan peringkat"),
    BotCommand("rest",        "😴 Istirahat & regen HP/MP"),
    BotCommand("book",        "📖 Ensiklopedia monster"),
    BotCommand("menu",        "📌 Tampilkan menu"),
    BotCommand("quest",       "📜 Quest harian & mingguan"),
    BotCommand("enhance",     "⚒️ Enhance item dengan Diamond"),
    BotCommand("title",       "🏅 Koleksi title karakter"),
    BotCommand("pvp",         "⚔️ Tantang pemain lain (grup)"),
    BotCommand("pvpstats",    "📊 Statistik PVP kamu"),
    BotCommand("war",         "⚔️ Menu war kerajaan"),
    BotCommand("warstats",    "📊 Statistik perang kerajaan"),
    BotCommand("infofoto",    "🖼️ Lihat foto/GIF class, item, pet"),
    BotCommand("resetbattle", "🔄 Reset battle jika stuck"),
    BotCommand("help",        "❓ Panduan bermain"),
]


def main():
    os.makedirs("data", exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()

    # ── Player Commands ───────────────────────────────────────────
    app.add_handler(CommandHandler("start",       start_handler))
    app.add_handler(CommandHandler("profile",     profile_handler))
    app.add_handler(CommandHandler("battle",      battle_handler))
    app.add_handler(CommandHandler("dungeon",     dungeon_handler))
    app.add_handler(CommandHandler("shop",        shop_handler))
    app.add_handler(CommandHandler("premiumshop", premium_shop_handler))
    app.add_handler(CommandHandler("inventory",   inventory_handler))  # backward compat
    app.add_handler(CommandHandler("equipment",   inventory_handler))  # new name
    app.add_handler(CommandHandler("market",      market_handler))
    app.add_handler(CommandHandler("transfer",    transfer_handler))
    app.add_handler(CommandHandler("book",        book_handler))
    app.add_handler(CommandHandler("daily",       daily_handler))
    app.add_handler(CommandHandler("leaderboard", leaderboard_handler))
    app.add_handler(CommandHandler("rest",        rest_handler))
    app.add_handler(CommandHandler("help",        help_handler))
    app.add_handler(CommandHandler("menu",        menu_cmd_handler))
    app.add_handler(CommandHandler("quest",        quest_handler))
    app.add_handler(CommandHandler("enhance",      enhance_handler))
    app.add_handler(CommandHandler("title",        title_handler))
    app.add_handler(CommandHandler("pvp",          pvp_handler))
    app.add_handler(CommandHandler("pvpstats",     pvpstats_handler))
    app.add_handler(CommandHandler("resetbattle",  reset_battle_handler))   # Fix battle stuck
    app.add_handler(CommandHandler("war",          war_handler))
    app.add_handler(CommandHandler("warstats",     warstats_handler))
    app.add_handler(CommandHandler("setkerajaan",  setkerajaan_handler))

    # ── Admin Commands ────────────────────────────────────────────
    app.add_handler(CommandHandler("admin",        admin_handler))
    app.add_handler(CommandHandler("adminhelp",    adminhelp_handler))
    app.add_handler(CommandHandler("addcoin",      addcoin_handler))
    app.add_handler(CommandHandler("addgold",      addgold_handler))
    app.add_handler(CommandHandler("adddiamond",   adddiamond_handler))
    app.add_handler(CommandHandler("addstone",     addstone_handler))
    app.add_handler(CommandHandler("setvip",       setvip_handler))
    app.add_handler(CommandHandler("setmedia",     setmedia_reply_handler))
    app.add_handler(CommandHandler("addadmin",     addadmin_handler))
    app.add_handler(CommandHandler("removeadmin",  removeadmin_handler))
    app.add_handler(CommandHandler("ban",          ban_handler))
    app.add_handler(CommandHandler("unban",        unban_handler))
    app.add_handler(CommandHandler("resetplayer",  resetplayer_handler))
    app.add_handler(CommandHandler("resetall",     resetall_handler))
    app.add_handler(CommandHandler("setlevel",     setlevel_handler))
    app.add_handler(CommandHandler("giveallgold",     giveallgold_handler))
    app.add_handler(CommandHandler("givealldiamond",  givealldiamond_handler))
    app.add_handler(CommandHandler("giveitem",        giveitem_handler))
    app.add_handler(CommandHandler("groupboss",    group_boss_handler))
    app.add_handler(CommandHandler("grub",         group_boss_handler))
    app.add_handler(CommandHandler("resetgroupboss", reset_group_boss_handler))  # Admin: reset stuck group boss
    app.add_handler(CommandHandler("setchannel",   setchannel_handler))          # Admin: set market channel
    app.add_handler(CommandHandler("broadcast",    broadcast_handler))
    app.add_handler(CommandHandler("infofoto",     infofoto_handler))

    # ── Callbacks ─────────────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(gender_handler,            pattern=r"^gender_"))
    app.add_handler(CallbackQueryHandler(class_selection_handler,   pattern=r"^class_"))
    app.add_handler(CallbackQueryHandler(battle_action_handler,     pattern=r"^battle_"))
    app.add_handler(CallbackQueryHandler(shop_action_handler,       pattern=r"^shop_"))
    app.add_handler(CallbackQueryHandler(premium_shop_action_handler, pattern=r"^pshop_"))
    app.add_handler(CallbackQueryHandler(dungeon_action_handler,    pattern=r"^dungeon_"))
    app.add_handler(CallbackQueryHandler(inventory_action_handler,  pattern=r"^inv_"))
    app.add_handler(CallbackQueryHandler(market_action_handler,     pattern=r"^market_"))
    app.add_handler(CallbackQueryHandler(market_action_handler,     pattern=r"^mkt_"))
    app.add_handler(CallbackQueryHandler(transfer_action_handler,   pattern=r"^transfer_"))
    app.add_handler(CallbackQueryHandler(book_action_handler,       pattern=r"^book_"))
    app.add_handler(CallbackQueryHandler(lb_action_handler,         pattern=r"^lb_"))
    app.add_handler(CallbackQueryHandler(admin_action_handler,      pattern=r"^admin_"))
    app.add_handler(CallbackQueryHandler(rest_action_handler,       pattern=r"^rest_"))
    app.add_handler(CallbackQueryHandler(group_boss_action_handler, pattern=r"^gb_"))
    app.add_handler(CallbackQueryHandler(pvp_action_handler,        pattern=r"^pvp_"))
    app.add_handler(CallbackQueryHandler(quest_action_handler,      pattern=r"^quest_"))
    app.add_handler(CallbackQueryHandler(enhance_action_handler,    pattern=r"^enhance_"))
    app.add_handler(CallbackQueryHandler(title_action_handler,      pattern=r"^title_"))
    app.add_handler(CallbackQueryHandler(profile_handler,           pattern=r"^profile$"))
    app.add_handler(CallbackQueryHandler(profile_media_handler,     pattern=r"^profile_media$"))
    app.add_handler(CallbackQueryHandler(profile_rename_handler,    pattern=r"^profile_rename$"))
    app.add_handler(CallbackQueryHandler(profile_rename_cancel_handler, pattern=r"^profile_rename_cancel$"))
    app.add_handler(CallbackQueryHandler(infofoto_action_handler,   pattern=r"^infofoto_"))
    app.add_handler(CallbackQueryHandler(menu_cb_handler,           pattern=r"^menu$"))
    app.add_handler(CallbackQueryHandler(menu_action_handler,       pattern=r"^menu_"))
    app.add_handler(CallbackQueryHandler(noop_handler,              pattern=r"^noop$"))

    # ── War Callbacks ─────────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(war_menu_handler,          pattern=r"^war_menu$"))
    app.add_handler(CallbackQueryHandler(war_declare_handler,       pattern=r"^war_declare$"))
    app.add_handler(CallbackQueryHandler(war_vote_handler,          pattern=r"^war_vote_yes$"))
    app.add_handler(CallbackQueryHandler(war_vote_handler,          pattern=r"^war_vote_no$"))
    app.add_handler(CallbackQueryHandler(war_vote_status_handler,   pattern=r"^war_vote_status$"))
    app.add_handler(CallbackQueryHandler(war_status_handler,        pattern=r"^war_status$"))
    app.add_handler(CallbackQueryHandler(war_info_handler,          pattern=r"^war_info$"))
    app.add_handler(CallbackQueryHandler(war_history_handler,       pattern=r"^war_history$"))

    # ── Text input ────────────────────────────────────────────────
    # market_price_input_handler di group 0 agar diperiksa lebih dulu
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, market_price_input_handler), group=0)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, name_input_handler), group=1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, rename_input_handler), group=2)

    async def post_init(application):
        await application.bot.set_my_commands(PLAYER_COMMANDS)
        logger.info("✅ Bot commands registered.")

    app.post_init = post_init
    app.add_error_handler(error_handler)

    logger.info("⚔️  Legends of Eternity v9.0 — READY!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


# ════════════════════════════════════════════════════════════════
#  Global Error Handler
# ════════════════════════════════════════════════════════════════
async def error_handler(update: object, context) -> None:
    import traceback
    logger.error("Exception saat handle update:", exc_info=context.error)
    tb_str = "".join(traceback.format_exception(None, context.error, context.error.__traceback__))
    logger.error(f"Traceback:\n{tb_str}")
    # Jika ada query, kirim notifikasi error ke user
    if update and hasattr(update, "callback_query") and update.callback_query:
        try:
            await update.callback_query.answer("❌ Terjadi kesalahan internal. Coba lagi.", show_alert=True)
        except Exception:
            pass
    elif update and hasattr(update, "message") and update.message:
        try:
            await update.message.reply_text("❌ Terjadi kesalahan internal. Coba beberapa saat lagi.")
        except Exception:
            pass


if __name__ == "__main__":
    keep_alive()
    main()
