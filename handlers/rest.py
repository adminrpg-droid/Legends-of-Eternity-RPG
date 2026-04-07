"""
handlers/rest.py — Sistem Istirahat (Regen HP & MP)

Spesifikasi (dari readme & bot.py):
- Regen +15 HP & +12 MP setiap 10 detik
- Berhenti otomatis saat HP & MP penuh
- Tombol Batal untuk berhenti manual
- Maksimum 5 menit (300 detik) per sesi
- Cooldown 30 detik setelah berhenti
"""

import asyncio
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest, TelegramError

from database import get_player, save_player

# ── Konstanta ──────────────────────────────────────────────────
REST_REGEN_HP = 15        # HP regen per tick
REST_REGEN_MP = 12        # MP regen per tick
REST_TICK_SEC = 10        # Interval regen (detik)
REST_MAX_SEC  = 300       # Maks durasi sesi (5 menit)
REST_COOLDOWN = 30        # Cooldown setelah berhenti (detik)


# ════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════

def _build_rest_message(player: dict, now: float) -> tuple:
    """Bangun teks + markup untuk pesan rest aktif."""
    elapsed  = int(now - player.get("rest_start", now))
    sisa_sec = max(0, REST_MAX_SEC - elapsed)
    menit    = sisa_sec // 60
    detik    = sisa_sec % 60

    hp_now = player["hp"]
    mp_now = player["mp"]
    max_hp = player["max_hp"]
    max_mp = player["max_mp"]

    hp_pct = int((hp_now / max_hp) * 10) if max_hp else 0
    mp_pct = int((mp_now / max_mp) * 10) if max_mp else 0
    hp_bar = "🟩" * hp_pct + "⬜" * (10 - hp_pct)
    mp_bar = "🟦" * mp_pct + "⬜" * (10 - mp_pct)

    text = (
        "╔══════════════════════════════════╗\n"
        "║       😴  *ISTIRAHAT*            ║\n"
        "╚══════════════════════════════════╝\n\n"
        f"❤️ HP  : {hp_bar}\n"
        f"       {hp_now}/{max_hp}\n\n"
        f"💙 MP  : {mp_bar}\n"
        f"       {mp_now}/{max_mp}\n\n"
        f"⏱️ Sisa : `{menit}m {detik:02d}s`\n"
        f"🔄 Regen: +{REST_REGEN_HP} HP & +{REST_REGEN_MP} MP tiap {REST_TICK_SEC}s\n\n"
        "_Tekan Batal untuk berhenti istirahat._"
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Batal", callback_data="rest_cancel")]
    ])
    return text, markup


async def _show_rest_status(target, player: dict, user_id: int, is_msg: bool = False):
    """Tampilkan status rest yang sedang berjalan."""
    now = time.time()
    text, markup = _build_rest_message(player, now)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        try:
            await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
        except Exception:
            await target.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)


def _stop_rest(player: dict, user_id: int, reason: str = "manual"):
    """Hentikan sesi rest dan set cooldown."""
    player["is_resting"]          = False
    player["rest_start"]          = 0
    player["rest_msg_id"]         = None
    player["rest_cooldown_until"] = time.time() + REST_COOLDOWN
    save_player(user_id, player)


