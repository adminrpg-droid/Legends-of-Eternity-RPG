import time
from data.items import get_item, RARITY_STARS


def hp_bar(current: int, max_val: int, length: int = 10) -> str:
    if max_val <= 0:
        return "░" * length
    ratio = max(0, min(1, current / max_val))
    filled = int(ratio * length)
    bar = "█" * filled + "░" * (length - filled)
    pct = int(ratio * 100)
    return f"`{bar}` {current}/{max_val} ({pct}%)"


def exp_bar(current: int, needed: int, length: int = 10) -> str:
    if needed <= 0:
        return "█" * length
    ratio = max(0, min(1, current / needed))
    filled = int(ratio * length)
    bar = "▓" * filled + "░" * (length - filled)
    return f"`{bar}` {current}/{needed}"


def vip_badge(player: dict) -> str:
    if not player.get("vip", {}).get("active"):
        return ""
    tier = player["vip"].get("tier", "")
    badges = {
        "vip_silver": " 🥈VIP",
        "vip_gold":   " 🥇VIP",
        "vip_diamond":" 💎VIP",
    }
    return badges.get(tier, "")


def format_profile(player: dict, telegram_id: int = None, viewer_id: int = None) -> str:
    """
    Format profil karakter.
    viewer_id: jika diisi, tampilkan label 'Profil [nama]' (bukan profil sendiri).
    """
    from models.database import is_admin
    vip  = vip_badge(player)
    gender_icon = "♀️" if player.get("gender") == "female" else "♂️"
    
    equip = player.get("equipment", {})
    weapon_item = get_item(equip.get("weapon", "") or "")
    armor_item  = get_item(equip.get("armor", "") or "")
    weapon_str = weapon_item.get("name", "─ Kosong") if weapon_item else "─ Kosong"
    armor_str  = armor_item.get("name", "─ Kosong") if armor_item else "─ Kosong"

    vip_line = ""
    if player.get("vip", {}).get("active"):
        tier = player["vip"].get("tier", "")
        expires = player["vip"].get("expires", 0)
        days_left = max(0, int((expires - time.time()) / 86400))
        tier_names = {"vip_silver": "🥈 Silver", "vip_gold": "🥇 Gold", "vip_diamond": "💎 Diamond"}
        vip_line = f"\n║  {tier_names.get(tier, 'VIP')} — Sisa {days_left} hari"

    # Badge admin
    uid = telegram_id or player.get("telegram_id", player.get("user_id", "?"))
    admin_badge = " 👑ADMIN" if is_admin(uid) else ""

    crit = player.get("crit", 10)

    # Label header berbeda jika melihat profil orang lain
    if viewer_id and viewer_id != uid:
        header = f"║  {player['emoji']} *PROFIL {player['name'].upper()}*{vip}{admin_badge}"
    else:
        header = f"║       {player['emoji']} *PROFIL KARAKTER*{vip}{admin_badge}      ║"

    # Skill list
    bought_skills = player.get("bought_skills", [])
    skills_line = ""
    if bought_skills:
        skills_line = f"\n║  🔮 Skill Extra: {', '.join(s['name'] for s in bought_skills[:3])}"

    # Rest/sleep status
    rest_line = ""
    if player.get("is_resting"):
        rest_line = "\n║  😴 *Sedang Istirahat...*"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"{header}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  {gender_icon} *{player['name']}* — Lv.{player['level']}\n"
        f"║  🆔 ID: `{uid}`\n"
        f"║  ⚔️ Kelas: *{player['class'].capitalize()}*\n"
        f"║  💰 Coin : *{player.get('coin',0)}*  💎 Diamond: *{player.get('diamond',0)}*\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ HP : {player['hp']}/{player['max_hp']}\n"
        f"║  💙 MP : {player['mp']}/{player['max_mp']}\n"
        f"║  ⚔️ ATK: {player['atk']}   🛡️ DEF: {player['def']}\n"
        f"║  💨 SPD: {player['spd']}   🎯 CRIT: {crit}%\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ✨ EXP: {exp_bar(player['exp'], player['exp_needed'], 8)}\n"
        f"║  🗡️ Kill: {player.get('kills',0)}  💀 Boss: {player.get('boss_kills',0)}\n"
        f"║  🏆 Menang: {player.get('wins',0)}  💔 Kalah: {player.get('losses',0)}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🗡️ Senjata : {weapon_str}\n"
        f"║  🛡️ Armor   : {armor_str}\n"
        f"{vip_line}"
        f"{skills_line}"
        f"{rest_line}\n"
        f"╚══════════════════════════════════╝"
    )
    return text


def format_item_card(item_id: str, item: dict) -> str:
    rarity = item.get("rarity", "common")
    stars  = RARITY_STARS.get(rarity, "⭐")
    stats_str = ", ".join(
        f"+{v} {k.upper().replace('MAX_','MAX ')}" for k, v in item.get("stats", {}).items()
    )
    return (
        f"*{item['name']}*  {stars}\n"
        f"_{item.get('desc','')}_\n"
        f"📊 {stats_str or 'Konsumable'}\n"
        f"💰 Harga: {item.get('price','?')} Coin"
    )
