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
        "admin_media_special": lambda: _media_list(query, "special"),
        "admin_media_pet":     lambda: _media_list(query, "pet"),
        "admin_respawn_boss":  lambda: _respawn_menu(query),
        "admin_group_boss_menu": lambda: _group_boss_admin_menu(query),
        "admin_ban_list":      lambda: _ban_list(query),
        "admin_manage_admins": lambda: _manage_admins(query, user.id),
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
        [InlineKeyboardButton("💎 Beri Diamond",      callback_data="admin_add_diamond")],
        [
            InlineKeyboardButton("🚫 Daftar Ban",      callback_data="admin_ban_list"),
            InlineKeyboardButton("👑 Kelola Admin",     callback_data="admin_manage_admins"),
        ],
        [InlineKeyboardButton("📖 Edit Media",         callback_data="admin_book")],
        [InlineKeyboardButton("👹 Respawn Boss",        callback_data="admin_respawn_boss")],
        [InlineKeyboardButton("⚔️ Group Boss Raid",     callback_data="admin_group_boss_menu")],
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
        "💎 *Tambah Diamond*\n\n`/adddiamond <user_id> <jumlah>`\n\nContoh: `/adddiamond 123456789 100`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_panel")]]))


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
        "║   👑  *PANDUAN ADMIN v5*         ║\n"
        "╚══════════════════════════════════╝\n\n"
        "⚙️ *PANEL & INFO*\n"
        "/admin — Buka panel admin\n"
        "/adminhelp — Panduan ini\n\n"
        "👥 *MANAJEMEN PEMAIN*\n"
        "`/addcoin <id> <jml>` — Tambah Gold\n"
        "`/adddiamond <id> <jml>` — Tambah Diamond\n"
        "`/setvip <id> <silver|gold|diamond>` — Beri VIP\n\n"
        "🚫 *BAN & UNBAN*\n"
        "`/ban <id> [alasan]` — Ban pemain\n"
        "`/unban <id>` — Unban pemain\n\n"
        "👑 *MANAJEMEN ADMIN* _(Super Admin Only)_\n"
        "`/addadmin <id>` — Tambah admin baru\n"
        "`/removeadmin <id>` — Hapus admin\n\n"
        "🎮 *GAME*\n"
        "`/groupboss` — Spawn boss raid di grup _(Admin Only)_\n\n"
        "🖼️ *MEDIA (Foto/GIF)*\n"
        "`/setmedia monster <nama> <url>` — Gambar monster\n"
        "`/setmedia boss <id> <url>` — Gambar boss\n"
        "`/setmedia dungeon <id> <url>` — Gambar dungeon\n"
        "`/setmedia item <id> <url>` — Gambar item\n"
        "`/setmedia special <class> <url>` — ⚡ Foto/GIF Special\n"
        "`/setmedia pet <id> <url>` — 🐾 Foto/GIF Pet\n\n"
        "📌 *KETENTUAN ADMIN:*\n"
        "• Admin gratis semua item & tidak kena biaya\n"
        "• Admin tidak tampil di Leaderboard\n"
        "• Profil admin tidak bisa dilihat pemain biasa\n"
        "• Admin tidak bisa di-ban\n"
        "• Super Admin tidak bisa dihapus"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ════════════════════════════════════════════════════════════════
#  RESET COMMANDS (Admin Only)
# ════════════════════════════════════════════════════════════════
async def resetplayer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/resetplayer <user_id> — Reset data satu pemain."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Akses ditolak!")
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: `/resetplayer <user_id>`\n\n"
            "⚠️ Ini akan menghapus SEMUA data pemain (level, item, gold, dll)",
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
    char_class = player.get("class", "warrior")
    gender = player.get("gender", "male")
    username = player.get("username", "")

    from database import create_player, CLASS_STATS
    new_player = create_player(uid, name, char_class, gender, username)
    await update.message.reply_text(
        f"✅ *{name}* (`{uid}`) berhasil di-reset!\n"
        f"Semua progress, item, dan gold telah dihapus.\n"
        f"Karakter dimulai dari awal.",
        parse_mode="Markdown"
    )


async def resetall_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/resetall — Reset data SEMUA pemain (Super Admin only)."""
    user = update.effective_user
    if not is_super_admin(user.id):
        await update.message.reply_text("❌ Hanya Super Admin yang bisa melakukan reset semua!")
        return

    # Konfirmasi dengan kata kunci
    if not context.args or context.args[0] != "KONFIRMASI":
        await update.message.reply_text(
            "⚠️ *PERINGATAN BERBAHAYA!*\n\n"
            "Perintah ini akan **MENGHAPUS SEMUA DATA** seluruh pemain!\n\n"
            "Untuk konfirmasi, ketik:\n"
            "`/resetall KONFIRMASI`",
            parse_mode="Markdown"
        )
        return

    players = get_all_players()
    count = 0
    from database import create_player
    for uid_str, p in players.items():
        uid = int(uid_str)
        if is_admin(uid):
            continue  # Skip admin
        name = p.get("name", f"ID:{uid}")
        char_class = p.get("class", "warrior")
        gender = p.get("gender", "male")
        username = p.get("username", "")
        create_player(uid, name, char_class, gender, username)
        count += 1

    await update.message.reply_text(
        f"✅ *Reset Selesai!*\n\n"
        f"🗑️ {count} pemain telah di-reset.\n"
        f"_(Data admin tidak terpengaruh)_",
        parse_mode="Markdown"
    )


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
