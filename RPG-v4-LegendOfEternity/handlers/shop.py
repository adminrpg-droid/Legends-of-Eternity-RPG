from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, apply_vip, is_admin
from items import (
    CONSUMABLES, get_class_weapons, get_class_armors,
    VIP_PACKAGES, COIN_PACKAGES, DIAMOND_PACKAGES, get_item, RARITY_STARS,
    SHOP_SKILLS, get_class_skills
)


def _coin_line(player: dict) -> str:
    return f"💰 Coin: *{player.get('coin',0):,}*  💎 Diamond: *{player.get('diamond',0)}*"


def _shop_main_keyboard(player: dict) -> InlineKeyboardMarkup:
    char_class = player.get("class", "warrior")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("─── 🧪 KONSUMABLE ───", callback_data="shop_cat_consumable")],
        [InlineKeyboardButton("🧪 Lihat Konsumable", callback_data="shop_view_consumable")],
        [InlineKeyboardButton("─── ⚔️ SENJATA ───", callback_data="shop_cat_weapon")],
        [InlineKeyboardButton(f"⚔️ Senjata {char_class.capitalize()}", callback_data="shop_view_weapon")],
        [InlineKeyboardButton("─── 🛡️ ARMOR ───", callback_data="shop_cat_armor")],
        [InlineKeyboardButton(f"🛡️ Armor {char_class.capitalize()}", callback_data="shop_view_armor")],
        [InlineKeyboardButton("─── 💎 VIP & TOPUP ───", callback_data="shop_cat_vip")],
        [
            InlineKeyboardButton("🏅 Beli VIP", callback_data="shop_view_vip"),
            InlineKeyboardButton("💰 Topup Coin", callback_data="shop_view_coin"),
        ],
        [InlineKeyboardButton("💎 Topup Diamond", callback_data="shop_view_diamond")],
        [InlineKeyboardButton("─── 🔮 SKILL ───", callback_data="shop_cat_skill")],
        [InlineKeyboardButton(f"🔮 Beli Skill {char_class.capitalize()}", callback_data="shop_view_skill")],
    ])


async def shop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return

    text = (
        "╔══════════════════════════════════╗\n"
        "║       🛒  *TOKO ETERNITY*        ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_coin_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "🛍️ Pilih kategori item:"
    )
    await update.message.reply_text(text, parse_mode="Markdown",
                                    reply_markup=_shop_main_keyboard(player))


async def shop_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)

    if not player:
        await query.answer("❌ Ketik /start!", show_alert=True)
        return

    if action in ("shop_cat_consumable", "shop_cat_weapon", "shop_cat_armor",
                  "shop_cat_vip", "shop_cat_skill", "shop_main"):
        text = (
            "╔══════════════════════════════════╗\n"
            "║       🛒  *TOKO ETERNITY*        ║\n"
            "╠══════════════════════════════════╣\n"
            f"║  {_coin_line(player)}\n"
            "╚══════════════════════════════════╝\n\n"
            "🛍️ Pilih kategori item:"
        )
        await query.edit_message_text(text, parse_mode="Markdown",
                                      reply_markup=_shop_main_keyboard(player))
        return

    if action == "shop_view_consumable":
        await _show_consumables(query, player); return
    if action == "shop_view_weapon":
        await _show_weapons(query, player); return
    if action == "shop_view_armor":
        await _show_armors(query, player); return
    if action == "shop_view_vip":
        await _show_vip(query, player); return
    if action == "shop_view_coin":
        await _show_coin_packages(query, player); return
    if action == "shop_view_diamond":
        await _show_diamond_packages(query, player); return
    if action == "shop_view_skill":
        await _show_skills(query, player); return

    if action.startswith("shop_buy_skill_"):
        await _buy_skill(query, player, user.id, action.replace("shop_buy_skill_", "")); return
    if action.startswith("shop_buy_cons_"):
        await _buy_consumable(query, player, user.id, action.replace("shop_buy_cons_", "")); return
    if action.startswith("shop_buy_wpn_"):
        await _buy_equipment(query, player, user.id, action.replace("shop_buy_wpn_", ""), "weapon"); return
    if action.startswith("shop_buy_arm_"):
        await _buy_equipment(query, player, user.id, action.replace("shop_buy_arm_", ""), "armor"); return
    if action.startswith("shop_vip_info_"):
        await _show_vip_info(query, player, action.replace("shop_vip_info_", "")); return


