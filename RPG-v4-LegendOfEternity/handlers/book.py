import json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models.database import get_player
from data.monsters import MONSTERS, BOSSES, DUNGEONS


def _load_media() -> dict:
    path = "data/media.json"
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


async def book_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    await _show_book_menu(update.message, is_msg=True)


async def book_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data

    if action == "book_main":
        await _show_book_menu(query)
        return
    if action == "book_monsters":
        await _show_monster_list(query)
        return
    if action == "book_bosses":
        await _show_boss_list(query)
        return
    if action == "book_dungeons":
        await _show_dungeon_list(query)
        return
    if action.startswith("book_mon_"):
        name = action.replace("book_mon_", "").replace("_", " ")
        await _show_monster_detail(query, name)
        return
    if action.startswith("book_boss_"):
        boss_id = action.replace("book_boss_", "")
        await _show_boss_detail(query, boss_id)
        return
    if action.startswith("book_dg_"):
        did = int(action.replace("book_dg_", ""))
        await _show_dungeon_detail(query, did)
        return


async def _show_book_menu(target, is_msg=False):
    text = (
        "╔══════════════════════════════════╗\n"
        "║     📖  *BOOK OF ETERNITY*       ║\n"
        "╠══════════════════════════════════╣\n"
        "║  Ensiklopedia dunia Eternity     ║\n"
        "╚══════════════════════════════════╝\n\n"
        "Pilih kategori yang ingin dilihat:"
    )
    keyboard = [
        [InlineKeyboardButton("👾 Monster Rare",    callback_data="book_monsters")],
        [InlineKeyboardButton("💀 Boss Legendaris", callback_data="book_bosses")],
        [InlineKeyboardButton("🏰 Dungeon Guide",   callback_data="book_dungeons")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def _show_monster_list(query):
    text = (
        "╔══════════════════════════════════╗\n"
        "║    👾  *DAFTAR MONSTER*          ║\n"
        "╚══════════════════════════════════╝\n\n"
        "Tap monster untuk melihat detail:\n"
    )
    # Group by tier
    tiers = {1: "⭐ Tier 1 (Pemula)", 2: "⭐⭐ Tier 2 (Menengah)",
             3: "⭐⭐⭐ Tier 3 (Kuat)", 4: "⭐⭐⭐⭐ Tier 4 (Epik)"}
    buttons = []
    for tier_num, tier_label in tiers.items():
        buttons.append([InlineKeyboardButton(f"── {tier_label} ──", callback_data="book_monsters")])
        for name, m in MONSTERS.items():
            if m["tier"] == tier_num:
                btn_label = f"{m['emoji']} {name} | HP:{m['hp']} ATK:{m['atk']}"
                cb_name   = name.replace(" ", "_")
                buttons.append([InlineKeyboardButton(btn_label, callback_data=f"book_mon_{cb_name}")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="book_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_monster_detail(query, name: str):
    monster = MONSTERS.get(name)
    if not monster:
        await query.answer("Monster tidak ditemukan!", show_alert=True)
        return

    media = _load_media()
    img   = media.get(f"monster:{name}")

    tier_stars = "⭐" * monster["tier"]
    gold_min, gold_max = monster.get("gold", (0, 0))
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {monster['emoji']} *{name}*                   ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🏅 Tier   : {tier_stars}\n"
        f"║  ❤️ HP     : {monster['hp']}\n"
        f"║  ⚔️ ATK    : {monster['atk']}\n"
        f"║  🛡️ DEF    : {monster['def']}\n"
        f"║  ✨ EXP    : {monster['exp']}\n"
        f"║  💰 Gold   : {gold_min}–{gold_max} Coin\n"
        f"╚══════════════════════════════════╝\n\n"
        f"_Gunakan strategi yang tepat untuk mengalahkan monster ini!_"
    )

    cb_name = name.replace(" ", "_")
    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke List", callback_data="book_monsters")]]

    if img:
        try:
            await query.message.reply_photo(photo=img, caption=text,
                                            parse_mode="Markdown",
                                            reply_markup=InlineKeyboardMarkup(keyboard))
            await query.message.delete()
            return
        except Exception:
            pass

    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def _show_boss_list(query):
    text = (
        "╔══════════════════════════════════╗\n"
        "║   💀  *BOSS LEGENDARIS*          ║\n"
        "╚══════════════════════════════════╝\n\n"
        "Boss yang mendiami dunia Eternity:\n"
    )
    buttons = []
    for boss_id, boss in BOSSES.items():
        wb = " 🌍" if boss.get("world_boss") else ""
        label = f"{boss['emoji']} {boss['name']}{wb} | HP:{boss['hp']}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"book_boss_{boss_id}")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="book_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_boss_detail(query, boss_id: str):
    boss = BOSSES.get(boss_id)
    if not boss:
        await query.answer("Boss tidak ditemukan!", show_alert=True)
        return

    media = _load_media()
    img   = media.get(f"boss:{boss_id}")

    wb_tag = "\n🌍 *WORLD BOSS* — Musuh terkuat!" if boss.get("world_boss") else ""
    gold_min, gold_max = boss.get("gold", (0, 0))
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {boss['emoji']} *{boss['name']}*             ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ HP  : {boss['hp']}\n"
        f"║  ⚔️ ATK : {boss['atk']}\n"
        f"║  🛡️ DEF : {boss['def']}\n"
        f"║  ✨ EXP : {boss['exp']}\n"
        f"║  💰 Gold: {gold_min}–{gold_max} Coin\n"
        f"╚══════════════════════════════════╝\n"
        f"{wb_tag}\n\n"
        f"📝 _{boss.get('desc', '')}_\n\n"
        f"💥 *Special:* {boss.get('special', '-')}"
    )

    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke List", callback_data="book_bosses")]]

    if img:
        try:
            await query.message.reply_photo(photo=img, caption=text,
                                            parse_mode="Markdown",
                                            reply_markup=InlineKeyboardMarkup(keyboard))
            await query.message.delete()
            return
        except Exception:
            pass

    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def _show_dungeon_list(query):
    text = (
        "╔══════════════════════════════════╗\n"
        "║   🏰  *PANDUAN DUNGEON*          ║\n"
        "╚══════════════════════════════════╝\n\n"
        "Semua dungeon di dunia Eternity:\n"
    )
    buttons = []
    for did, dg in DUNGEONS.items():
        label = f"{dg['emoji']} {dg['name']} | Min.Lv {dg['min_level']}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"book_dg_{did}")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="book_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_dungeon_detail(query, did: int):
    dg = DUNGEONS.get(did)
    if not dg:
        await query.answer("Dungeon tidak ditemukan!", show_alert=True)
        return

    media = _load_media()
    img   = media.get(f"dungeon:{did}")

    boss_id   = dg.get("boss","")
    from data.monsters import BOSSES
    boss_data = BOSSES.get(boss_id, {})
    monsters_str = ", ".join(dg.get("monsters", []))

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {dg['emoji']} *{dg['name']}*                ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🔓 Min Level  : {dg['min_level']}\n"
        f"║  🏚️ Total Lantai: {dg['floor_count']}\n"
        f"╚══════════════════════════════════╝\n\n"
        f"📝 _{dg['desc']}_\n\n"
        f"👾 *Monster:* {monsters_str}\n\n"
        f"👑 *Boss:* {boss_data.get('emoji','')} {boss_data.get('name','?')}\n"
        f"💥 {boss_data.get('special','')}\n\n"
        f"🎁 *Hadiah Boss:* Item langka sesuai kelasmu!"
    )

    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke List", callback_data="book_dungeons")]]

    if img:
        try:
            await query.message.reply_photo(photo=img, caption=text,
                                            parse_mode="Markdown",
                                            reply_markup=InlineKeyboardMarkup(keyboard))
            await query.message.delete()
            return
        except Exception:
            pass

    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
