import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import (
    get_player, save_player, get_all_players,
    is_admin, is_super_admin,
    apply_vip,
    add_admin, remove_admin, get_all_admins,
    ban_player, unban_player, is_banned, _load_bans,
)
from items import VIP_PACKAGES

try:
    from monster import DUNGEONS, BOSSES
except ImportError:
    DUNGEONS, BOSSES = {}, {}


# ════════════════════════════════════════════════════════════════
#  ENTRY POINTS
# ════════════════════════════════════════════════════════════════
async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ *Akses Ditolak!*", parse_mode="Markdown")
        return
    await _panel(update.message, is_msg=True)


async def admin_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    if not is_admin(user.id):
        await query.answer("❌ Bukan admin!", show_alert=True)
        return
    data = query.data

    routes = {
        "admin_panel":         lambda: _panel(query),
        "admin_players":       lambda: _all_players(query),
        "admin_give_vip":      lambda: _give_vip_menu(query),
        "admin_add_coin":      lambda: _coin_info(query),
        "admin_add_diamond":   lambda: _diamond_info(query),
        "admin_book":          lambda: _book_info(query),
        "admin_respawn_boss":  lambda: _respawn_menu(query),
        "admin_ban_list":      lambda: _ban_list(query),
        "admin_manage_admins": lambda: _manage_admins(query, user.id),
    }
    if data in routes:
        await routes[data]()
        return

    if data.startswith("admin_setvip_"):
        parts  = data.replace("admin_setvip_", "").split("_uid_")
        await _do_give_vip(query, int(parts[1]), parts[0])
        return
    if data.startswith("admin_rb_dungeon_"):
        await _do_respawn(query, context, user.id, int(data.replace("admin_rb_dungeon_", "")))
        return
    if data.startswith("admin_unban_"):
        uid = int(data.replace("admin_unban_", ""))
        unban_player(uid)
        await query.answer(f"✅ Pemain {uid} di-unban!", show_alert=True)
        await _ban_list(query)
        return
    if data.startswith("admin_removeadmin_"):
        uid = int(data.replace("admin_removeadmin_", ""))
        if not is_super_admin(user.id):
            await query.answer("❌ Hanya Super Admin!", show_alert=True)
            return
        remove_admin(uid)
        await query.answer(f"✅ Admin {uid} dihapus!", show_alert=True)
        await _manage_admins(query, user.id)
        return


# ════════════════════════════════════════════════════════════════
#  PANEL
# ════════════════════════════════════════════════════════════════
async def _panel(target, is_msg=False):
    players = get_all_players()
    bans    = _load_bans()
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║     👑  *ADMIN PANEL*            ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  👥 Total Pemain : {len(players)}\n"
        f"║  🚫 Total Banned : {len(bans)}\n"
        f"╚══════════════════════════════════╝\n\nPilih aksi:"
    )
    kb = [
        [InlineKeyboardButton("👥 Semua Pemain",      callback_data="admin_players")],
        [
            InlineKeyboardButton("🏅 Beri VIP",       callback_data="admin_give_vip"),
            InlineKeyboardButton("💰 Beri Coin",       callback_data="admin_add_coin"),
        ],
        [InlineKeyboardButton("💎 Beri Diamond",      callback_data="admin_add_diamond")],
        [
            InlineKeyboardButton("🚫 Daftar Ban",      callback_data="admin_ban_list"),
            InlineKeyboardButton("👑 Kelola Admin",     callback_data="admin_manage_admins"),
        ],
        [InlineKeyboardButton("📖 Edit Media",         callback_data="admin_book")],
        [InlineKeyboardButton("👹 Respawn Boss",        callback_data="admin_respawn_boss")],
        [InlineKeyboardButton("🏠 Menu",               callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(kb)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def _all_players(query):
    players = get_all_players()
    text = "╔══ 👥 *SEMUA PEMAIN* ══╗\n\n"
    for uid, p in list(players.items())[:20]:
        vip    = "💎" if p.get("vip", {}).get("active") else ""
        banned = "🚫" if is_banned(int(uid)) else ""
        adm    = "👑" if is_admin(int(uid)) else ""
        text  += f"{p['emoji']} *{p['name']}* {vip}{adm}{banned}\n   ID:`{uid}` Lv.{p['level']} 💰{p.get('coin',0)}\n\n"
    await query.edit_message_text(text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")]]))


async def _give_vip_menu(query):
    players = get_all_players()
    buttons = [[InlineKeyboardButton(f"{p['name']} (ID:{uid})", callback_data=f"admin_vip_select_{uid}")]
               for uid, p in list(players.items())[:10]]
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")])
    await query.edit_message_text("🏅 *Pilih pemain untuk diberi VIP:*", parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _do_give_vip(query, uid: int, vip_id: str):
    player  = get_player(uid)
    vip_pkg = VIP_PACKAGES.get(vip_id)
    if not player or not vip_pkg:
        await query.answer("Data tidak valid!", show_alert=True)
        return
    player = apply_vip(player, vip_id, vip_pkg["effects"], vip_pkg["duration_days"])
    save_player(uid, player)
    await query.edit_message_text(
        f"✅ VIP *{vip_pkg['name']}* diberikan ke *{player['name']}*!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")]]))


async def _coin_info(query):
    await query.edit_message_text(
        "💰 *Tambah Coin*\n\n`/addcoin <user_id> <jumlah>`\n\nContoh: `/addcoin 123456789 1000`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")]]))


