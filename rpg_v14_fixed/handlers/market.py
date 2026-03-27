import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, get_market, add_market_listing, remove_market_listing
from items import get_item, RARITY_STARS, ALL_ITEMS, SHOP_SKILLS, PREMIUM_SKILLS, PET_SHOP, GOD_SSSR_SKILLS, GOD_SSSR_PETS


# ─── Helper ──────────────────────────────────────────────────────────────

def _get_all_sellable_items(player: dict) -> list:
    """Kumpulkan semua item yang bisa dijual. Return list of (source, slot, item_id, item, currency)"""
    sellable = []
    equip = player.get("equipment", {})
    inv   = player.get("inventory", {})

    # Weapon & Armor
    for slot in ("weapon", "armor"):
        item_id = equip.get(slot)
        if not item_id:
            continue
        item = get_item(item_id)
        if item and item.get("sellable", True):
            sellable.append(("equip", slot, item_id, item, "gold"))

    # Skill (bought_skills)
    for entry in player.get("bought_skills", []):
        skill_id = entry.get("id", "") if isinstance(entry, dict) else entry
        skill = SHOP_SKILLS.get(skill_id) or PREMIUM_SKILLS.get(skill_id) or GOD_SSSR_SKILLS.get(skill_id)
        if skill:
            currency = "diamond" if skill.get("diamond_price") or skill.get("rarity") in ("SSR","UR","GOD","GOD SSSR") else "gold"
            sellable.append(("skill", skill_id, skill_id, skill, currency))

    # Pet
    pet_id = player.get("pet")
    if pet_id:
        pet = PET_SHOP.get(pet_id) or GOD_SSSR_PETS.get(pet_id)
        if pet:
            currency = "diamond" if pet.get("diamond_price") or pet.get("rarity") in ("SSR","UR","GOD","GOD SSSR") else "gold"
            sellable.append(("pet", pet_id, pet_id, pet, currency))

    # Evolution Stone
    evo_count = inv.get("evolution_stone", 0)
    if evo_count > 0:
        from items import EVOLUTION_STONE
        evo_item = EVOLUTION_STONE.get("evolution_stone", {})
        if evo_item:
            sellable.append(("inv", "evolution_stone", "evolution_stone", evo_item, "diamond"))

    return sellable


def _remove_item_from_player(player: dict, source: str, slot: str, item_id: str, item: dict):
    equip = player.setdefault("equipment", {})
    inv   = player.setdefault("inventory", {})
    if source == "equip":
        for stat, val in item.get("stats", {}).items():
            player[stat] = max(1, player.get(stat, 0) - val)
        equip[slot] = None
    elif source == "skill":
        player["bought_skills"] = [
            s for s in player.get("bought_skills", [])
            if (s.get("id") if isinstance(s, dict) else s) != item_id
        ]
        if equip.get("skill") == item_id:
            equip["skill"] = None
    elif source == "pet":
        if player.get("pet") == item_id:
            player["pet"] = None
            player["pet_tier"] = 1
    elif source == "inv":
        inv[item_id] = max(0, inv.get(item_id, 0) - 1)


def _give_item_to_buyer(player: dict, item_id: str, item: dict, source: str):
    equip = player.setdefault("equipment", {})
    inv   = player.setdefault("inventory", {})
    item_type = item.get("type", "")

    if item_type in ("weapon", "armor"):
        slot = item_type
        old  = equip.get(slot)
        if old:
            old_item = ALL_ITEMS.get(old, {})
            for s, v in old_item.get("stats", {}).items():
                player[s] = max(1, player.get(s, 0) - v)
        equip[slot] = item_id
        for s, v in item.get("stats", {}).items():
            player[s] = player.get(s, 0) + v
    elif source == "skill":
        bought = player.setdefault("bought_skills", [])
        existing_ids = [(s.get("id") if isinstance(s, dict) else s) for s in bought]
        if item_id not in existing_ids:
            bought.append({"id": item_id, "name": item.get("name", item_id)})
    elif source == "pet":
        player["pet"] = item_id
        player.setdefault("pet_tier", 1)
    elif source == "inv":
        inv[item_id] = inv.get(item_id, 0) + 1


def _get_listing_item(listing: dict):
    src = listing.get("item_source", "equip")
    iid = listing.get("item_id", "")
    if src == "skill":
        return SHOP_SKILLS.get(iid) or PREMIUM_SKILLS.get(iid) or GOD_SSSR_SKILLS.get(iid)
    elif src == "pet":
        return PET_SHOP.get(iid) or GOD_SSSR_PETS.get(iid)
    else:
        return get_item(iid)


