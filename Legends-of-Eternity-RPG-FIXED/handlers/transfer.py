import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, get_all_players
from items import get_item, ALL_ITEMS, SHOP_SKILLS, PREMIUM_SKILLS, GOD_SSSR_SKILLS, PET_SHOP, GOD_SSSR_PETS


TRANSFER_LIMIT = 3      # max per week
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
        item_key = action[len("transfer_item_"):]
        context.user_data["transfer_item"] = item_key
        await _ask_recipient(query, item_key, player)
        return

    if action.startswith("transfer_to_"):
        # Format: transfer_to_{target_id}__k__{item_key}
        raw = action[len("transfer_to_"):]
        sep = raw.find("__k__")
        if sep == -1:
            await query.answer("❌ Data tidak valid!", show_alert=True)
            return
        target_id = int(raw[:sep])
        item_key  = raw[sep + 5:]
        # Fallback jika item_key terlalu panjang dan disimpan di context
        if item_key == "ctx":
            item_key = context.user_data.pop(f"transfer_key_{target_id}", "")
            if not item_key:
                await query.answer("❌ Data sesi habis, coba lagi!", show_alert=True)
                return
        await _confirm_transfer(query, player, user.id, target_id, item_key)
        return


async def _show_transfer_menu(target, player: dict, user_id: int, is_msg=False):
    now   = time.time()
    reset = player.get("transfer_week_reset", now)
    if now - reset > WEEK_SECONDS:
        player["transfer_weekly"]     = 0
        player["transfer_week_reset"] = now
        save_player(user_id, player)

    used       = player.get("transfer_weekly", 0)
    remain     = max(0, TRANSFER_LIMIT - used)
    days_reset = max(0, int((reset + WEEK_SECONDS - now) / 86400))

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   📦  *TRANSFER ITEM*            ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🔁 Sisa Transfer: *{remain}/{TRANSFER_LIMIT}* minggu ini\n"
        f"║  🔄 Reset dalam: {days_reset} hari\n"
        f"╠══════════════════════════════════╣\n"
        f"║  Item yang bisa ditransfer:\n"
        f"║  ⚔️ Senjata  🛡️ Armor  🔮 Skill\n"
        f"║  💠 Evolution Stone\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Transfer item ke pemain lain max *{TRANSFER_LIMIT}x per minggu*.\n\n"
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
    inv   = player.get("inventory", {})
    text  = (
        f"╔══════════════════════════════════╗\n"
        f"║  📤  *PILIH ITEM UNTUK DIKIRIM*  ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih item yang ingin dikirim ke pemain lain:"
    )
    buttons = []

    # Senjata
    wpn_id = equip.get("weapon")
    if wpn_id:
        item = get_item(wpn_id)
        if item:
            buttons.append([InlineKeyboardButton(
                f"⚔️ {item['name']}",
                callback_data=f"transfer_item_weapon__{wpn_id}"
            )])

    # Armor
    arm_id = equip.get("armor")
    if arm_id:
        item = get_item(arm_id)
        if item:
            buttons.append([InlineKeyboardButton(
                f"🛡️ {item['name']}",
                callback_data=f"transfer_item_armor__{arm_id}"
            )])

    # Skill (bought_skills)
    for entry in player.get("bought_skills", []):
        skill_id = entry.get("id", "") if isinstance(entry, dict) else entry
        skill = SHOP_SKILLS.get(skill_id) or PREMIUM_SKILLS.get(skill_id) or GOD_SSSR_SKILLS.get(skill_id)
        if skill:
            buttons.append([InlineKeyboardButton(
                f"🔮 {skill['name']}",
                callback_data=f"transfer_item_skill__{skill_id}"
            )])

    # Evolution Stone
    evo_count = inv.get("evolution_stone", 0)
    if evo_count > 0:
        buttons.append([InlineKeyboardButton(
            f"💠 Evolution Stone (punya: {evo_count})",
            callback_data=f"transfer_item_evo_stone__1"
        )])

    if not buttons:
        text += "\n\n❌ Tidak ada item yang bisa ditransfer."
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="transfer_menu")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _ask_recipient(query, item_key: str, player: dict):
    # Parse item_key: "type__id"
    parts = item_key.split("__", 1)
    item_type = parts[0]
    item_id   = parts[1] if len(parts) > 1 else ""

    item_name = _get_item_name(item_type, item_id, player)
    players = get_all_players()

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  👤  *PILIH PENERIMA*            ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Item: *{item_name}*\n\n"
        f"Pilih pemain penerima:\n"
        f"_(Tampil 10 pemain terakhir aktif)_"
    )
    buttons = []
    count = 0
    for uid, p in players.items():
        if int(uid) == query.from_user.id:
            continue
        cb = f"transfer_to_{uid}__k__{item_key}"
        if len(cb) > 64:
            # item_key terlalu panjang, simpan ke context dan gunakan placeholder
            context.user_data[f"transfer_key_{uid}"] = item_key
            cb = f"transfer_to_{uid}__k__ctx"
        buttons.append([InlineKeyboardButton(
            f"{p['emoji']} {p['name']} Lv.{p['level']} ({p['class']})",
            callback_data=cb
        )])
        count += 1
        if count >= 10:
            break

    if not buttons:
        text += "\n\n❌ Tidak ada pemain lain yang ditemukan."

    buttons.append([InlineKeyboardButton("⬅️ Batal", callback_data="transfer_send")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


def _get_item_name(item_type: str, item_id: str, player: dict) -> str:
    if item_type == "weapon":
        item = get_item(item_id)
        return item["name"] if item else item_id
    elif item_type == "armor":
        item = get_item(item_id)
        return item["name"] if item else item_id
    elif item_type == "skill":
        skill = SHOP_SKILLS.get(item_id) or PREMIUM_SKILLS.get(item_id) or GOD_SSSR_SKILLS.get(item_id)
        return skill["name"] if skill else item_id
    elif item_type == "evo_stone":
        return "💠 Evolution Stone"
    return item_id


async def _confirm_transfer(query, player: dict, user_id: int, target_id: int, item_key: str):
    now   = time.time()
    reset = player.get("transfer_week_reset", now)
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

    parts     = item_key.split("__", 1)
    item_type = parts[0]
    item_id   = parts[1] if len(parts) > 1 else ""

    equip = player.setdefault("equipment", {})
    inv   = player.setdefault("inventory", {})
    t_equip = target_player.setdefault("equipment", {})
    t_inv   = target_player.setdefault("inventory", {})

    item_name = _get_item_name(item_type, item_id, player)

    # ── Weapon ───────────────────────────────────────────────────
    if item_type == "weapon":
        item = get_item(item_id)
        if not item or equip.get("weapon") != item_id:
            await query.answer("❌ Senjata tidak ditemukan!", show_alert=True)
            return
        for stat, val in item.get("stats", {}).items():
            player[stat] = max(1, player.get(stat, 0) - val)
        equip["weapon"] = None
        # Remove enhance level
        player.setdefault("enhance_levels", {}).pop("weapon", None)

        old = t_equip.get("weapon")
        if old:
            old_item = ALL_ITEMS.get(old, {})
            for s, v in old_item.get("stats", {}).items():
                target_player[s] = max(1, target_player.get(s, 0) - v)
        t_equip["weapon"] = item_id
        for s, v in item.get("stats", {}).items():
            target_player[s] = target_player.get(s, 0) + v

    # ── Armor ────────────────────────────────────────────────────
    elif item_type == "armor":
        item = get_item(item_id)
        if not item or equip.get("armor") != item_id:
            await query.answer("❌ Armor tidak ditemukan!", show_alert=True)
            return
        for stat, val in item.get("stats", {}).items():
            player[stat] = max(1, player.get(stat, 0) - val)
        equip["armor"] = None
        player.setdefault("enhance_levels", {}).pop("armor", None)

        old = t_equip.get("armor")
        if old:
            old_item = ALL_ITEMS.get(old, {})
            for s, v in old_item.get("stats", {}).items():
                target_player[s] = max(1, target_player.get(s, 0) - v)
        t_equip["armor"] = item_id
        for s, v in item.get("stats", {}).items():
            target_player[s] = target_player.get(s, 0) + v

    # ── Skill ────────────────────────────────────────────────────
    elif item_type == "skill":
        bought = player.get("bought_skills", [])
        ids = [(s.get("id") if isinstance(s, dict) else s) for s in bought]
        if item_id not in ids:
            await query.answer("❌ Skill tidak ditemukan!", show_alert=True)
            return
        player["bought_skills"] = [
            s for s in bought
            if (s.get("id") if isinstance(s, dict) else s) != item_id
        ]
        if equip.get("skill") == item_id:
            equip["skill"] = None
        player.setdefault("enhance_levels", {}).pop("skill", None)
        # Give to target
        t_bought = target_player.setdefault("bought_skills", [])
        t_ids = [(s.get("id") if isinstance(s, dict) else s) for s in t_bought]
        if item_id not in t_ids:
            skill = SHOP_SKILLS.get(item_id) or PREMIUM_SKILLS.get(item_id) or GOD_SSSR_SKILLS.get(item_id)
            t_bought.append({"id": item_id, "name": skill.get("name", item_id) if skill else item_id})

    # ── Evolution Stone ──────────────────────────────────────────
    elif item_type == "evo_stone":
        evo_count = inv.get("evolution_stone", 0)
        if evo_count <= 0:
            await query.answer("❌ Evolution Stone tidak cukup!", show_alert=True)
            return
        inv["evolution_stone"] = evo_count - 1
        t_inv["evolution_stone"] = t_inv.get("evolution_stone", 0) + 1
        item_name = "💠 Evolution Stone"

    else:
        await query.answer("❌ Tipe item tidak dikenal!", show_alert=True)
        return

    player["transfer_weekly"] = used + 1
    save_player(user_id, player)
    save_player(target_id, target_player)

    remain = TRANSFER_LIMIT - player["transfer_weekly"]
    await query.edit_message_text(
        f"✅ *Transfer berhasil!*\n\n"
        f"📦 *{item_name}* dikirim ke *{target_player['name']}*\n"
        f"🔁 Sisa transfer minggu ini: {remain}/{TRANSFER_LIMIT}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📦 Transfer Lagi", callback_data="transfer_menu")
        ]])
    )