async def _diamond_info(query):
    await query.edit_message_text(
        "💎 *Tambah Diamond*\n\n`/adddiamond <user_id> <jumlah>`\n\nContoh: `/adddiamond 123456789 100`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")]]))


async def _book_info(query):
    await query.edit_message_text(
        "📖 *EDITOR MEDIA*\n\n"
        "`/setmedia monster <nama> <url>`\n"
        "`/setmedia boss <id> <url>`\n"
        "`/setmedia dungeon <id> <url>`\n"
        "`/setmedia item <id> <url>`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")]]))


async def _ban_list(query):
    bans = _load_bans()
    text = "🚫 *DAFTAR BANNED*\n\n" + ("_Tidak ada._" if not bans else "")
    buttons = []
    for uid, info in list(bans.items())[:15]:
        p    = get_player(int(uid))
        name = p["name"] if p else f"ID:{uid}"
        text += f"• *{name}* (`{uid}`)\n  📝 {info.get('reason','?')}\n\n"
        buttons.append([InlineKeyboardButton(f"✅ Unban {name}", callback_data=f"admin_unban_{uid}")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


async def _manage_admins(query, viewer_id: int):
    admins  = get_all_admins()
    text    = "👑 *DAFTAR ADMIN*\n\n"
    buttons = []
    for aid in admins:
        p    = get_player(aid)
        name = p["name"] if p else f"ID:{aid}"
        sup  = " ⭐SUPER" if is_super_admin(aid) else ""
        text += f"• *{name}* (`{aid}`){sup}\n"
        if not is_super_admin(aid) and is_super_admin(viewer_id):
            buttons.append([InlineKeyboardButton(f"❌ Hapus {name}", callback_data=f"admin_removeadmin_{aid}")])
    text += "\n\n`/addadmin <id>` — Tambah admin\n`/removeadmin <id>` — Hapus admin"
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


# ── Respawn Boss ─────────────────────────────────────────────────
async def _respawn_menu(query):
    text    = "👹 *RESPAWN BOSS*\n\nPilih dungeon:"
    buttons = [
        [InlineKeyboardButton(f"{dg['emoji']} {dg['name']} → {BOSSES.get(dg['boss'],{}).get('name','Boss')}",
                              callback_data=f"admin_rb_dungeon_{did}")]
        for did, dg in DUNGEONS.items()
    ]
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


async def _do_respawn(query, context, admin_id: int, dungeon_id: int):
    dg = DUNGEONS.get(dungeon_id)
    if not dg:
        await query.answer("Dungeon tidak valid!", show_alert=True)
        return
    boss_data = BOSSES.get(dg["boss"], {})
    context.bot_data[f"boss_respawn_{dungeon_id}"] = {
        "boss_id": dg["boss"], "respawn_at": time.time(), "by_admin": admin_id
    }
    await query.edit_message_text(
        f"✅ *Boss Respawn Berhasil!*\n🏰 {dg['name']}\n👹 {boss_data.get('name','?')} {boss_data.get('emoji','')}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👹 Respawn Lagi", callback_data="admin_respawn_boss")],
            [InlineKeyboardButton("⬅️ Admin Panel",  callback_data="admin_panel")],
        ]))
    try:
        await context.bot.send_message(admin_id,
            f"📢 *Boss di-respawn!*\n🏰 {dg['name']}\n👹 {boss_data.get('name','?')}", parse_mode="Markdown")
    except Exception:
        pass