def _type_tag(source: str) -> str:
    return {"weapon":"⚔️","armor":"🛡️","equip":"⚔️","skill":"🔮","pet":"🐾","inv":"💠","evolution_stone":"💠"}.get(source,"📦")


# ─── Handlers ────────────────────────────────────────────────────────────

async def market_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    await _show_market(update.message, player, is_msg=True)


async def market_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        return

    if action == "market_browse":
        await _show_market(query, player)
        return
    if action == "market_mylist":
        await _show_my_listings(query, player, user.id)
        return
    if action == "market_sell":
        await _show_sell_menu(query, player)
        return

    if action.startswith("market_sell_item_"):
        raw   = action.replace("market_sell_item_", "", 1)
        parts = raw.split("|")
        source  = parts[0] if len(parts) >= 3 else "equip"
        slot    = parts[1] if len(parts) >= 3 else parts[0]
        item_id = parts[2] if len(parts) >= 3 else (parts[1] if len(parts) >= 2 else raw)
        context.user_data["market_sell_source"] = source
        context.user_data["market_sell_slot"]   = slot
        context.user_data["market_sell_item"]   = item_id
        await _ask_sell_price(query, source, slot, item_id)
        return

    if action.startswith("market_confirm_sell_"):
        raw = action.replace("market_confirm_sell_", "", 1)
        try:
            c_idx    = raw.rfind("_c_")
            p_idx    = raw.rfind("_p_")
            currency = raw[c_idx+3:] if c_idx != -1 else "gold"
            price    = int(raw[p_idx+3:c_idx if c_idx != -1 else len(raw)])
            meta     = raw[:p_idx]
            parts    = meta.split("|")
            source   = parts[0] if len(parts) >= 3 else "equip"
            slot     = parts[1] if len(parts) >= 3 else parts[0]
            item_id  = parts[2] if len(parts) >= 3 else (parts[1] if len(parts) >= 2 else meta)
        except Exception:
            await query.answer("❌ Data tidak valid!", show_alert=True)
            return
        await _confirm_sell(query, player, user.id, source, slot, item_id, price, currency)
        return

    if action.startswith("market_buy_"):
        listing_id = action.replace("market_buy_", "")
        await _buy_listing(query, player, user.id, listing_id)
        return

    if action.startswith("market_cancel_"):
        listing_id = action.replace("market_cancel_", "")
        await _cancel_listing(query, player, user.id, listing_id)
        return


async def _show_market(target, player: dict, is_msg=False):
    market = get_market()
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║     🏪  *MARKET ETERNITY*        ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🪙 Gold: *{player.get('coin',0):,}*\n"
        f"║  💎 Diamond: *{player.get('diamond',0)}*\n"
        f"╚══════════════════════════════════╝\n\n"
    )
    if not market:
        text += "📭 Market masih kosong. Jual item duluan!"
    else:
        text += f"📦 *{len(market)} item dijual:*\n\n"
        for lid, listing in list(market.items())[:10]:
            item = _get_listing_item(listing)
            if not item:
                continue
            stars    = RARITY_STARS.get(item.get("rarity","common"),"⭐")
            currency = listing.get("currency","gold")
            cur_icon = "💎" if currency == "diamond" else "🪙"
            src      = listing.get("item_source","equip")
            tag      = _type_tag(src)
            text += (
                f"• {tag} {item['name']} {stars}\n"
                f"  👤 {listing['seller_name']} — {cur_icon} {listing['price']}\n"
            )

    keyboard = [
        [InlineKeyboardButton("🛍️ Beli Item", callback_data="market_buy_list"),
         InlineKeyboardButton("💼 Jual Item",  callback_data="market_sell")],
        [InlineKeyboardButton("📋 Daftar Jualku", callback_data="market_mylist")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="market_browse")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def _show_sell_menu(query, player: dict):
    sellable = _get_all_sellable_items(player)
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   💼  *JUAL ITEM KE MARKET*      ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih item yang ingin dijual:\n"
        f"_(Weapon⚔️ Armor🛡️ Skill🔮 Pet🐾 Evo💠)_"
    )
    buttons = []
    for source, slot, item_id, item, currency in sellable:
        stars    = RARITY_STARS.get(item.get("rarity","common"),"⭐")
        cur_icon = "💎" if currency == "diamond" else "🪙"
        tag      = _type_tag(source)
        # Truncate callback to 64 chars
        cb_data  = f"market_sell_item_{source}|{slot}|{item_id}"[:64]
        buttons.append([InlineKeyboardButton(f"{tag}{item['name']} {stars}[{cur_icon}]", callback_data=cb_data)])
    if not buttons:
        text += "\n\n❌ Tidak ada item yang bisa dijual."
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="market_browse")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


