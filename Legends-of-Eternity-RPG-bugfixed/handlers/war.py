"""
war.py
──────
Fitur War Antar Kerajaan — Legends of Eternity

Sistem:
  • 2 kerajaan: Kerajaan A & Kerajaan B (masing-masing dimiliki oleh grup Telegram)
  • Raja      = Super Admin (pemilik bot)
  • Pangeran  = Admin grup
  • Hanya admin grup yang bisa menyatakan war
  • Semua member grup wajib voting: Setuju / Tolak
  • Notifikasi dikirim ke kedua grup

Commands & Callbacks:
  /war              — Lihat status kerajaan & menu war
  /setkerajaan A/B  — Admin set kerajaan untuk grup ini
  /warstats         — Statistik perang
  war_menu          — Callback tombol War dari menu utama
  war_declare       — Admin nyatakan perang
  war_vote_yes/no   — Vote dari member
  war_status        — Lihat status war aktif
"""

import json
import os
import time
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import is_admin, is_super_admin, get_player, get_all_players, save_player

logger = logging.getLogger(__name__)

WAR_FILE      = "data/war.json"
KINGDOM_FILE  = "data/kingdoms.json"

# ─── Konstanta ───────────────────────────────────────────────────
VOTE_DURATION      = 120   # detik untuk voting (2 menit)
MIN_VOTE_RATIO     = 0.5   # 50% member harus setuju agar war diterima
WAR_DURATION       = 3600  # durasi war aktif (1 jam)

# ─── I/O Helpers ─────────────────────────────────────────────────

def _load_war() -> dict:
    try:
        if os.path.exists(WAR_FILE):
            with open(WAR_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_war(data: dict):
    os.makedirs("data", exist_ok=True)
    tmp = WAR_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, WAR_FILE)


def _load_kingdoms() -> dict:
    try:
        if os.path.exists(KINGDOM_FILE):
            with open(KINGDOM_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_kingdoms(data: dict):
    os.makedirs("data", exist_ok=True)
    tmp = KINGDOM_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, KINGDOM_FILE)


# ─── Kingdom Helpers ─────────────────────────────────────────────

def get_kingdom_by_group(group_id: int) -> str | None:
    """Kembalikan 'A' atau 'B' atau None jika grup belum terdaftar."""
    kingdoms = _load_kingdoms()
    for k, info in kingdoms.items():
        if info.get("group_id") == group_id:
            return k
    return None


def get_kingdom_info(kingdom: str) -> dict | None:
    kingdoms = _load_kingdoms()
    return kingdoms.get(kingdom)


def get_enemy_kingdom(kingdom: str) -> str:
    return "B" if kingdom == "A" else "A"


def get_active_war() -> dict | None:
    war = _load_war()
    active = war.get("active_war")
    if active and active.get("status") in ("voting", "active"):
        return active
    return None


def _kingdom_emoji(k: str) -> str:
    return "🔵" if k == "A" else "🔴"


def _format_war_status(war_data: dict) -> str:
    attacker = war_data.get("attacker", "?")
    defender = war_data.get("defender", "?")
    status   = war_data.get("status", "?")
    a_emoji  = _kingdom_emoji(attacker)
    d_emoji  = _kingdom_emoji(defender)

    if status == "voting":
        votes_yes = len(war_data.get("votes_yes", []))
        votes_no  = len(war_data.get("votes_no", []))
        deadline  = war_data.get("vote_deadline", 0)
        sisa      = max(0, int(deadline - time.time()))
        return (
            f"╔══════════════════════════════════╗\n"
            f"║  ⚔️  *DEKLARASI PERANG!*  ⚔️    ║\n"
            f"╚══════════════════════════════════╝\n\n"
            f"{a_emoji} *Kerajaan {attacker}* menyatakan perang kepada\n"
            f"{d_emoji} *Kerajaan {defender}*!\n\n"
            f"🗳️ *Voting Sedang Berlangsung:*\n"
            f"✅ Setuju: *{votes_yes}* suara\n"
            f"❌ Tolak : *{votes_no}* suara\n\n"
            f"⏳ Waktu tersisa: *{sisa}* detik\n\n"
            f"_Semua member kerajaan wajib vote!_"
        )
    elif status == "active":
        deadline = war_data.get("war_deadline", 0)
        sisa     = max(0, int(deadline - time.time()))
        a_pts    = war_data.get("score", {}).get(attacker, 0)
        d_pts    = war_data.get("score", {}).get(defender, 0)
        return (
            f"╔══════════════════════════════════╗\n"
            f"║  🔥  *PERANG SEDANG BERLANGSUNG!*║\n"
            f"╚══════════════════════════════════╝\n\n"
            f"{a_emoji} *Kerajaan {attacker}* vs {d_emoji} *Kerajaan {defender}*\n\n"
            f"🏆 *Skor Sementara:*\n"
            f"{a_emoji} Kerajaan {attacker}: *{a_pts}* poin\n"
            f"{d_emoji} Kerajaan {defender}: *{d_pts}* poin\n\n"
            f"⏳ Perang berakhir dalam: *{sisa // 60}m {sisa % 60}s*\n\n"
            f"💡 _Mainkan game untuk mengumpulkan poin perang!_"
        )
    else:
        return f"ℹ️ Status war: {status}"