# ════════════════════════════════════════════════════════════════
#  COMMAND HANDLERS
# ════════════════════════════════════════════════════════════════
async def addcoin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: `/addcoin <user_id> <jumlah>`", parse_mode="Markdown")
        return
    try:
        uid, amount = int(args[0]), int(args[1])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    player = get_player(uid)
    if not player:
        await update.message.reply_text(f"❌ Pemain ID `{uid}` tidak ditemukan!", parse_mode="Markdown")
        return
    player["coin"] = player.get("coin", 0) + amount
    save_player(uid, player)
    await update.message.reply_text(
        f"✅ +{amount:,} Coin → *{player['name']}*\nTotal: {player['coin']:,} Coin", parse_mode="Markdown")


async def adddiamond_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: `/adddiamond <user_id> <jumlah>`", parse_mode="Markdown")
        return
    try:
        uid, amount = int(args[0]), int(args[1])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    player = get_player(uid)
    if not player:
        await update.message.reply_text(f"❌ Pemain ID `{uid}` tidak ditemukan!", parse_mode="Markdown")
        return
    player["diamond"] = player.get("diamond", 0) + amount
    save_player(uid, player)
    await update.message.reply_text(
        f"✅ +{amount:,} Diamond → *{player['name']}*\nTotal: {player['diamond']:,} Diamond", parse_mode="Markdown")


async def setvip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: `/setvip <user_id> <silver|gold|diamond>`", parse_mode="Markdown")
        return
    try:
        uid = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    vip_id = {"silver": "vip_silver", "gold": "vip_gold", "diamond": "vip_diamond"}.get(args[1].lower())
    if not vip_id:
        await update.message.reply_text("❌ Tier tidak valid! Gunakan: silver/gold/diamond")
        return
    player = get_player(uid)
    if not player:
        await update.message.reply_text(f"❌ Pemain `{uid}` tidak ditemukan!", parse_mode="Markdown")
        return
    vip_pkg = VIP_PACKAGES[vip_id]
    player  = apply_vip(player, vip_id, vip_pkg["effects"], vip_pkg["duration_days"])
    save_player(uid, player)
    await update.message.reply_text(
        f"✅ VIP *{vip_pkg['name']}* aktif untuk *{player['name']}*!", parse_mode="Markdown")


async def setmedia_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "Usage: `/setmedia <type> <id> <url>`\nTypes: monster, boss, dungeon, item", parse_mode="Markdown")
        return
    import json, os
    media_file = "data/media.json"
    os.makedirs("data", exist_ok=True)
    media = {}
    if os.path.exists(media_file):
        with open(media_file) as f:
            media = json.load(f)
    key        = f"{args[0].lower()}:{args[1]}"
    media[key] = args[2]
    with open(media_file, "w") as f:
        json.dump(media, f, indent=2)
    await update.message.reply_text(f"✅ Media *{key}* diset!", parse_mode="Markdown")