async def _rest_loop(context: ContextTypes.DEFAULT_TYPE,
                     user_id: int, chat_id: int, msg_id: int):
    """
    Loop async background: regen HP/MP setiap tick,
    update pesan, dan hentikan saat kondisi terpenuhi.
    """
    start = time.time()

    while True:
        await asyncio.sleep(REST_TICK_SEC)
        now    = time.time()
        player = get_player(user_id)

        # Guard: player tidak ada atau sudah berhenti
        if not player or not player.get("is_resting"):
            return

        # Guard: msg_id berbeda → sesi baru sudah dimulai
        if player.get("rest_msg_id") != msg_id:
            return

        # Cek timeout 5 menit
        elapsed = now - player.get("rest_start", start)
        if elapsed >= REST_MAX_SEC:
            _stop_rest(player, user_id, reason="timeout")
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id, message_id=msg_id,
                    text=(
                        "⏰ *Sesi istirahat selesai (5 menit)!*\n\n"
                        f"❤️ HP: {player['hp']}/{player['max_hp']}\n"
                        f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
                        "_Lanjutkan petualanganmu!_"
                    ),
                    parse_mode="Markdown"
                )
            except (BadRequest, TelegramError):
                pass
            return

        # Regen — clamp ke max
        player["hp"] = min(player["max_hp"], player["hp"] + REST_REGEN_HP)
        player["mp"] = min(player["max_mp"], player["mp"] + REST_REGEN_MP)

        # Berhenti otomatis jika HP & MP penuh
        if player["hp"] >= player["max_hp"] and player["mp"] >= player["max_mp"]:
            player["hp"] = player["max_hp"]
            player["mp"] = player["max_mp"]
            _stop_rest(player, user_id, reason="full")
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id, message_id=msg_id,
                    text=(
                        "✅ *HP dan MP sudah penuh!*\n\n"
                        f"❤️ HP: {player['hp']}/{player['max_hp']}\n"
                        f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
                        "_Kamu segar kembali. Siap bertarung!_ 💪"
                    ),
                    parse_mode="Markdown"
                )
            except (BadRequest, TelegramError):
                pass
            return

        # Simpan progress & update pesan
        save_player(user_id, player)
        text, markup = _build_rest_message(player, now)
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id, message_id=msg_id,
                text=text, parse_mode="Markdown", reply_markup=markup
            )
        except (BadRequest, TelegramError):
            # Pesan sudah hilang → hentikan loop
            _stop_rest(player, user_id, reason="msg_gone")
            return


# ════════════════════════════════════════════════════════════════
#  COMMAND HANDLER  /rest
# ════════════════════════════════════════════════════════════════

async def rest_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return

    now = time.time()

    # Cek cooldown
    rest_cd_until = player.get("rest_cooldown_until", 0)
    if now < rest_cd_until:
        sisa = int(rest_cd_until - now)
        await update.message.reply_text(
            f"⏳ *Kamu masih lelah!*\nCooldown: `{sisa}` detik lagi.",
            parse_mode="Markdown"
        )
        return

    # HP & MP sudah penuh
    if player["hp"] >= player["max_hp"] and player["mp"] >= player["max_mp"]:
        await update.message.reply_text(
            f"✅ *HP dan MP kamu sudah penuh!*\n"
            f"❤️ {player['hp']}/{player['max_hp']}  "
            f"💙 {player['mp']}/{player['max_mp']}",
            parse_mode="Markdown"
        )
        return

    # Sudah is_resting — tampilkan status saja
    if player.get("is_resting"):
        await _show_rest_status(update.message, player, user.id, is_msg=True)
        return

    # Mulai sesi rest baru
    player["is_resting"]   = True
    player["rest_start"]   = now
    player["rest_msg_id"]  = None
    player["rest_chat_id"] = update.message.chat_id
    save_player(user.id, player)

    text, markup = _build_rest_message(player, now)
    msg = await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

    player["rest_msg_id"] = msg.message_id
    save_player(user.id, player)

    asyncio.create_task(
        _rest_loop(context, user.id, update.message.chat_id, msg.message_id)
    )


# ════════════════════════════════════════════════════════════════
#  CALLBACK HANDLER  rest_*
# ════════════════════════════════════════════════════════════════

async def rest_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)

    if not player:
        return

    if action == "rest_cancel":
        if not player.get("is_resting"):
            try:
                await query.edit_message_text("ℹ️ Kamu tidak sedang istirahat.")
            except Exception:
                pass
            return

        _stop_rest(player, user.id, reason="manual")
        try:
            await query.edit_message_text(
                f"🛑 *Istirahat dihentikan.*\n\n"
                f"❤️ HP: {player['hp']}/{player['max_hp']}\n"
                f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
                f"⏳ Cooldown `{REST_COOLDOWN}` detik.",
                parse_mode="Markdown"
            )
        except Exception:
            await query.message.reply_text(
                f"🛑 *Istirahat dihentikan.*\n"
                f"❤️ {player['hp']}/{player['max_hp']}  "
                f"💙 {player['mp']}/{player['max_mp']}",
                parse_mode="Markdown"
            )
        return

    await query.answer("Aksi tidak dikenal.", show_alert=True)