# ─── /setkerajaan ─────────────────────────────────────────────────

async def setkerajaan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /setkerajaan A atau /setkerajaan B — daftarkan grup ini ke kerajaan."""
    msg  = update.message
    user = update.effective_user
    chat = update.effective_chat

    if chat.type not in ("group", "supergroup"):
        await msg.reply_text("❌ Command ini hanya bisa digunakan di dalam *grup*!", parse_mode="Markdown")
        return

    if not is_admin(user.id):
        await msg.reply_text("❌ Hanya *admin* yang bisa mendaftarkan kerajaan.", parse_mode="Markdown")
        return

    args = context.args
    if not args or args[0].upper() not in ("A", "B"):
        await msg.reply_text(
            "❌ Penggunaan: `/setkerajaan A` atau `/setkerajaan B`",
            parse_mode="Markdown"
        )
        return

    kingdom = args[0].upper()
    kingdoms = _load_kingdoms()

    # Cek apakah kerajaan ini sudah dipakai grup lain
    for k, info in kingdoms.items():
        if k == kingdom and info.get("group_id") and info["group_id"] != chat.id:
            await msg.reply_text(
                f"❌ *Kerajaan {kingdom}* sudah terdaftar oleh grup lain!\n"
                f"Hubungi Super Admin untuk mereset.",
                parse_mode="Markdown"
            )
            return

    emoji = _kingdom_emoji(kingdom)
    kingdoms[kingdom] = {
        "group_id":   chat.id,
        "group_name": chat.title or f"Grup {kingdom}",
        "set_by":     user.id,
        "set_at":     time.time(),
    }
    _save_kingdoms(kingdoms)

    await msg.reply_text(
        f"✅ *Kerajaan {kingdom}* berhasil didaftarkan!\n\n"
        f"{emoji} *Kerajaan {kingdom}*\n"
        f"🏰 Grup: *{chat.title}*\n"
        f"👑 Didaftarkan oleh: [{user.first_name}](tg://user?id={user.id})\n\n"
        f"_Gunakan /war untuk melihat status & menu perang._",
        parse_mode="Markdown"
    )


# ─── /war command ─────────────────────────────────────────────────

async def war_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /war — tampilkan status & menu war."""
    msg  = update.message
    user = update.effective_user
    chat = update.effective_chat

    player = get_player(user.id)
    if not player:
        await msg.reply_text("❌ Kamu belum punya karakter! Ketik /start dulu.")
        return

    # BUG FIX #6: tag the player's kingdom affiliation based on which group they
    # called /war from. This is the only way to identify attacker-side players since
    # "kingdom" is never written elsewhere — without this, add_war_point() can never
    # credit attacker kills (the voter-list fallback only covers defenders).
    if chat.type in ("group", "supergroup"):
        player_kingdom = get_kingdom_by_group(chat.id)
        if player_kingdom and player.get("kingdom") != player_kingdom:
            player["kingdom"] = player_kingdom
            save_player(user.id, player)

    kingdoms = _load_kingdoms()
    ka = kingdoms.get("A")
    kb = kingdoms.get("B")

    active = get_active_war()

    text = (
        "╔══════════════════════════════════╗\n"
        "║  ⚔️  *SISTEM WAR KERAJAAN*  ⚔️  ║\n"
        "╚══════════════════════════════════╝\n\n"
        "🔵 *Kerajaan A*: " + (ka.get("group_name", "Belum terdaftar") if ka else "❌ Belum terdaftar") + "\n"
        "🔴 *Kerajaan B*: " + (kb.get("group_name", "Belum terdaftar") if kb else "❌ Belum terdaftar") + "\n\n"
    )

    if active:
        text += _format_war_status(active)
    else:
        text += "🕊️ *Tidak ada perang aktif saat ini.*\n\n_Admin grup dapat menyatakan perang._"

    keyboard = _war_keyboard(user.id, chat.id if chat.type in ("group", "supergroup") else None)
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


