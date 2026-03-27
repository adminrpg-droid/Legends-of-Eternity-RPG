from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player
from items import get_item, RARITY_STARS, ALL_ITEMS, SHOP_SKILLS


async def inventory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    await _show_equipment(update.message, player, is_msg=True)


async def inventory_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        return

    if action == "inv_main":
        await _show_equipment(query, player)
        return

    if action == "inv_equip":
        await _show_equipment(query, player)
        return

    if action == "inv_items":
        await _show_items(query, player)
        return

    if action == "inv_skills":
        await _show_skills_equip(query, player)
        return

    if action.startswith("inv_use_"):
        item_id = action.replace("inv_use_", "")
        await _use_item(query, player, user.id, item_id)
        return

    if action.startswith("inv_unequip_"):
        slot = action.replace("inv_unequip_", "")
        await _unequip_slot(query, player, user.id, slot)
        return

    if action.startswith("inv_equip_skill_"):
        skill_id = action.replace("inv_equip_skill_", "")
        await _equip_skill(query, player, user.id, skill_id)
        return

    if action == "inv_unequip_skill":
        await _unequip_skill(query, player, user.id)
        return

    if action == "inv_heal_full":
        active_battle = context.user_data.get(f"b_{user.id}")
        active_dungeon = context.user_data.get(f"dg_{user.id}")
        if active_battle or active_dungeon:
            await query.answer("❌ Tidak bisa saat dalam pertempuran!", show_alert=True)
            return
        player["hp"] = player["max_hp"]
        player["mp"] = player["max_mp"]
        save_player(user.id, player)
        await query.answer("❤️ HP & MP dipulihkan penuh! (Rest di kota)", show_alert=True)
        await _show_equipment(query, player)
        return


async def _show_equipment(target, player: dict, is_msg=False):
    equip  = player.get("equipment", {})

    wpn_id = equip.get("weapon")
    arm_id = equip.get("armor")
    skl_id = equip.get("skill")
    wpn    = get_item(wpn_id) if wpn_id else None
    arm    = get_item(arm_id) if arm_id else None
    skl    = SHOP_SKILLS.get(skl_id) if skl_id else None

    wpn_txt = f"{wpn['name']}" if wpn else "─ Kosong"
    arm_txt = f"{arm['name']}" if arm else "─ Kosong"
    skl_txt = f"{skl['name']}" if skl else f"─ {player.get('skill','Skill Default')} (Default)"

    inv    = player.get("inventory", {})
    total_items = sum(v for v in inv.values() if isinstance(v, int) and v > 0)

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║     ⚔️  *EQUIPMENT & ITEM*       ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ {player['hp']}/{player['max_hp']}  💙 {player['mp']}/{player['max_mp']}\n"
        f"║  🪙 Gold: {player.get('coin',0):,}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🗡️ Senjata : {wpn_txt}\n"
        f"║  🛡️ Armor   : {arm_txt}\n"
        f"║  🔮 Skill   : {skl_txt}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  📦 ATK:{player['atk']} DEF:{player['def']} SPD:{player.get('spd',0)} CRIT:{player.get('crit',10)}%\n"
        f"║  📦 Item tersimpan: {total_items} buah\n"
        f"╚══════════════════════════════════╝"
    )

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Detail Equipment",  callback_data="inv_equip"),
            InlineKeyboardButton("📦 Item/Potion", callback_data="inv_items"),
        ],
        [InlineKeyboardButton("🔮 Equip Skill", callback_data="inv_skills")],
        [InlineKeyboardButton("🛖 Rest (Pulihkan HP/MP)", callback_data="inv_heal_full")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def _show_equipment_detail(query, player: dict):
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

    # Skill slot
    skl_id = equip.get("skill")
    if skl_id:
        skl = SHOP_SKILLS.get(skl_id)
        if skl:
            text += f"*🔮 Skill:* {skl['name']}\n_{skl['desc']}_\n\n"
            buttons.append([InlineKeyboardButton("♻️ Lepas Skill", callback_data="inv_unequip_skill")])
    else:
        text += f"*🔮 Skill:* ─ Default ({player.get('skill','Skill')})\n\n"

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="inv_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_skills_equip(query, player: dict):
    """Tampilkan daftar skill yang dimiliki untuk di-equip."""
    bought_raw = player.get("bought_skills", [])
    equip_skill = player.get("equipment", {}).get("skill")

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║     🔮  *EQUIP SKILL*            ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih skill untuk digunakan saat battle.\n"
        f"_(Skill yang di-equip menggantikan skill default)_\n\n"
        f"Skill aktif: *{SHOP_SKILLS.get(equip_skill, {}).get('name', 'Default') if equip_skill else 'Default'}*\n\n"
    )

    buttons = []
    if not bought_raw:
        text += "❌ Belum punya skill. Beli di /shop → Skill"
    else:
        for entry in bought_raw:
            if isinstance(entry, str):
                sid = entry
                sk = SHOP_SKILLS.get(sid, {})
            else:
                sid = entry.get("id", "")
                sk = SHOP_SKILLS.get(sid, entry)
            if not sk:
                continue
            equipped = " ✅" if equip_skill == sid else ""
            label = f"🔮 {sk.get('name','?')}{equipped}"
            buttons.append([InlineKeyboardButton(label, callback_data=f"inv_equip_skill_{sid}")])

    if equip_skill:
        buttons.append([InlineKeyboardButton("♻️ Lepas Skill (Gunakan Default)", callback_data="inv_unequip_skill")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="inv_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _equip_skill(query, player: dict, user_id: int, skill_id: str):
    bought_raw = player.get("bought_skills", [])
    owned_ids = []
    for entry in bought_raw:
        if isinstance(entry, str):
            owned_ids.append(entry)
        else:
            owned_ids.append(entry.get("id", ""))

    if skill_id not in owned_ids:
        await query.answer("❌ Kamu tidak memiliki skill ini!", show_alert=True)
        return

    sk = SHOP_SKILLS.get(skill_id, {})
    equip = player.setdefault("equipment", {})
    equip["skill"] = skill_id
    save_player(user_id, player)
    await query.answer(f"✅ {sk.get('name','Skill')} di-equip!", show_alert=True)
    await _show_skills_equip(query, player)


async def _unequip_skill(query, player: dict, user_id: int):
    equip = player.setdefault("equipment", {})
    equip["skill"] = None
    save_player(user_id, player)
    await query.answer("♻️ Skill dilepas! Menggunakan skill default.", show_alert=True)
    await _show_skills_equip(query, player)


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
        text += "📭 Inventory kosong!\n\nBeli item di /shop"

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
    # Item tetap ada di inventory
    save_player(user_id, player)
    await query.answer(f"♻️ {item['name'] if item else 'Item'} dilepas! (tetap di inventory)", show_alert=True)
    await _show_equipment(query, player)
