"""
market_channel.py
─────────────────
Fitur:
  • /setchannel <channel_id>  — Admin set channel untuk market P2P
  • post_listing_to_channel() — Dipanggil market.py saat ada listing baru
  • Keterangan listing cantik: nama item, harga, rarity, penjual (via ID Telegram)
  • Admin: ID tidak bisa di-klik/dilihat siapa pemiliknya
  • Non-admin: ID Telegram bisa diklik (tg://user?id=...)
"""

import os
import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import is_admin, get_player

_CHANNEL_FILE = "data/market_channel.json"


# ─── Simpan / Load channel ID ────────────────────────────────────

def _load_channel() -> dict:
    try:
        with open(_CHANNEL_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_channel(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(_CHANNEL_FILE, "w") as f:
        json.dump(data, f)


def get_market_channel_id() -> int | None:
    """Return channel_id jika sudah di-set, atau None."""
    data = _load_channel()
    return data.get("channel_id")


# ─── Command /setchannel ────────────────────────────────────────

async def setchannel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /setchannel <channel_id>  — Atur channel market P2P."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Hanya admin yang bisa menggunakan command ini.")
        return

    args = context.args
    if not args:
        ch = get_market_channel_id()
        if ch:
            await update.message.reply_text(
                f"📢 *Channel Market sekarang:* `{ch}`\n\n"
                f"Untuk ubah: `/setchannel <channel_id>`\n"
                f"Contoh: `/setchannel -1001234567890`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "📢 *Channel Market belum diset.*\n\n"
                "Gunakan: `/setchannel <channel_id>`\n"
                "Contoh: `/setchannel -1001234567890`\n\n"
                "💡 Pastikan bot sudah jadi *admin* di channel tersebut.",
                parse_mode="Markdown"
            )
        return

    raw = args[0].strip()
    try:
        channel_id = int(raw)
    except ValueError:
        await update.message.reply_text(
            "❌ Format tidak valid. Gunakan angka, misal: `/setchannel -1001234567890`",
            parse_mode="Markdown"
        )
        return

    _save_channel({"channel_id": channel_id})
    await update.message.reply_text(
        f"✅ *Channel Market berhasil diset!*\n\n"
        f"📢 Channel ID: `{channel_id}`\n\n"
        f"Semua listing baru di market P2P akan otomatis dipost ke channel ini.\n"
        f"Pastikan bot sudah jadi **admin** di channel tersebut.",
        parse_mode="Markdown"
    )


# ─── Post listing ke channel ─────────────────────────────────────

async def post_listing_to_channel(
    bot,
    seller_id: int,
    seller_name: str,
    item_name: str,
    item_rarity: str,
    item_type_tag: str,
    item_desc: str,
    price: int,
    currency: str,
    listing_id: str,
    image_url: str | None = None,
):
    """
    Kirim info listing baru ke channel market.
    - Admin: hanya tampil ID (tidak bisa diklik)
    - Non-admin: tampil mention yang bisa diklik
    """
    channel_id = get_market_channel_id()
    if not channel_id:
        return

    cur_icon = "💎" if currency == "diamond" else "🪙"
    cur_name = "Diamond" if currency == "diamond" else "Gold"

    # Rarity styling
    rarity_icons = {
        "common":   "⬜ Common",
        "uncommon": "🟩 Uncommon",
        "rare":     "🔵 Rare",
        "epic":     "🟣 Epic",
        "ssr":      "🟡 SSR",
        "ur":       "🔱 UR",
        "god":      "🌟 GOD",
        "god sssr": "🔱✨ GOD SSSR",
    }
    rarity_label = rarity_icons.get(item_rarity.lower(), f"⭐ {item_rarity}")

    # Seller display: admin tersembunyi, non-admin bisa diklik
    if is_admin(seller_id):
        seller_display = f"🔒 `[Admin]`"
    else:
        seller_display = f"[{seller_name}](tg://user?id={seller_id})"

    # Timestamp
    ts = time.strftime("%d %b %Y • %H:%M WIB", time.localtime())

    text = (
        f"╔════════════════════════════╗\n"
        f"║  🏪  *LISTING BARU — MARKET P2P*  ║\n"
        f"╚════════════════════════════╝\n\n"
        f"{item_type_tag} *{item_name}*\n"
        f"✨ Rarity: {rarity_label}\n"
        f"📝 _{item_desc}_\n\n"
        f"{'─'*30}\n\n"
        f"💰 *Harga:* {cur_icon} `{price:,} {cur_name}`\n\n"
        f"👤 *Penjual:* {seller_display}\n"
        f"🕐 {ts}\n\n"
        f"{'─'*30}\n"
        f"📌 _Beli di dalam game via_ /market"
    )

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏪 Buka Market In-Game", url="https://t.me/YourBotUsername")],
    ])

    try:
        if image_url:
            await bot.send_photo(
                chat_id=channel_id,
                photo=image_url,
                caption=text,
                parse_mode="Markdown",
                reply_markup=markup
            )
        else:
            await bot.send_message(
                chat_id=channel_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=markup
            )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Gagal post ke channel market: {e}")
