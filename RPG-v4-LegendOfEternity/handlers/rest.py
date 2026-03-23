# ═══════════════════════════════════════════════════════════════
#  LEGENDS OF ETERNITY — Rest / Sleep Handler
#  FITUR BARU: /rest — Tidur untuk regenerasi HP & MP lebih cepat
# ═══════════════════════════════════════════════════════════════
import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models.database import get_player, save_player

# Konfigurasi regen saat istirahat
REST_TICK_SECONDS = 10       # regen tiap 10 detik
REST_HP_REGEN     = 15       # HP per tick
REST_MP_REGEN     = 12       # MP per tick
REST_MAX_DURATION = 300      # maks 5 menit istirahat
REST_COOLDOWN     = 60       # cooldown setelah berhenti istirahat (detik)


async def rest_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai/cek status istirahat."""
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return

    now = time.time()

    # Cek cooldown setelah istirahat sebelumnya
    rest_cd_until = player.get("rest_cooldown_until", 0)
    if now < rest_cd_until:
        sisa = int(rest_cd_until - now)
        await update.message.reply_text(
            f"⏳ *Kamu masih lelah!*\n"
            f"Cooldown istirahat: `{sisa}` detik lagi.\n\n"
            f"_Tunggu sebentar sebelum istirahat kembali._",
            parse_mode="Markdown"
        )
        return

    # Cek apakah sudah penuh
    hp_full = player["hp"] >= player["max_hp"]
    mp_full = player["mp"] >= player["max_mp"]
    if hp_full and mp_full:
        await update.message.reply_text(
            f"✅ *HP dan MP kamu sudah penuh!*\n"
            f"❤️ HP: {player['hp']}/{player['max_hp']}\n"
            f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
            f"_Tidak perlu istirahat._",
            parse_mode="Markdown"
        )
        return

    # Cek apakah sedang istirahat
    if player.get("is_resting"):
        await _show_rest_status(update.message, player, user.id, is_msg=True)
        return

    # Mulai istirahat
    player["is_resting"]    = True
    player["rest_start"]    = now
    player["rest_msg_id"]   = None
    save_player(user.id, player)

    # Kirim pesan awal
    text, markup = _build_rest_message(player, now)
    msg = await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

    # Simpan message_id untuk update nanti
    player["rest_msg_id"]   = msg.message_id
    player["rest_chat_id"]  = update.effective_chat.id
    save_player(user.id, player)

    # Mulai loop regen di background
    asyncio.create_task(_rest_loop(context, user.id, update.effective_chat.id, msg.message_id))


async def rest_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback dari tombol batal istirahat."""
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)

    if not player:
        return

    if action == "rest_cancel":
        await _cancel_rest(query, player, user.id)
        return

    if action == "rest_start":
        # Dipanggil dari menu
        now = time.time()
        rest_cd_until = player.get("rest_cooldown_until", 0)
        if time.time() < rest_cd_until:
            sisa = int(rest_cd_until - now)
            await query.answer(f"⏳ Cooldown {sisa}s lagi!", show_alert=True)
            return
        if player.get("is_resting"):
            await query.answer("Kamu sudah istirahat!", show_alert=True)
            return
        hp_full = player["hp"] >= player["max_hp"]
        mp_full = player["mp"] >= player["max_mp"]
        if hp_full and mp_full:
            await query.answer("HP & MP sudah penuh!", show_alert=True)
            return

        player["is_resting"]   = True
        player["rest_start"]   = now
        player["rest_msg_id"]  = None
        player["rest_chat_id"] = query.message.chat_id
        save_player(user.id, player)

        text, markup = _build_rest_message(player, now)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)

        player["rest_msg_id"] = query.message.message_id
        save_player(user.id, player)
        asyncio.create_task(_rest_loop(context, user.id, query.message.chat_id, query.message.message_id))


