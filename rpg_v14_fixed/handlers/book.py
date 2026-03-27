import json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player
from monster import MONSTERS, BOSSES, DUNGEONS
from items import (
    RARITY_STARS, get_class_weapons, get_class_armors,
    SHOP_SKILLS, PREMIUM_SKILLS, CLASS_SPECIALS,
    PET_SHOP, GOD_SSSR_WEAPONS, GOD_SSSR_ARMORS, GOD_SSSR_SKILLS,
    GOD_SSSR_PETS, GOD_SSSR_SPECIALS
)

CLASSES = {
    "warrior":     "⚔️ Warrior",
    "mage":        "🔮 Mage",
    "archer":      "🏹 Archer",
    "rogue":       "🗡️ Rogue",
    "assassin":    "💉 Assassin",
    "reaper":"💀 Reaper",
}


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
    await _show_book_menu(update.message, player, is_msg=True)


async def book_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        return

    if action == "book_main":
        await _show_book_menu(query, player)
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

    # ── Item Encyclopedia ──────────────────────────────────────────────
    if action == "book_items":
        await _show_items_menu(query, player)
        return
    if action.startswith("book_items_class_"):
        cls = action.replace("book_items_class_", "")
        await _show_class_items_menu(query, cls)
        return
    if action.startswith("book_weapons_"):
        cls = action.replace("book_weapons_", "")
        await _show_class_weapons(query, cls)
        return
    if action.startswith("book_armors_"):
        cls = action.replace("book_armors_", "")
        await _show_class_armors(query, cls)
        return
    if action.startswith("book_skills_"):
        cls = action.replace("book_skills_", "")
        await _show_class_skills(query, cls)
        return
    if action.startswith("book_specials_"):
        cls = action.replace("book_specials_", "")
        await _show_class_specials(query, cls)
        return
    if action.startswith("book_pets_"):
        rarity = action.replace("book_pets_", "")
        await _show_pets(query, rarity)
        return


# ─── Main Menu ────────────────────────────────────────────────────────────────

