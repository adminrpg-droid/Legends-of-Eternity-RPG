import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, get_all_players
from items import get_item, ALL_ITEMS


TRANSFER_LIMIT = 2      # max per week
WEEK_SECONDS   = 604800  # 7 days in seconds


async def transfer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    await _show_transfer_menu(update.message, player, user.id, is_msg=True)


async def transfer_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        return

    if action == "transfer_menu":
        await _show_transfer_menu(query, player, user.id)
        return

    if action == "transfer_send":
        await _show_send_item(query, player)
        return

    if action.startswith("transfer_item_"):
        item_id = action.replace("transfer_item_", "")
        context.user_data["transfer_item"] = item_id
        await _ask_recipient(query, item_id)
        return

    if action.startswith("transfer_to_"):
        # Format: transfer_to_{target_id}_i_{item_id}
        # item_id may contain underscores, so split only on first _i_
        raw = action.replace("transfer_to_", "", 1)
        sep_idx = raw.find("_i_")
        if sep_idx == -1:
            await query.answer("❌ Data tidak valid!", show_alert=True)
            return
        target_id = int(raw[:sep_idx])
        item_id   = raw[sep_idx + 3:]
        await _confirm_transfer(query, player, user.id, target_id, item_id)
        return


async def _show_transfer_menu(target, player: dict, user_id: int, is_msg=False):
    # Check weekly reset
    now   = time.time()
    reset = player.get("transfer_week_reset", now)
    if now - reset > WEEK_SECONDS:
        player["transfer_weekly"]     = 0
        player["transfer_week_reset"] = now
        save_player(user_id, player)

    used    = player.get("transfer_weekly", 0)
    remain  = max(0, TRANSFER_LIMIT - used)
    days_reset = max(0, int((reset + WEEK_SECONDS - now) / 86400))

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   📦  *TRANSFER ITEM*            ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🔁 Sisa Transfer: *{remain}/{TRANSFER_LIMIT}* minggu ini\n"
        f"║  🔄 Reset dalam: {days_reset} hari\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Kamu bisa mentransfer senjata atau armor ke\n"
        f"pemain lain maksimal *{TRANSFER_LIMIT}x per minggu*.\n\n"
        f"⚠️ Item yang ditransfer akan langsung dilepas dari slotmu."
    )
    keyboard = [
        [InlineKeyboardButton("📤 Kirim Item", callback_data="transfer_send")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def _show_send_item(query, player: dict):
    equip = player.get("equipment", {})
    text  = (
        f"╔══════════════════════════════════╗\n"
        f"║  📤  *PILIH ITEM UNTUK DIKIRIM*  ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih item yang ingin dikirim ke pemain lain:"
    )
    buttons = []
    for slot in ("weapon", "armor"):
        item_id = equip.get(slot)
        if item_id:
            item = get_item(item_id)
            if item:
                buttons.append([InlineKeyboardButton(
                    f"📦 {item['name']}",
                    callback_data=f"transfer_item_{item_id}"
                )])

    if not buttons:
        text += "\n\n❌ Tidak ada item yang bisa ditransfer."
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="transfer_menu")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _ask_recipient(query, item_id: str):
    item    = get_item(item_id)
    players = get_all_players()

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  👤  *PILIH PENERIMA*            ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Item: *{item['name'] if item else item_id}*\n\n"
        f"Pilih pemain penerima:\n"
        f"_(Tampil 10 pemain terakhir aktif)_"
    )
    buttons = []
    count = 0
    for uid, p in players.items():
        if int(uid) == query.from_user.id:
            continue
        buttons.append([InlineKeyboardButton(
            f"{p['emoji']} {p['name']} Lv.{p['level']} ({p['class']})",
            callback_data=f"transfer_to_{uid}_i_{item_id}"
        )])
        count += 1
        if count >= 10:
            break

    if not buttons:
        text += "\n\n❌ Tidak ada pemain lain yang ditemukan."

    buttons.append([InlineKeyboardButton("⬅️ Batal", callback_data="transfer_send")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _confirm_transfer(query, player: dict, user_id: int, target_id: int, item_id: str):
    now    = time.time()
    reset  = player.get("transfer_week_reset", now)
    if now - reset > WEEK_SECONDS:
        player["transfer_weekly"]     = 0
        player["transfer_week_reset"] = now

    used = player.get("transfer_weekly", 0)
    if used >= TRANSFER_LIMIT:
        await query.answer(
            f"❌ Batas transfer minggu ini ({TRANSFER_LIMIT}x) sudah tercapai!",
            show_alert=True
        )
        return

    target_player = get_player(target_id)
    if not target_player:
        await query.answer("❌ Pemain tujuan tidak ditemukan!", show_alert=True)
        return

    item  = get_item(item_id)
    if not item:
        await query.answer("❌ Item tidak valid!", show_alert=True)
        return

    equip = player.setdefault("equipment", {})
    slot  = item["type"]
    if equip.get(slot) != item_id:
        await query.answer("❌ Item sudah tidak ada!", show_alert=True)
        return

    # Remove from sender
    for stat, val in item.get("stats", {}).items():
        player[stat] = max(1, player.get(stat, 0) - val)
    equip[slot] = None
    player["transfer_weekly"] = used + 1
    save_player(user_id, player)

    # Give to receiver
    t_equip = target_player.setdefault("equipment", {})
    old     = t_equip.get(slot)
    if old:
        old_item = ALL_ITEMS.get(old, {})
        for stat, val in old_item.get("stats", {}).items():
            target_player[stat] = max(1, target_player.get(stat, 0) - val)
    t_equip[slot] = item_id
    for stat, val in item.get("stats", {}).items():
        target_player[stat] = target_player.get(stat, 0) + val
    save_player(target_id, target_player)

    remain = TRANSFER_LIMIT - player["transfer_weekly"]
    await query.edit_message_text(
        f"✅ *Transfer berhasil!*\n\n"
        f"📦 *{item['name']}* dikirim ke *{target_player['name']}*\n"
        f"🔁 Sisa transfer minggu ini: {remain}/{TRANSFER_LIMIT}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📦 Transfer Lagi", callback_data="transfer_menu")
        ]])
    )