def _build_rest_message(player: dict, now: float) -> tuple:
    rest_start = player.get("rest_start", now)
    elapsed    = int(now - rest_start)
    hp_diff    = player["max_hp"] - player["hp"]
    mp_diff    = player["max_mp"] - player["mp"]

    # Estimasi waktu selesai
    ticks_hp = (hp_diff // REST_HP_REGEN + 1) if hp_diff > 0 else 0
    ticks_mp = (mp_diff // REST_MP_REGEN + 1) if mp_diff > 0 else 0
    ticks_needed = max(ticks_hp, ticks_mp)
    eta = ticks_needed * REST_TICK_SECONDS

    text = (
        f"😴 *ISTIRAHAT*\n\n"
        f"❤️ HP: {player['hp']}/{player['max_hp']} (+{REST_HP_REGEN}/10s)\n"
        f"💙 MP: {player['mp']}/{player['max_mp']} (+{REST_MP_REGEN}/10s)\n\n"
        f"⏱️ Sudah istirahat: `{elapsed}s`\n"
        f"⏳ Estimasi penuh: ~`{eta}s`\n\n"
        f"_Regen berjalan otomatis. Batal untuk lanjut main._"
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Batal Istirahat", callback_data="rest_cancel")],
    ])
    return text, markup


async def _show_rest_status(target, player: dict, user_id: int, is_msg=False):
    now  = time.time()
    text, markup = _build_rest_message(player, now)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def _cancel_rest(query, player: dict, user_id: int):
    """Batalkan istirahat dan set cooldown."""
    now  = time.time()
    player["is_resting"]         = False
    player["rest_start"]         = 0
    player["rest_cooldown_until"] = now + REST_COOLDOWN
    save_player(user_id, player)

    await query.edit_message_text(
        f"▶️ *Istirahat dibatalkan!*\n\n"
        f"❤️ HP: {player['hp']}/{player['max_hp']}\n"
        f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
        f"⏳ Cooldown istirahat: {REST_COOLDOWN}s",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Menu", callback_data="menu")]
        ])
    )


async def _rest_loop(context, user_id: int, chat_id: int, message_id: int):
    """Background task: regen HP/MP setiap REST_TICK_SECONDS detik."""
    start_time = time.time()
    while True:
        await asyncio.sleep(REST_TICK_SECONDS)

        player = get_player(user_id)
        if not player:
            break

        # Cek apakah masih istirahat
        if not player.get("is_resting"):
            break

        # Durasi maks
        elapsed = time.time() - player.get("rest_start", start_time)
        if elapsed >= REST_MAX_DURATION:
            player["is_resting"]          = False
            player["rest_start"]          = 0
            player["rest_cooldown_until"] = time.time() + REST_COOLDOWN
            save_player(user_id, player)
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=(
                        f"⏰ *Istirahat selesai!* (Maks {REST_MAX_DURATION}s)\n\n"
                        f"❤️ HP: {player['hp']}/{player['max_hp']}\n"
                        f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
                        f"_Kamu sudah segar kembali!_"
                    ),
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🏠 Menu", callback_data="menu")]
                    ])
                )
            except Exception:
                pass
            break

        # Regen HP & MP
        already_full = player["hp"] >= player["max_hp"] and player["mp"] >= player["max_mp"]
        if already_full:
            player["is_resting"]          = False
            player["rest_start"]          = 0
            player["rest_cooldown_until"] = time.time() + REST_COOLDOWN
            save_player(user_id, player)
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=(
                        f"✅ *HP & MP sudah penuh!*\n\n"
                        f"❤️ HP: {player['hp']}/{player['max_hp']}\n"
                        f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
                        f"_Siap untuk bertarung lagi!_"
                    ),
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⚔️ Battle", callback_data="battle_start"),
                         InlineKeyboardButton("🏠 Menu", callback_data="menu")]
                    ])
                )
            except Exception:
                pass
            break

        old_hp = player["hp"]
        old_mp = player["mp"]
        player["hp"] = min(player["max_hp"], player["hp"] + REST_HP_REGEN)
        player["mp"] = min(player["max_mp"], player["mp"] + REST_MP_REGEN)
        save_player(user_id, player)

        # Update pesan
        now  = time.time()
        text, markup = _build_rest_message(player, player.get("rest_start", start_time))
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=markup
            )
        except Exception:
            pass