def _war_keyboard(user_id: int, group_id: int | None) -> InlineKeyboardMarkup:
    rows = []
    active = get_active_war()

    if active:
        if active["status"] == "voting":
            # Cek apakah user dari grup defender
            defender = active.get("defender")
            ki = get_kingdom_info(defender)
            if ki and group_id and ki.get("group_id") == group_id:
                rows.append([
                    InlineKeyboardButton("✅ Setuju Perang", callback_data="war_vote_yes"),
                    InlineKeyboardButton("❌ Tolak Perang",  callback_data="war_vote_no"),
                ])
        rows.append([InlineKeyboardButton("📊 Status Perang", callback_data="war_status")])
    else:
        if is_admin(user_id) and group_id:
            k = get_kingdom_by_group(group_id)
            if k:
                rows.append([InlineKeyboardButton("⚔️ Nyatakan Perang!", callback_data="war_declare")])

    rows.append([
        InlineKeyboardButton("🏰 Info Kerajaan", callback_data="war_info"),
        InlineKeyboardButton("📜 Riwayat War",   callback_data="war_history"),
    ])
    rows.append([InlineKeyboardButton("🏠 Menu Utama", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


# ─── Callback: war_menu (dari tombol menu utama) ──────────────────


async def _show_war_menu(target, player: dict, user_id: int, is_msg: bool = False, group_id=None):
    """Helper: tampilkan war menu ke target (message). Dipanggil dari bot.py menu_war callback."""
    kingdoms = _load_kingdoms()
    ka = kingdoms.get("A")
    kb = kingdoms.get("B")
    active = get_active_war()

    text = (
        "╔══════════════════════════════════╗\n"
        "║  ⚔️  *SISTEM WAR KERAJAAN*  ⚔️  ║\n"
        "╚══════════════════════════════════╝\n\n"
        "🔵 *Kerajaan A*: " + (ka.get("group_name", "Belum terdaftar") if ka else "❌ Belum terdaftar") + "\n"
        "🔴 *Kerajaan B*: " + (kb.get("group_name", "Belum terdaftar") if kb else "❌ Belum terdaftar") + "\n\n"
    )

    if active:
        text += _format_war_status(active)
    else:
        text += "🕊️ *Tidak ada perang aktif saat ini.*\n\n_Admin grup dapat menyatakan perang di dalam grup._"

    keyboard = _war_keyboard(user_id, group_id)
    await target.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def war_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    chat  = query.message.chat

    player = get_player(user.id)
    if not player:
        await query.message.reply_text("❌ Kamu belum punya karakter! Ketik /start dulu.")
        return

    kingdoms = _load_kingdoms()
    ka = kingdoms.get("A")
    kb = kingdoms.get("B")
    active = get_active_war()

    text = (
        "╔══════════════════════════════════╗\n"
        "║  ⚔️  *SISTEM WAR KERAJAAN*  ⚔️  ║\n"
        "╚══════════════════════════════════╝\n\n"
        "🔵 *Kerajaan A*: " + (ka.get("group_name", "Belum terdaftar") if ka else "❌ Belum terdaftar") + "\n"
        "🔴 *Kerajaan B*: " + (kb.get("group_name", "Belum terdaftar") if kb else "❌ Belum terdaftar") + "\n\n"
    )

    if active:
        text += _format_war_status(active)
    else:
        text += "🕊️ *Tidak ada perang aktif saat ini.*\n\n_Admin grup dapat menyatakan perang di dalam grup._"

    group_id = chat.id if chat.type in ("group", "supergroup") else None
    keyboard = _war_keyboard(user.id, group_id)
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


# ─── Callback: war_info ──────────────────────────────────────────

async def war_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    kingdoms = _load_kingdoms()
    ka = kingdoms.get("A")
    kb = kingdoms.get("B")

    war_data = _load_war()
    history  = war_data.get("history", [])
    a_wins   = sum(1 for w in history if w.get("winner") == "A")
    b_wins   = sum(1 for w in history if w.get("winner") == "B")
    total    = len(history)

    text = (
        "╔══════════════════════════════════╗\n"
        "║  🏰  *INFO KERAJAAN*  🏰        ║\n"
        "╚══════════════════════════════════╝\n\n"
        "🔵 *KERAJAAN A*\n"
    )
    if ka:
        text += (
            f"🏰 Nama Grup: *{ka.get('group_name','?')}*\n"
            f"🆔 Group ID: `{ka.get('group_id','?')}`\n\n"
        )
    else:
        text += "❌ Belum terdaftar\n\n"

    text += "🔴 *KERAJAAN B*\n"
    if kb:
        text += (
            f"🏰 Nama Grup: *{kb.get('group_name','?')}*\n"
            f"🆔 Group ID: `{kb.get('group_id','?')}`\n\n"
        )
    else:
        text += "❌ Belum terdaftar\n\n"

    text += (
        f"📊 *STATISTIK PERANG:*\n"
        f"Total War: *{total}*\n"
        f"🔵 Kerajaan A Menang: *{a_wins}*\n"
        f"🔴 Kerajaan B Menang: *{b_wins}*\n\n"
        f"💡 _Daftarkan grup dengan /setkerajaan A atau B (admin only)_"
    )

    await query.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Kembali", callback_data="war_menu")
        ]])
    )


