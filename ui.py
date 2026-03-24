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
    vip         = vip_badge(player)
    gender_icon = "♀️" if player.get("gender") == "female" else "♂️"
    uid         = telegram_id or player.get("telegram_id", player.get("user_id", "?"))

    equip      = player.get("equipment", {})
    weapon_str = (get_item(equip.get("weapon") or "") or {}).get("name", "─ Kosong")
    armor_str  = (get_item(equip.get("armor") or "") or {}).get("name", "─ Kosong")

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
        skills_line = f"\n║  🔮 Skill: {', '.join(s['name'] for s in bought[:3])}"

    rest_line = "\n║  😴 *Sedang Istirahat...*" if player.get("is_resting") else ""

    return (
        f"╔══════════════════════════════════╗\n"
        f"{header}\n"
        f"╠══════════════════════════════════╣\n"
        f"║  {gender_icon} *{player['name']}* — Lv.{player['level']}\n"
        f"║  🆔 ID: `{uid}`\n"
        f"║  ⚔️ Kelas: *{player['class'].capitalize()}*\n"
        f"║  💰 Coin: *{player.get('coin',0)}*  💎 Diamond: *{player.get('diamond',0)}*\n"
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
        f"║  🗡️ Senjata: {weapon_str}\n"
        f"║  🛡️ Armor  : {armor_str}"
        f"{vip_line}"
        f"{skills_line}"
        f"{rest_line}\n"
        f"╚══════════════════════════════════╝"
    )


def format_item_card(item_id: str, item: dict) -> str:
    stars     = RARITY_STARS.get(item.get("rarity", "common"), "⭐")
    stats_str = ", ".join(
        f"+{v} {k.upper().replace('MAX_','MAX ')}"
        for k, v in item.get("stats", {}).items()
    )
    return (
        f"*{item['name']}*  {stars}\n"
        f"_{item.get('desc','')}_\n"
        f"📊 {stats_str or 'Konsumable'}\n"
        f"💰 Harga: {item.get('price','?'):,} Coin"
    )
