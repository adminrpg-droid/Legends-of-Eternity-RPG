# ═══════════════════════════════════════════════════════════════
#  LEGENDS OF ETERNITY — Inventory Handler
# ═══════════════════════════════════════════════════════════════
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models.database import get_player, save_player
from data.items import get_item, RARITY_STARS, ALL_ITEMS


async def inventory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    await _show_inventory(update.message, player, is_msg=True)


async def inventory_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        return

    if action == "inv_main":
        await _show_inventory(query, player)
        return

    if action == "inv_equip":
        await _show_equipment(query, player)
        return

    if action == "inv_items":
        await _show_items(query, player)
        return

    if action.startswith("inv_use_"):
        item_id = action.replace("inv_use_", "")
        await _use_item(query, player, user.id, item_id)
        return

    if action.startswith("inv_unequip_"):
        slot = action.replace("inv_unequip_", "")
        await _unequip_slot(query, player, user.id, slot)
        return

    if action == "inv_heal_full":
        player["hp"] = player["max_hp"]
        player["mp"] = player["max_mp"]
        save_player(user.id, player)
        await query.answer("❤️ HP & MP dipulihkan penuh! (Rest di kota)", show_alert=True)
        await _show_inventory(query, player)
        return


async def _show_inventory(target, player: dict, is_msg=False):
    equip  = player.get("equipment", {})
    inv    = player.get("inventory", {})

    wpn_id = equip.get("weapon")
    arm_id = equip.get("armor")
    wpn    = get_item(wpn_id) if wpn_id else None
    arm    = get_item(arm_id) if arm_id else None

    wpn_txt = f"{wpn['name']}" if wpn else "─ Kosong"
    arm_txt = f"{arm['name']}" if arm else "─ Kosong"

    total_items = sum(v for v in inv.values() if isinstance(v, int) and v > 0)

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║       🎒  *INVENTORY*            ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ {player['hp']}/{player['max_hp']}  💙 {player['mp']}/{player['max_mp']}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🗡️ Senjata : {wpn_txt}\n"
        f"║  🛡️ Armor   : {arm_txt}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  📦 Item tersimpan: {total_items} buah\n"
        f"╚══════════════════════════════════╝"
    )

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Equipment",  callback_data="inv_equip"),
            InlineKeyboardButton("📦 Item/Potion", callback_data="inv_items"),
        ],
        [InlineKeyboardButton("🛖 Rest (Pulihkan HP/MP)", callback_data="inv_heal_full")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def _show_equipment(query, player: dict):
    equip = player.get("equipment", {})
    text  = (
        f"╔══════════════════════════════════╗\n"
        f"║    ⚔️  *EQUIPMENT TERPASANG*     ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ⚔️ ATK: {player['atk']}  🛡️ DEF: {player['def']}\n"
        f"║  💨 SPD: {player['spd']}  🎯 CRIT: {player.get('crit',10)}%\n"
        f"╚══════════════════════════════════╝\n\n"
    )

    buttons = []
    for slot, label in (("weapon", "🗡️ Senjata"), ("armor", "🛡️ Armor")):
        item_id = equip.get(slot)
        if item_id:
            item  = get_item(item_id)
            stars = RARITY_STARS.get(item.get("rarity","common"),"⭐") if item else ""
            name  = item["name"] if item else item_id
            stats = ", ".join(f"+{v} {k.upper()}" for k,v in item.get("stats",{}).items()) if item else ""
            text += f"*{label}:* {name} {stars}\n_{stats}_\n\n"
            buttons.append([InlineKeyboardButton(
                f"♻️ Lepas {label}", callback_data=f"inv_unequip_{slot}"
            )])
        else:
            text += f"*{label}:* ─ Kosong\n\n"

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="inv_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_items(query, player: dict):
    inv = player.get("inventory", {})
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║    📦  *ITEM & POTION*           ║\n"
        f"╚══════════════════════════════════╝\n\n"
    )
    buttons = []
    has_items = False
    for item_id, qty in inv.items():
        if not isinstance(qty, int) or qty <= 0:
            continue
        item = get_item(item_id)
        if not item:
            continue
        has_items = True
        text += f"• *{item['name']}* x{qty}\n  _{item.get('desc','')}_\n\n"
        if item.get("type") == "consumable":
            buttons.append([InlineKeyboardButton(
                f"🧪 Pakai {item['name']} (x{qty})",
                callback_data=f"inv_use_{item_id}"
            )])

    if not has_items:
        text += "📭 Inventory kosong!"

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="inv_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _use_item(query, player: dict, user_id: int, item_id: str):
    inv  = player.get("inventory", {})
    qty  = inv.get(item_id, 0)
    if qty <= 0:
        await query.answer("❌ Item habis!", show_alert=True)
        return

    item = get_item(item_id)
    if not item or item.get("type") != "consumable":
        await query.answer("❌ Item tidak bisa dipakai!", show_alert=True)
        return

    effect = item.get("effect", {})
    msgs   = []

    hp_eff = effect.get("hp", 0)
    mp_eff = effect.get("mp", 0)

    if hp_eff:
        if hp_eff >= 9999:
            restored = player["max_hp"] - player["hp"]
            player["hp"] = player["max_hp"]
        else:
            restored = min(hp_eff, player["max_hp"] - player["hp"])
            player["hp"] = min(player["max_hp"], player["hp"] + hp_eff)
        msgs.append(f"❤️ +{restored} HP")

    if mp_eff:
        restored_mp = min(mp_eff, player["max_mp"] - player["mp"])
        player["mp"] = min(player["max_mp"], player["mp"] + mp_eff)
        msgs.append(f"💙 +{restored_mp} MP")

    inv[item_id] -= 1
    save_player(user_id, player)

    result = " | ".join(msgs) if msgs else "Digunakan!"
    await query.answer(f"✅ {item['name']} → {result}", show_alert=True)
    await _show_items(query, player)


async def _unequip_slot(query, player: dict, user_id: int, slot: str):
    equip   = player.setdefault("equipment", {})
    item_id = equip.get(slot)
    if not item_id:
        await query.answer("Slot sudah kosong!", show_alert=True)
        return

    item = get_item(item_id)
    if item:
        for stat, val in item.get("stats", {}).items():
            player[stat] = max(1, player.get(stat, 0) - val)

    equip[slot] = None
    save_player(user_id, player)
    await query.answer(f"♻️ {item['name'] if item else 'Item'} dilepas!", show_alert=True)
    await _show_equipment(query, player)