# ─── Callback: war_history ───────────────────────────────────────

async def war_history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    war_data = _load_war()
    history  = war_data.get("history", [])

    if not history:
        text = "📜 *Riwayat Perang*\n\nBelum ada perang yang tercatat."
    else:
        text = "📜 *RIWAYAT PERANG TERAKHIR*\n\n"
        for i, w in enumerate(reversed(history[-5:]), 1):
            attacker = w.get("attacker", "?")
            defender = w.get("defender", "?")
            winner   = w.get("winner", "?")
            a_score  = w.get("score", {}).get(attacker, 0)
            d_score  = w.get("score", {}).get(defender, 0)
            ended_at = w.get("ended_at", 0)
            tgl      = time.strftime("%d %b %Y", time.localtime(ended_at)) if ended_at else "?"
            w_emoji  = _kingdom_emoji(winner) if winner != "draw" else "🤝"
            text += (
                f"*#{i} — {tgl}*\n"
                f"  {_kingdom_emoji(attacker)}K.{attacker} vs {_kingdom_emoji(defender)}K.{defender}\n"
                f"  Skor: {a_score} — {d_score}\n"
                f"  Pemenang: {w_emoji} Kerajaan {winner}\n\n"
            )

    await query.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Kembali", callback_data="war_menu")
        ]])
    )


# ─── Callback: war_status ────────────────────────────────────────

async def war_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    active = get_active_war()
    if not active:
        await query.message.reply_text(
            "🕊️ *Tidak ada perang aktif saat ini.*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Kembali", callback_data="war_menu")
            ]])
        )
        return

    text = _format_war_status(active)
    await query.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh",  callback_data="war_status"),
            InlineKeyboardButton("⬅️ Kembali",  callback_data="war_menu"),
        ]])
    )


# ─── Callback: war_declare ───────────────────────────────────────

