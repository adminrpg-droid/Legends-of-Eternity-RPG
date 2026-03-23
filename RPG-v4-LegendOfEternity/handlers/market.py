# ═══════════════════════════════════════════════════════════════
#  LEGENDS OF ETERNITY — Market Handler
# ═══════════════════════════════════════════════════════════════
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models.database import get_player, save_player, get_market, add_market_listing, remove_market_listing
from data.items import get_item, RARITY_STARS


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
        item_id = action.replace("market_sell_item_", "")
        context.user_data["market_sell_item"] = item_id
        await _ask_sell_price(query, item_id)
        return

    if action.startswith("market_confirm_sell_"):
        parts  = action.replace("market_confirm_sell_", "").split("_p_")
        item_id = parts[0]
        price   = int(parts[1])
        await _confirm_sell(query, player, user.id, item_id, price)
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
        f"║  💰 Coin: *{player.get('coin',0)}*\n"
        f"╚══════════════════════════════════╝\n\n"
    )

    if not market:
        text += "📭 Market masih kosong. Jual item duluan!"
    else:
        text += f"📦 *{len(market)} item dijual:*\n\n"
        for lid, listing in list(market.items())[:10]:
            item = get_item(listing["item_id"])
            if not item:
                continue
            stars = RARITY_STARS.get(item.get("rarity", "common"), "⭐")
            text += (
                f"• {item['name']} {stars}\n"
                f"  👤 {listing['seller_name']} — 💰 {listing['price']} Coin\n"
            )

    keyboard = [
        [
            InlineKeyboardButton("🛍️ Beli Item",  callback_data="market_buy_list"),
            InlineKeyboardButton("💼 Jual Item",   callback_data="market_sell"),
        ],
        [InlineKeyboardButton("📋 Daftar Jualku", callback_data="market_mylist")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def _show_sell_menu(query, player: dict):
    equip = player.get("equipment", {})
    text  = (
        f"╔══════════════════════════════════╗\n"
        f"║   💼  *JUAL ITEM KE MARKET*      ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih item yang ingin dijual:\n"
        f"_(Hanya senjata & armor yang bisa dijual)_"
    )
    buttons = []
    for slot in ("weapon", "armor"):
        item_id = equip.get(slot)
        if item_id:
            item = get_item(item_id)
            if item and item.get("sellable"):
                stars = RARITY_STARS.get(item.get("rarity","common"),"⭐")
                buttons.append([
                    InlineKeyboardButton(
                        f"{item['name']} {stars}",
                        callback_data=f"market_sell_item_{item_id}"
                    )
                ])
    if not buttons:
        text += "\n\n❌ Tidak ada item yang bisa dijual saat ini."
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="market_browse")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _ask_sell_price(query, item_id: str):
    item = get_item(item_id)
    if not item:
        await query.answer("Item tidak valid!", show_alert=True)
        return

    base_price = item.get("price", 100)
    suggested  = int(base_price * 0.6)

    # Offer a few preset prices
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  💰  *TENTUKAN HARGA JUAL*       ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Item: *{item['name']}*\n"
        f"Harga toko: {base_price} Coin\n\n"
        f"Pilih harga jual:"
    )
    prices  = [
        int(base_price * 0.3),
        int(base_price * 0.5),
        int(base_price * 0.7),
        int(base_price * 0.9),
    ]
    buttons = []
    for p in prices:
        buttons.append([InlineKeyboardButton(
            f"💰 {p} Coin",
            callback_data=f"market_confirm_sell_{item_id}_p_{p}"
        )])
    buttons.append([InlineKeyboardButton("⬅️ Batal", callback_data="market_sell")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _confirm_sell(query, player: dict, user_id: int, item_id: str, price: int):
    from data.items import ALL_ITEMS
    item = get_item(item_id)
    if not item:
        await query.answer("Item tidak valid!", show_alert=True)
        return

    equip = player.setdefault("equipment", {})
    slot  = item["type"]

    if equip.get(slot) != item_id:
        await query.answer("Item sudah tidak dipakai!", show_alert=True)
        return

    # Remove stats
    for stat, val in item.get("stats", {}).items():
        player[stat] = max(1, player.get(stat, 0) - val)

    equip[slot] = None
    add_market_listing(user_id, player["name"], item_id, item, price)
    save_player(user_id, player)

    await query.edit_message_text(
        f"✅ *{item['name']}* berhasil dimasukkan ke market!\n"
        f"Harga: 💰 {price} Coin\n\n"
        f"Tunggu pembeli menghubungimu.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏪 Lihat Market", callback_data="market_browse")
        ]])
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
            item = get_item(listing["item_id"])
            if not item:
                continue
            stars = RARITY_STARS.get(item.get("rarity","common"),"⭐")
            buttons.append([InlineKeyboardButton(
                f"{item['name']} {stars} — {listing['price']}💰 ({listing['seller_name']})",
                callback_data=f"market_buy_{lid}"
            )])
        if not buttons:
            await query.answer("Tidak ada item yang dijual orang lain!", show_alert=True)
            return
        buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="market_browse")])
        await query.edit_message_text(
            "🛍️ *Pilih item untuk dibeli:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Buy specific item
    market  = get_market()
    listing = market.get(listing_id)
    if not listing:
        await query.answer("Item sudah terjual!", show_alert=True)
        return

    if listing["seller_id"] == user_id:
        await query.answer("Tidak bisa beli item sendiri!", show_alert=True)
        return

    price = listing["price"]
    if player.get("coin", 0) < price:
        await query.answer(f"❌ Coin tidak cukup! Butuh {price}", show_alert=True)
        return

    item = get_item(listing["item_id"])
    if not item:
        await query.answer("Item tidak valid!", show_alert=True)
        return

    # Transfer coin to seller
    seller_player = get_player(listing["seller_id"])
    if seller_player:
        seller_player["coin"] = seller_player.get("coin", 0) + price
        save_player(listing["seller_id"], seller_player)

    player["coin"] -= price

    # Give item to buyer
    from data.items import ALL_ITEMS
    equip = player.setdefault("equipment", {})
    slot  = item["type"]
    old   = equip.get(slot)
    if old:
        old_item = ALL_ITEMS.get(old, {})
        for stat, val in old_item.get("stats", {}).items():
            player[stat] = max(1, player.get(stat, 0) - val)

    equip[slot] = listing["item_id"]
    for stat, val in item.get("stats", {}).items():
        player[stat] = player.get(stat, 0) + val

    remove_market_listing(listing_id)
    save_player(user_id, player)

    await query.edit_message_text(
        f"✅ *{item['name']}* berhasil dibeli!\n"
        f"💰 -{price} Coin | Terpasang otomatis!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏪 Market", callback_data="market_browse")
        ]])
    )


