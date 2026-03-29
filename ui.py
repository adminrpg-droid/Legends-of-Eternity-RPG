import time
from items import get_item, RARITY_STARS


def hp_bar(current: int, max_val: int, length: int = 10) -> str:
    if max_val <= 0:
        return "░" * length
    ratio  = max(0, min(1, current / max_val))
    filled = int(ratio * length)
    return f"`{'█'*filled}{'░'*(length-filled)}` {current}/{max_val} ({int(ratio*100)}%)"


def exp_bar(current: int, needed: int, length: int = 10) -> str:
    if needed <= 0:
        return "█" * length
    ratio  = max(0, min(1, current / needed))
    filled = int(ratio * length)
    return f"`{'▓'*filled}{'░'*(length-filled)}` {current}/{needed}"


def vip_badge(player: dict) -> str:
    if not player.get("vip", {}).get("active"):
        return ""
    badges = {"vip_silver": " 🥈VIP", "vip_gold": " 🥇VIP", "vip_diamond": " 💎VIP"}
    return badges.get(player["vip"].get("tier", ""), "")


def format_profile(player: dict, telegram_id: int = None, viewer_id: int = None) -> str:
    from database import is_admin
    from handlers.title import ALL_TITLES
    vip         = vip_badge(player)
    gender_icon = "♀️" if player.get("gender") == "female" else "♂️"
    uid         = telegram_id or player.get("telegram_id", player.get("user_id", "?"))

    # Title
    active_title_id = player.get("active_title", "newcomer")
    t_data   = ALL_TITLES.get(active_title_id, {})
    title_line = f"\n║  {t_data.get('emoji','🏅')} Title: *{t_data.get('name','Pendatang Baru')}*" if t_data else ""

    equip      = player.get("equipment", {})
    weapon_id  = equip.get("weapon") or ""
    armor_id   = equip.get("armor") or ""
    skill_id   = equip.get("skill") or ""
    wpn_item   = get_item(weapon_id) if weapon_id else {}
    arm_item   = get_item(armor_id) if armor_id else {}

    def _rarity_badge(item: dict) -> str:
        r = item.get("rarity","")
        if r == "GOD SSSR": return " 🔱[GOD SSSR]"
        if r == "GOD":      return " 🌟[GOD]"
        if r == "UR":       return " 💜[UR]"
        if r == "SSR":      return " 💎[SSR]"
        if r == "legendary":return " ⭐⭐⭐⭐⭐"
        return ""

    # Enhance levels
    enh_levels  = player.get("enhance_levels", {})
    wpn_enh_lv  = enh_levels.get("weapon", 0)
    arm_enh_lv  = enh_levels.get("armor", 0)
    skl_enh_lv  = enh_levels.get("skill", 0)
    _enh_emoji  = ["","⬆️","✨","💫","🌟","⚡","🔥","💥","🌈","👑","🔱"]
    def _enh_tag(lv): return f" {_enh_emoji[lv]}+{lv}" if lv > 0 else ""

    weapon_str = (wpn_item.get("name","─ Kosong") + _rarity_badge(wpn_item) + _enh_tag(wpn_enh_lv)) if wpn_item else "─ Kosong"
    armor_str  = (arm_item.get("name","─ Kosong") + _rarity_badge(arm_item) + _enh_tag(arm_enh_lv)) if arm_item else "─ Kosong"

    # Active skill badge
    from items import SHOP_SKILLS, PREMIUM_SKILLS, GOD_SSSR_SKILLS
    skill_item = SHOP_SKILLS.get(skill_id) or PREMIUM_SKILLS.get(skill_id) or GOD_SSSR_SKILLS.get(skill_id) if skill_id else None
    skill_badge = _rarity_badge(skill_item) if skill_item else ""
    skill_name  = (skill_item.get("name","") + skill_badge + _enh_tag(skl_enh_lv)) if skill_item else "─ Default"

    # Pet badge
    from items import PET_SHOP, GOD_SSSR_PETS
    pet_id2   = player.get("pet")
    pet_item2 = (PET_SHOP.get(pet_id2) or GOD_SSSR_PETS.get(pet_id2)) if pet_id2 else None
    pet_badge = _rarity_badge(pet_item2) if pet_item2 else ""

    vip_line = ""
    if player.get("vip", {}).get("active"):
        tier      = player["vip"].get("tier", "")
        days_left = max(0, int((player["vip"].get("expires", 0) - time.time()) / 86400))
        tnames    = {"vip_silver": "🥈 Silver", "vip_gold": "🥇 Gold", "vip_diamond": "💎 Diamond"}
        vip_line  = f"\n║  {tnames.get(tier,'VIP')} — Sisa {days_left} hari"

    admin_badge = " 👑ADMIN" if is_admin(uid) else ""
    crit        = player.get("crit", 10)

    if viewer_id and viewer_id != uid:
        header = f"║  {player['emoji']} *PROFIL {player['name'].upper()}*{vip}{admin_badge}"
    else:
        header = f"║  {player['emoji']} *PROFIL KARAKTER*{vip}{admin_badge}"

    skills_line = ""
    bought = player.get("bought_skills", [])
    if bought:
        names = []
        for s in bought[:3]:
            names.append(s["name"] if isinstance(s, dict) else s)
        skills_line = f"\n║  🔮 Skill: {', '.join(names)}"

    # Class tier & pet lines
    from items import EVOLUTION_TIERS, PET_EVOLUTION_TIERS, PET_SHOP, CLASS_SPECIALS
    class_tier = player.get("class_tier", 1)
    tier_info  = EVOLUTION_TIERS.get(class_tier, EVOLUTION_TIERS[1])
    tier_line  = f"\n║  {tier_info['emoji']} Tier: *{tier_info['name']}* ({class_tier}/10)"

    pet_id   = player.get("pet")
    pet_line = ""
    if pet_id:
        pet      = PET_SHOP.get(pet_id, {}) or GOD_SSSR_PETS.get(pet_id, {})
        pet_tier = player.get("pet_tier", 1)
        ptinfo   = PET_EVOLUTION_TIERS.get(pet_tier, PET_EVOLUTION_TIERS[1])
        pet_r    = pet.get("rarity","")
        if pet_r == "GOD SSSR": pet_badge2 = " 🔱[GOD SSSR]"
        elif pet_r == "GOD":    pet_badge2 = " 🌟[GOD]"
        elif pet_r == "UR":     pet_badge2 = " 💜[UR]"
        elif pet_r == "SSR":    pet_badge2 = " 💎[SSR]"
        else:                   pet_badge2 = ""
        pet_line = f"\n║  🐾 Pet: *{pet.get('name', pet_id)}*{pet_badge2} {ptinfo['emoji']} T{pet_tier}"

    char_class = player.get("class", "warrior")
    special    = CLASS_SPECIALS.get(char_class, {})
    special_line = ""
    if special:
        special_line = f"\n║  ⚡ Special: _{special.get('name','')}_"

    evo_stones = player.get("inventory", {}).get("evolution_stone", 0)
    stone_line = f"\n║  💠 Evo Stone: *{evo_stones}*" if evo_stones else ""

    rest_line = "\n║  😴 *Sedang Istirahat...*" if player.get("is_resting") else ""

    pvp       = player.get("pvp_stats", {})
    pvp_total = pvp.get("wins", 0) + pvp.get("losses", 0)
    pvp_wr    = f"{int(pvp['wins']/pvp_total*100)}%" if pvp_total > 0 else "N/A"
    pvp_line  = (
        f"\n║  ⚔️ PVP: *{pvp.get('wins',0)}W* / *{pvp.get('losses',0)}L*"
        f"  ({pvp_wr})  🔥{pvp.get('streak',0)}"
    ) if pvp_total > 0 else ""

    return (
        f"╔══════════════════════════════════╗\n"
        f"{header}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  {gender_icon} *{player['name']}* — Lv.{player['level']}\n"
        f"║  🆔 ID: `{uid}`\n"
        f"║  ⚔️ Kelas: *{player['class'].replace('_',' ').title()}*\n"
        f"║  🪙 Gold: *{player.get('coin',0):,}*  💎 Diamond: *{player.get('diamond',0)}*\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ HP : {player['hp']}/{player['max_hp']}\n"
        f"║  💙 MP : {player['mp']}/{player['max_mp']}\n"
        f"║  ⚔️ ATK: {player['atk']}   🛡️ DEF: {player['def']}\n"
        f"║  💨 SPD: {player['spd']}   🎯 CRIT: {crit}%\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ✨ EXP: {exp_bar(player['exp'], player['exp_needed'], 8)}\n"
        f"║  🗡️ Kill: {player.get('kills',0)}  💀 Boss: {player.get('boss_kills',0)}\n"
        f"║  🏆 Menang: {player.get('wins',0)}  💔 Kalah: {player.get('losses',0)}\n"
        f"{pvp_line}"
        f"╠══════════════════════════════════╣\n"
        f"║  🗡️ Senjata: {weapon_str}\n"
        f"║  🛡️ Armor  : {armor_str}\n"
        f"║  🔮 Skill  : {skill_name}"
        f"{vip_line}"
        f"{tier_line}"
        f"{pet_line}"
        f"{special_line}"
        f"{stone_line}"
        f"{skills_line}"
        f"{title_line}"
        f"{rest_line}\n"
        f"╚══════════════════════════════════╝"
    )


def format_item_card(item_id: str, item: dict) -> str:
    stars     = RARITY_STARS.get(item.get("rarity", "common"), "⭐")
    stats_str = ", ".join(
        f"+{v} {k.upper().replace('MAX_','MAX ')}"
        for k, v in item.get("stats", {}).items()
    )
    # BUG FIX: price bisa None (item premium/diamond-only) — jangan format :, langsung
    price = item.get("price")
    dp    = item.get("diamond_price")
    if price is not None:
        price_str = f"🪙 {price:,} Gold"
    elif dp is not None:
        price_str = f"💎 {dp} Diamond"
    else:
        price_str = "🎁 Drop/Event Only"
    return (
        f"*{item['name']}*  {stars}\n"
        f"_{item.get('desc','')}_\n"
        f"📊 {stats_str or 'Konsumable'}\n"
        f"💰 Harga: {price_str}"
    )
