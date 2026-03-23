# ═══════════════════════════════════════════════════════════════
#  LEGENDS OF ETERNITY — Admin Panel Handler
#  UPDATE: Admin bisa respawn boss berdasarkan dungeon yang dipilih
# ═══════════════════════════════════════════════════════════════
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models.database import get_player, save_player, get_all_players, is_admin, apply_vip
from data.monsters import MONSTERS, BOSSES, DUNGEONS, get_boss
from data.items import VIP_PACKAGES


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    await _show_admin_panel(update.message, is_msg=True)


async def admin_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user

    if not is_admin(user.id):
        await query.answer("❌ Bukan admin!", show_alert=True)
        return

    if action == "admin_panel":
        await _show_admin_panel(query)
        return

    if action == "admin_players":
        await _show_all_players(query)
        return

    if action == "admin_give_vip":
        await _show_give_vip(query, context)
        return

    if action == "admin_add_coin":
        await _show_add_coin(query, context)
        return

    if action == "admin_add_diamond":
        await _show_add_diamond(query, context)
        return

    if action.startswith("admin_setvip_"):
        parts  = action.replace("admin_setvip_", "").split("_uid_")
        vip_id = parts[0]
        uid    = int(parts[1])
        await _give_vip(query, uid, vip_id)
        return

    if action == "admin_book":
        await _show_book_editor(query)
        return

    # ── Respawn Boss ─────────────────────────────────────────────
    if action == "admin_respawn_boss":
        await _show_respawn_boss_menu(query)
        return

    if action.startswith("admin_rb_dungeon_"):
        did = int(action.replace("admin_rb_dungeon_", ""))
        await _respawn_boss_for_dungeon(query, context, user.id, did)
        return


async def _show_admin_panel(target, is_msg=False):
    players = get_all_players()
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║     👑  *ADMIN PANEL*            ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  👥 Total Pemain: {len(players)}\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih aksi admin:"
    )
    keyboard = [
        [InlineKeyboardButton("👥 Lihat Semua Pemain", callback_data="admin_players")],
        [
            InlineKeyboardButton("🏅 Beri VIP",     callback_data="admin_give_vip"),
            InlineKeyboardButton("💰 Beri Coin",     callback_data="admin_add_coin"),
        ],
        [InlineKeyboardButton("💎 Beri Diamond",   callback_data="admin_add_diamond")],
        [InlineKeyboardButton("📖 Edit Book/Media", callback_data="admin_book")],
        [InlineKeyboardButton("👹 Respawn Boss",    callback_data="admin_respawn_boss")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def _show_all_players(query):
    players = get_all_players()
    text    = f"╔══ 👥 *SEMUA PEMAIN* ══╗\n\n"
    for uid, p in list(players.items())[:20]:
        vip = "💎" if p.get("vip", {}).get("active") else ""
        text += (
            f"{p['emoji']} *{p['name']}* {vip}\n"
            f"   ID: `{uid}` | Lv.{p['level']} | {p['class']}\n"
            f"   💰{p.get('coin',0)} | 💎{p.get('diamond',0)}\n\n"
        )
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")
        ]])
    )


async def _show_give_vip(query, context):
    players = get_all_players()
    text    = "🏅 *Pilih pemain untuk diberi VIP:*\n"
    buttons = []
    for uid, p in list(players.items())[:10]:
        buttons.append([InlineKeyboardButton(
            f"{p['name']} (ID:{uid})",
            callback_data=f"admin_vip_select_{uid}"
        )])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _give_vip(query, uid: int, vip_id: str):
    player = get_player(uid)
    if not player:
        await query.answer("Pemain tidak ditemukan!", show_alert=True)
        return
    vip_pkg = VIP_PACKAGES.get(vip_id)
    if not vip_pkg:
        await query.answer("VIP tidak valid!", show_alert=True)
        return

    player = apply_vip(player, vip_id, vip_pkg["effects"], vip_pkg["duration_days"])
    save_player(uid, player)
    await query.edit_message_text(
        f"✅ VIP *{vip_pkg['name']}* diberikan kepada *{player['name']}*!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")
        ]])
    )


async def _show_add_coin(query, context):
    text = (
        "💰 *Tambah Coin ke Pemain*\n\n"
        "Gunakan command:\n"
        "`/addcoin <user_id> <jumlah>`\n\n"
        "Contoh: `/addcoin 123456789 1000`"
    )
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup([[
                                      InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")
                                  ]]))


async def _show_add_diamond(query, context):
    text = (
        "💎 *Tambah Diamond ke Pemain*\n\n"
        "Gunakan command:\n"
        "`/adddiamond <user_id> <jumlah>`\n\n"
        "Contoh: `/adddiamond 123456789 100`"
    )
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup([[
                                      InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")
                                  ]]))


async def _show_book_editor(query):
    text = (
        "📖 *EDITOR BOOK & MEDIA*\n\n"
        "Gunakan command berikut untuk mengatur gambar/gif:\n\n"
        "`/setmedia monster <nama_monster> <url/gif>`\n"
        "`/setmedia boss <boss_id> <url/gif>`\n"
        "`/setmedia dungeon <dungeon_id> <url/gif>`\n"
        "`/setmedia item <item_id> <url/gif>`\n\n"
        "Contoh:\n"
        "`/setmedia monster Goblin https://example.com/goblin.gif`"
    )
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup([[
                                      InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")
                                  ]]))


