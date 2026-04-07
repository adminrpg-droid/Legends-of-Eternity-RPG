from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player
from items import get_item, RARITY_STARS, ALL_ITEMS, SHOP_SKILLS, PREMIUM_SKILLS, GOD_SSSR_SKILLS


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

    if action == "inv_choose_pet":
        await _show_choose_pet(query, player)
        return
    if action.startswith("inv_equip_pet_"):
        pet_id = action.replace("inv_equip_pet_", "")
        await _equip_pet_from_inv(query, player, user.id, pet_id)
        return
    if action == "inv_choose_weapon":
        await _show_choose_weapon(query, player)
        return
    if action == "inv_choose_armor":
        await _show_choose_armor(query, player)
        return
    if action.startswith("inv_equip_weapon_"):
        item_id = action.replace("inv_equip_weapon_", "")
        await _equip_item_from_inv(query, player, user.id, item_id, "weapon")
        return
    if action.startswith("inv_equip_armor_"):
        item_id = action.replace("inv_equip_armor_", "")
        await _equip_item_from_inv(query, player, user.id, item_id, "armor")
        return
    if action.startswith("inv_use_"):
        item_id = action.replace("inv_use_", "")
        await _use_item(query, player, user.id, item_id)
        return

    # BUG FIX: cek inv_unequip_skill SEBELUM startswith("inv_unequip_")
    # agar tidak tertangkap salah oleh handler _unequip_slot dengan slot="skill"
    if action == "inv_unequip_skill":
        await _unequip_skill(query, player, user.id)
        return

    if action.startswith("inv_unequip_"):
        slot = action.replace("inv_unequip_", "")
        await _unequip_slot(query, player, user.id, slot)
        return

    if action.startswith("inv_equip_skill_"):
        skill_id = action.replace("inv_equip_skill_", "")
        await _equip_skill(query, player, user.id, skill_id)
        return

    if action == "inv_heal_full":
        active_battle = context.bot_data.get(f"b_{user.id}")
        active_dungeon = context.bot_data.get(f"dg_{user.id}")
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
    _ALL_SKILLS = {**SHOP_SKILLS, **PREMIUM_SKILLS, **GOD_SSSR_SKILLS}
    skl    = _ALL_SKILLS.get(skl_id) if skl_id else None

    wpn_txt = f"{wpn['name']}" if wpn else "─ Kosong"
    arm_txt = f"{arm['name']}" if arm else "─ Kosong"
    skl_txt = f"{skl['name']}" if skl else f"─ {player.get('skill','Skill Default')} (Default)"

    # Pet info
    from items import PET_SHOP
    active_pet_id = player.get("pet")
    owned_pets = player.get("owned_pets", [])
    if active_pet_id and active_pet_id not in owned_pets:
        owned_pets = list(owned_pets) + [active_pet_id]
    pet_count = len(owned_pets)
    pet_txt = "─ Tidak ada"
    if active_pet_id and active_pet_id in PET_SHOP:
        pet_txt = PET_SHOP[active_pet_id]["name"]
    elif active_pet_id:
        pet_txt = active_pet_id.replace("_", " ").title()

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
        f"║  🐾 Pet     : {pet_txt} ({pet_count} dimiliki)\n"
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
        [
            InlineKeyboardButton("🗡️ Ganti Senjata", callback_data="inv_choose_weapon"),
            InlineKeyboardButton("🛡️ Ganti Armor",   callback_data="inv_choose_armor"),
        ],
        [InlineKeyboardButton("🔮 Equip Skill", callback_data="inv_skills")],
        [InlineKeyboardButton(f"🐾 Ganti Pet ({pet_count} dimiliki)", callback_data="inv_choose_pet")],
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
        _all_sk = {**SHOP_SKILLS, **PREMIUM_SKILLS, **GOD_SSSR_SKILLS}
        skl = _all_sk.get(skl_id)
        if skl:
            text += f"*🔮 Skill:* {skl['name']}\n_{skl.get('desc','')}_\n\n"
            buttons.append([InlineKeyboardButton("♻️ Lepas Skill", callback_data="inv_unequip_skill")])
        else:
            text += f"*🔮 Skill:* {skl_id} (equipped)\n\n"
            buttons.append([InlineKeyboardButton("♻️ Lepas Skill", callback_data="inv_unequip_skill")])
    else:
        text += f"*🔮 Skill:* ─ Default ({player.get('skill','Skill')})\n\n"

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="inv_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_skills_equip(query, player: dict):
    """Tampilkan daftar skill yang dimiliki untuk di-equip."""
    from items import SHOP_SKILLS, PREMIUM_SKILLS, GOD_SSSR_SKILLS
    ALL_SKILLS_POOL = {**SHOP_SKILLS, **PREMIUM_SKILLS, **GOD_SSSR_SKILLS}

    bought_raw = player.get("bought_skills", [])
    equip_skill = player.get("equipment", {}).get("skill")

    active_name = "Default"
    if equip_skill:
        sk_data = ALL_SKILLS_POOL.get(equip_skill, {})
        active_name = sk_data.get("name", equip_skill)

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║     🔮  *EQUIP SKILL*            ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih skill untuk digunakan saat battle.\n"
        f"_(Skill yang di-equip menggantikan skill default)_\n\n"
        f"Skill aktif: *{active_name}*\n\n"
    )

    buttons = []
    if not bought_raw:
        text += "❌ Belum punya skill. Beli di /shop → Skill"
    else:
        for entry in bought_raw:
            if isinstance(entry, str):
                sid = entry
                sk = ALL_SKILLS_POOL.get(sid, {})
            else:
                sid = entry.get("id", "")
                sk = ALL_SKILLS_POOL.get(sid) or entry
            if not sid:
                continue
            name = sk.get("name", sid)
            rarity = sk.get("rarity","")
            stars = RARITY_STARS.get(rarity,"") if rarity else ""
            desc = sk.get("desc", "")
            equipped = " ✅ *[AKTIF]*" if equip_skill == sid else ""
            img_info = " 🖼️" if sk.get("image") else ""
            text += f"• *{name}* {stars}{img_info}{equipped}\n  _{desc}_\n\n"
            label = f"🔮 {name}{' ✅' if equip_skill == sid else ''}"
            buttons.append([InlineKeyboardButton(label, callback_data=f"inv_equip_skill_{sid}")])

    if equip_skill:
        buttons.append([InlineKeyboardButton("♻️ Lepas Skill (Gunakan Default)", callback_data="inv_unequip_skill")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="inv_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _equip_skill(query, player: dict, user_id: int, skill_id: str):
    from items import SHOP_SKILLS, PREMIUM_SKILLS, GOD_SSSR_SKILLS
    ALL_SKILLS_POOL = {**SHOP_SKILLS, **PREMIUM_SKILLS, **GOD_SSSR_SKILLS}

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

    sk = ALL_SKILLS_POOL.get(skill_id, {})
    equip = player.setdefault("equipment", {})
    equip["skill"] = skill_id
    save_player(user_id, player)
    await query.answer(f"✅ {sk.get('name', skill_id)} di-equip!", show_alert=True)
    await _show_skills_equip(query, player)


async def _unequip_skill(query, player: dict, user_id: int):
    equip = player.setdefault("equipment", {})
    equip["skill"] = None
    save_player(user_id, player)
    await query.answer("♻️ Skill dilepas! Menggunakan skill default.", show_alert=True)
    await _show_skills_equip(query, player)


async def _show_items(query, player: dict):
    inv = player.get("inventory", {})
    hp     = player.get("hp", 0)
    max_hp = player.get("max_hp", 1)
    mp     = player.get("mp", 0)
    max_mp = player.get("max_mp", 1)
    hp_bar = int((hp / max_hp) * 10) if max_hp > 0 else 0
    mp_bar = int((mp / max_mp) * 10) if max_mp > 0 else 0
    hp_fill = "█" * hp_bar + "░" * (10 - hp_bar)
    mp_fill = "█" * mp_bar + "░" * (10 - mp_bar)
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║    📦  *ITEM & POTION*           ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ HP: {hp}/{max_hp}\n"
        f"║  [{hp_fill}]\n"
        f"║  💙 MP: {mp}/{max_mp}\n"
        f"║  [{mp_fill}]\n"
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
    hp_now = player.get("hp", 0)
    max_hp = player.get("max_hp", 1)
    mp_now = player.get("mp", 0)
    max_mp = player.get("max_mp", 1)
    status_msg = (
        f"✅ {item['name']} → {result}\n"
        f"❤️ HP: {hp_now}/{max_hp}  💙 MP: {mp_now}/{max_mp}"
    )
    await query.answer(status_msg, show_alert=True)
    await _show_items(query, player)


async def _show_choose_weapon(query, player: dict):
    """Tampilkan senjata di inventory untuk dipilih dipakai + foto/gif jika tersedia."""
    from items import get_item, ALL_ITEMS
    inv = player.get("inventory", {})
    equip = player.get("equipment", {})
    current_wpn = equip.get("weapon")
    buttons = []
    item_list = []
    for item_id, qty in inv.items():
        if not isinstance(qty, int) or qty <= 0:
            continue
        item = ALL_ITEMS.get(item_id)
        if not item or item.get("type") != "weapon":
            continue
        equipped_tag = " ✅" if current_wpn == item_id else ""
        stars = RARITY_STARS.get(item.get("rarity","common"),"⭐")
        stats = " | ".join(f"+{v} {k.upper()}" for k,v in item.get("stats",{}).items())
        label = f"🗡️ {item['name']}{equipped_tag}"
        item_list.append((item_id, item, stars, stats))
        buttons.append([InlineKeyboardButton(label, callback_data=f"inv_equip_weapon_{item_id}")])
    if not buttons:
        buttons.append([InlineKeyboardButton("📭 Tidak ada senjata di inventory", callback_data="noop")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="inv_main")])

    # Bangun teks dengan daftar detail item
    text = "🗡️ *PILIH SENJATA*\n\nPilih senjata dari inventory:\n\n"
    for item_id, item, stars, stats in item_list:
        equipped_mark = " ✅ *[TERPASANG]*" if current_wpn == item_id else ""
        img_info = "🖼️ Foto tersedia" if item.get("image") else ""
        text += f"• *{item['name']}* {stars}{equipped_mark}\n  _{stats}_\n  {img_info}\n\n"

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    # Kirim foto senjata yang sedang terpasang (jika ada)
    if current_wpn:
        cur_item = ALL_ITEMS.get(current_wpn, {})
        img = cur_item.get("image")
        if img:
            try:
                await query.message.reply_photo(photo=img, caption=f"🗡️ *{cur_item['name']}* — Senjata terpasang", parse_mode="Markdown")
            except Exception:
                pass


async def _show_choose_armor(query, player: dict):
    """Tampilkan armor di inventory untuk dipilih dipakai + foto/gif jika tersedia."""
    from items import get_item, ALL_ITEMS
    inv = player.get("inventory", {})
    equip = player.get("equipment", {})
    current_arm = equip.get("armor")
    buttons = []
    item_list = []
    for item_id, qty in inv.items():
        if not isinstance(qty, int) or qty <= 0:
            continue
        item = ALL_ITEMS.get(item_id)
        if not item or item.get("type") != "armor":
            continue
        equipped_tag = " ✅" if current_arm == item_id else ""
        stars = RARITY_STARS.get(item.get("rarity","common"),"⭐")
        stats = " | ".join(f"+{v} {k.upper()}" for k,v in item.get("stats",{}).items())
        item_list.append((item_id, item, stars, stats))
        label = f"🛡️ {item['name']}{equipped_tag}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"inv_equip_armor_{item_id}")])
    if not buttons:
        buttons.append([InlineKeyboardButton("📭 Tidak ada armor di inventory", callback_data="noop")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="inv_main")])

    text = "🛡️ *PILIH ARMOR*\n\nPilih armor dari inventory:\n\n"
    for item_id, item, stars, stats in item_list:
        equipped_mark = " ✅ *[TERPASANG]*" if current_arm == item_id else ""
        img_info = "🖼️ Foto tersedia" if item.get("image") else ""
        text += f"• *{item['name']}* {stars}{equipped_mark}\n  _{stats}_\n  {img_info}\n\n"

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    # Kirim foto armor yang sedang terpasang (jika ada)
    if current_arm:
        cur_item = ALL_ITEMS.get(current_arm, {})
        img = cur_item.get("image")
        if img:
            try:
                await query.message.reply_photo(photo=img, caption=f"🛡️ *{cur_item['name']}* — Armor terpasang", parse_mode="Markdown")
            except Exception:
                pass