async def addadmin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tambah admin baru — hanya Super Admin."""
    user = update.effective_user
    if not is_super_admin(user.id):
        await update.message.reply_text("❌ Hanya Super Admin yang bisa menambah admin!")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/addadmin <user_id>`", parse_mode="Markdown")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    ok = add_admin(uid)
    if ok:
        p    = get_player(uid)
        name = p["name"] if p else f"ID:{uid}"
        await update.message.reply_text(
            f"✅ *{name}* (`{uid}`) ditambahkan sebagai Admin!\n"
            f"Mereka kini punya akses penuh ke panel admin.",
            parse_mode="Markdown")
    else:
        await update.message.reply_text(f"⚠️ ID `{uid}` sudah menjadi admin.", parse_mode="Markdown")


async def removeadmin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hapus admin — hanya Super Admin."""
    user = update.effective_user
    if not is_super_admin(user.id):
        await update.message.reply_text("❌ Hanya Super Admin yang bisa menghapus admin!")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/removeadmin <user_id>`", parse_mode="Markdown")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    ok = remove_admin(uid)
    if ok:
        await update.message.reply_text(f"✅ Admin `{uid}` berhasil dihapus.", parse_mode="Markdown")
    else:
        await update.message.reply_text(
            f"⚠️ ID `{uid}` bukan admin atau adalah Super Admin (tidak bisa dihapus).", parse_mode="Markdown")


async def ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ban <user_id> [alasan]"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: `/ban <user_id> [alasan]`\nContoh: `/ban 123456789 Cheating`", parse_mode="Markdown")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Melanggar aturan"
    ok     = ban_player(uid, reason, banned_by=update.effective_user.id)
    if ok:
        p    = get_player(uid)
        name = p["name"] if p else f"ID:{uid}"
        await update.message.reply_text(
            f"🚫 *{name}* (`{uid}`) di-ban!\n📝 Alasan: {reason}", parse_mode="Markdown")
    else:
        await update.message.reply_text(
            f"❌ Tidak bisa mem-ban ID `{uid}`.\n_(Admin tidak bisa di-ban)_", parse_mode="Markdown")


async def unban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/unban <user_id>"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/unban <user_id>`", parse_mode="Markdown")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah!")
        return
    ok = unban_player(uid)
    if ok:
        p    = get_player(uid)
        name = p["name"] if p else f"ID:{uid}"
        await update.message.reply_text(
            f"✅ *{name}* (`{uid}`) di-unban! Mereka bisa bermain kembali.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"⚠️ ID `{uid}` tidak ada dalam daftar ban.", parse_mode="Markdown")


async def adminhelp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/adminhelp — Panduan khusus admin."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    text = (
        "╔══════════════════════════════════╗\n"
        "║   👑  *PANDUAN ADMIN v5*         ║\n"
        "╚══════════════════════════════════╝\n\n"
        "⚙️ *PANEL & INFO*\n"
        "/admin — Buka panel admin\n"
        "/adminhelp — Panduan ini\n\n"
        "👥 *MANAJEMEN PEMAIN*\n"
        "`/addcoin <id> <jml>` — Tambah Coin\n"
        "`/adddiamond <id> <jml>` — Tambah Diamond\n"
        "`/setvip <id> <silver|gold|diamond>` — Beri VIP\n\n"
        "🚫 *BAN & UNBAN*\n"
        "`/ban <id> [alasan]` — Ban pemain\n"
        "`/unban <id>` — Unban pemain\n\n"
        "👑 *MANAJEMEN ADMIN* _(Super Admin Only)_\n"
        "`/addadmin <id>` — Tambah admin baru\n"
        "`/removeadmin <id>` — Hapus admin\n\n"
        "🎮 *GAME*\n"
        "`/groupboss` — Spawn boss raid di grup\n"
        "`/setmedia <type> <id> <url>` — Set media\n\n"
        "📌 *KETENTUAN ADMIN:*\n"
        "• Admin gratis semua item & tidak kena biaya\n"
        "• Admin tidak tampil di Leaderboard\n"
        "• Profil admin tidak bisa dilihat pemain biasa\n"
        "• Admin tidak bisa di-ban\n"
        "• Super Admin tidak bisa dihapus"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
