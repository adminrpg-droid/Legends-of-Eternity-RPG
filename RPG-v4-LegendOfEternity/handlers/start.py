# ═══════════════════════════════════════════════════════════════
#  LEGENDS OF ETERNITY — Start & Main Menu Handler
# ═══════════════════════════════════════════════════════════════
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from models.database import get_player, create_player, save_player, CLASS_STATS, is_admin

CHOOSING_GENDER = 1
CHOOSING_CLASS  = 2
ENTERING_NAME   = 3

OFFICIAL_GROUP   = "https://t.me/your_group"    # Ganti dengan link grup
OFFICIAL_CHANNEL = "https://t.me/your_channel"  # Ganti dengan link channel


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)

    if player:
        await show_main_menu(update, context)
    else:
        await show_welcome(update, context)


async def show_welcome(update, context):
    user = update.effective_user
    text = (
        "╔══════════════════════════════════╗\n"
        "║  ⚔️  *LEGENDS OF ETERNITY*  ⚔️   ║\n"
        "║      — Telegram RPG Game —       ║\n"
        "╚══════════════════════════════════╝\n\n"
        f"🌟 Selamat datang, *{user.first_name}*!\n\n"
        "Dunia Eternity menantimu...\n"
        "Monster menghuni setiap sudut, dungeon misterius\n"
        "tersembunyi di balik kegelapan, dan harta karun\n"
        "menanti para pahlawan pemberani.\n\n"
        "⚡ *Pilih jenis kelamin karaktermu:*"
    )
    keyboard = [
        [
            InlineKeyboardButton("♂️ Laki-laki", callback_data="gender_male"),
            InlineKeyboardButton("♀️ Perempuan", callback_data="gender_female"),
        ],
        [
            InlineKeyboardButton("💬 Grup Official", url=OFFICIAL_GROUP),
            InlineKeyboardButton("📢 Channel Official", url=OFFICIAL_CHANNEL),
        ],
    ]
    msg = update.message if hasattr(update, "message") and update.message else None
    if msg:
        await msg.reply_text(text, parse_mode="Markdown",
                             reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown",
                                                      reply_markup=InlineKeyboardMarkup(keyboard))