async def _ask_sell_price(query, source: str, slot: str, item_id: str):
    if source == "skill":
        item = SHOP_SKILLS.get(item_id) or PREMIUM_SKILLS.get(item_id) or GOD_SSSR_SKILLS.get(item_id)
    elif source == "pet":
        item = PET_SHOP.get(item_id) or GOD_SSSR_PETS.get(item_id)
    else:
        item = get_item(item_id)

    if not item:
        await query.answer("Item tidak valid!", show_alert=True)
        return

    rarity     = item.get("rarity","common")
    is_diamond = rarity in ("SSR","UR","GOD","GOD SSSR") or bool(item.get("diamond_price"))
    base_price = item.get("diamond_price") or item.get("price") or 100
    currency   = "diamond" if is_diamond else "gold"
    cur_icon   = "💎" if is_diamond else "🪙"
    stars      = RARITY_STARS.get(rarity,"⭐")
    meta       = f"{source}|{slot}|{item_id}"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  💰  *TENTUKAN HARGA JUAL*       ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Item: *{item['name']}* {stars}\n"
        f"Harga toko: {base_price} {cur_icon}\n"
        f"Mata uang: {'💎 Diamond' if is_diamond else '🪙 Gold'}\n\n"
        f"Pilih harga jual:"
    )
    prices  = [max(1,int(base_price*m)) for m in (0.3,0.5,0.75,1.0,1.5)]
    buttons = []
    for p in prices:
        cb = f"market_confirm_sell_{meta}_p_{p}_c_{currency}"[:64]
        buttons.append([InlineKeyboardButton(f"{cur_icon} {p} {'Diamond' if is_diamond else 'Gold'}", callback_data=cb)])
    buttons.append([InlineKeyboardButton("⬅️ Batal", callback_data="market_sell")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


async def _confirm_sell(query, player: dict, user_id: int, source: str, slot: str, item_id: str, price: int, currency: str):
    if source == "skill":
        item = SHOP_SKILLS.get(item_id) or PREMIUM_SKILLS.get(item_id) or GOD_SSSR_SKILLS.get(item_id)
    elif source == "pet":
        item = PET_SHOP.get(item_id) or GOD_SSSR_PETS.get(item_id)
    else:
        item = get_item(item_id)

    if not item:
        await query.answer("Item tidak valid!", show_alert=True)
        return

    # Verify ownership
    equip = player.get("equipment", {})
    inv   = player.get("inventory", {})
    owned = False
    if source == "equip":
        owned = equip.get(slot) == item_id
    elif source == "skill":
        owned = item_id in [(s.get("id") if isinstance(s,dict) else s) for s in player.get("bought_skills",[])]
    elif source == "pet":
        owned = player.get("pet") == item_id
    elif source == "inv":
        owned = inv.get(item_id, 0) > 0

    if not owned:
        await query.answer("Item sudah tidak kamu miliki!", show_alert=True)
        return

    _remove_item_from_player(player, source, slot, item_id, item)
    add_market_listing(user_id, player["name"], item_id, item, price, currency=currency, item_source=source)
    save_player(user_id, player)

    cur_icon = "💎" if currency == "diamond" else "🪙"
    await query.edit_message_text(
        f"✅ *{item['name']}* berhasil dimasukkan ke market!\n"
        f"Harga: {cur_icon} {price} {'Diamond' if currency=='diamond' else 'Gold'}\n\n"
        f"Barang telah dilepas dari equipment/inventorimu.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 Lihat Market", callback_data="market_browse")]])
    )