async def _equip_item_from_inv(query, player: dict, user_id: int, item_id: str, slot: str):
    """Equip weapon/armor dari inventory tanpa beli."""
    from items import get_item, ALL_ITEMS
    from database import save_player
    item = ALL_ITEMS.get(item_id)
    if not item:
        await query.answer("Item tidak ditemukan!", show_alert=True)
        return
    # BUG FIX #4: cek item benar-benar ada di inventory sebelum equip
    inv = player.setdefault("inventory", {})
    currently_equipped = player.get("equipment", {}).get(slot)
    if item_id != currently_equipped and inv.get(item_id, 0) <= 0:
        await query.answer("❌ Item tidak ada di inventory!", show_alert=True)
        return
    equip = player.setdefault("equipment", {})
    old_id = equip.get(slot)
    if old_id == item_id:
        await query.answer(f"✅ {item['name']} sudah terpasang!", show_alert=True)
        return
    # Lepas item lama, kembalikan stat
    if old_id:
        old_item = ALL_ITEMS.get(old_id, {})
        for stat, val in old_item.get("stats", {}).items():
            player[stat] = max(1, player.get(stat, 0) - val)
        # BUG FIX #6: clamp hp/mp agar tidak melebihi max_hp/max_mp baru setelah stat lama dikurangi
        player["hp"] = min(player.get("hp", 1), player.get("max_hp", 1))
        player["mp"] = min(player.get("mp", 0), player.get("max_mp", 0))
    # Pasang item baru
    equip[slot] = item_id
    for stat, val in item.get("stats", {}).items():
        player[stat] = player.get(stat, 0) + val
        if stat == "max_hp":
            player["hp"] = min(player.get("hp", 1) + val, player["max_hp"])
        if stat == "max_mp":
            player["mp"] = min(player.get("mp", 0) + val, player["max_mp"])
    save_player(user_id, player)
    await query.answer(f"✅ {item['name']} dipasang!", show_alert=True)
    if slot == "weapon":
        await _show_choose_weapon(query, player)
    else:
        await _show_choose_armor(query, player)


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
        # BUG FIX: clamp hp/mp agar tidak melebihi max_hp/max_mp baru setelah unequip
        player["hp"] = min(player.get("hp", 1), player.get("max_hp", 1))
        player["mp"] = min(player.get("mp", 0), player.get("max_mp", 0))

    equip[slot] = None
    # Item tetap ada di inventory
    save_player(user_id, player)
    await query.answer(f"♻️ {item['name'] if item else 'Item'} dilepas! (tetap di inventory)", show_alert=True)
    await _show_equipment(query, player)


