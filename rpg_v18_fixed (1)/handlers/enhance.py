"""
Enhance System — Legends of Eternity RPG
Enhance weapon, armor, skill, special, pet menggunakan Diamond.
Level enhance: +1 sampai +10. Setiap level meningkatkan stat.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, save_player
from items import get_item, ALL_ITEMS

# ─── CONFIG ──────────────────────────────────────────────────────
ENHANCE_COSTS = {
    1: 2,    # +1 → +2
    2: 4,    # +2 → +3
    3: 7,    # +3 → +4
    4: 12,   # +4 → +5
    5: 18,   # +5 → +6
    6: 28,   # +6 → +7
    7: 40,   # +7 → +8
    8: 60,   # +8 → +9
    9: 90,   # +9 → +10
    10: 0,   # Max
}

# Success rate per level
ENHANCE_SUCCESS = {
    1: 100, 2: 95, 3: 90, 4: 80, 5: 70,
    6: 60,  7: 50, 8: 40, 9: 30, 10: 0,
}

# Stat bonus per enhance level (multiplier on base stats)
ENHANCE_BONUS_PCT = {
    1: 0.05, 2: 0.10, 3: 0.16, 4: 0.23, 5: 0.32,
    6: 0.42, 7: 0.54, 8: 0.68, 9: 0.84, 10: 1.00,
}

ENHANCE_EMOJI = ["", "⬆️", "✨", "💫", "🌟", "⚡", "🔥", "💥", "🌈", "👑", "🔱"]


def get_enhance_level(player: dict, slot: str) -> int:
    return player.get("enhance_levels", {}).get(slot, 0)


def set_enhance_level(player: dict, slot: str, level: int) -> dict:
    if "enhance_levels" not in player:
        player["enhance_levels"] = {}
    player["enhance_levels"][slot] = level
    return player


def enhance_stat_bonus(base_stat: int, enhance_lv: int) -> int:
    if enhance_lv <= 0:
        return 0
    pct = ENHANCE_BONUS_PCT.get(enhance_lv, 0)
    return int(base_stat * pct)


# ─── HANDLER ─────────────────────────────────────────────────────
async def enhance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    await _show_enhance_main(update.message, player, user.id)


async def enhance_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        await query.answer("❌ Ketik /start!", show_alert=True)
        return

    if action == "enhance_main":
        await _show_enhance_main(query, player, user.id, edit=True)
        return

    if action.startswith("enhance_view_"):
        slot = action.replace("enhance_view_", "")
        await _show_enhance_slot(query, player, user.id, slot)
        return

    if action.startswith("enhance_do_"):
        slot = action.replace("enhance_do_", "")
        await _do_enhance(query, player, user.id, slot)
        return


async def _show_enhance_main(target, player: dict, user_id: int, edit: bool = False):
    diamond = player.get("diamond", 0)

    equip = player.get("equipment", {})
    wpn_id = equip.get("weapon")
    arm_id = equip.get("armor")
    pet_id = player.get("pet")

    wpn_lv  = get_enhance_level(player, "weapon")
    arm_lv  = get_enhance_level(player, "armor")
    skl_lv  = get_enhance_level(player, "skill")
    spc_lv  = get_enhance_level(player, "special")
    pet_lv  = get_enhance_level(player, "pet")

    wpn_name = (get_item(wpn_id) or {}).get("name", "─ Tidak ada") if wpn_id else "─ Tidak ada"
    arm_name = (get_item(arm_id) or {}).get("name", "─ Tidak ada") if arm_id else "─ Tidak ada"

    e = ENHANCE_EMOJI

    text = (
        "╔══════════════════════════════════╗\n"
        "║     ⚒️  *SISTEM ENHANCE*  ⚒️     ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  💎 Diamond: *{diamond}*\n"
        "╠══════════════════════════════════╣\n"
        f"║  ⚔️ Senjata: *{wpn_name}*  {e[wpn_lv]}+{wpn_lv}\n"
        f"║  🛡️ Armor: _{arm_name}_  {e[arm_lv]}+{arm_lv}\n"
        f"║  🔮 Skill: Level {skl_lv}/10  {e[skl_lv]}+{skl_lv}\n"
        f"║  ⚡ Special: Level {spc_lv}/10  {e[spc_lv]}+{spc_lv}\n"
        f"║  🐾 Pet: Level {pet_lv}/10  {e[pet_lv]}+{pet_lv}\n"
        "╠══════════════════════════════════╣\n"
        "║  Enhance meningkatkan stat item!\n"
        "║  Biaya: Diamond 💎\n"
        "╚══════════════════════════════════╝"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Enhance Senjata",  callback_data="enhance_view_weapon"),
         InlineKeyboardButton("🛡️ Enhance Armor",    callback_data="enhance_view_armor")],
        [InlineKeyboardButton("🔮 Enhance Skill",    callback_data="enhance_view_skill"),
         InlineKeyboardButton("⚡ Enhance Special",   callback_data="enhance_view_special")],
        [InlineKeyboardButton("🐾 Enhance Pet",      callback_data="enhance_view_pet")],
        [InlineKeyboardButton("🏠 Menu",             callback_data="menu")],
    ])
    if edit and hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        fn = target.reply_text if hasattr(target, "reply_text") else target.edit_message_text
        await fn(text, parse_mode="Markdown", reply_markup=keyboard)


async def _show_enhance_slot(query, player: dict, user_id: int, slot: str):
    import random

    slot_info = {
        "weapon":  ("⚔️", "Senjata",  "weapon"),
        "armor":   ("🛡️", "Armor",    "armor"),
        "skill":   ("🔮", "Skill",    None),
        "special": ("⚡", "Special",  None),
        "pet":     ("🐾", "Pet",      None),
    }
    icon, name, eq_key = slot_info.get(slot, ("❓", slot, None))

    current_lv = get_enhance_level(player, slot)
    diamond    = player.get("diamond", 0)

    if current_lv >= 10:
        status_text = "🔱 *MAX LEVEL! Enhance penuh!*"
        cost_text   = "—"
        can_enhance = False
    else:
        cost        = ENHANCE_COSTS.get(current_lv, 0)
        success_pct = ENHANCE_SUCCESS.get(current_lv, 0)
        status_text = (
            f"Enhance Berikutnya: +{current_lv} → +{current_lv+1}\n"
            f"💎 Biaya: *{cost} Diamond*\n"
            f"✅ Tingkat sukses: *{success_pct}%*"
        )
        cost_text   = f"{cost} Diamond"
        can_enhance = diamond >= cost

    # Show stat bonus
    bonus_lines = []
    if slot == "weapon":
        eq_id = player.get("equipment", {}).get("weapon")
        if eq_id:
            item = get_item(eq_id)
            if item:
                for stat, val in item.get("stats", {}).items():
                    bonus = enhance_stat_bonus(val, current_lv)
                    bonus_lines.append(f"+{bonus} {stat.upper().replace('MAX_','MAX ')}")
    elif slot == "armor":
        eq_id = player.get("equipment", {}).get("armor")
        if eq_id:
            item = get_item(eq_id)
            if item:
                for stat, val in item.get("stats", {}).items():
                    bonus = enhance_stat_bonus(val, current_lv)
                    bonus_lines.append(f"+{bonus} {stat.upper().replace('MAX_','MAX ')}")
    elif slot == "skill":
        base_bonus = player.get("atk", 0) // 5
        bonus_lines.append(f"+{enhance_stat_bonus(base_bonus, current_lv)} ATK saat pakai skill")
    elif slot == "special":
        base_bonus = player.get("max_mp", 0) // 5
        bonus_lines.append(f"+{enhance_stat_bonus(base_bonus, current_lv)} efek special")
    elif slot == "pet":
        base_bonus = 5
        bonus_lines.append(f"+{enhance_stat_bonus(base_bonus, current_lv)}% bonus pet")

    e = ENHANCE_EMOJI
    bonus_str = ", ".join(bonus_lines) if bonus_lines else "Belum ada item"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {icon} *ENHANCE {name.upper()}*\n"
        f"╠══════════════════════════════════╣\n"
        f"║  Level Saat Ini: {e[current_lv]} *+{current_lv}*\n"
        f"║  Bonus Saat Ini: _{bonus_str}_\n"
        f"╠══════════════════════════════════╣\n"
        f"║  {status_text}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  💎 Diamond kamu: *{diamond}*\n"
        f"╚══════════════════════════════════╝"
    )

    btns = []
    if can_enhance and current_lv < 10:
        btns.append([InlineKeyboardButton(f"⚒️ ENHANCE {name} → +{current_lv+1}", callback_data=f"enhance_do_{slot}")])
    elif not can_enhance and current_lv < 10:
        cost = ENHANCE_COSTS.get(current_lv, 0)
        btns.append([InlineKeyboardButton(f"❌ Diamond kurang (butuh {cost})", callback_data="enhance_main")])
    btns.append([InlineKeyboardButton("⬅️ Kembali", callback_data="enhance_main")])

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns))


async def _do_enhance(query, player: dict, user_id: int, slot: str):
    import random

    current_lv = get_enhance_level(player, slot)
    if current_lv >= 10:
        await query.answer("❌ Sudah MAX level!", show_alert=True)
        return

    cost        = ENHANCE_COSTS.get(current_lv, 0)
    success_pct = ENHANCE_SUCCESS.get(current_lv, 100)
    diamond     = player.get("diamond", 0)

    if diamond < cost:
        await query.answer(f"❌ Diamond tidak cukup! Butuh {cost}.", show_alert=True)
        return

    player["diamond"] -= cost
    roll = random.randint(1, 100)
    success = roll <= success_pct

    slot_names = {
        "weapon": "⚔️ Senjata", "armor": "🛡️ Armor",
        "skill": "🔮 Skill", "special": "⚡ Special", "pet": "🐾 Pet"
    }
    e = ENHANCE_EMOJI

    if success:
        new_lv = current_lv + 1
        player = set_enhance_level(player, slot, new_lv)
        save_player(user_id, player)

        result = (
            f"🎉 *ENHANCE BERHASIL!*\n\n"
            f"{slot_names.get(slot, slot)}: {e[current_lv]}+{current_lv} → {e[new_lv]}+{new_lv}\n\n"
            f"💎 Diamond tersisa: *{player['diamond']}*"
        )
        if new_lv == 10:
            result += "\n\n🔱 *MAX ENHANCE TERCAPAI! LUAR BIASA!*"
    else:
        save_player(user_id, player)
        result = (
            f"💔 *ENHANCE GAGAL!*\n\n"
            f"{slot_names.get(slot, slot)} tetap di {e[current_lv]}+{current_lv}\n"
            f"_(Diamond tetap terpotong)_\n\n"
            f"💎 Diamond tersisa: *{player['diamond']}*"
        )

    await query.edit_message_text(
        result,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚒️ Enhance Lagi", callback_data=f"enhance_view_{slot}")],
            [InlineKeyboardButton("⬅️ Menu Enhance",  callback_data="enhance_main")],
        ])
    )
