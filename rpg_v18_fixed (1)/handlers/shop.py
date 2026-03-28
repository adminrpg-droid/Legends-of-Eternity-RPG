from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, apply_vip, is_admin
from items import (
    CONSUMABLES, get_class_weapons, get_class_armors,
    VIP_PACKAGES, COIN_PACKAGES, DIAMOND_PACKAGES, get_item, RARITY_STARS,
    SHOP_SKILLS, get_class_skills, ALL_ITEMS
)


def _gold_line(player: dict) -> str:
    return f"🪙 Gold: *{player.get('coin',0):,}*  💎 Diamond: *{player.get('diamond',0)}*"


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
            InlineKeyboardButton("🪙 Topup Gold", callback_data="shop_view_coin"),
        ],
        [InlineKeyboardButton("💎 Topup Diamond", callback_data="shop_view_diamond")],
        [InlineKeyboardButton("─── 🔮 SKILL ───", callback_data="shop_cat_skill")],
        [InlineKeyboardButton(f"🔮 Beli Skill {char_class.capitalize()}", callback_data="shop_view_skill")],
        [InlineKeyboardButton("═══ 💎 PREMIUM ═══", callback_data="pshop_main")],
        [InlineKeyboardButton("SSR/UR/GOD Shop", callback_data="pshop_main"),
         InlineKeyboardButton("🐾 Pet Shop", callback_data="pshop_pet")],
        [InlineKeyboardButton("💠 Evolution System", callback_data="pshop_evolution")],
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
        f"║  {_gold_line(player)}\n"
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
                  "shop_cat_vip", "shop_cat_skill", "shop_main",
                  "shop_back_main"):
        text = (
            "╔══════════════════════════════════╗\n"
            "║       🛒  *TOKO ETERNITY*        ║\n"
            "╠══════════════════════════════════╣\n"
            f"║  {_gold_line(player)}\n"
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

    # Gold select → konfirmasi paket
    if action.startswith("shop_coin_select_"):
        pkg_id = action.replace("shop_coin_select_", "")
        await _show_coin_confirm(query, player, pkg_id); return

    # Diamond select → konfirmasi paket
    if action.startswith("shop_diamond_select_"):
        pkg_id = action.replace("shop_diamond_select_", "")
        await _show_diamond_confirm(query, player, pkg_id); return
    if action == "shop_view_skill":
        await _show_skills(query, player); return

    # ── Konfirmasi Pembelian ──────────────────────────────────────
    if action.startswith("shop_confirm_skill_"):
        await _buy_skill(query, player, user.id, action.replace("shop_confirm_skill_", "")); return
    if action.startswith("shop_confirm_cons_"):
        parts = action.replace("shop_confirm_cons_", "").rsplit("_qty", 1)
        item_id = parts[0]
        qty = int(parts[1]) if len(parts) > 1 else 1
        await _buy_consumable(query, player, user.id, item_id, qty); return
    if action.startswith("shop_confirm_wpn_"):
        await _buy_equipment(query, player, user.id, action.replace("shop_confirm_wpn_", ""), "weapon"); return
    if action.startswith("shop_confirm_arm_"):
        await _buy_equipment(query, player, user.id, action.replace("shop_confirm_arm_", ""), "armor"); return

    # ── Item Click → Tampilkan Konfirmasi ────────────────────────
    if action.startswith("shop_buy_skill_"):
        await _ask_buy_skill(query, player, action.replace("shop_buy_skill_", "")); return
    if action.startswith("shop_buy_cons_"):
        await _ask_buy_consumable(query, player, action.replace("shop_buy_cons_", "")); return
    if action.startswith("shop_buy_wpn_"):
        await _ask_buy_equipment(query, player, action.replace("shop_buy_wpn_", ""), "weapon"); return
    if action.startswith("shop_buy_arm_"):
        await _ask_buy_equipment(query, player, action.replace("shop_buy_arm_", ""), "armor"); return
    if action.startswith("shop_vip_info_"):
        await _show_vip_info(query, player, action.replace("shop_vip_info_", "")); return

    # Upload bukti transfer VIP
    if action.startswith("shop_vip_transfer_"):
        vip_id = action.replace("shop_vip_transfer_", "")
        await _request_transfer_proof(query, player, vip_id, "vip"); return
    if action.startswith("shop_coin_transfer_"):
        pkg_id = action.replace("shop_coin_transfer_", "")
        await _request_transfer_proof(query, player, pkg_id, "coin"); return
    if action.startswith("shop_diamond_transfer_"):
        pkg_id = action.replace("shop_diamond_transfer_", "")
        await _request_transfer_proof(query, player, pkg_id, "diamond"); return


# ─── KONFIRMASI BELI ─────────────────────────────────────────────
async def _ask_buy_consumable(query, player: dict, item_id: str):
    item = CONSUMABLES.get(item_id)
    if not item:
        await query.answer("Item tidak ditemukan!", show_alert=True)
        return
    price = item["price"]
    owned = player.get("inventory", {}).get(item_id, 0)
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   🛒  *KONFIRMASI PEMBELIAN*     ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"📦 *{item['name']}*\n"
        f"_{item['desc']}_\n\n"
        f"💰 Harga: *{price:,} Gold*\n"
        f"📦 Dimiliki: *{owned}*\n"
        f"🪙 Gold kamu: *{player.get('coin',0):,}*\n\n"
        f"❓ Yakin ingin membeli?"
    )
    buttons = [
        [
            InlineKeyboardButton("✅ Beli x1", callback_data=f"shop_confirm_cons_{item_id}_qty1"),
            InlineKeyboardButton("✅ Beli x5", callback_data=f"shop_confirm_cons_{item_id}_qty5"),
        ],
        [
            InlineKeyboardButton("✅ Beli x10", callback_data=f"shop_confirm_cons_{item_id}_qty10"),
        ],
        [InlineKeyboardButton("❌ Batal", callback_data="shop_view_consumable")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _ask_buy_equipment(query, player: dict, item_id: str, eq_type: str):
    item = ALL_ITEMS.get(item_id)
    if not item:
        await query.answer("Item tidak ditemukan!", show_alert=True)
        return
    price = item["price"]
    req_level = item.get("req_level", 1)
    stars = RARITY_STARS.get(item.get("rarity", "common"), "⭐")
    stats_txt = ", ".join(f"+{v} {k.upper()}" for k, v in item.get("stats", {}).items())
    level_warn = ""
    if player.get("level", 1) < req_level and not is_admin(player.get("user_id", 0)):
        level_warn = f"\n⚠️ *Butuh Level {req_level}!* (Kamu Lv.{player.get('level',1)})"
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   🛒  *KONFIRMASI PEMBELIAN*     ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"📦 *{item['name']}* {stars}\n"
        f"_{item['desc']}_\n"
        f"📊 Stats: _{stats_txt}_\n"
        f"🔓 Level: *{req_level}+*\n\n"
        f"💰 Harga: *{price:,} Gold*\n"
        f"🪙 Gold kamu: *{player.get('coin',0):,}*{level_warn}\n\n"
        f"❓ Yakin ingin membeli?"
    )
    prefix = "wpn" if eq_type == "weapon" else "arm"
    back_cb = "shop_view_weapon" if eq_type == "weapon" else "shop_view_armor"
    buttons = [
        [InlineKeyboardButton("✅ Ya, Beli!", callback_data=f"shop_confirm_{prefix}_{item_id}")],
        [InlineKeyboardButton("❌ Batal", callback_data=back_cb)],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _ask_buy_skill(query, player: dict, skill_id: str):
    from items import SHOP_SKILLS
    skill = SHOP_SKILLS.get(skill_id)
    if not skill:
        await query.answer("Skill tidak ditemukan!", show_alert=True)
        return
    price = skill["price"]
    req_level = skill.get("req_level", 1)
    stars = RARITY_STARS.get(skill.get("rarity", "rare"), "⭐⭐⭐")
    level_warn = ""
    if player.get("level", 1) < req_level:
        level_warn = f"\n⚠️ *Butuh Level {req_level}!* (Kamu Lv.{player.get('level',1)})"
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   🛒  *KONFIRMASI PEMBELIAN*     ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"🔮 *{skill['name']}* {stars}\n"
        f"_{skill['desc']}_\n"
        f"🔓 Level: *{req_level}+*\n\n"
        f"💰 Harga: *{price:,} Gold*\n"
        f"🪙 Gold kamu: *{player.get('coin',0):,}*{level_warn}\n\n"
        f"❓ Yakin ingin membeli skill ini?"
    )
    buttons = [
        [InlineKeyboardButton("✅ Ya, Beli!", callback_data=f"shop_confirm_skill_{skill_id}")],
        [InlineKeyboardButton("❌ Batal", callback_data="shop_view_skill")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


# ─── VIEWS ──────────────────────────────────────────────────────
async def _show_consumables(query, player: dict):
    text = (
        "╔══════════════════════════════════╗\n"
        "║    🧪  *KONSUMABLE*              ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_gold_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "Beli item untuk membantu di pertempuran:\n"
        "_(Klik item untuk konfirmasi & pilih jumlah)_"
    )
    buttons = []
    for iid, item in CONSUMABLES.items():
        price = item["price"]
        owned = player.get("inventory", {}).get(iid, 0)
        label = f"{item['name']} — {price:,}🪙 (punya:{owned})"
        buttons.append([InlineKeyboardButton(label, callback_data=f"shop_buy_cons_{iid}")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_weapons(query, player: dict):
    char_class = player.get("class", "warrior")
    weapons    = get_class_weapons(char_class)
    equip_wpn  = player.get("equipment", {}).get("weapon")
    player_lv  = player.get("level", 1)

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  ⚔️ *SENJATA {char_class.upper()}*\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_gold_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "Senjata yang tersedia untuk kelasmu:"
    )
    buttons = []
    inv = player.get("inventory", {})
    for iid, item in weapons.items():
        stars    = RARITY_STARS.get(item.get("rarity", "common"), "⭐")
        price    = item["price"]
        req_lv   = item.get("req_level", 1)
        lv_ok    = player_lv >= req_lv or is_admin(query.from_user.id)
        lv_tag   = "" if lv_ok else f" 🔒Lv{req_lv}"
        mark     = "✓" if player.get("coin", 0) >= price and lv_ok else "✗"

        # Jika sedang diequip → tampilkan sebagai "Terpasang", tidak bisa dibeli lagi
        if equip_wpn == iid:
            label = f"✅ {item['name']} {stars} — TERPASANG"
            buttons.append([InlineKeyboardButton(label, callback_data="noop")])
            continue

        # Jika sudah ada di inventory (pernah dibeli sebelumnya) → sembunyikan dari shop
        if inv.get(iid, 0) > 0:
            continue

        label = f"{item['name']} {stars} — {price:,}🪙 {mark}{lv_tag}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"shop_buy_wpn_{iid}")])

    if not buttons:
        buttons.append([InlineKeyboardButton("✅ Semua senjata sudah dimiliki!", callback_data="noop")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_armors(query, player: dict):
    char_class = player.get("class", "warrior")
    armors     = get_class_armors(char_class)
    equip_arm  = player.get("equipment", {}).get("armor")
    player_lv  = player.get("level", 1)

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  🛡️ *ARMOR {char_class.upper()}*\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_gold_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "Armor yang tersedia untuk kelasmu:"
    )
    buttons = []
    inv = player.get("inventory", {})
    for iid, item in armors.items():
        stars    = RARITY_STARS.get(item.get("rarity", "common"), "⭐")
        price    = item["price"]
        req_lv   = item.get("req_level", 1)
        lv_ok    = player_lv >= req_lv or is_admin(query.from_user.id)
        lv_tag   = "" if lv_ok else f" 🔒Lv{req_lv}"
        mark     = "✓" if player.get("coin", 0) >= price and lv_ok else "✗"

        # Jika sedang diequip → tampilkan sebagai "Terpasang", tidak bisa dibeli lagi
        if equip_arm == iid:
            label = f"✅ {item['name']} {stars} — TERPASANG"
            buttons.append([InlineKeyboardButton(label, callback_data="noop")])
            continue

        # Jika sudah ada di inventory (pernah dibeli) → sembunyikan dari shop
        if inv.get(iid, 0) > 0:
            continue

        label = f"{item['name']} {stars} — {price:,}🪙 {mark}{lv_tag}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"shop_buy_arm_{iid}")])

    if not buttons:
        buttons.append([InlineKeyboardButton("✅ Semua armor sudah dimiliki!", callback_data="noop")])
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
    vip = VIP_PACKAGES.get(vip_id)
    if not vip:
        await query.answer("VIP tidak ditemukan!", show_alert=True)
        return
    user_id = query.from_user.id
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
        f"2. ID Telegram kamu: `{user_id}`\n\n"
        "3. Setelah transfer, klik tombol di bawah untuk kirim bukti transfer ke admin\n\n"
        f"_Aktif selama {vip['duration_days']} hari setelah konfirmasi._"
    )
    buttons = [
        [InlineKeyboardButton("📸 Sudah Transfer → Kirim Bukti", callback_data=f"shop_vip_transfer_{vip_id}")],
        [InlineKeyboardButton("⬅️ Kembali ke VIP", callback_data="shop_view_vip")],
        [InlineKeyboardButton("🏠 Menu Toko", callback_data="shop_main")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_coin_packages(query, player: dict):
    user_id = query.from_user.id
    text = (
        "╔══════════════════════════════════╗\n"
        "║    🪙  *TOPUP GOLD*              ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_gold_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "🪙 *Pilih paket Gold yang ingin dibeli:*\n\n"
    )
    buttons = []
    for pid, pkg in COIN_PACKAGES.items():
        gold_amount = pkg.get("gold", pkg.get("amount", 0))
        price = pkg.get("price_idr", 0)
        text += f"🪙 *{pkg['name']}* — Rp {price:,}\n"
        buttons.append([InlineKeyboardButton(
            f"🪙 {pkg['name']}  —  Rp {price:,}",
            callback_data=f"shop_coin_select_{pid}"
        )])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_coin_confirm(query, player: dict, pkg_id: str):
    pkg = COIN_PACKAGES.get(pkg_id)
    if not pkg:
        await query.answer("Paket tidak ditemukan!", show_alert=True)
        return
    user_id = query.from_user.id
    gold_amount = pkg.get("gold", pkg.get("amount", 0))
    price = pkg.get("price_idr", 0)
    text = (
        "╔══════════════════════════════════╗\n"
        "║   🪙  *KONFIRMASI TOPUP GOLD*    ║\n"
        "╚══════════════════════════════════╝\n\n"
        f"📦 Paket  : *{pkg['name']}*\n"
        f"🪙 Gold   : *{gold_amount:,}*\n"
        f"💰 Harga  : *Rp {price:,}*\n\n"
        "💳 *Transfer ke:*\n"
        f"🏦 {pkg.get('bank','')} `{pkg.get('account','')}`\n"
        f"👤 {pkg.get('account_name','')}\n\n"
        f"🆔 ID kamu: `{user_id}`\n\n"
        "_Setelah transfer, klik tombol di bawah untuk mengirim bukti ke admin._"
    )
    buttons = [
        [InlineKeyboardButton(
            f"✅ Beli {pkg['name']} — Rp {price:,}",
            callback_data=f"shop_coin_transfer_{pkg_id}"
        )],
        [
            InlineKeyboardButton("⬅️ Ganti Paket", callback_data="shop_view_coin"),
            InlineKeyboardButton("🏠 Menu", callback_data="shop_main"),
        ],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_diamond_packages(query, player: dict):
    user_id = query.from_user.id

    # Build paket info
    lines = []
    for pid, pkg in DIAMOND_PACKAGES.items():
        diamonds = pkg.get("diamonds", 0)
        price    = pkg.get("price_idr", 0)
        lines.append(f"💎 *{pkg['name']}* — Rp {price:,}")

    pkg_text = "\n".join(lines)
    bank_info = list(DIAMOND_PACKAGES.values())[0]

    text = (
        "╔══════════════════════════════════╗\n"
        "║    💎  *TOPUP DIAMOND*           ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_gold_line(player)}\n"
        "╚══════════════════════════════════╝\n\n"
        "💎 *Pilih paket diamond:*\n\n"
        f"{pkg_text}\n\n"
        "💳 *Info Transfer:*\n"
        f"🏦 {bank_info['bank']} `{bank_info['account']}`\n"
        f"👤 {bank_info['account_name']}\n"
        f"🆔 ID kamu: `{user_id}`\n\n"
        "⬇️ *Klik paket yang ingin dibeli:*"
    )

    # Satu baris per paket → tombol jelas dan langsung klik
    buttons = []
    for pid, pkg in DIAMOND_PACKAGES.items():
        diamonds = pkg.get("diamonds", 0)
        price    = pkg.get("price_idr", 0)
        buttons.append([InlineKeyboardButton(
            f"💎 {diamonds} Diamond  —  Rp {price:,}",
            callback_data=f"shop_diamond_select_{pid}"
        )])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")])

    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_diamond_confirm(query, player: dict, pkg_id: str):
    """Konfirmasi pembelian diamond tertentu."""
    pkg = DIAMOND_PACKAGES.get(pkg_id)
    if not pkg:
        await query.answer("Paket tidak ditemukan!", show_alert=True)
        return

    user_id  = query.from_user.id
    diamonds = pkg.get("diamonds", 0)
    price    = pkg.get("price_idr", 0)

    text = (
        "╔══════════════════════════════════╗\n"
        "║  💎  *KONFIRMASI TOPUP DIAMOND*  ║\n"
        "╚══════════════════════════════════╝\n\n"
        f"📦 Paket   : *{pkg['name']}*\n"
        f"💎 Diamond : *{diamonds}*\n"
        f"💰 Harga   : *Rp {price:,}*\n\n"
        "💳 *Transfer ke:*\n"
        f"🏦 {pkg['bank']} `{pkg['account']}`\n"
        f"👤 {pkg['account_name']}\n\n"
        f"🆔 ID kamu: `{user_id}`\n\n"
        "⚠️ _Setelah transfer, klik tombol di bawah untuk mengirim bukti ke admin._"
    )

    buttons = [
        [InlineKeyboardButton(
            f"✅ Beli {diamonds} Diamond — Rp {price:,}",
            callback_data=f"shop_diamond_transfer_{pkg_id}"
        )],
        [
            InlineKeyboardButton("⬅️ Ganti Paket", callback_data="shop_view_diamond"),
            InlineKeyboardButton("🏠 Menu",        callback_data="shop_main"),
        ],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _request_transfer_proof(query, player: dict, pkg_id: str, pkg_type: str):
    """Instruksi kirim bukti transfer ke admin."""
    user_id = query.from_user.id

    if pkg_type == "vip":
        pkg = VIP_PACKAGES.get(pkg_id, {})
        pkg_name = pkg.get("name", pkg_id)
        bank = pkg.get("bank", "")
        account = pkg.get("account", "")
        account_name = pkg.get("account_name", "")
        amount = f"Rp {pkg.get('price_idr', 0):,}"
    elif pkg_type == "coin":
        pkg = COIN_PACKAGES.get(pkg_id, {})
        pkg_name = pkg.get("name", pkg_id)
        bank = pkg.get("bank", "")
        account = pkg.get("account", "")
        account_name = pkg.get("account_name", "")
        amount = f"Rp {pkg.get('price_idr', 0):,}"
    else:
        pkg = DIAMOND_PACKAGES.get(pkg_id, {})
        pkg_name = pkg.get("name", pkg_id)
        bank = pkg.get("bank", "")
        account = pkg.get("account", "")
        account_name = pkg.get("account_name", "")
        amount = f"Rp {pkg.get('price_idr', 0):,}"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  📸  *KIRIM BUKTI TRANSFER*      ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"📦 Paket: *{pkg_name}*\n"
        f"💰 Nominal: *{amount}*\n\n"
        f"🏦 Rekening Tujuan:\n"
        f"   Bank: *{bank}*\n"
        f"   No: `{account}`\n"
        f"   A/N: *{account_name}*\n\n"
        f"📋 *Cara Kirim Bukti Transfer:*\n"
        f"1. Screenshot bukti transfer kamu\n"
        f"2. Kirim foto tersebut ke admin bot\n"
        f"3. Sertakan pesan:\n"
        f"   `TOPUP {pkg_name}`\n"
        f"   `ID: {user_id}`\n"
        f"   `Nama: {player.get('name', 'unknown')}`\n\n"
        f"👑 *Contact Admin untuk kirim bukti:*\n"
        f"Admin akan memverifikasi dalam 1x24 jam.\n\n"
        f"_Jangan lupa sertakan ID kamu: `{user_id}`_"
    )
    buttons = [
        [InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


# ─── BUY LOGIC ──────────────────────────────────────────────────
async def _buy_consumable(query, player: dict, user_id: int, item_id: str, qty: int = 1):
    item = CONSUMABLES.get(item_id)
    if not item:
        await query.answer("Item tidak ditemukan!", show_alert=True)
        return

    price = item["price"] * qty
    admin = is_admin(user_id)

    if not admin and player.get("coin", 0) < price:
        await query.answer(
            f"❌ Gold tidak cukup! Butuh {price:,}, punya {player.get('coin',0):,}",
            show_alert=True
        )
        return

    if not admin:
        player["coin"] -= price

    inv = player.setdefault("inventory", {})
    inv[item_id] = inv.get(item_id, 0) + qty
    save_player(user_id, player)

    await query.answer(f"✅ {item['name']} x{qty} dibeli! (-{price:,} Gold)", show_alert=True)
    await _show_consumables(query, player)


async def _buy_equipment(query, player: dict, user_id: int, item_id: str, eq_type: str):
    item = ALL_ITEMS.get(item_id)
    if not item:
        await query.answer("Item tidak ditemukan!", show_alert=True)
        return

    item_class = item.get("class")
    if item_class and item_class != player.get("class") and not is_admin(user_id):
        await query.answer("❌ Item ini bukan untuk kelasmu!", show_alert=True)
        return

    # Level check — SSR/UR/GOD tidak perlu level
    req_level = item.get("req_level", 1)
    rarity = item.get("rarity", "")
    is_premium_rarity = rarity in ("SSR", "UR", "GOD")
    if not is_premium_rarity and player.get("level", 1) < req_level and not is_admin(user_id):
        await query.answer(
            f"❌ Butuh Level {req_level}! Kamu masih Lv.{player.get('level',1)}",
            show_alert=True
        )
        return

    price = item["price"]
    admin = is_admin(user_id)

    if not admin and player.get("coin", 0) < price:
        await query.answer(
            f"❌ Gold tidak cukup! Butuh {price:,}🪙, punya {player.get('coin',0):,}🪙",
            show_alert=True
        )
        return

    if not admin:
        player["coin"] -= price

    equip  = player.setdefault("equipment", {})
    old_id = equip.get(eq_type)

    # Jika item yang sama sudah terpasang, tidak perlu proses stat lagi
    if old_id == item_id:
        save_player(user_id, player)
        await query.answer(f"ℹ️ {item['name']} sudah terpasang!", show_alert=True)
        if eq_type == "weapon":
            await _show_weapons(query, player)
        else:
            await _show_armors(query, player)
        return

    # Lepas item lama — item lama TIDAK hilang, masuk inventory
    if old_id:
        old_item = ALL_ITEMS.get(old_id, {})
        for stat, val in old_item.get("stats", {}).items():
            player[stat] = max(1, player.get(stat, 0) - val)
        # Simpan item lama ke inventory
        inv = player.setdefault("inventory", {})
        inv[old_id] = inv.get(old_id, 0) + 1

    # Pasang item baru
    equip[eq_type] = item_id
    # Simpan item baru juga di inventory (increment, bukan overwrite ke 1)
    inv = player.setdefault("inventory", {})
    inv[item_id] = inv.get(item_id, 0) + 1
    for stat, val in item.get("stats", {}).items():
        player[stat] = player.get(stat, 0) + val
        if stat == "max_hp":
            player["hp"] = min(player.get("hp", 1) + val, player["max_hp"])
        if stat == "max_mp":
            player["mp"] = min(player.get("mp", 0) + val, player["max_mp"])

    save_player(user_id, player)
    old_name = ALL_ITEMS.get(old_id, {}).get("name", "") if old_id else ""
    old_txt  = f"\n♻️ {old_name} tersimpan di inventory." if old_name else ""
    await query.answer(f"✅ {item['name']} terpasang permanen!{old_txt}", show_alert=True)

    if eq_type == "weapon":
        await _show_weapons(query, player)
    else:
        await _show_armors(query, player)


# ─── SKILL SHOP ─────────────────────────────────────────────────
async def _show_skills(query, player: dict):
    char_class = player.get("class", "warrior")
    skills     = get_class_skills(char_class)
    bought_raw = player.get("bought_skills", [])
    bought     = {
        (s if isinstance(s, str) else s["id"])
        for s in bought_raw
    }
    player_lv  = player.get("level", 1)

    text = (
        "╔══════════════════════════════════╗\n"
        "║     🔮  *SKILL SHOP*             ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {_gold_line(player)}\n"
        f"║  Kelas: *{char_class.capitalize()}*\n"
        "╚══════════════════════════════════╝\n\n"
        "🔮 Pilih skill untuk dibeli:\n"
        "_(Skill aktif sesuai equipment yang digunakan saat battle)_\n\n"
    )

    buttons = []
    for sid, sk in skills.items():
        stars  = RARITY_STARS.get(sk.get("rarity", "rare"), "⭐⭐⭐")
        price  = sk["price"]
        req_lv = sk.get("req_level", 1)
        lv_ok  = player_lv >= req_lv or is_admin(query.from_user.id)
        lv_tag = "" if lv_ok else f" 🔒Lv{req_lv}"

        # Skill yang sudah dibeli → sembunyikan dari shop
        if sid in bought:
            continue

        mark   = "✓" if player.get("coin", 0) >= price and lv_ok else "✗"
        label  = f"{sk['name']} {stars} — {price:,}🪙 {mark}{lv_tag}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"shop_buy_skill_{sid}")])

    if not buttons:
        buttons.append([InlineKeyboardButton("✅ Semua skill sudah dimiliki!", callback_data="noop")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="shop_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _buy_skill(query, player: dict, user_id: int, skill_id: str):
    from items import SHOP_SKILLS
    skill = SHOP_SKILLS.get(skill_id)
    if not skill:
        await query.answer("Skill tidak ditemukan!", show_alert=True)
        return

    char_class = player.get("class", "warrior")
    if skill.get("class") != char_class and not is_admin(user_id):
        await query.answer("❌ Skill ini bukan untuk kelasmu!", show_alert=True)
        return

    # Level check
    req_level = skill.get("req_level", 1)
    if player.get("level", 1) < req_level and not is_admin(user_id):
        await query.answer(
            f"❌ Butuh Level {req_level}! Kamu masih Lv.{player.get('level',1)}",
            show_alert=True
        )
        return

    bought    = player.setdefault("bought_skills", [])
    # Normalize
    normalized = []
    for entry in bought:
        if isinstance(entry, str):
            sk_data = SHOP_SKILLS.get(entry, {})
            normalized.append({
                "id":     entry,
                "name":   sk_data.get("name", entry),
                "desc":   sk_data.get("desc", ""),
                "effect": sk_data.get("effect", {}),
                "class":  sk_data.get("class", char_class),
            })
        else:
            normalized.append(entry)
    player["bought_skills"] = normalized
    bought = normalized
    owned_ids = [s["id"] for s in bought]
    if skill_id in owned_ids:
        await query.answer("✅ Skill sudah dimiliki!", show_alert=True)
        return

    price = skill["price"]
    admin = is_admin(user_id)
    if not admin and player.get("coin", 0) < price:
        await query.answer(
            f"❌ Gold tidak cukup! Butuh {price:,}🪙, punya {player.get('coin',0):,}🪙",
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
        f"Equip di menu Equipment saat battle.",
        show_alert=True
    )
    await _show_skills(query, player)


# ════════════════════════════════════════════════════════════════
#  PREMIUM SHOP — SSR/UR/GOD + PET + EVOLUTION
# ════════════════════════════════════════════════════════════════
from items import (
    PREMIUM_WEAPONS, PREMIUM_ARMORS, PREMIUM_SKILLS, PET_SHOP,
    EVOLUTION_TIERS, PET_EVOLUTION_TIERS, EVOLUTION_STONE,
    CLASS_SPECIALS, RARITY_STARS,
    get_premium_weapons, get_premium_armors, get_premium_skills,
    get_class_tier_name, get_pet_tier_name
)

RARITY_COLOR = {
    "SSR": "✨", "UR": "💜", "GOD": "🌟",
    "common": "⚪", "uncommon": "🟢", "rare": "🔵",
    "epic": "🟣", "legendary": "🟡"
}


async def premium_shop_handler(update, context):
    """Entry: /premiumshop or button callback"""
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        if hasattr(update, "message") and update.message:
            await update.message.reply_text("❌ Ketik /start dulu!")
        return
    await _show_premium_main(update.message if hasattr(update, "message") and update.message else None,
                             player, edit=False)


async def premium_shop_action_handler(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    player = get_player(user.id)
    if not player:
        await query.answer("❌ Ketik /start!", show_alert=True)
        return

    action = query.data
    char_class = player.get("class", "warrior")

    if action == "pshop_main":
        await _show_premium_main(query, player, edit=True)
        return
    if action == "pshop_weapon":
        await _show_premium_weapons(query, player)
        return
    if action == "pshop_armor":
        await _show_premium_armors(query, player)
        return
    if action == "pshop_skill":
        await _show_premium_skills(query, player)
        return
    if action == "pshop_pet":
        await _show_pet_shop(query, player)
        return
    if action == "pshop_evolution":
        await _show_evolution_info(query, player)
        return
    if action == "pshop_special":
        await _show_class_special(query, player)
        return
    if action.startswith("pshop_evolve_class"):
        await _evolve_class(query, player, user.id)
        return
    if action.startswith("pshop_evolve_pet"):
        await _evolve_pet(query, player, user.id)
        return
    if action.startswith("pshop_buy_pweapon_"):
        item_id = action.replace("pshop_buy_pweapon_", "")
        await _buy_premium_item(query, player, user.id, item_id, "weapon")
        return
    if action.startswith("pshop_buy_parmor_"):
        item_id = action.replace("pshop_buy_parmor_", "")
        await _buy_premium_item(query, player, user.id, item_id, "armor")
        return
    if action.startswith("pshop_buy_pskill_"):
        skill_id = action.replace("pshop_buy_pskill_", "")
        await _buy_premium_skill(query, player, user.id, skill_id)
        return
    if action.startswith("pshop_buy_pet_"):
        pet_id = action.replace("pshop_buy_pet_", "")
        await _buy_pet(query, player, user.id, pet_id)
        return


async def _show_premium_main(target, player: dict, edit: bool = True):
    char_class = player.get("class", "warrior")
    tier = player.get("class_tier", 1)
    tier_info = get_class_tier_name(tier)
    pet_id = player.get("pet")
    pet_tier = player.get("pet_tier", 0)

    text = (
        "╔══════════════════════════════════╗\n"
        "║    💎  *PREMIUM SHOP ETERNITY*   ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  💎 Diamond: *{player.get('diamond', 0)}*\n"
        f"║  🎯 Class: *{char_class.replace('_', ' ').title()}* {tier_info['emoji']} Tier {tier}\n"
        f"║  🐾 Pet: *{'Tidak ada' if not pet_id else pet_id.replace('_',' ').title()}*"
        + (f" {get_pet_tier_name(pet_tier)['emoji']} Tier {pet_tier}" if pet_id else "") + "\n"
        "╚══════════════════════════════════╝\n\n"
        "✨ *Item SSR/UR/GOD dibeli dengan Diamond!*\n"
        "💠 *Evolution Stone* drop dari Boss (0.1% rate)"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Senjata SSR/UR/GOD", callback_data="pshop_weapon"),
         InlineKeyboardButton("🛡️ Armor SSR/UR/GOD", callback_data="pshop_armor")],
        [InlineKeyboardButton("🔮 Skill SSR/UR/GOD", callback_data="pshop_skill"),
         InlineKeyboardButton("🐾 Pet Shop", callback_data="pshop_pet")],
        [InlineKeyboardButton("⚡ Class Special Info", callback_data="pshop_special"),
         InlineKeyboardButton("💠 Evolution System", callback_data="pshop_evolution")],
        [InlineKeyboardButton("🛒 Toko Biasa", callback_data="shop_main")],
    ])
    if edit and hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    elif hasattr(target, "reply_text"):
        await target.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def _show_premium_weapons(query, player: dict):
    char_class = player.get("class", "warrior")
    items = get_premium_weapons(char_class)
    diamond = player.get("diamond", 0)

    lines = [f"⚔️ *SENJATA SSR/UR/GOD — {char_class.replace('_',' ').title()}*\n"
             f"💎 Diamond kamu: *{diamond}*\n"]
    buttons = []
    for item_id, item in items.items():
        rarity = item["rarity"]
        icon = RARITY_COLOR.get(rarity, "")
        owned = item_id in player.get("inventory", {}) or player.get("equipment", {}).get("weapon") == item_id
        owned_tag = " ✅" if owned else ""
        lines.append(
            f"{icon} *{item['name']}*{owned_tag}\n"
            f"  {item['desc']}\n"
            f"  💎 {item['diamond_price']} diamond | Semua Level\n"
        )
        if not owned:
            buttons.append([InlineKeyboardButton(
                f"Beli {rarity} {item['name'][:20]}",
                callback_data=f"pshop_buy_pweapon_{item_id}"
            )])

    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")])
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_premium_armors(query, player: dict):
    char_class = player.get("class", "warrior")
    items = get_premium_armors(char_class)
    diamond = player.get("diamond", 0)

    lines = [f"🛡️ *ARMOR SSR/UR/GOD — {char_class.replace('_',' ').title()}*\n"
             f"💎 Diamond kamu: *{diamond}*\n"]
    buttons = []
    for item_id, item in items.items():
        rarity = item["rarity"]
        icon = RARITY_COLOR.get(rarity, "")
        owned = item_id in player.get("inventory", {}) or player.get("equipment", {}).get("armor") == item_id
        owned_tag = " ✅" if owned else ""
        lines.append(
            f"{icon} *{item['name']}*{owned_tag}\n"
            f"  {item['desc']}\n"
            f"  💎 {item['diamond_price']} diamond | Semua Level\n"
        )
        if not owned:
            buttons.append([InlineKeyboardButton(
                f"Beli {rarity} {item['name'][:20]}",
                callback_data=f"pshop_buy_parmor_{item_id}"
            )])

    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")])
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_premium_skills(query, player: dict):
    char_class = player.get("class", "warrior")
    items = get_premium_skills(char_class)
    diamond = player.get("diamond", 0)

    lines = [f"🔮 *SKILL SSR/UR/GOD — {char_class.replace('_',' ').title()}*\n"
             f"💎 Diamond kamu: *{diamond}*\n"]
    buttons = []
    for skill_id, skill in items.items():
        rarity = skill["rarity"]
        icon = RARITY_COLOR.get(rarity, "")
        owned = skill_id in player.get("bought_skills", [])
        owned_tag = " ✅" if owned else ""
        lines.append(
            f"{icon} *{skill['name']}*{owned_tag}\n"
            f"  {skill['desc']}\n"
            f"  💎 {skill['diamond_price']} diamond | Semua Level\n"
        )
        if not owned:
            buttons.append([InlineKeyboardButton(
                f"Beli {rarity} {skill['name'][:20]}",
                callback_data=f"pshop_buy_pskill_{skill_id}"
            )])

    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")])
    await query.edit_message_text("\n".join(lines), parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_pet_shop(query, player: dict):
    diamond = player.get("diamond", 0)
    coin = player.get("coin", 0)
    current_pet = player.get("pet")

    lines = [
        "🐾 *PET SHOP ETERNITY*\n"
        f"💎 Diamond: *{diamond}* | 🪙 Gold: *{coin:,}*\n"
        f"🐾 Pet sekarang: *{'Tidak ada' if not current_pet else current_pet.replace('_', ' ').title()}*\n"
    ]
    buttons = []
    for pet_id, pet in PET_SHOP.items():
        rarity = pet["rarity"]
        icon = RARITY_COLOR.get(rarity, "⚪")
        owned = current_pet == pet_id
        owned_tag = " (AKTIF ✅)" if owned else ""
        if pet["diamond_price"]:
            price_str = f"💎 {pet['diamond_price']}"
        else:
            price_str = f"🪙 {pet['price']:,}"
        lines.append(
            f"{icon} *{pet['name']}*{owned_tag}\n"
            f"  {pet['desc']}\n"
            f"  🔮 {pet['passive']}\n"
            f"  {price_str} | Tier {pet['tier']}\n"
        )
        if not owned:
            buttons.append([InlineKeyboardButton(
                f"Beli {rarity}: {pet['name'][:22]}",
                callback_data=f"pshop_buy_pet_{pet_id}"
            )])

    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")])
    # Split text if too long
    full_text = "\n".join(lines)
    if len(full_text) > 4000:
        full_text = full_text[:3900] + "\n...(scroll untuk lihat semua)"
    await query.edit_message_text(full_text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_class_special(query, player: dict):
    char_class = player.get("class", "warrior")
    from items import CLASS_SPECIALS
    special = CLASS_SPECIALS.get(char_class, {})
    tier = player.get("class_tier", 1)
    tier_info = get_class_tier_name(tier)

    text = (
        f"⚡ *CLASS SPECIAL — {char_class.replace('_',' ').title()}*\n"
        f"Tier: {tier_info['emoji']} *{tier_info['name']}* (Tier {tier}/10)\n\n"
        f"🌟 *{special.get('name', 'N/A')}*\n"
        f"{special.get('desc', '-')}\n\n"
        f"⚡ *Trigger:* {special.get('trigger', '-')}\n\n"
        f"📋 *STATUS EFFECT SISTEM:*\n"
        f"🔥 Burn — DoT 8 DMG/ronde (2 ronde)\n"
        f"☠️ Poison — DoT 12 DMG/ronde (3 ronde)\n"
        f"⚡ Stun — Skip 1 giliran musuh\n"
        f"❄️ Freeze — Skip 2 giliran musuh\n"
        f"🩸 Bleed — DoT 15 DMG/ronde (3 ronde)\n"
        f"🐌 Slow — SPD musuh -50% (2 ronde)\n"
        f"💜 Curse — DEF musuh -50% (3 ronde)\n"
        f"🛡️ Shield — Damage diterima -40% (3 ronde)\n\n"
        f"💠 *Tingkatkan tier* lewat Evolution System!"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💠 Evolution System", callback_data="pshop_evolution")],
        [InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")],
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def _show_evolution_info(query, player: dict):
    class_tier = player.get("class_tier", 1)
    pet_id = player.get("pet")
    pet_tier = player.get("pet_tier", 0)
    stones = player.get("inventory", {}).get("evolution_stone", 0)

    ct = get_class_tier_name(class_tier)
    next_ct = get_class_tier_name(class_tier + 1) if class_tier < 10 else None
    stones_needed_class = next_ct["evolution_stone_needed"] if next_ct else 0

    pt_text = "Tidak punya pet"
    stones_needed_pet = 0
    can_evolve_pet = False
    if pet_id and pet_tier > 0:
        pt = get_pet_tier_name(pet_tier)
        next_pt = get_pet_tier_name(pet_tier + 1) if pet_tier < 10 else None
        stones_needed_pet = next_pt["evolution_stone_needed"] if next_pt else 0
        can_evolve_pet = (pet_tier < 10 and stones >= stones_needed_pet)
        pt_text = f"{pt['emoji']} *{pt['name']}* (Tier {pet_tier}/10)"

    can_evolve_class = (class_tier < 10 and stones >= stones_needed_class)

    text = (
        "╔══════════════════════════════════╗\n"
        "║   💠  *EVOLUTION SYSTEM*  💠    ║\n"
        "╚══════════════════════════════════╝\n\n"
        f"💠 *Evolution Stone:* {stones} buah\n"
        f"_(Drop dari Boss rate 0.1% — sangat langka!)_\n\n"
        f"⚔️ *CLASS TIER:* {ct['emoji']} Tier {class_tier}/10 — {ct['name']}\n"
        f"  Multiplier Stat: *x{ct['stat_mult']}*\n"
    )
    if next_ct:
        text += (
            f"  → Tier {class_tier+1}: {next_ct['emoji']} {next_ct['name']} (x{next_ct['stat_mult']})\n"
            f"  Butuh: 💠 *{stones_needed_class} Evolution Stone*\n"
        )
    else:
        text += "  ✅ *TIER MAX! GOD TIER TERCAPAI!*\n"

    text += f"\n🐾 *PET TIER:* {pt_text}\n"
    if pet_id and pet_tier < 10:
        next_pt2 = get_pet_tier_name(pet_tier + 1)
        text += (
            f"  → Tier {pet_tier+1}: {next_pt2['emoji']} {next_pt2['name']} (x{next_pt2['stat_mult']})\n"
            f"  Butuh: 💠 *{stones_needed_pet} Evolution Stone*\n"
        )

    text += "\n📋 *TIER LIST (Class/Pet):*\n"
    for tier_num, info in EVOLUTION_TIERS.items():
        text += f"  {info['emoji']} Tier {tier_num}: {info['name']} (x{info['stat_mult']})\n"

    btns = []
    if can_evolve_class:
        btns.append([InlineKeyboardButton(f"⬆️ Evolve Class ke Tier {class_tier+1}!", callback_data="pshop_evolve_class")])
    if can_evolve_pet:
        btns.append([InlineKeyboardButton(f"🐾 Evolve Pet ke Tier {pet_tier+1}!", callback_data="pshop_evolve_pet")])
    btns.append([InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")])

    if len(text) > 4000:
        text = text[:3900]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns))


async def _evolve_class(query, player: dict, user_id: int):
    class_tier = player.get("class_tier", 1)
    if class_tier >= 10:
        await query.answer("✅ Sudah MAX Tier GOD!", show_alert=True)
        return

    next_tier_info = get_class_tier_name(class_tier + 1)
    stones_needed = next_tier_info["evolution_stone_needed"]
    stones = player.get("inventory", {}).get("evolution_stone", 0)

    if stones < stones_needed:
        await query.answer(f"❌ Butuh {stones_needed} Evolution Stone! Kamu punya {stones}.", show_alert=True)
        return

    player["inventory"]["evolution_stone"] = stones - stones_needed
    player["class_tier"] = class_tier + 1

    mult = next_tier_info["stat_mult"] / get_class_tier_name(class_tier)["stat_mult"]
    player["max_hp"] = int(player["max_hp"] * mult)
    player["max_mp"] = int(player["max_mp"] * mult)
    player["atk"]    = int(player["atk"] * mult)
    player["def"]    = int(player["def"] * mult)
    player["spd"]    = int(player["spd"] * mult)
    player["hp"]     = player["max_hp"]
    player["mp"]     = player["max_mp"]

    save_player(user_id, player)
    await query.edit_message_text(
        f"🎊 *EVOLUTION BERHASIL!*\n\n"
        f"⬆️ Class naik ke Tier *{class_tier+1}* — {next_tier_info['emoji']} *{next_tier_info['name']}*\n"
        f"✨ Semua stat ditingkatkan x{next_tier_info['stat_mult']}!\n"
        f"💠 Sisa Evolution Stone: {player['inventory']['evolution_stone']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")]])
    )


async def _evolve_pet(query, player: dict, user_id: int):
    pet_id = player.get("pet")
    pet_tier = player.get("pet_tier", 0)

    if not pet_id:
        await query.answer("❌ Kamu belum punya pet!", show_alert=True)
        return
    if pet_tier >= 10:
        await query.answer("✅ Pet sudah MAX Tier LEGENDARY!", show_alert=True)
        return

    next_tier_info = get_pet_tier_name(pet_tier + 1)
    stones_needed = next_tier_info["evolution_stone_needed"]
    stones = player.get("inventory", {}).get("evolution_stone", 0)

    if stones < stones_needed:
        await query.answer(f"❌ Butuh {stones_needed} Evolution Stone! Kamu punya {stones}.", show_alert=True)
        return

    player["inventory"]["evolution_stone"] = stones - stones_needed
    player["pet_tier"] = pet_tier + 1
    save_player(user_id, player)

    await query.edit_message_text(
        f"🎊 *PET EVOLUTION BERHASIL!*\n\n"
        f"🐾 Pet naik ke Tier *{pet_tier+1}* — {next_tier_info['emoji']} *{next_tier_info['name']}*\n"
        f"✨ Stat pet x{next_tier_info['stat_mult']}!\n"
        f"💠 Sisa Evolution Stone: {player['inventory']['evolution_stone']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")]])
    )


async def _buy_premium_item(query, player: dict, user_id: int, item_id: str, eq_type: str):
    from items import ALL_ITEMS
    item = ALL_ITEMS.get(item_id)
    if not item:
        await query.answer("❌ Item tidak ditemukan!", show_alert=True)
        return

    cost = item.get("diamond_price", 0)
    diamond = player.get("diamond", 0)

    if diamond < cost:
        await query.answer(f"❌ Diamond tidak cukup! Butuh {cost}, kamu punya {diamond}.", show_alert=True)
        return

    # SSR/UR/GOD tidak membutuhkan level — semua bisa beli!
    # Level check dihapus untuk premium items

    player["diamond"] -= cost
    inv = player.setdefault("inventory", {})
    inv[item_id] = inv.get(item_id, 0) + 1
    save_player(user_id, player)

    await query.edit_message_text(
        f"✅ *Berhasil membeli!*\n\n"
        f"{item['name']}\n"
        f"{item['desc']}\n\n"
        f"💎 Diamond tersisa: {player['diamond']}\n\n"
        f"_Equip di /equipment_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")]])
    )


async def _buy_premium_skill(query, player: dict, user_id: int, skill_id: str):
    skill = PREMIUM_SKILLS.get(skill_id)
    if not skill:
        await query.answer("❌ Skill tidak ditemukan!", show_alert=True)
        return

    cost = skill.get("diamond_price", 0)
    if player.get("diamond", 0) < cost:
        await query.answer(f"❌ Diamond kurang! Butuh {cost}.", show_alert=True)
        return

    # Cek apakah skill sudah dimiliki (handle both str and dict entries)
    bought_ids = []
    for s in player.get("bought_skills", []):
        bought_ids.append(s if isinstance(s, str) else s.get("id", ""))
    if skill_id in bought_ids:
        await query.answer("❌ Skill sudah dimiliki!", show_alert=True)
        return

    player["diamond"] -= cost
    if "bought_skills" not in player:
        player["bought_skills"] = []
    # Simpan sebagai dict agar konsisten dengan format lain
    player["bought_skills"].append({"id": skill_id, "name": skill.get("name", skill_id)})
    save_player(user_id, player)

    await query.edit_message_text(
        f"✅ *Skill berhasil dibeli!*\n\n"
        f"🔮 *{skill['name']}*\n"
        f"{skill['desc']}\n\n"
        f"💎 Diamond tersisa: {player['diamond']}\n"
        f"_Equip di /equipment_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")]])
    )