async def _buy_listing(query, player: dict, user_id: int, listing_id: str):
    if listing_id == "list":
        market = get_market()
        if not market:
            await query.answer("Market kosong!", show_alert=True)
            return
        buttons = []
        for lid, listing in list(market.items())[:8]:
            if listing["seller_id"] == user_id:
                continue
            item = _get_listing_item(listing)
            if not item:
                continue
            currency = listing.get("currency","gold")
            cur_icon = "💎" if currency == "diamond" else "🪙"
            stars    = RARITY_STARS.get(item.get("rarity","common"),"⭐")
            src      = listing.get("item_source","equip")
            tag      = _type_tag(src)
            buttons.append([InlineKeyboardButton(
                f"{tag}{item['name']} {stars} — {cur_icon}{listing['price']} ({listing['seller_name']})",
                callback_data=f"market_buy_{lid}"
            )])
        if not buttons:
            await query.answer("Tidak ada item dari orang lain!", show_alert=True)
            return
        buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="market_browse")])
        await query.edit_message_text(
            "🛍️ *Pilih item untuk dibeli:*\n_(💎=Diamond 🪙=Gold)_",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    market  = get_market()
    listing = market.get(listing_id)
    if not listing:
        await query.answer("Item sudah terjual!", show_alert=True)
        return
    if listing["seller_id"] == user_id:
        await query.answer("Tidak bisa beli item sendiri!", show_alert=True)
        return

    price    = listing["price"]
    currency = listing.get("currency","gold")

    if currency == "diamond":
        if player.get("diamond",0) < price:
            await query.answer(f"❌ Diamond tidak cukup! Butuh {price} 💎", show_alert=True)
            return
    else:
        if player.get("coin",0) < price:
            await query.answer(f"❌ Gold tidak cukup! Butuh {price} 🪙", show_alert=True)
            return

    item = _get_listing_item(listing)
    if not item:
        await query.answer("Item tidak valid!", show_alert=True)
        return

    # Transfer to seller
    seller_player = get_player(listing["seller_id"])
    if seller_player:
        if currency == "diamond":
            seller_player["diamond"] = seller_player.get("diamond",0) + price
        else:
            seller_player["coin"] = seller_player.get("coin",0) + price
        save_player(listing["seller_id"], seller_player)

    if currency == "diamond":
        player["diamond"] = player.get("diamond",0) - price
    else:
        player["coin"] = player.get("coin",0) - price

    src = listing.get("item_source","equip")
    _give_item_to_buyer(player, listing["item_id"], item, src)
    remove_market_listing(listing_id)
    save_player(user_id, player)

    cur_icon = "💎" if currency == "diamond" else "🪙"
    stars    = RARITY_STARS.get(item.get("rarity","common"),"⭐")
    await query.edit_message_text(
        f"✅ *{item['name']}* {stars} berhasil dibeli!\n"
        f"{cur_icon} -{price} {'Diamond' if currency=='diamond' else 'Gold'}\n"
        f"Item sudah masuk ke equipment/inventorimu!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏪 Market", callback_data="market_browse")]])
    )


async def _show_my_listings(query, player: dict, user_id: int):
    market = get_market()
    my     = {lid: l for lid, l in market.items() if l["seller_id"] == user_id}
    text   = "╔══════════════════════════════════╗\n║   📋  *ITEM JUALKU*              ║\n╚══════════════════════════════════╝\n\n"
    buttons = []
    if not my:
        text += "📭 Tidak ada item yang sedang dijual."
    else:
        text += f"*{len(my)} item dijual:*\n"
        for lid, listing in my.items():
            item = _get_listing_item(listing)
            if not item:
                continue
            currency = listing.get("currency","gold")
            cur_icon = "💎" if currency == "diamond" else "🪙"
            src      = listing.get("item_source","equip")
            tag      = _type_tag(src)
            text += f"• {tag} {item['name']} — {cur_icon}{listing['price']}\n"
            buttons.append([InlineKeyboardButton(f"❌ Cabut {item['name']}", callback_data=f"market_cancel_{lid}")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="market_browse")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


async def _cancel_listing(query, player: dict, user_id: int, listing_id: str):
    market  = get_market()
    listing = market.get(listing_id)
    if not listing or listing["seller_id"] != user_id:
        await query.answer("Listing tidak ditemukan!", show_alert=True)
        return
    item = _get_listing_item(listing)
    remove_market_listing(listing_id)
    if item:
        src = listing.get("item_source","equip")
        _give_item_to_buyer(player, listing["item_id"], item, src)
        save_player(user_id, player)
    await query.answer(f"✅ {item['name'] if item else 'Item'} dicabut dari market!", show_alert=True)
    await _show_my_listings(query, player, user_id)