# ─── VIEWS ──────────────────────────────────────────────────────
async def _show_consumables(query, player: dict):
    text = (
        "╔══════════════════════════════════╗\n"
        "║    🧪  *KONSUMABLE*              ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_coin_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "Beli item untuk membantu di pertempuran:"
    )
    buttons = []
    for iid, item in CONSUMABLES.items():
        price = item["price"]
        owned = player.get("inventory", {}).get(iid, 0)
        label = f"{item['name']} — {price:,}💰 (punya:{owned})"
        buttons.append([InlineKeyboardButton(label, callback_data=f"shop_buy_cons_{iid}")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_weapons(query, player: dict):
    char_class = player.get("class", "warrior")
    weapons    = get_class_weapons(char_class)
    equip_wpn  = player.get("equipment", {}).get("weapon")

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  ⚔️ *SENJATA {char_class.upper()}*\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_coin_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "Senjata yang tersedia untuk kelasmu:"
    )
    buttons = []
    for iid, item in weapons.items():
        stars    = RARITY_STARS.get(item.get("rarity", "common"), "⭐")
        price    = item["price"]
        equipped = " ✅" if equip_wpn == iid else ""
        mark     = "✓" if player.get("coin", 0) >= price else "✗"
        label = f"{item['name']} {stars} — {price:,}💰 {mark}{equipped}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"shop_buy_wpn_{iid}")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_armors(query, player: dict):
    char_class = player.get("class", "warrior")
    armors     = get_class_armors(char_class)
    equip_arm  = player.get("equipment", {}).get("armor")

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  🛡️ *ARMOR {char_class.upper()}*\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_coin_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "Armor yang tersedia untuk kelasmu:"
    )
    buttons = []
    for iid, item in armors.items():
        stars    = RARITY_STARS.get(item.get("rarity", "common"), "⭐")
        price    = item["price"]
        equipped = " ✅" if equip_arm == iid else ""
        mark     = "✓" if player.get("coin", 0) >= price else "✗"
        label = f"{item['name']} {stars} — {price:,}💰 {mark}{equipped}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"shop_buy_arm_{iid}")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_vip(query, player: dict):
    vip_active = player.get("vip", {}).get("active", False)
    vip_status = "✅ VIP AKTIF" if vip_active else "❌ Tidak ada VIP"
    text = (
        "╔══════════════════════════════════╗\n"
        "║      🏅  *PAKET VIP*             ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  Status VIP: {vip_status}\n"
        "╚══════════════════════════════════╝\n\n"
        "🌟 VIP memberikan keuntungan ekstra dalam pertempuran!\n\n"
        "🥈 *VIP Silver* — Rp 15.000/bulan\n"
        "Crit +4%, HP +20, MP +15, ATK +3\n\n"
        "🥇 *VIP Gold* — Rp 30.000/bulan\n"
        "Crit +8%, HP +45, MP +30, ATK +7\n\n"
        "💎 *VIP Diamond* — Rp 75.000/bulan\n"
        "Crit +14%, HP +85, MP +55, ATK +13\n\n"
        "_Pembelian melalui transfer bank. Tap untuk detail._"
    )
    buttons = [
        [InlineKeyboardButton("🥈 Beli VIP Silver",  callback_data="shop_vip_info_vip_silver")],
        [InlineKeyboardButton("🥇 Beli VIP Gold",    callback_data="shop_vip_info_vip_gold")],
        [InlineKeyboardButton("💎 Beli VIP Diamond", callback_data="shop_vip_info_vip_diamond")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_vip_info(query, player: dict, vip_id: str):
    # FIX: gunakan key yang benar dari VIP_PACKAGES dict
    vip = VIP_PACKAGES.get(vip_id)
    if not vip:
        await query.answer("VIP tidak ditemukan!", show_alert=True)
        return
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {vip['name']} — Detail\n"
        "╚══════════════════════════════════╝\n\n"
        f"💡 *{vip['desc']}*\n\n"
        "💳 *Cara Pembelian:*\n"
        "1. Transfer ke rekening berikut:\n"
        f"   🏦 Bank: *{vip['bank']}*\n"
        f"   📋 Nomor: `{vip['account']}`\n"
        f"   👤 A/N: *{vip['account_name']}*\n"
        f"   💰 Nominal: Rp {vip['price_idr']:,}\n\n"
        "2. Kirim bukti transfer ke admin\n"
        f"   beserta *ID Telegram* kamu: `{query.from_user.id}`\n\n"
        "3. Admin akan aktifkan VIP dalam 1x24 jam\n\n"
        f"_Aktif selama {vip['duration_days']} hari setelah konfirmasi._"
    )
    buttons = [
        [InlineKeyboardButton("⬅️ Kembali ke VIP", callback_data="shop_view_vip")],
        [InlineKeyboardButton("🏠 Menu Toko", callback_data="shop_main")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_coin_packages(query, player: dict):
    text = (
        "╔══════════════════════════════════╗\n"
        "║    💰  *TOPUP COIN*              ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_coin_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "💰 Beli coin untuk berbelanja di toko!\n\n"
    )
    for pid, pkg in COIN_PACKAGES.items():
        text += f"*{pkg['name']}* — Rp {pkg['price_idr']:,}\n"
    text += (
        "\n💳 *Cara Topup:*\n"
        f"Transfer ke 🏦 {COIN_PACKAGES['coins_small']['bank']} "
        f"`{COIN_PACKAGES['coins_small']['account']}` "
        f"{COIN_PACKAGES['coins_small']['account_name']}\n"
        f"Kirim bukti + ID kamu: `{query.from_user.id}` ke admin"
    )
    buttons = [[InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_diamond_packages(query, player: dict):
    text = (
        "╔══════════════════════════════════╗\n"
        "║    💎  *TOPUP DIAMOND*           ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_coin_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "💎 Diamond untuk item premium!\n\n"
    )
    for pid, pkg in DIAMOND_PACKAGES.items():
        text += f"*{pkg['name']}* — Rp {pkg['price_idr']:,}\n"
    text += (
        "\n💳 *Cara Topup:*\n"
        f"Transfer ke 🏦 {DIAMOND_PACKAGES['diamond_small']['bank']} "
        f"`{DIAMOND_PACKAGES['diamond_small']['account']}` "
        f"{DIAMOND_PACKAGES['diamond_small']['account_name']}\n"
        f"Kirim bukti + ID kamu: `{query.from_user.id}` ke admin"
    )
    buttons = [[InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


# ─── BUY LOGIC ──────────────────────────────────────────────────
async def _buy_consumable(query, player: dict, user_id: int, item_id: str):
    item = CONSUMABLES.get(item_id)
    if not item:
        await query.answer("Item tidak ditemukan!", show_alert=True)
        return

    price = item["price"]
    admin = is_admin(user_id)

    if not admin and player.get("coin", 0) < price:
        await query.answer(
            f"❌ Coin tidak cukup! Butuh {price:,}, punya {player.get('coin',0):,}",
            show_alert=True
        )
        return

    if not admin:
        player["coin"] -= price

    inv = player.setdefault("inventory", {})
    inv[item_id] = inv.get(item_id, 0) + 1
    save_player(user_id, player)

    await query.answer(f"✅ {item['name']} dibeli!", show_alert=False)
    await _show_consumables(query, player)


async def _buy_equipment(query, player: dict, user_id: int, item_id: str, eq_type: str):
    from items import ALL_ITEMS
    item = ALL_ITEMS.get(item_id)
    if not item:
        await query.answer("Item tidak ditemukan!", show_alert=True)
        return

    item_class = item.get("class")
    if item_class and item_class != player.get("class") and not is_admin(user_id):
        await query.answer("❌ Item ini bukan untuk kelasmu!", show_alert=True)
        return

    price = item["price"]
    admin = is_admin(user_id)

    if not admin and player.get("coin", 0) < price:
        await query.answer(
            f"❌ Coin tidak cukup! Butuh {price:,}💰, punya {player.get('coin',0):,}💰",
            show_alert=True
        )
        return

    if not admin:
        player["coin"] -= price

    equip  = player.setdefault("equipment", {})
    old_id = equip.get(eq_type)

    # Lepas item lama
    if old_id:
        old_item = ALL_ITEMS.get(old_id, {})
        for stat, val in old_item.get("stats", {}).items():
            player[stat] = max(1, player.get(stat, 0) - val)

    # Pasang item baru
    equip[eq_type] = item_id
    for stat, val in item.get("stats", {}).items():
        player[stat] = player.get(stat, 0) + val
        if stat == "max_hp":
            player["hp"] = min(player.get("hp", 1) + val, player["max_hp"])
        if stat == "max_mp":
            player["mp"] = min(player.get("mp", 0) + val, player["max_mp"])

    save_player(user_id, player)
    old_name = ALL_ITEMS.get(old_id, {}).get("name", "") if old_id else ""
    old_txt  = f"\n♻️ {old_name} dilepas." if old_name else ""
    await query.answer(f"✅ {item['name']} terpasang!{old_txt}", show_alert=True)

    if eq_type == "weapon":
        await _show_weapons(query, player)
    else:
        await _show_armors(query, player)


# ─── SKILL SHOP ─────────────────────────────────────────────────
async def _show_skills(query, player: dict):
    char_class = player.get("class", "warrior")
    skills     = get_class_skills(char_class)
    bought     = {s["id"] for s in player.get("bought_skills", [])}

    text = (
        "╔══════════════════════════════════╗\n"
        "║     🔮  *SKILL SHOP*             ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_coin_line(player)}\n"
        f"║  Kelas: *{char_class.capitalize()}*\n"
        "╚══════════════════════════════════╝\n\n"
        "🔮 Pilih skill untuk dibeli:\n"
        "_(Skill dapat dipakai saat battle sebagai pengganti skill utama)_\n\n"
    )

    buttons = []
    for sid, sk in skills.items():
        stars  = RARITY_STARS.get(sk.get("rarity", "rare"), "⭐⭐⭐")
        price  = sk["price"]
        owned  = " ✅ Dimiliki" if sid in bought else ""
        mark   = "✓" if (player.get("coin", 0) >= price or sid in bought) else "✗"
        label  = f"{sk['name']} {stars} — {price:,}💰 {mark}{owned}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"shop_buy_skill_{sid}")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _buy_skill(query, player: dict, user_id: int, skill_id: str):
    skill = SHOP_SKILLS.get(skill_id)
    if not skill:
        await query.answer("Skill tidak ditemukan!", show_alert=True)
        return

    char_class = player.get("class", "warrior")
    if skill.get("class") != char_class and not is_admin(user_id):
        await query.answer("❌ Skill ini bukan untuk kelasmu!", show_alert=True)
        return

    bought    = player.setdefault("bought_skills", [])
    owned_ids = [s["id"] for s in bought]
    if skill_id in owned_ids:
        await query.answer("✅ Skill sudah dimiliki!", show_alert=True)
        return

    price = skill["price"]
    admin = is_admin(user_id)
    if not admin and player.get("coin", 0) < price:
        await query.answer(
            f"❌ Coin tidak cukup! Butuh {price:,}💰, punya {player.get('coin',0):,}💰",
            show_alert=True
        )
        return

    if not admin:
        player["coin"] -= price

    bought.append({
        "id":     skill_id,
        "name":   skill["name"],
        "desc":   skill["desc"],
        "effect": skill["effect"],
        "class":  skill["class"],
    })
    save_player(user_id, player)

    stars = RARITY_STARS.get(skill.get("rarity", "rare"), "⭐⭐⭐")
    await query.answer(
        f"✅ {skill['name']} {stars} berhasil dibeli!\n"
        f"Gunakan di battle dengan tombol 'Skill'.",
        show_alert=True
    )
    await _show_skills(query, player)