# ─── RESPAWN BOSS ────────────────────────────────────────────────
async def _show_respawn_boss_menu(query):
    """Tampilkan pilihan dungeon untuk respawn boss."""
    text = (
        "👹 *RESPAWN BOSS*\n\n"
        "Pilih dungeon untuk respawn boss-nya:\n"
        "_(Boss akan di-reset dan siap dilawan kembali di dungeon tersebut)_"
    )
    buttons = []
    for did, dg in DUNGEONS.items():
        boss_data = BOSSES.get(dg["boss"], {})
        buttons.append([InlineKeyboardButton(
            f"{dg['emoji']} {dg['name']} → 👹 {boss_data.get('name','Boss')}",
            callback_data=f"admin_rb_dungeon_{did}"
        )])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _respawn_boss_for_dungeon(query, context, admin_id: int, dungeon_id: int):
    """Respawn boss untuk dungeon tertentu — kirim notif ke grup jika ada."""
    dg = DUNGEONS.get(dungeon_id)
    if not dg:
        await query.answer("Dungeon tidak valid!", show_alert=True)
        return

    boss_id   = dg["boss"]
    boss_data = BOSSES.get(boss_id, {})

    # Simpan info boss yang di-respawn ke context agar dungeon handler bisa cek
    if not hasattr(context, "bot_data"):
        context.bot_data = {}
    context.bot_data[f"boss_respawn_{dungeon_id}"] = {
        "boss_id":    boss_id,
        "respawn_at": time.time(),
        "by_admin":   admin_id,
    }

    await query.edit_message_text(
        f"✅ *Boss Respawn Berhasil!*\n\n"
        f"🏰 Dungeon: *{dg['name']}*\n"
        f"👹 Boss: *{boss_data.get('name','?')}* {boss_data.get('emoji','')}\n\n"
        f"_Boss kini siap dilawan kembali di dungeon ini._\n"
        f"_Pemain dapat masuk dungeon dan melawan boss seperti biasa._",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👹 Respawn Boss Lain", callback_data="admin_respawn_boss")],
            [InlineKeyboardButton("⬅️ Admin Panel",       callback_data="admin_panel")],
        ])
    )

    # Broadcast notifikasi ke semua pemain yang online (kirim ke saved message admin saja)
    # Di implementasi nyata bisa kirim ke channel grup
    try:
        await context.bot.send_message(
            chat_id=admin_id,
            text=(
                f"📢 *BOSS TELAH DI-RESPAWN!*\n\n"
                f"🏰 Dungeon: *{dg['name']}*\n"
                f"👹 Boss: *{boss_data.get('name','?')}* {boss_data.get('emoji','')}\n\n"
                f"_Pemain bisa masuk dungeon dan melawan boss sekarang!_"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass


# ─── Admin Commands ──────────────────────────────────────────────
async def addcoin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /addcoin <user_id> <amount>")
        return
    try:
        uid    = int(args[0])
        amount = int(args[1])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    player = get_player(uid)
    if not player:
        await update.message.reply_text(f"❌ Pemain ID {uid} tidak ditemukan!")
        return
    player["coin"] = player.get("coin", 0) + amount
    save_player(uid, player)
    await update.message.reply_text(
        f"✅ +{amount} Coin diberikan ke *{player['name']}*\n"
        f"Total Coin: {player['coin']}",
        parse_mode="Markdown"
    )


async def adddiamond_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /adddiamond <user_id> <amount>")
        return
    try:
        uid    = int(args[0])
        amount = int(args[1])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    player = get_player(uid)
    if not player:
        await update.message.reply_text(f"❌ Pemain ID {uid} tidak ditemukan!")
        return
    player["diamond"] = player.get("diamond", 0) + amount
    save_player(uid, player)
    await update.message.reply_text(
        f"✅ +{amount} Diamond diberikan ke *{player['name']}*\n"
        f"Total Diamond: {player['diamond']}",
        parse_mode="Markdown"
    )


async def setvip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /setvip <user_id> <silver|gold|diamond>"
        )
        return
    try:
        uid = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    tier_map = {"silver": "vip_silver", "gold": "vip_gold", "diamond": "vip_diamond"}
    vip_id   = tier_map.get(args[1].lower())
    if not vip_id:
        await update.message.reply_text("❌ Tier VIP tidak valid!")
        return
    player  = get_player(uid)
    vip_pkg = VIP_PACKAGES[vip_id]
    player  = apply_vip(player, vip_id, vip_pkg["effects"], vip_pkg["duration_days"])
    save_player(uid, player)
    await update.message.reply_text(
        f"✅ VIP {vip_pkg['name']} aktif untuk {player['name']}!",
        parse_mode="Markdown"
    )


async def setmedia_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Set image/gif for game entity."""
    user = update.effective_user
    if not is_admin(user.id):
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "Usage: /setmedia <type> <id> <url>\n"
            "Types: monster, boss, dungeon, item"
        )
        return

    entity_type = args[0].lower()
    entity_id   = args[1]
    url         = args[2]

    import json, os
    media_file = "data/media.json"
    os.makedirs("data", exist_ok=True)
    media = {}
    if os.path.exists(media_file):
        with open(media_file) as f:
            media = json.load(f)

    key = f"{entity_type}:{entity_id}"
    media[key] = url
    with open(media_file, "w") as f:
        json.dump(media, f, indent=2)

    await update.message.reply_text(
        f"✅ Media untuk *{entity_type}:{entity_id}* berhasil diset!",
        parse_mode="Markdown"
    )
