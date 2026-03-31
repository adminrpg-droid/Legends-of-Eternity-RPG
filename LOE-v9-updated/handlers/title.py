"""
Title System — Legends of Eternity RPG
Pemain bisa mendapatkan title dari achievement & quest.
Title dapat ditampilkan di profil.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, save_player

# ─── TITLE DEFINITIONS ───────────────────────────────────────────
ALL_TITLES = {
    # Starter
    "newcomer":      {"name": "Pendatang Baru",    "emoji": "🌱", "desc": "Baru bergabung di dunia Eternity",    "condition": "auto"},
    # Kill milestones
    "monster_slayer":{"name": "Pembunuh Monster",  "emoji": "⚔️", "desc": "Bunuh 50 monster",                   "condition": "kills_50"},
    "veteran":       {"name": "Veteran",            "emoji": "🗡️", "desc": "Bunuh 200 monster",                  "condition": "kills_200"},
    "demon_hunter":  {"name": "Pemburu Iblis",      "emoji": "👹", "desc": "Bunuh 500 monster",                  "condition": "kills_500"},
    "legend":        {"name": "Legenda",             "emoji": "🌟", "desc": "Bunuh 1000 monster",                 "condition": "kills_1000"},
    # Boss milestones
    "boss_challenger":{"name": "Penantang Boss",   "emoji": "💀", "desc": "Bunuh 5 boss",                       "condition": "boss_5"},
    "boss_slayer":   {"name": "Pembantai Boss",     "emoji": "👑", "desc": "Bunuh 20 boss",                     "condition": "boss_20"},
    "boss_king":     {"name": "Raja Boss",          "emoji": "🔱", "desc": "Bunuh 50 boss",                     "condition": "boss_50"},
    # Level milestones
    "adventurer":    {"name": "Petualang",          "emoji": "🗺️", "desc": "Capai Level 10",                    "condition": "level_10"},
    "hero":          {"name": "Pahlawan",           "emoji": "🦸", "desc": "Capai Level 25",                    "condition": "level_25"},
    "champion":      {"name": "Juara",              "emoji": "🏆", "desc": "Capai Level 40",                    "condition": "level_40"},
    "god_tier":      {"name": "GOD TIER",           "emoji": "☀️", "desc": "Capai Level 50",                    "condition": "level_50"},
    # Enhancement
    "enhancer":      {"name": "Penguatan Pertama",  "emoji": "⚒️", "desc": "Enhance item pertama kali",          "condition": "enhance_1"},
    "max_enhancer":  {"name": "Master Enhance",     "emoji": "🔱", "desc": "Capai +10 enhance di item manapun",  "condition": "enhance_max"},
    # Special
    "rich":          {"name": "Kaya Raya",          "emoji": "💰", "desc": "Kumpulkan 100.000 Gold",             "condition": "gold_100k"},
    "diamond_lord":  {"name": "Lord Diamond",       "emoji": "💎", "desc": "Kumpulkan 100 Diamond",              "condition": "diamond_100"},
    "dungeon_explorer":{"name":"Penjelajah Dungeon","emoji": "🕳️", "desc": "Selesaikan 10 dungeon",              "condition": "dungeon_10"},
    "vip_member":    {"name": "VIP Member",         "emoji": "👑", "desc": "Punya status VIP aktif",             "condition": "vip"},
}


def check_and_award_titles(player: dict) -> tuple:
    """Check all conditions and award new titles. Returns (player, new_titles_list)."""
    if "titles" not in player:
        player["titles"] = []
    if "active_title" not in player:
        player["active_title"] = "newcomer"
        if "newcomer" not in player["titles"]:
            player["titles"].append("newcomer")

    new_titles = []
    kills       = player.get("kills", 0)
    boss_kills  = player.get("boss_kills", 0)
    level       = player.get("level", 1)
    coin        = player.get("coin", 0)
    diamond     = player.get("diamond", 0)
    dungeon_clears = player.get("dungeon_clears", 0)

    conditions = {
        "kills_50":    kills >= 50,
        "kills_200":   kills >= 200,
        "kills_500":   kills >= 500,
        "kills_1000":  kills >= 1000,
        "boss_5":      boss_kills >= 5,
        "boss_20":     boss_kills >= 20,
        "boss_50":     boss_kills >= 50,
        "level_10":    level >= 10,
        "level_25":    level >= 25,
        "level_40":    level >= 40,
        "level_50":    level >= 50,
        "gold_100k":   coin >= 100_000,
        "diamond_100": diamond >= 100,
        "dungeon_10":  dungeon_clears >= 10,
        "vip":         player.get("vip", {}).get("active", False),
        "enhance_1":   any(v > 0 for v in player.get("enhance_levels", {}).values()),
        "enhance_max": any(v >= 10 for v in player.get("enhance_levels", {}).values()),
    }

    for tid, t in ALL_TITLES.items():
        if tid in player["titles"]:
            continue
        cond = t.get("condition", "")
        if cond == "auto":
            player["titles"].append(tid)
            new_titles.append(tid)
        elif conditions.get(cond, False):
            player["titles"].append(tid)
            new_titles.append(tid)

    return player, new_titles


# ─── HANDLERS ────────────────────────────────────────────────────
async def title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    player, _ = check_and_award_titles(player)
    save_player(user.id, player)
    await _show_titles(update.message, player, user.id)


async def title_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    action = query.data
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        await query.answer("❌ Ketik /start!", show_alert=True)
        return

    player, _ = check_and_award_titles(player)

    if action == "title_main":
        save_player(user.id, player)
        await _show_titles(query, player, user.id, edit=True)
        return

    if action.startswith("title_equip_"):
        tid = action.replace("title_equip_", "")
        if tid in player.get("titles", []):
            player["active_title"] = tid
            save_player(user.id, player)
            t = ALL_TITLES.get(tid, {})
            await query.answer(f"✅ Title [{t.get('emoji','')} {t.get('name','')}] diaktifkan!", show_alert=True)
        await _show_titles(query, player, user.id, edit=True)
        return


async def _show_titles(target, player: dict, user_id: int, edit: bool = False):
    owned  = player.get("titles", [])
    active = player.get("active_title", "newcomer")
    t_act  = ALL_TITLES.get(active, {})

    lines = [
        "╔══════════════════════════════════╗\n"
        "║      🏅  *KOLEKSI TITLE*  🏅     ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  Title Aktif: {t_act.get('emoji','')} *{t_act.get('name','─')}*\n"
        f"║  Dimiliki: {len(owned)}/{len(ALL_TITLES)} Title\n"
        "╠══════════════════════════════════╣\n"
    ]

    buttons = []
    for tid, t in ALL_TITLES.items():
        if tid in owned:
            marker = "✅ " if tid == active else "🔓 "
            lines.append(f"║ {marker}{t['emoji']} *{t['name']}*\n║   _{t['desc']}_\n")
            if tid != active:
                buttons.append([InlineKeyboardButton(f"🎖️ Pakai: {t['emoji']} {t['name']}", callback_data=f"title_equip_{tid}")])
        else:
            lines.append(f"║ 🔒 _{t['name']}_ — {t['desc']}\n")

    lines.append("╚══════════════════════════════════╝")
    buttons.append([InlineKeyboardButton("🏠 Menu", callback_data="menu")])

    text = "".join(lines)
    keyboard = InlineKeyboardMarkup(buttons)

    if edit and hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        fn = target.reply_text if hasattr(target, "reply_text") else target.edit_message_text
        await fn(text, parse_mode="Markdown", reply_markup=keyboard)
