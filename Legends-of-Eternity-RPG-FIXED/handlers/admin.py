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
        "admin_set_level":     lambda: _setlevel_info(query),
        "admin_book":          lambda: _book_info(query),
        "admin_media_special": lambda: _media_list(query, "special"),
        "admin_media_pet":     lambda: _media_list(query, "pet"),
        "admin_respawn_boss":  lambda: _respawn_menu(query),
        "admin_group_boss_menu": lambda: _group_boss_admin_menu(query),
        "admin_ban_list":      lambda: _ban_list(query),
        "admin_manage_admins": lambda: _manage_admins(query, user.id),
        "admin_reset_player_menu": lambda: _reset_player_menu(query),
        "admin_reset_all_menu":    lambda: _reset_all_menu(query),
        "admin_help_inline":       lambda: _admin_help_inline(query),
    }
    if data in routes:
        await routes[data]()
        return

    if data.startswith("admin_vip_select_"):
        uid = int(data.replace("admin_vip_select_", ""))
        await _select_vip_tier(query, uid)
        return

    if data.startswith("admin_setvip_"):
        parts  = data.replace("admin_setvip_", "").split("_uid_")
        await _do_give_vip(query, int(parts[1]), parts[0])
        return
    if data.startswith("admin_rb_dungeon_"):
        await _do_respawn(query, context, user.id, int(data.replace("admin_rb_dungeon_", "")))
        return
    if data.startswith("admin_reset_confirm_player_"):
        uid = int(data.replace("admin_reset_confirm_player_", ""))
        await _do_reset_player(query, uid)
        return
    if data == "admin_reset_confirm_all":
        if not is_super_admin(user.id):
            await query.answer("❌ Hanya Super Admin!", show_alert=True)
            return
        await _do_reset_all(query)
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
            InlineKeyboardButton("🪙 Beri Gold",       callback_data="admin_add_coin"),
        ],
        [
            InlineKeyboardButton("💎 Beri Diamond",   callback_data="admin_add_diamond"),
            InlineKeyboardButton("🎯 Set Level",       callback_data="admin_set_level"),
        ],
        [
            InlineKeyboardButton("🚫 Daftar Ban",      callback_data="admin_ban_list"),
            InlineKeyboardButton("👑 Kelola Admin",     callback_data="admin_manage_admins"),
        ],
        [InlineKeyboardButton("📖 Edit Media",         callback_data="admin_book")],
        [InlineKeyboardButton("👹 Respawn Boss",        callback_data="admin_respawn_boss")],
        [InlineKeyboardButton("⚔️ Group Boss Raid",     callback_data="admin_group_boss_menu")],
        [
            InlineKeyboardButton("🗑️ Reset Pemain",     callback_data="admin_reset_player_menu"),
            InlineKeyboardButton("💣 Reset Semua",      callback_data="admin_reset_all_menu"),
        ],
        [InlineKeyboardButton("❓ Bantuan Admin",      callback_data="admin_help_inline")],
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


async def _select_vip_tier(query, uid: int):
    """Tampilkan pilihan tier VIP setelah memilih pemain."""
    player = get_player(uid)
    name   = player["name"] if player else f"ID:{uid}"
    buttons = [
        [InlineKeyboardButton("🥈 VIP Silver",  callback_data=f"admin_setvip_vip_silver_uid_{uid}")],
        [InlineKeyboardButton("🥇 VIP Gold",    callback_data=f"admin_setvip_vip_gold_uid_{uid}")],
        [InlineKeyboardButton("💎 VIP Diamond", callback_data=f"admin_setvip_vip_diamond_uid_{uid}")],
        [InlineKeyboardButton("⬅️ Kembali",     callback_data="admin_give_vip")],
    ]
    await query.edit_message_text(
        f"🏅 *Pilih tier VIP untuk* *{name}*:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


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
        "🪙 *Tambah Gold*\n\n`/addcoin <user_id> <jumlah>`\n\nContoh: `/addcoin 123456789 1000`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")]]))


async def _diamond_info(query):
    await query.edit_message_text(
        "💎 *Tambah Diamond*\n\n`/adddiamond <user_id> <jumlah>`\n\nContoh: `/adddiamond 123456789 100`\n\n"
        "💠 *Tambah Evolution Stone*\n\n`/addstone <user_id> <jumlah>`\n\nContoh: `/addstone 123456789 5`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")]]))