async def _show_book_menu(target, player: dict, is_msg=False):
    char_class = player.get("class", "warrior")
    cls_name   = CLASSES.get(char_class, char_class.title())
    text = (
        "╔══════════════════════════════════╗\n"
        "║     📖  *BOOK OF ETERNITY*       ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  Kelasmu: *{cls_name}*\n"
        "╚══════════════════════════════════╝\n\n"
        "Pilih kategori yang ingin dilihat:"
    )
    keyboard = [
        [InlineKeyboardButton("👾 Monster",         callback_data="book_monsters"),
         InlineKeyboardButton("💀 Boss",             callback_data="book_bosses")],
        [InlineKeyboardButton("🏰 Dungeon Guide",    callback_data="book_dungeons")],
        [InlineKeyboardButton("📚 Ensiklopedia Item",callback_data="book_items")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


# ─── Item Encyclopedia ────────────────────────────────────────────────────────

async def _show_items_menu(query, player: dict):
    char_class = player.get("class", "warrior")
    cls_name   = CLASSES.get(char_class, char_class.title())
    text = (
        "╔══════════════════════════════════╗\n"
        "║   📚  *ENSIKLOPEDIA ITEM*        ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  Kelasmu: *{cls_name}*\n"
        "╚══════════════════════════════════╝\n\n"
        "Pilih kelas untuk melihat semua item yang tersedia:\n"
        "_(Termasuk item GOD SSSR eksklusif!)_"
    )
    buttons = []
    for cls_key, cls_label in CLASSES.items():
        tag = " ← Kelasmu" if cls_key == char_class else ""
        buttons.append([InlineKeyboardButton(
            f"{cls_label}{tag}",
            callback_data=f"book_items_class_{cls_key}"
        )])
    buttons.append([InlineKeyboardButton("🐾 Semua Pet", callback_data="book_pets_all")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="book_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_class_items_menu(query, cls: str):
    cls_name = CLASSES.get(cls, cls.title())
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  *ITEM — {cls_name}*\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih kategori item untuk kelas *{cls_name}*:"
    )
    keyboard = [
        [InlineKeyboardButton("⚔️ Weapon",   callback_data=f"book_weapons_{cls}"),
         InlineKeyboardButton("🛡️ Armor",    callback_data=f"book_armors_{cls}")],
        [InlineKeyboardButton("🔮 Skill",    callback_data=f"book_skills_{cls}"),
         InlineKeyboardButton("⚡ Special",  callback_data=f"book_specials_{cls}")],
        [InlineKeyboardButton("⬅️ Kembali",  callback_data="book_items")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def _show_class_weapons(query, cls: str):
    cls_name = CLASSES.get(cls, cls.title())
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  ⚔️ *WEAPON — {cls_name}*\n"
        f"╚══════════════════════════════════╝\n\n"
    )

    # Normal weapons
    normal = get_class_weapons(cls)
    # Premium weapons
    from items import PREMIUM_WEAPONS
    premium = {k: v for k, v in PREMIUM_WEAPONS.items() if v.get("class") == cls}
    # GOD SSSR weapons
    god_sssr = {k: v for k, v in GOD_SSSR_WEAPONS.items() if v.get("class") == cls}

    all_weapons = {**normal, **premium, **god_sssr}

    rarity_order = {"common":0,"uncommon":1,"rare":2,"epic":3,"legendary":4,"SSR":5,"UR":6,"GOD":7,"GOD SSSR":8}
    sorted_weapons = sorted(all_weapons.items(), key=lambda x: rarity_order.get(x[1].get("rarity","common"),0))

    for wid, w in sorted_weapons:
        stars  = RARITY_STARS.get(w.get("rarity","common"),"⭐")
        stats  = w.get("stats",{})
        s_str  = " | ".join(f"+{v} {k.upper()}" for k, v in list(stats.items())[:3])
        price_str = ""
        if w.get("diamond_price"):
            price_str = f"💎 {w['diamond_price']}"
        elif w.get("price"):
            price_str = f"🪙 {w['price']:,}"
        else:
            price_str = "🎁 Drop Boss"
        lv = w.get("req_level",1)
        text += f"• *{w['name']}* {stars}\n  📊 {s_str}\n  🔓 Lv.{lv} | {price_str}\n\n"

    if len(text) > 3800:
        text = text[:3800] + "\n_...dan lebih banyak lagi!_"

    keyboard = [
        [InlineKeyboardButton("⬅️ Kembali", callback_data=f"book_items_class_{cls}")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def _show_class_armors(query, cls: str):
    cls_name = CLASSES.get(cls, cls.title())
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  🛡️ *ARMOR — {cls_name}*\n"
        f"╚══════════════════════════════════╝\n\n"
    )

    from items import get_class_armors, PREMIUM_ARMORS
    normal  = get_class_armors(cls)
    premium = {k: v for k, v in PREMIUM_ARMORS.items() if v.get("class") == cls}
    god_sssr= {k: v for k, v in GOD_SSSR_ARMORS.items() if v.get("class") == cls}

    all_armors = {**normal, **premium, **god_sssr}
    rarity_order = {"common":0,"uncommon":1,"rare":2,"epic":3,"legendary":4,"SSR":5,"UR":6,"GOD":7,"GOD SSSR":8}
    sorted_armors = sorted(all_armors.items(), key=lambda x: rarity_order.get(x[1].get("rarity","common"),0))

    for aid, a in sorted_armors:
        stars  = RARITY_STARS.get(a.get("rarity","common"),"⭐")
        stats  = a.get("stats",{})
        s_str  = " | ".join(f"+{v} {k.upper()}" for k, v in list(stats.items())[:3])
        price_str = ""
        if a.get("diamond_price"):
            price_str = f"💎 {a['diamond_price']}"
        elif a.get("price"):
            price_str = f"🪙 {a['price']:,}"
        else:
            price_str = "🎁 Drop Boss"
        lv = a.get("req_level",1)
        text += f"• *{a['name']}* {stars}\n  📊 {s_str}\n  🔓 Lv.{lv} | {price_str}\n\n"

    if len(text) > 3800:
        text = text[:3800] + "\n_...dan lebih banyak lagi!_"

    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup([[
                                      InlineKeyboardButton("⬅️ Kembali", callback_data=f"book_items_class_{cls}")
                                  ]]))


async def _show_class_skills(query, cls: str):
    cls_name = CLASSES.get(cls, cls.title())
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  🔮 *SKILL — {cls_name}*\n"
        f"╚══════════════════════════════════╝\n\n"
    )

    # Normal skills
    normal   = {k: v for k, v in SHOP_SKILLS.items() if v.get("class") == cls}
    # Premium skills
    premium  = {k: v for k, v in PREMIUM_SKILLS.items() if v.get("class") == cls}
    # GOD SSSR skills
    god_sssr = {k: v for k, v in GOD_SSSR_SKILLS.items() if v.get("class") == cls}

    rarity_order = {"rare":0,"epic":1,"legendary":2,"SSR":3,"UR":4,"GOD":5,"GOD SSSR":6}

    for pool_name, pool in [("Skill Biasa", normal), ("Premium", premium), ("🔱 GOD SSSR", god_sssr)]:
        if not pool:
            continue
        text += f"*── {pool_name} ──*\n"
        sorted_pool = sorted(pool.items(), key=lambda x: rarity_order.get(x[1].get("rarity","rare"),0))
        for sid, s in sorted_pool:
            stars = RARITY_STARS.get(s.get("rarity","rare"),"⭐")
            eff   = s.get("effect",{})
            dmg   = eff.get("dmg_mult",1.0)
            mp    = eff.get("mp_cost",0)
            cd    = eff.get("cooldown",0)
            price_str = ""
            if s.get("diamond_price"):
                price_str = f"💎 {s['diamond_price']}"
            elif pool_name == "🔱 GOD SSSR":
                price_str = "🎁 Drop Boss 0.1%"
            else:
                price_str = "🪙 Gold"
            text += (
                f"• *{s['name']}* {stars}\n"
                f"  _{s.get('desc','')}_\n"
                f"  ⚡ {dmg}x DMG | 💙 {mp} MP | ⏳ CD:{cd} | {price_str}\n\n"
            )

    if len(text) > 3800:
        text = text[:3800] + "\n_...dan lebih banyak lagi!_"

    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup([[
                                      InlineKeyboardButton("⬅️ Kembali", callback_data=f"book_items_class_{cls}")
                                  ]]))


async def _show_class_specials(query, cls: str):
    cls_name = CLASSES.get(cls, cls.title())
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  ⚡ *SPECIAL — {cls_name}*\n"
        f"╚══════════════════════════════════╝\n\n"
        f"*Passive Ability bawaan kelas {cls_name}:*\n\n"
    )

    # Normal special
    normal_sp = CLASS_SPECIALS.get(cls)
    if normal_sp:
        text += (
            f"*── Class Special ──*\n"
            f"• *{normal_sp['name']}*\n"
            f"  _{normal_sp.get('desc','')}_\n"
            f"  Trigger: `{normal_sp.get('trigger','passive')}`\n\n"
        )

    # GOD SSSR special
    god_sp = GOD_SSSR_SPECIALS.get(cls)
    if god_sp:
        stars = RARITY_STARS.get("GOD SSSR","🔱")
        text += (
            f"*── 🔱 GOD SSSR Special ──*\n"
            f"• *{god_sp['name']}* {stars}\n"
            f"  _{god_sp.get('desc','')}_\n"
            f"  Cara Dapat: 🎁 Drop Boss (0.1% rate)\n\n"
        )

    text += "_Special aktif otomatis saat kondisi terpenuhi._"

    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup([[
                                      InlineKeyboardButton("⬅️ Kembali", callback_data=f"book_items_class_{cls}")
                                  ]]))