async def _show_choose_pet(query, player: dict):
    """Tampilkan daftar pet yang dimiliki untuk diganti."""
    from items import PET_SHOP
    active_pet_id = player.get("pet")
    owned_pets = player.get("owned_pets", [])
    # Backward compat
    if active_pet_id and active_pet_id not in owned_pets:
        owned_pets = list(owned_pets) + [active_pet_id]

    RARITY_COLOR = {
        "SSR": "✨", "UR": "💜", "GOD": "🌟", "GOD SSSR": "🔱",
        "common": "⚪", "uncommon": "🟢", "rare": "🔵",
        "epic": "🟣", "legendary": "🟡"
    }

    if not owned_pets:
        await query.answer("❌ Kamu belum punya pet! Beli di /shop → Premium → Pet Shop.", show_alert=True)
        return

    text = (
        "╔══════════════════════════════════╗\n"
        "║     🐾  *PILIH PET AKTIF*        ║\n"
        "╚══════════════════════════════════╝\n\n"
        f"Pet aktif sekarang: *{PET_SHOP.get(active_pet_id, {}).get('name', active_pet_id or 'Tidak ada')}*\n\n"
        "Pilih pet yang ingin diaktifkan:\n"
        "_(Semua pet milikmu tersimpan permanen)_"
    )

    buttons = []
    for pet_id in owned_pets:
        pet = PET_SHOP.get(pet_id)
        if not pet:
            continue
        rarity = pet.get("rarity", "common")
        icon = RARITY_COLOR.get(rarity, "⚪")
        active_tag = " ⚡AKTIF" if pet_id == active_pet_id else ""
        label = f"{icon} {pet['name']}{active_tag}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"inv_equip_pet_{pet_id}")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="inv_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _equip_pet_from_inv(query, player: dict, user_id: int, pet_id: str):
    """Aktifkan pet yang sudah dimiliki."""
    from items import PET_SHOP
    owned_pets = player.get("owned_pets", [])
    active_pet_id = player.get("pet")
    # Backward compat
    if active_pet_id and active_pet_id not in owned_pets:
        owned_pets = list(owned_pets) + [active_pet_id]

    if pet_id not in owned_pets:
        await query.answer("❌ Pet ini bukan milikmu!", show_alert=True)
        return

    if pet_id == active_pet_id:
        await query.answer("✅ Pet ini sudah aktif!", show_alert=True)
        return

    pet = PET_SHOP.get(pet_id)
    if not pet:
        await query.answer("❌ Pet tidak ditemukan!", show_alert=True)
        return

    # BUG FIX: pet_tier harus dilacak per-pet agar evolusi tiap pet tersimpan terpisah.
    # Gunakan dict "pet_tiers" {pet_id: tier}. Fallback ke nilai lama untuk backward compat.
    pet_tiers = player.setdefault("pet_tiers", {})
    # Simpan tier pet yang sedang aktif sebelum switch (jika ada)
    if active_pet_id and active_pet_id != pet_id:
        pet_tiers[active_pet_id] = player.get("pet_tier", 1)
    # Load tier pet baru (dari pet_tiers jika sudah pernah dievolve, else tier default)
    new_tier = pet_tiers.get(pet_id, pet.get("tier", 1))
    player["pet"] = pet_id
    player["pet_tier"] = new_tier
    player["pet_tiers"] = pet_tiers
    player["owned_pets"] = owned_pets
    save_player(user_id, player)

    await query.answer(f"✅ {pet['name']} sekarang aktif!", show_alert=True)
    await _show_choose_pet(query, player)