async def _buy_pet(query, player: dict, user_id: int, pet_id: str):
    pet = PET_SHOP.get(pet_id)
    if not pet:
        await query.answer("❌ Pet tidak ditemukan!", show_alert=True)
        return

    if player.get("pet") == pet_id:
        await query.answer("❌ Pet ini sudah aktif!", show_alert=True)
        return

    if pet.get("diamond_price"):
        cost = pet["diamond_price"]
        if player.get("diamond", 0) < cost:
            await query.answer(f"❌ Diamond kurang! Butuh {cost}.", show_alert=True)
            return
        player["diamond"] -= cost
    else:
        cost = pet["price"]
        if player.get("coin", 0) < cost:
            await query.answer(f"❌ Gold kurang! Butuh {cost:,}.", show_alert=True)
            return
        player["coin"] -= cost

    player["pet"] = pet_id
    player["pet_tier"] = pet.get("tier", 1)
    save_player(user_id, player)

    await query.edit_message_text(
        f"🐾 *Pet berhasil dibeli & diaktifkan!*\n\n"
        f"{pet['name']}\n"
        f"{pet['desc']}\n\n"
        f"🔮 *Passive:* {pet['passive']}\n\n"
        f"Pet akan memberikan bonus saat battle!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali ke Toko", callback_data="shop_main")]])
    )