async def _show_my_listings(query, player: dict, user_id: int):
    market = get_market()
    my     = {lid: l for lid, l in market.items() if l["seller_id"] == user_id}

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   📋  *ITEM JUALKU*              ║\n"
        f"╚══════════════════════════════════╝\n\n"
    )

    buttons = []
    if not my:
        text += "📭 Tidak ada item yang sedang dijual."
    else:
        text += f"*{len(my)} item dijual:*\n"
        for lid, listing in my.items():
            item = get_item(listing["item_id"])
            if not item:
                continue
            text += f"• {item['name']} — {listing['price']}💰\n"
            buttons.append([InlineKeyboardButton(
                f"❌ Cabut {item['name']}", callback_data=f"market_cancel_{lid}"
            )])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="market_browse")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _cancel_listing(query, player: dict, user_id: int, listing_id: str):
    market  = get_market()
    listing = market.get(listing_id)
    if not listing or listing["seller_id"] != user_id:
        await query.answer("Listing tidak ditemukan!", show_alert=True)
        return

    item = get_item(listing["item_id"])
    remove_market_listing(listing_id)

    # Give item back
    if item:
        from data.items import ALL_ITEMS
        equip = player.setdefault("equipment", {})
        slot  = item["type"]
        equip[slot] = listing["item_id"]
        for stat, val in item.get("stats", {}).items():
            player[stat] = player.get(stat, 0) + val
        save_player(user_id, player)

    await query.answer(f"✅ {item['name'] if item else 'Item'} dicabut dari market!", show_alert=True)
    await _show_my_listings(query, player, user_id)