async def war_declare_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin menyatakan perang dari dalam grup."""
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    chat  = query.message.chat

    # Hanya dari grup
    if chat.type not in ("group", "supergroup"):
        await query.answer("❌ Deklarasi perang hanya bisa dari grup kerajaan!", show_alert=True)
        return

    if not is_admin(user.id):
        await query.answer("❌ Hanya admin/pangeran yang bisa menyatakan perang!", show_alert=True)
        return

    attacker_k = get_kingdom_by_group(chat.id)
    if not attacker_k:
        await query.message.reply_text(
            "❌ Grup ini belum terdaftar sebagai kerajaan!\n"
            "Gunakan `/setkerajaan A` atau `/setkerajaan B` (admin only).",
            parse_mode="Markdown"
        )
        return

    defender_k = get_enemy_kingdom(attacker_k)
    defender_info = get_kingdom_info(defender_k)
    if not defender_info:
        await query.message.reply_text(
            f"❌ *Kerajaan {defender_k}* belum terdaftar!\n"
            f"Minta admin kerajaan musuh untuk mendaftarkan grup mereka dulu.",
            parse_mode="Markdown"
        )
        return

    active = get_active_war()
    if active:
        await query.message.reply_text(
            "❌ Sudah ada perang yang sedang berlangsung!\n"
            f"Status: *{active.get('status','?')}*",
            parse_mode="Markdown"
        )
        return

    # Mulai sesi war dengan voting
    now = time.time()
    war_data = _load_war()
    war_data["active_war"] = {
        "attacker":      attacker_k,
        "defender":      defender_k,
        "declared_by":   user.id,
        "declared_at":   now,
        "status":        "voting",
        "vote_deadline": now + VOTE_DURATION,
        "votes_yes":     [],
        "votes_no":      [],
        "score":         {attacker_k: 0, defender_k: 0},
    }
    _save_war(war_data)

    a_emoji = _kingdom_emoji(attacker_k)
    d_emoji = _kingdom_emoji(defender_k)

    # Notifikasi di grup penyerang
    attacker_text = (
        f"╔══════════════════════════════════╗\n"
        f"║  ⚔️  *DEKLARASI PERANG!*  ⚔️    ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"👑 [{user.first_name}](tg://user?id={user.id}) selaku pemimpin\n"
        f"{a_emoji} *Kerajaan {attacker_k}* telah menyatakan PERANG\n"
        f"kepada {d_emoji} *Kerajaan {defender_k}*!\n\n"
        f"⏳ Kerajaan musuh sedang voting untuk *menerima atau menolak*.\n"
        f"Tunggu hasil voting dalam *{VOTE_DURATION // 60} menit*."
    )
    await query.message.reply_text(attacker_text, parse_mode="Markdown")

    # Kirim notifikasi + voting ke grup defender
    defender_group_id = defender_info.get("group_id")
    if defender_group_id:
        defender_text = (
            f"╔══════════════════════════════════╗\n"
            f"║  🚨  *PERNYATAAN PERANG!*  🚨   ║\n"
            f"╚══════════════════════════════════╝\n\n"
            f"{a_emoji} *Kerajaan {attacker_k}* menyatakan PERANG\n"
            f"kepada {d_emoji} *Kerajaan {defender_k}* (Kerajaan Kita)!\n\n"
            f"👑 Dideklarasikan oleh: [{user.first_name}](tg://user?id={user.id})\n\n"
            f"🗳️ *Semua member wajib voting!*\n"
            f"Apakah kita menerima atau menolak tantangan perang ini?\n\n"
            f"⏳ Waktu voting: *{VOTE_DURATION // 60} menit*"
        )
        vote_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Terima Perang!", callback_data="war_vote_yes"),
                InlineKeyboardButton("❌ Tolak Perang",   callback_data="war_vote_no"),
            ],
            [InlineKeyboardButton("📊 Lihat Hasil Vote", callback_data="war_vote_status")],
        ])
        try:
            await context.bot.send_message(
                chat_id=defender_group_id,
                text=defender_text,
                parse_mode="Markdown",
                reply_markup=vote_keyboard
            )
        except Exception as e:
            logger.warning(f"Gagal kirim notif war ke defender group: {e}")

    # Schedule: cek hasil voting setelah VOTE_DURATION
    asyncio.create_task(_check_vote_result(context, VOTE_DURATION))


# ─── Callback: war_vote_yes / war_vote_no ────────────────────────

async def war_vote_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    chat  = query.message.chat
    vote  = "yes" if query.data == "war_vote_yes" else "no"

    active = get_active_war()
    if not active or active["status"] != "voting":
        await query.answer("❌ Tidak ada voting perang aktif saat ini!", show_alert=True)
        return

    # Cek apakah user dari grup defender
    defender = active.get("defender")
    ki = get_kingdom_info(defender)
    if not ki or ki.get("group_id") != chat.id:
        await query.answer("❌ Hanya member Kerajaan yang diserang yang bisa voting!", show_alert=True)
        return

    uid = user.id

    # BUG FIX #6 (complement): tag defender voters with their kingdom so
    # add_war_point() can credit them via player["kingdom"] (not just votes fallback).
    voter_player = get_player(uid)
    if voter_player and voter_player.get("kingdom") != defender:
        voter_player["kingdom"] = defender
        save_player(uid, voter_player)

    war_data = _load_war()
    # BUG FIX: gunakan .get() agar tidak KeyError jika file war kosong / key hilang
    aw = war_data.get("active_war")
    if not aw or aw.get("status") not in ("voting", "active"):
        await query.answer("❌ Tidak ada voting aktif!", show_alert=True)
        return

    # Hapus vote sebelumnya jika ada
    if uid in aw["votes_yes"]:
        aw["votes_yes"].remove(uid)
    if uid in aw["votes_no"]:
        aw["votes_no"].remove(uid)

    # Tambah vote baru
    if vote == "yes":
        aw["votes_yes"].append(uid)
        icon = "✅"
        msg  = "Kamu memilih *Terima Perang*!"
    else:
        aw["votes_no"].append(uid)
        icon = "❌"
        msg  = "Kamu memilih *Tolak Perang*!"

    # BUG FIX: pastikan aw ditulis balik ke war_data sebelum disimpan
    war_data["active_war"] = aw
    _save_war(war_data)

    yes_count = len(aw["votes_yes"])
    no_count  = len(aw["votes_no"])
    sisa      = max(0, int(aw.get("vote_deadline", 0) - time.time()))

    await query.answer(
        f"{icon} Vote kamu tercatat!\n✅ {yes_count} | ❌ {no_count}",
        show_alert=True
    )


async def war_vote_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan hasil vote sementara."""
    query = update.callback_query
    await query.answer()

    active = get_active_war()
    if not active or active["status"] != "voting":
        await query.message.reply_text("❌ Tidak ada voting aktif.", parse_mode="Markdown")
        return

    yes = len(active.get("votes_yes", []))
    no  = len(active.get("votes_no", []))
    sisa = max(0, int(active.get("vote_deadline", 0) - time.time()))
    attacker = active.get("attacker", "?")
    defender = active.get("defender", "?")

    text = (
        f"🗳️ *STATUS VOTING PERANG*\n\n"
        f"{_kingdom_emoji(attacker)} Kerajaan {attacker} vs {_kingdom_emoji(defender)} Kerajaan {defender}\n\n"
        f"✅ Setuju Perang: *{yes}* suara\n"
        f"❌ Tolak Perang : *{no}* suara\n\n"
        f"⏳ Sisa waktu: *{sisa}* detik"
    )

    await query.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Terima Perang!", callback_data="war_vote_yes"),
                InlineKeyboardButton("❌ Tolak Perang",   callback_data="war_vote_no"),
            ],
            [InlineKeyboardButton("🔄 Refresh Status", callback_data="war_vote_status")],
        ])
    )