async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = "male" if query.data == "gender_male" else "female"
    context.user_data["pending_gender"] = gender

    g_icon = "♂️" if gender == "male" else "♀️"
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {g_icon} *PILIH KELAS KARAKTER*         ║\n"
        f"╚══════════════════════════════════╝\n\n"
        "Setiap kelas memiliki keunikan & gaya bermain berbeda.\n"
        "Pilih yang sesuai dengan caramu bertarung!\n\n"
        "⚔️ *Pilih kelasmu:*"
    )

    class_buttons = [
        [InlineKeyboardButton("⚔️ Warrior — Tank & Kuat", callback_data="class_warrior")],
        [InlineKeyboardButton("🔮 Mage — Sihir Dahsyat", callback_data="class_mage")],
        [InlineKeyboardButton("🏹 Archer — Cepat & Tepat", callback_data="class_archer")],
        [InlineKeyboardButton("🗡️ Rogue — Stealthy & Kritis", callback_data="class_rogue")],
        [InlineKeyboardButton("💉 Assassin — Pembunuh Instan", callback_data="class_assassin")],
        [InlineKeyboardButton("💀 Necromancer — Kuasai Kematian", callback_data="class_necromancer")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(class_buttons))


async def class_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    char_class = query.data.replace("class_", "")
    context.user_data["pending_class"] = char_class

    stats = CLASS_STATS[char_class]
    gender = context.user_data.get("pending_gender", "male")
    gender_title = stats["gender_f"] if gender == "female" else stats["gender_m"]
    g_icon = "♂️" if gender == "male" else "♀️"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {stats['emoji']} *{char_class.upper()}*  {g_icon}              ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"_{stats['lore']}_\n\n"
        f"📊 *Stats Awal:*\n"
        f"❤️ HP  : {stats['max_hp']}\n"
        f"💙 MP  : {stats['max_mp']}\n"
        f"⚔️ ATK : {stats['atk']}\n"
        f"🛡️ DEF : {stats['def']}\n"
        f"💨 SPD : {stats['spd']}\n"
        f"🎯 CRIT: {stats['crit']}%\n"
        f"✨ Skill: *{stats['skill']}*\n"
        f"_{stats['skill_desc']}_\n\n"
        f"✏️ *Ketik nama karakter kamu:*\n"
        f"_(contoh: Aria, Zephyr, Leon)_"
    )

    context.user_data["awaiting_name"] = True
    context.user_data["name_message_id"] = query.message.message_id

    keyboard = [[InlineKeyboardButton("⬅️ Ganti Kelas", callback_data=f"gender_{gender}")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def name_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_name"):
        return

    name = update.message.text.strip()
    if len(name) < 2 or len(name) > 16:
        await update.message.reply_text(
            "❌ Nama harus 2–16 karakter!\nCoba lagi:"
        )
        return

    user       = update.effective_user
    char_class = context.user_data.get("pending_class", "warrior")
    gender     = context.user_data.get("pending_gender", "male")
    username   = user.username or ""

    context.user_data["awaiting_name"] = False
    player = create_player(user.id, name, char_class, gender, username)

    stats = CLASS_STATS[char_class]
    g_icon  = "♂️" if gender == "male" else "♀️"
    g_title = stats["gender_f"] if gender == "female" else stats["gender_m"]

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   ✨ *PETUALANGAN DIMULAI!*  ✨  ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"🎉 Selamat datang, *{name}*! {g_icon}\n"
        f"🧬 Kelas: *{stats['emoji']} {char_class.capitalize()}* ({g_title})\n\n"
        f"📊 *STATS AWAL:*\n"
        f"❤️ HP  : {player['hp']}/{player['max_hp']}\n"
        f"💙 MP  : {player['mp']}/{player['max_mp']}\n"
        f"⚔️ ATK : {player['atk']}\n"
        f"🛡️ DEF : {player['def']}\n"
        f"💨 SPD : {player['spd']}\n"
        f"🎯 CRIT: {player['crit']}%\n"
        f"💰 Coin: *0*  💎 Diamond: *0*\n\n"
        f"🎁 Kamu mendapat *2 Health Potion* & *1 Mana Potion*!\n"
        f"⚡ Perjalananmu dimulai sekarang!\n\n"
        f"📌 Gunakan /help untuk panduan lengkap."
    )

    keyboard = [[InlineKeyboardButton("🏠 Menu Utama", callback_data="menu")]]
    await update.message.reply_text(text, parse_mode="Markdown",
                                    reply_markup=InlineKeyboardMarkup(keyboard))


async def show_main_menu(update_or_query, context):
    is_query = hasattr(update_or_query, "data") or (
        hasattr(update_or_query, "callback_query") and update_or_query.callback_query
    )

    if hasattr(update_or_query, "from_user"):
        user = update_or_query.from_user
    elif hasattr(update_or_query, "effective_user"):
        user = update_or_query.effective_user
    else:
        user = update_or_query.callback_query.from_user if hasattr(update_or_query, "callback_query") else None

    if not user:
        return

    player = get_player(user.id)
    if not player:
        text = "❌ Ketik /start untuk memulai!"
        if hasattr(update_or_query, "edit_message_text"):
            await update_or_query.edit_message_text(text)
        return

    from models.database import check_vip_expiry
    player = check_vip_expiry(player)
    save_player(user.id, player)

    vip_str = ""
    if player.get("vip", {}).get("active"):
        tier = player["vip"].get("tier", "")
        tmap = {"vip_silver":"🥈VIP", "vip_gold":"🥇VIP", "vip_diamond":"💎VIP"}
        vip_str = f"  {tmap.get(tier,'VIP')}"

    g_icon = "♀️" if player.get("gender") == "female" else "♂️"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  🏰 *LEGENDS OF ETERNITY*  🏰   ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  {player['emoji']} *{player['name']}* {g_icon} Lv.{player['level']}{vip_str}\n"
        f"║  ❤️ {player['hp']}/{player['max_hp']}  💙 {player['mp']}/{player['max_mp']}\n"
        f"║  💰 {player.get('coin',0)} Coin  💎 {player.get('diamond',0)} Diamond\n"
        f"╚══════════════════════════════════╝\n\n"
        f"🌟 Mau ngapain hari ini, petualang?\n\n"
        f"📌 *Menu Cepat:*\n"
        f"⚔️ /battle   🏰 /dungeon   🛒 /shop\n"
        f"🎒 /inventory   📜 /profile   🏪 /market\n"
        f"📅 /daily   🏆 /leaderboard   ❓ /help"
    )

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Battle",    callback_data="menu"),
            InlineKeyboardButton("🏰 Dungeon",   callback_data="menu"),
        ],
        [
            InlineKeyboardButton("🛒 Shop",      callback_data="menu"),
            InlineKeyboardButton("🎒 Inventory", callback_data="menu"),
        ],
        [
            InlineKeyboardButton("📜 Profile",   callback_data="profile"),
            InlineKeyboardButton("🏪 Market",    callback_data="menu"),
        ],
        [
            InlineKeyboardButton("💬 Grup Official",   url=OFFICIAL_GROUP),
            InlineKeyboardButton("📢 Channel Official", url=OFFICIAL_CHANNEL),
        ],
    ]

    try:
        if hasattr(update_or_query, "edit_message_text"):
            await update_or_query.edit_message_text(
                text, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif hasattr(update_or_query, "message"):
            await update_or_query.message.reply_text(
                text, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception:
        pass