async def _show_pets(query, rarity_filter: str):
    text = (
        "╔══════════════════════════════════╗\n"
        "║   🐾  *DAFTAR PET*              ║\n"
        "╚══════════════════════════════════╝\n\n"
    )

    rarity_order = {"common":0,"uncommon":1,"rare":2,"epic":3,"SSR":4,"UR":5,"GOD":6,"GOD SSSR":7}
    all_pets = {**PET_SHOP, **GOD_SSSR_PETS}

    if rarity_filter != "all":
        all_pets = {k: v for k, v in all_pets.items() if v.get("rarity") == rarity_filter}

    sorted_pets = sorted(all_pets.items(), key=lambda x: rarity_order.get(x[1].get("rarity","common"),0))

    for pid, pet in sorted_pets:
        stars = RARITY_STARS.get(pet.get("rarity","common"),"⭐")
        price_str = ""
        if pet.get("diamond_price"):
            price_str = f"💎 {pet['diamond_price']}"
        elif pet.get("price"):
            price_str = f"🪙 {pet['price']:,}"
        else:
            price_str = "🎁 Drop Boss 0.1%"
        eff = pet.get("effect",{})
        eff_str = " | ".join(f"+{v} {k.replace('_bonus','').upper()}" for k,v in list(eff.items())[:3] if isinstance(v,(int,float)) and v > 0)
        text += (
            f"• *{pet['name']}* {stars}\n"
            f"  _{pet.get('desc','')}_\n"
            f"  📊 {eff_str or 'Spesial'} | {price_str}\n"
            f"  🌀 Passive: _{pet.get('passive','')}_\n\n"
        )

    if len(text) > 3800:
        text = text[:3800] + "\n_...dan lebih banyak lagi!_"

    buttons = [
        [InlineKeyboardButton("⬅️ Kembali", callback_data="book_items")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


# ─── Monster / Boss / Dungeon (unchanged logic) ────────────────────────────────

async def _show_monster_list(query):
    text = (
        "╔══════════════════════════════════╗\n"
        "║    👾  *DAFTAR MONSTER*          ║\n"
        "╚══════════════════════════════════╝\n\n"
        "Tap monster untuk melihat detail:\n"
    )
    tiers = {1:"⭐ Tier 1 (Pemula)",2:"⭐⭐ Tier 2 (Menengah)",
             3:"⭐⭐⭐ Tier 3 (Kuat)",4:"⭐⭐⭐⭐ Tier 4 (Epik)"}
    buttons = []
    for tier_num, tier_label in tiers.items():
        buttons.append([InlineKeyboardButton(f"── {tier_label} ──", callback_data="book_monsters")])
        for name, m in MONSTERS.items():
            if m["tier"] == tier_num:
                btn_label = f"{m['emoji']} {name} | HP:{m['hp']} ATK:{m['atk']}"
                cb_name   = name.replace(" ","_")
                buttons.append([InlineKeyboardButton(btn_label, callback_data=f"book_mon_{cb_name}")])
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="book_main")])
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def _show_monster_detail(query, name: str):
    monster = MONSTERS.get(name)
    if not monster:
        await query.answer("Monster tidak ditemukan!", show_alert=True)
        return
    media     = _load_media()
    img       = media.get(f"monster:{name}")
    tier_stars= "⭐" * monster["tier"]
    gold_min, gold_max = monster.get("gold",(0,0))
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {monster['emoji']} *{name}*\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🏅 Tier : {tier_stars}\n"
        f"║  ❤️ HP   : {monster['hp']}\n"
        f"║  ⚔️ ATK  : {monster['atk']}\n"
        f"║  🛡️ DEF  : {monster['def']}\n"
        f"║  ✨ EXP  : {monster['exp']}\n"
        f"║  💰 Gold : {gold_min}–{gold_max}\n"
        f"╚══════════════════════════════════╝\n\n"
        f"_Gunakan strategi yang tepat untuk mengalahkan monster ini!_"
    )
    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke List", callback_data="book_monsters")]]
    if img:
        try:
            await query.message.reply_photo(photo=img, caption=text, parse_mode="Markdown",
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
        wb    = " 🌍" if boss.get("world_boss") else ""
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
    media     = _load_media()
    img       = media.get(f"boss:{boss_id}")
    wb_tag    = "\n🌍 *WORLD BOSS* — Musuh terkuat!" if boss.get("world_boss") else ""
    gold_min, gold_max = boss.get("gold",(0,0))
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {boss['emoji']} *{boss['name']}*\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ HP  : {boss['hp']}\n"
        f"║  ⚔️ ATK : {boss['atk']}\n"
        f"║  🛡️ DEF : {boss['def']}\n"
        f"║  ✨ EXP : {boss['exp']}\n"
        f"║  💰 Gold: {gold_min}–{gold_max}\n"
        f"╚══════════════════════════════════╝\n"
        f"{wb_tag}\n\n"
        f"📝 _{boss.get('desc','')}_\n\n"
        f"💥 *Special:* {boss.get('special','-')}\n\n"
        f"🎁 *Drop:* Item sesuai kelas + chance GOD SSSR 0.1%"
    )
    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke List", callback_data="book_bosses")]]
    if img:
        try:
            await query.message.reply_photo(photo=img, caption=text, parse_mode="Markdown",
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
    media     = _load_media()
    img       = media.get(f"dungeon:{did}")
    boss_id   = dg.get("boss","")
    boss_data = BOSSES.get(boss_id,{})
    monsters_str = ", ".join(dg.get("monsters",[]))
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {dg['emoji']} *{dg['name']}*\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🔓 Min Level   : {dg['min_level']}\n"
        f"║  🏚️ Total Lantai: {dg['floor_count']}\n"
        f"╚══════════════════════════════════╝\n\n"
        f"📝 _{dg['desc']}_\n\n"
        f"👾 *Monster:* {monsters_str}\n\n"
        f"👑 *Boss:* {boss_data.get('emoji','')} {boss_data.get('name','?')}\n"
        f"💥 {boss_data.get('special','')}\n\n"
        f"🎁 *Hadiah Boss:* Item langka sesuai kelasmu!\n"
        f"🔱 *0.1% chance:* Item GOD SSSR ultra-langka!"
    )
    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke List", callback_data="book_dungeons")]]
    if img:
        try:
            await query.message.reply_photo(photo=img, caption=text, parse_mode="Markdown",
                                            reply_markup=InlineKeyboardMarkup(keyboard))
            await query.message.delete()
            return
        except Exception:
            pass
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