async def _admin_help_inline(query):
    text = (
        "╔══════════════════════════════════╗\n"
        "║   👑  *PANDUAN ADMIN LENGKAP*    ║\n"
        "╚══════════════════════════════════╝\n\n"
        "⚙️ *PANEL*\n"
        "`/admin` — Panel GUI  |  `/adminhelp` — Panduan\n\n"
        "👥 *MANAJEMEN PEMAIN*\n"
        "`/addcoin <id> <jml>` — Tambah Gold\n"
        "`/adddiamond <id> <jml>` — Tambah Diamond\n"
        "`/addstone <id> <jml>` — Evolution Stone\n"
        "`/setvip <id> <silver|gold|diamond>` — Beri VIP\n"
        "`/setlevel <id> <level>` — Set level pemain\n\n"
        "🗑️ *RESET*\n"
        "`/resetplayer <id>` — Reset 1 pemain (harus /start ulang)\n"
        "`/resetall KONFIRMASI` — Reset SEMUA pemain\n\n"
        "🚫 *BAN*\n"
        "`/ban <id> [alasan]`  |  `/unban <id>`\n\n"
        "👑 *ADMIN* _(Super Admin Only)_\n"
        "`/addadmin <id>`  |  `/removeadmin <id>`\n\n"
        "🖼️ *MEDIA*\n"
        "`/setmedia <type> <id> <url>`\n"
        "Type: `monster` `boss` `dungeon` `item` `special` `pet`\n\n"
        "🎮 *GAME*\n"
        "`/groupboss` — Spawn boss raid di grup\n\n"
        "📌 *HAK ADMIN:* Gratis shop, tidak kena biaya enhance,\n"
        "tidak tampil leaderboard, tidak bisa di-ban."
    )
    await query.edit_message_text(text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Admin Panel", callback_data="admin_panel")]]))


async def _book_info(query):
    from items import CLASS_SPECIALS, PET_SHOP
    specials_list = "\n".join(f"  • `{k}` — {v.get('name','')}" for k, v in CLASS_SPECIALS.items())
    pets_list     = "\n".join(f"  • `{k}` — {v.get('name','')}" for k, v in list(PET_SHOP.items())[:8])
    text = (
        "📖 *EDITOR MEDIA ADMIN*\n\n"
        "━━━ 🖼️ *Format Command:* ━━━\n"
        "`/setmedia <type> <id> <url_foto_atau_gif>`\n\n"
        "━━━ *Tipe yang Tersedia:* ━━━\n"
        "• `monster` — gambar monster\n"
        "• `boss` — gambar boss dungeon\n"
        "• `dungeon` — gambar dungeon\n"
        "• `item` — gambar item\n"
        "• `special` — foto/GIF class special\n"
        "• `pet` — foto/GIF pet\n\n"
        "━━━ ⚡ *ID Special (kelas):* ━━━\n"
        f"{specials_list}\n\n"
        "━━━ 🐾 *ID Pet:* ━━━\n"
        f"{pets_list}\n\n"
        "📌 *Contoh:*\n"
        "`/setmedia special warrior https://i.imgur.com/abc.gif`\n"
        "`/setmedia pet fire_fox https://i.imgur.com/def.gif`\n"
        "`/setmedia monster goblin https://i.imgur.com/xyz.jpg`"
    )
    keyboard = [
        [InlineKeyboardButton("⚡ Lihat Semua Special", callback_data="admin_media_special")],
        [InlineKeyboardButton("🐾 Lihat Semua Pet",     callback_data="admin_media_pet")],
        [InlineKeyboardButton("⬅️ Kembali",             callback_data="admin_panel")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def _media_list(query, media_type: str):
    """Tampilkan semua media yang sudah diset untuk type tertentu (special/pet)."""
    import json, os
    media_file = "data/media.json"
    media = {}
    if os.path.exists(media_file):
        with open(media_file) as f:
            media = json.load(f)

    prefix  = f"{media_type}:"
    entries = {k: v for k, v in media.items() if k.startswith(prefix)}

    icon_map = {"special": "⚡", "pet": "🐾"}
    icon     = icon_map.get(media_type, "🖼️")

    if not entries:
        text = f"{icon} *Media {media_type.capitalize()}*\n\n_Belum ada media yang diset._\n\nGunakan:\n`/setmedia {media_type} <id> <url>`"
    else:
        lines = [f"{icon} *Media {media_type.capitalize()} ({len(entries)} item):*\n"]
        for k, v in entries.items():
            item_id = k.replace(prefix, "")
            short_url = v[:40] + "..." if len(v) > 40 else v
            lines.append(f"• `{item_id}` → `{short_url}`")
        text = "\n".join(lines)

    keyboard = [
        [InlineKeyboardButton("⬅️ Kembali ke Media", callback_data="admin_book")],
        [InlineKeyboardButton("🔙 Admin Panel",       callback_data="admin_panel")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


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


# ── Reset Player ──────────────────────────────────────────────────
async def _reset_player_menu(query):
    players = get_all_players()
    buttons = []
    for uid, p in list(players.items())[:20]:
        admin_tag = " 👑" if is_admin(int(uid)) else ""
        buttons.append([InlineKeyboardButton(
            f"{p['emoji']} {p['name']} (Lv.{p['level']}){admin_tag}",
            callback_data=f"admin_reset_confirm_player_{uid}"
        )])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")])
    await query.edit_message_text(
        "🗑️ *RESET PEMAIN*\n\nPilih pemain yang ingin di-reset:\n_(Semua data akan dihapus total, harus /start ulang untuk pilih kelas)_\n⚠️ Admin bisa di-reset, tapi status admin tetap.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def _do_reset_player(query, uid: int):
    player = get_player(uid)
    if not player:
        await query.answer("❌ Pemain tidak ditemukan!", show_alert=True)
        return
    from database import _load, _save, DB_PATH
    db = _load(DB_PATH)
    name = player.get("name", f"ID:{uid}")
    if str(uid) in db:
        del db[str(uid)]
        _save(db, DB_PATH)
    await query.answer(f"✅ {name} di-reset total! Harus /start ulang.", show_alert=True)
    await _reset_player_menu(query)


async def _reset_all_menu(query):
    buttons = [
        [InlineKeyboardButton("💣 KONFIRMASI RESET SEMUA", callback_data="admin_reset_confirm_all")],
        [InlineKeyboardButton("⬅️ Batal", callback_data="admin_panel")],
    ]
    await query.edit_message_text(
        "⚠️ *PERINGATAN BERBAHAYA!*\n\nIni akan mereset data *SEMUA* pemain termasuk admin!\n_Semua orang harus /start ulang dan pilih kelas dari awal._\n\nTekan tombol konfirmasi untuk melanjutkan.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def _do_reset_all(query):
    from database import _load, _save, DB_PATH
    db = _load(DB_PATH)
    count = len(db)
    db.clear()
    _save(db, DB_PATH)
    await query.edit_message_text(
        f"✅ *Reset Semua Selesai!*\n🗑️ {count} pemain telah di-reset total.\n_(Semua pemain — termasuk admin — harus /start ulang untuk memilih kelas)_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Admin Panel", callback_data="admin_panel")]])
    )


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


async def _group_boss_admin_menu(query):
    """Admin: Menu untuk spawn Group Boss Raid."""
    from monster import DUNGEONS
    buttons = []
    for did, dg in DUNGEONS.items():
        buttons.append([InlineKeyboardButton(
            f"{dg['emoji']} {dg['name']} (Lv.{dg['min_level']}+) — {dg['floor_count']} Lantai",
            callback_data=f"gb_spawn_{did}"
        )])
    buttons.append([InlineKeyboardButton("◀️ Kembali ke Panel", callback_data="admin_panel")])
    await query.edit_message_text(
        "⚔️ *ADMIN — GROUP BOSS RAID*\n\n"
        "Pilih dungeon untuk spawn Boss Raid di grup ini:\n"
        "_(Semua pemain grup bisa JOIN setelah boss di-spawn)_\n\n"
        "⚠️ Pastikan command ini digunakan di grup, bukan di chat pribadi.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


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
        f"✅ +{amount:,} Gold → *{player['name']}*\nTotal: {player['coin']:,} Gold", parse_mode="Markdown")


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
    VALID_TYPES = ("monster", "boss", "dungeon", "item", "special", "pet")
    if len(args) < 3:
        await update.message.reply_text(
            "Usage: `/setmedia <type> <id> <url>`\n"
            f"Types: {', '.join(VALID_TYPES)}\n\n"
            "Contoh:\n"
            "`/setmedia special warrior https://link.gif`\n"
            "`/setmedia pet fire_fox https://link.jpg`",
            parse_mode="Markdown")
        return

    media_type = args[0].lower()
    if media_type not in VALID_TYPES:
        await update.message.reply_text(
            f"❌ Tipe tidak valid! Gunakan: {', '.join(VALID_TYPES)}", parse_mode="Markdown")
        return

    import json, os
    media_file = "data/media.json"
    os.makedirs("data", exist_ok=True)
    media = {}
    if os.path.exists(media_file):
        with open(media_file) as f:
            media = json.load(f)

    key        = f"{media_type}:{args[1]}"
    media[key] = args[2]
    with open(media_file, "w") as f:
        json.dump(media, f, indent=2)

    # Preview icon berdasarkan tipe
    icons = {"special": "⚡", "pet": "🐾", "monster": "👾", "boss": "💀", "dungeon": "🏰", "item": "📦"}
    icon  = icons.get(media_type, "🖼️")
    await update.message.reply_text(
        f"✅ {icon} Media *{key}* berhasil diset!\n\n"
        f"🔗 URL: `{args[2]}`",
        parse_mode="Markdown"
    )


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
        "║   👑  *PANDUAN ADMIN LENGKAP*    ║\n"
        "╚══════════════════════════════════╝\n\n"
        "⚙️ *PANEL & NAVIGASI*\n"
        "`/admin` — Buka panel admin (GUI)\n"
        "`/adminhelp` — Panduan ini\n\n"
        "👥 *MANAJEMEN PEMAIN*\n"
        "`/addcoin <id> <jml>` — Tambah Gold ke pemain\n"
        "`/addgold <id> <jml>` — Alias addcoin\n"
        "`/adddiamond <id> <jml>` — Tambah Diamond\n"
        "`/addstone <id> <jml>` — Beri Evolution Stone 💠\n"
        "`/setvip <id> <silver|gold|diamond>` — Beri VIP\n"
        "`/setlevel <id> <level>` — Set level pemain\n\n"
        "🗑️ *RESET DATA*\n"
        "`/resetplayer <id>` — Reset 1 pemain ke awal\n"
        "`/resetall KONFIRMASI` — Reset SEMUA pemain\n"
        "_(Reset = hapus data total, pemain harus /start ulang pilih kelas)_\n"
        "_(Admin juga bisa di-reset melalui panel /admin)_\n\n"
        "🚫 *BAN & UNBAN*\n"
        "`/ban <id> [alasan]` — Ban pemain\n"
        "`/unban <id>` — Unban pemain\n\n"
        "👑 *MANAJEMEN ADMIN* _(Super Admin Only)_\n"
        "`/addadmin <id>` — Tambah admin baru\n"
        "`/removeadmin <id>` — Hapus admin\n\n"
        "🎮 *GAME MASTER*\n"
        "`/groupboss` — Spawn boss raid di grup\n\n"
        "🖼️ *MEDIA (Foto/GIF)*\n"
        "`/setmedia monster <nama> <url>`\n"
        "`/setmedia boss <id> <url>`\n"
        "`/setmedia dungeon <id> <url>`\n"
        "`/setmedia item <id> <url>`\n"
        "`/setmedia special <class> <url>` — ⚡ GIF Special\n"
        "`/setmedia pet <id> <url>` — 🐾 GIF Pet\n\n"
        "📋 *FORMAT ID CLASS untuk setmedia special:*\n"
        "`warrior` `mage` `archer` `rogue` `assassin` `reaper`\n\n"
        "📌 *HAK ISTIMEWA ADMIN:*\n"
        "• Gratis semua item di shop\n"
        "• Tidak kena biaya enhance\n"
        "• Tidak tampil di Leaderboard\n"
        "• Tidak bisa di-ban oleh admin lain\n"
        "• Super Admin tidak bisa dihapus\n\n"
        "💡 *TIP:* Gunakan /admin untuk akses GUI panel\n"
        "semua fitur di atas tersedia via tombol inline!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ════════════════════════════════════════════════════════════════
#  RESET COMMANDS (Admin Only)
# ════════════════════════════════════════════════════════════════
async def resetplayer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/resetplayer <user_id> — Reset data satu pemain (hapus total, harus /start ulang)."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: `/resetplayer <user_id>`\n\n"
            "⚠️ Data pemain akan dihapus total.\n"
            "Pemain harus `/start` ulang untuk pilih kelas.",
            parse_mode="Markdown")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah! Gunakan ID angka.")
        return

    player = get_player(uid)
    if not player:
        await update.message.reply_text(f"❌ Pemain ID `{uid}` tidak ditemukan!", parse_mode="Markdown")
        return

    name = player.get("name", f"ID:{uid}")
    from database import _load, _save, DB_PATH
    db = _load(DB_PATH)
    if str(uid) in db:
        del db[str(uid)]
        _save(db, DB_PATH)
    await update.message.reply_text(
        f"✅ *{name}* (`{uid}`) berhasil di-reset total!\n"
        f"Pemain harus /start ulang untuk memilih kelas.",
        parse_mode="Markdown"
    )


async def resetall_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/resetall — Reset data SEMUA pemain termasuk admin (Super Admin only)."""
    user = update.effective_user
    if not is_super_admin(user.id):
        await update.message.reply_text("❌ Hanya Super Admin yang bisa melakukan reset semua!")
        return

    if not context.args or context.args[0] != "KONFIRMASI":
        await update.message.reply_text(
            "⚠️ *PERINGATAN BERBAHAYA!*\n\n"
            "Perintah ini akan *MENGHAPUS TOTAL* data semua pemain!\n"
            "_(Termasuk admin — semua harus /start ulang pilih kelas)_\n\n"
            "Untuk konfirmasi, ketik:\n"
            "`/resetall KONFIRMASI`",
            parse_mode="Markdown"
        )
        return

    from database import _load, _save, DB_PATH
    db = _load(DB_PATH)
    count = len(db)
    db.clear()
    _save(db, DB_PATH)

    await update.message.reply_text(
        f"✅ *Reset Semua Selesai!*\n\n"
        f"🗑️ {count} pemain telah di-reset total.\n"
        f"_(Semua pemain harus /start ulang untuk memilih kelas)_",
        parse_mode="Markdown"
    )


async def setlevel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/setlevel <user_id> <level> — Set level pemain."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: `/setlevel <user_id> <level>`\n\nContoh: `/setlevel 123456789 50`",
            parse_mode="Markdown")
        return
    try:
        uid, level = int(args[0]), int(args[1])
    except ValueError:
        await update.message.reply_text("❌ Format salah! Gunakan angka.")
        return
    if level < 1 or level > 999:
        await update.message.reply_text("❌ Level harus antara 1–999!")
        return
    player = get_player(uid)
    if not player:
        await update.message.reply_text(f"❌ Pemain ID `{uid}` tidak ditemukan!", parse_mode="Markdown")
        return
    old_level = player.get("level", 1)
    player["level"] = level
    # Sesuaikan exp
    player["exp"] = 0
    player["exp_needed"] = level * 100
    save_player(uid, player)
    await update.message.reply_text(
        f"✅ Level *{player['name']}* diubah: Lv.{old_level} → Lv.{level}",
        parse_mode="Markdown")


# ── Admin Set Level via Panel ─────────────────────────────────────
async def _setlevel_info(query):
    await query.edit_message_text(
        "🎯 *Set Level Pemain*\n\n`/setlevel <user_id> <level>`\n\nContoh: `/setlevel 123456789 50`\n\nLevel bisa diset 1–999.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")]]))


async def addgold_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/addgold <user_id> <jumlah> — Alias addcoin dengan nama gold."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: `/addgold <user_id> <jumlah>`", parse_mode="Markdown")
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
        f"✅ +{amount:,} Gold → *{player['name']}*\nTotal: {player['coin']:,} Gold", parse_mode="Markdown")


async def addstone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/addstone <user_id> <jumlah> — Beri Evolution Stone ke pemain."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "💠 *Tambah Evolution Stone*\n\n`/addstone <user_id> <jumlah>`\n\nContoh: `/addstone 123456789 5`",
            parse_mode="Markdown"
        )
        return
    try:
        uid, amount = int(args[0]), int(args[1])
    except ValueError:
        await update.message.reply_text("❌ Format salah! Gunakan angka.")
        return
    if amount <= 0:
        await update.message.reply_text("❌ Jumlah harus lebih dari 0!")
        return
    player = get_player(uid)
    if not player:
        await update.message.reply_text(f"❌ Pemain ID `{uid}` tidak ditemukan!", parse_mode="Markdown")
        return
    inv = player.setdefault("inventory", {})
    inv["evolution_stone"] = inv.get("evolution_stone", 0) + amount
    save_player(uid, player)
    total = inv["evolution_stone"]
    await update.message.reply_text(
        f"✅ *Evolution Stone diberikan!*\n\n"
        f"👤 Pemain: *{player['name']}*\n"
        f"💠 +{amount} Evolution Stone\n"
        f"💠 Total Stone: *{total}*",
        parse_mode="Markdown"
    )


# ════════════════════════════════════════════════════════════════
#  BROADCAST (Admin Only)
# ════════════════════════════════════════════════════════════════
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/broadcast <pesan> — Kirim pesan ke semua pemain (khusus admin)."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Akses ditolak! Hanya admin.")
        return

    # Ambil pesan broadcast
    if not context.args:
        await update.message.reply_text(
            "📢 *BROADCAST*\n\n"
            "Usage: `/broadcast <pesan>`\n\n"
            "Contoh:\n`/broadcast Server akan maintenance jam 22:00!`",
            parse_mode="Markdown"
        )
        return

    message = " ".join(context.args)
    admin_name = user.first_name or "Admin"

    broadcast_text = (
        f"📢 *PENGUMUMAN RESMI*\n"
        f"{'━'*30}\n"
        f"{message}\n"
        f"{'━'*30}\n"
        f"_— {admin_name} (Admin)_"
    )

    players = get_all_players()
    success = 0
    failed  = 0

    await update.message.reply_text(f"📤 Mengirim broadcast ke {len(players)} pemain...")

    for uid_str in players:
        try:
            await context.bot.send_message(
                chat_id=int(uid_str),
                text=broadcast_text,
                parse_mode="Markdown"
            )
            success += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ *Broadcast selesai!*\n\n"
        f"Terkirim: {success} pemain\n"
        f"Gagal   : {failed} pemain",
        parse_mode="Markdown"
    )


# ════════════════════════════════════════════════════════════════
#  SETMEDIA via REPLY FOTO/GIF (Admin Only)
# ════════════════════════════════════════════════════════════════
async def setmedia_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/setmedia <type> <name> — Set media via reply foto/gif."""
    user = update.effective_user
    if not is_admin(user.id):
        return

    msg  = update.message
    args = context.args
    VALID_TYPES = ("monster", "boss", "dungeon", "item", "special", "pet", "class", "weapon", "armor", "skill", "evolution_stone")

    # Cek apakah ini reply ke foto/gif
    reply = msg.reply_to_message
    if not reply:
        await msg.reply_text(
            "📸 *SETMEDIA VIA REPLY*\n\n"
            "Cara pakai:\n"
            "1. Reply ke foto/GIF yang ingin diset\n"
            "2. Ketik: `/setmedia <type> <nama>`\n\n"
            f"Types: `{', '.join(VALID_TYPES)}`\n\n"
            "Contoh:\n"
            "`/setmedia special warrior` (reply ke GIF)\n"
            "`/setmedia pet fire_fox` (reply ke foto)\n"
            "`/setmedia class mage` (reply ke foto)\n"
            "`/setmedia weapon iron_sword` (reply ke foto)",
            parse_mode="Markdown"
        )
        return

    if len(args) < 2:
        await msg.reply_text(
            "❌ Kurang argumen!\n\n"
            "Format: `/setmedia <type> <nama>`\n"
            f"Types: `{', '.join(VALID_TYPES)}`",
            parse_mode="Markdown"
        )
        return

    media_type = args[0].lower()
    media_name = args[1].lower()

    if media_type not in VALID_TYPES:
        await msg.reply_text(f"❌ Tipe tidak valid! Gunakan: `{', '.join(VALID_TYPES)}`", parse_mode="Markdown")
        return

    # Ambil file_id dari foto atau animasi/gif
    file_id = None
    media_kind = None
    if reply.photo:
        file_id   = reply.photo[-1].file_id  # Ambil resolusi tertinggi
        media_kind = "foto"
    elif reply.animation:
        file_id   = reply.animation.file_id
        media_kind = "GIF"
    elif reply.document and reply.document.mime_type == "image/gif":
        file_id   = reply.document.file_id
        media_kind = "GIF"
    elif reply.video:
        file_id   = reply.video.file_id
        media_kind = "video"

    if not file_id:
        await msg.reply_text("❌ Pesan yang di-reply harus berisi foto, GIF, atau animasi!")
        return

    import json, os
    media_file = "data/media.json"
    os.makedirs("data", exist_ok=True)
    media = {}
    if os.path.exists(media_file):
        with open(media_file) as f:
            media = json.load(f)

    key        = f"{media_type}:{media_name}"
    media[key] = file_id
    with open(media_file, "w") as f:
        json.dump(media, f, indent=2)

    icons = {
        "special": "⚡", "pet": "🐾", "monster": "👾", "boss": "💀",
        "dungeon": "🏰", "item": "📦", "class": "⚔️", "weapon": "🗡️",
        "armor": "🛡️", "skill": "🔮", "evolution_stone": "💠"
    }
    icon = icons.get(media_type, "🖼️")
    await msg.reply_text(
        f"✅ {icon} Media *{key}* berhasil diset!\n\n"
        f"Jenis: {media_kind}\n"
        f"File ID: `{file_id[:30]}...`",
        parse_mode="Markdown"
    )


# ════════════════════════════════════════════════════════════════
#  INFO FOTO/GIF — Tampilkan semua foto/gif ke pemain
# ════════════════════════════════════════════════════════════════
async def infofoto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/infofoto — Tampilkan semua foto/gif yang tersedia (bisa dilihat semua pemain)."""
    import json, os
    media_file = "data/media.json"
    if not os.path.exists(media_file):
        await update.message.reply_text("📭 Belum ada foto/GIF yang diset oleh admin.")
        return

    with open(media_file) as f:
        media = json.load(f)

    if not media:
        await update.message.reply_text("📭 Belum ada foto/GIF yang diset oleh admin.")
        return

    # Kelompokkan per tipe
    groups = {}
    for key, file_id in media.items():
        if ":" in key:
            mtype, mname = key.split(":", 1)
        else:
            mtype, mname = "lainnya", key
        groups.setdefault(mtype, []).append((mname, file_id))

    icons = {
        "class": "⚔️ Class", "weapon": "🗡️ Senjata", "armor": "🛡️ Armor",
        "skill": "🔮 Skill", "pet": "🐾 Pet", "special": "⚡ Special",
        "monster": "👾 Monster", "boss": "💀 Boss", "dungeon": "🏰 Dungeon",
        "item": "📦 Item", "evolution_stone": "💠 Evo Stone"
    }

    text = (
        "╔══════════════════════════════════╗\n"
        "║   🖼️  *GALERI FOTO & GIF*        ║\n"
        "╚══════════════════════════════════╝\n\n"
        "Klik tombol di bawah untuk melihat foto/GIF!\n"
    )

    buttons = []
    for mtype, entries in groups.items():
        label = icons.get(mtype, f"🖼️ {mtype.title()}")
        buttons.append([InlineKeyboardButton(f"{label} ({len(entries)})", callback_data=f"infofoto_{mtype}")])
    buttons.append([InlineKeyboardButton("🏠 Menu", callback_data="menu")])

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


async def infofoto_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan foto/GIF per kategori."""
    import json, os
    query = update.callback_query
    await query.answer()

    media_file = "data/media.json"
    media = {}
    if os.path.exists(media_file):
        with open(media_file) as f:
            media = json.load(f)

    mtype = query.data[len("infofoto_"):]
    icons = {
        "class": "⚔️", "weapon": "🗡️", "armor": "🛡️", "skill": "🔮",
        "pet": "🐾", "special": "⚡", "monster": "👾", "boss": "💀",
        "dungeon": "🏰", "item": "📦", "evolution_stone": "💠"
    }
    icon = icons.get(mtype, "🖼️")

    entries = [(k.split(":",1)[1], v) for k, v in media.items() if k.startswith(f"{mtype}:")]
    if not entries:
        await query.answer("Belum ada media untuk kategori ini!", show_alert=True)
        return

    # Kirim satu per satu sebagai album atau individual
    await query.message.reply_text(
        f"{icon} *{mtype.title()}* — {len(entries)} media:",
        parse_mode="Markdown"
    )
    for name, file_id in entries[:10]:  # max 10
        try:
            # Coba kirim sebagai animasi dulu, fallback ke foto
            try:
                await query.message.reply_animation(
                    animation=file_id,
                    caption=f"{icon} `{name}`",
                    parse_mode="Markdown"
                )
            except Exception:
                await query.message.reply_photo(
                    photo=file_id,
                    caption=f"{icon} `{name}`",
                    parse_mode="Markdown"
                )
        except Exception:
            pass