# ─── Background task: cek hasil voting ───────────────────────────

async def _check_vote_result(context, delay: float):
    """Tunggu voting selesai, lalu proses hasilnya."""
    await asyncio.sleep(delay)
    war_data = _load_war()
    active = war_data.get("active_war")
    if not active or active.get("status") != "voting":
        return

    attacker = active["attacker"]
    defender = active["defender"]
    yes_votes = len(active.get("votes_yes", []))
    no_votes  = len(active.get("votes_no", []))
    total_votes = yes_votes + no_votes

    a_emoji = _kingdom_emoji(attacker)
    d_emoji = _kingdom_emoji(defender)

    attacker_info = get_kingdom_info(attacker)
    defender_info = get_kingdom_info(defender)

    # Jika suara setuju lebih banyak DAN memenuhi quorum MIN_VOTE_RATIO → perang diterima
    quorum_met = (total_votes > 0) and (yes_votes / total_votes >= MIN_VOTE_RATIO)
    if yes_votes > no_votes and quorum_met:
        # War diterima!
        now = time.time()
        active["status"]       = "active"
        active["war_deadline"] = now + WAR_DURATION
        war_data["active_war"] = active
        _save_war(war_data)

        result_text = (
            f"╔══════════════════════════════════╗\n"
            f"║  🔥  *PERANG DIMULAI!*  🔥       ║\n"
            f"╚══════════════════════════════════╝\n\n"
            f"🗳️ Hasil voting: ✅ {yes_votes} vs ❌ {no_votes}\n\n"
            f"{d_emoji} *Kerajaan {defender}* menerima tantangan perang!\n"
            f"{a_emoji} *Kerajaan {attacker}* vs {d_emoji} *Kerajaan {defender}*\n\n"
            f"⏳ Durasi perang: *{WAR_DURATION // 60} menit*\n\n"
            f"💡 Mainkan game untuk mengumpulkan poin perang!\n"
            f"🏆 Kerajaan dengan poin terbanyak menang!"
        )

        # Notif ke kedua grup
        for info in [attacker_info, defender_info]:
            if info and info.get("group_id"):
                try:
                    await context.bot.send_message(
                        chat_id=info["group_id"],
                        text=result_text,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.warning(f"Gagal kirim notif war start: {e}")

        # Schedule: akhiri war setelah WAR_DURATION
        asyncio.create_task(_end_war(context, WAR_DURATION))

    else:
        # Perang ditolak / gagal quorum
        war_data["active_war"] = {"status": "idle"}
        _save_war(war_data)

        # Tentukan alasan penolakan: jika tidak ada quorum → "tidak cukup suara",
        # jika yes <= no → "ditolak mayoritas"
        if total_votes == 0 or (yes_votes / total_votes < MIN_VOTE_RATIO and yes_votes <= no_votes):
            reason = "tidak cukup suara"
        else:
            reason = "ditolak mayoritas"
        result_text = (
            f"╔══════════════════════════════════╗\n"
            f"║  🕊️  *PERANG DITOLAK!*  🕊️      ║\n"
            f"╚══════════════════════════════════╝\n\n"
            f"🗳️ Hasil voting: ✅ {yes_votes} vs ❌ {no_votes}\n\n"
            f"{d_emoji} *Kerajaan {defender}* menolak tantangan perang!\n\n"
            f"_{reason.capitalize()}_\n"
            f"Kerajaan tetap damai... untuk sementara. 🕊️"
        )

        for info in [attacker_info, defender_info]:
            if info and info.get("group_id"):
                try:
                    await context.bot.send_message(
                        chat_id=info["group_id"],
                        text=result_text,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.warning(f"Gagal kirim notif war tolak: {e}")


# ─── Background task: akhiri war ─────────────────────────────────

async def _end_war(context, delay: float):
    """Akhiri perang setelah waktu habis."""
    await asyncio.sleep(delay)
    war_data = _load_war()
    active = war_data.get("active_war")
    if not active or active.get("status") != "active":
        return

    attacker = active["attacker"]
    defender = active["defender"]
    score    = active.get("score", {attacker: 0, defender: 0})
    a_score  = score.get(attacker, 0)
    d_score  = score.get(defender, 0)

    if a_score > d_score:
        winner = attacker
    elif d_score > a_score:
        winner = defender
    else:
        winner = "draw"

    a_emoji = _kingdom_emoji(attacker)
    d_emoji = _kingdom_emoji(defender)
    w_emoji = _kingdom_emoji(winner) if winner != "draw" else "🤝"

    # Simpan ke history
    history = war_data.get("history", [])
    history.append({
        "attacker": attacker,
        "defender": defender,
        "score":    score,
        "winner":   winner,
        "ended_at": time.time(),
    })
    war_data["history"]    = history[-20:]  # simpan 20 terakhir
    war_data["active_war"] = {"status": "idle"}
    _save_war(war_data)

    if winner == "draw":
        result_line = "⚖️ *IMBANG!* Tidak ada pemenang."
    else:
        result_line = f"{w_emoji} *Kerajaan {winner} MENANG!* 🏆"

    result_text = (
        f"╔══════════════════════════════════╗\n"
        f"║  🏁  *PERANG BERAKHIR!*  🏁      ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"{a_emoji} *Kerajaan {attacker}*: {a_score} poin\n"
        f"{d_emoji} *Kerajaan {defender}*: {d_score} poin\n\n"
        f"{result_line}\n\n"
        f"_Terima kasih telah berjuang untuk kerajaan!_\n"
        f"_Gunakan /war untuk melihat statistik perang._"
    )

    attacker_info = get_kingdom_info(attacker)
    defender_info = get_kingdom_info(defender)
    for info in [attacker_info, defender_info]:
        if info and info.get("group_id"):
            try:
                await context.bot.send_message(
                    chat_id=info["group_id"],
                    text=result_text,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.warning(f"Gagal kirim notif war end: {e}")


# ─── War poin: dipanggil saat player kill monster selama war aktif ─

def add_war_point(user_id: int, points: int = 1):
    """
    Tambah poin war untuk kerajaan milik user.
    Dipanggil dari battle/dungeon handler saat war aktif.
    Afiliasi kerajaan dicari lewat field 'kingdom' di data player,
    dengan fallback ke voter list dari sesi voting.
    """
    war_data = _load_war()
    active   = war_data.get("active_war")
    if not active or active.get("status") != "active":
        return

    attacker = active.get("attacker")
    defender = active.get("defender")

    # Cari afiliasi kerajaan dari data player
    player_kingdom = None
    try:
        player = get_player(user_id)
        player_kingdom = player.get("kingdom") if player else None
    except Exception:
        pass

    # Fallback: voter dari sesi voting pasti dari pihak defender
    if not player_kingdom:
        if user_id in active.get("votes_yes", []) or user_id in active.get("votes_no", []):
            player_kingdom = defender

    if not player_kingdom or player_kingdom not in (attacker, defender):
        return

    score = active.setdefault("score", {attacker: 0, defender: 0})
    score[player_kingdom] = score.get(player_kingdom, 0) + points
    war_data["active_war"] = active
    _save_war(war_data)


# ─── /warstats ────────────────────────────────────────────────────

async def warstats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistik perang kerajaan."""
    msg  = update.message
    war_data = _load_war()
    history  = war_data.get("history", [])

    if not history:
        await msg.reply_text(
            "📊 *Statistik Perang*\n\nBelum ada perang yang tercatat.",
            parse_mode="Markdown"
        )
        return

    a_wins   = sum(1 for w in history if w.get("winner") == "A")
    b_wins   = sum(1 for w in history if w.get("winner") == "B")
    draws    = sum(1 for w in history if w.get("winner") == "draw")
    total    = len(history)

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  📊  *STATISTIK PERANG*  📊      ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"🔵 *Kerajaan A* — Menang: *{a_wins}* / {total}\n"
        f"🔴 *Kerajaan B* — Menang: *{b_wins}* / {total}\n"
        f"🤝 Imbang: *{draws}*\n\n"
        f"📜 *5 Perang Terakhir:*\n"
    )

    for w in reversed(history[-5:]):
        attacker = w.get("attacker", "?")
        defender = w.get("defender", "?")
        winner   = w.get("winner", "?")
        a_score  = w.get("score", {}).get(attacker, 0)
        d_score  = w.get("score", {}).get(defender, 0)
        tgl      = time.strftime("%d/%m/%Y", time.localtime(w.get("ended_at", 0)))
        w_emoji  = _kingdom_emoji(winner) if winner != "draw" else "🤝"
        text += (
            f"• {tgl}: K.{attacker}({a_score}) vs K.{defender}({d_score}) "
            f"→ {w_emoji}K.{winner}\n"
        )

    await msg.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⚔️ Menu War", callback_data="war_menu")
        ]])
    )
