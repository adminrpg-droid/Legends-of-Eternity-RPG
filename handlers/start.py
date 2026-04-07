from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from database import get_player, create_player, save_player, CLASS_STATS, is_admin

CHOOSING_GENDER = 1
CHOOSING_CLASS  = 2
ENTERING_NAME   = 3

OFFICIAL_GROUP   = "https://t.me/loerpgo"    # Ganti dengan link grup
OFFICIAL_CHANNEL = "https://t.me/loerpgof"  # Ganti dengan link channel


def _get_market_channel_url() -> str | None:
    """Ambil URL channel market jika sudah diset."""
    try:
        from handlers.market_channel import get_market_channel_id
        ch_id = get_market_channel_id()
        if ch_id:
            # channel_id biasanya -100XXXXXXXXXX, ubah ke t.me/c/XXXXXXXXXX
            ch_str = str(ch_id)
            if ch_str.startswith("-100"):
                return f"https://t.me/c/{ch_str[4:]}"
            return None
    except Exception:
        pass
    return None


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    from database import is_banned
    if is_banned(user.id):
        await update.message.reply_text("🚫 *Akunmu telah di-ban!*\nHubungi admin untuk informasi lebih lanjut.", parse_mode="Markdown")
        return

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
        "║          —  RPG Game —       ║\n"
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
    market_url = _get_market_channel_url()
    if market_url:
        keyboard.append([InlineKeyboardButton("🏪 Channel Market P2P", url=market_url)])
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
    context.bot_data[f"{user.id}_pending_gender"] = gender

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
        [InlineKeyboardButton("💉 Assassin — Eksekusi & Racun", callback_data="class_assassin")],
        [InlineKeyboardButton("☠️ Reaper — Panen Jiwa", callback_data="class_reaper")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(class_buttons))


async def class_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    char_class = query.data.replace("class_", "")
    context.bot_data[f"{user.id}_pending_class"] = char_class

    stats = CLASS_STATS[char_class]
    gender = context.bot_data.get(f"{user.id}_pending_gender", "male")
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

    context.bot_data[f"{user.id}_awaiting_name"] = True
    context.bot_data[f"{user.id}_name_message_id"] = query.message.message_id

    keyboard = [[InlineKeyboardButton("⬅️ Ganti Kelas", callback_data=f"gender_{gender}")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def name_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user       = update.effective_user
    if not context.bot_data.get(f"{user.id}_awaiting_name"):
        return

    name = update.message.text.strip()
    if len(name) < 2 or len(name) > 16:
        await update.message.reply_text(
            "❌ Nama harus 2–16 karakter!\nCoba lagi:"
        )
        return
    char_class = context.bot_data.get(f"{user.id}_pending_class", "warrior")
    gender     = context.bot_data.get(f"{user.id}_pending_gender", "male")
    username   = user.username or ""

    context.bot_data[f"{user.id}_awaiting_name"] = False
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
        f"🪙 Gold: *0*  💎 Diamond: *0*\n\n"
        f"🎁 Kamu mendapat *2 Health Potion* & *1 Mana Potion*!\n"
        f"⚡ Perjalananmu dimulai sekarang!\n\n"
        f"📌 Gunakan /help untuk panduan lengkap."
    )

    keyboard = [[InlineKeyboardButton("🏠 Menu Utama", callback_data="menu")]]
    await update.message.reply_text(text, parse_mode="Markdown",
                                    reply_markup=InlineKeyboardMarkup(keyboard))


async def show_main_menu(update_or_query, context):
    # Determine if this is a CallbackQuery or Update/Message
    from telegram import CallbackQuery, Update as TGUpdate

    if isinstance(update_or_query, CallbackQuery):
        user = update_or_query.from_user
        is_query = True
    elif isinstance(update_or_query, TGUpdate):
        user = update_or_query.effective_user
        is_query = False
    elif hasattr(update_or_query, "from_user"):
        # Raw CallbackQuery-like object
        user = update_or_query.from_user
        is_query = hasattr(update_or_query, "edit_message_text")
    else:
        return

    player = get_player(user.id)
    if not player:
        text = "❌ Ketik /start untuk memulai!"
        if hasattr(update_or_query, "edit_message_text"):
            await update_or_query.edit_message_text(text)
        return

    from database import check_vip_expiry
    player = check_vip_expiry(player)
    save_player(user.id, player)

    vip_str = ""
    if player.get("vip", {}).get("active"):
        tier = player["vip"].get("tier", "")
        tmap = {"vip_silver":"🥈VIP", "vip_gold":"🥇VIP", "vip_diamond":"💎VIP"}
        vip_str = f"  {tmap.get(tier,'VIP')}"

    g_icon = "♀️" if player.get("gender") == "female" else "♂️"

    hp_pct  = int(player['hp']/max(1,player['max_hp'])*100)
    mp_pct  = int(player['mp']/max(1,player['max_mp'])*100)
    hp_bar_ = "█" * (hp_pct//10) + "░" * (10 - hp_pct//10)
    mp_bar_ = "█" * (mp_pct//10) + "░" * (10 - mp_pct//10)
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  🏰 *LEGENDS OF ETERNITY *  🏰 ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  {player['emoji']} *{player['name']}* {g_icon} Lv.{player['level']}{vip_str}\n"
        f"║  ❤️ `{hp_bar_}` {player['hp']}/{player['max_hp']}\n"
        f"║  💙 `{mp_bar_}` {player['mp']}/{player['max_mp']}\n"
        f"║  🪙 {player.get('coin',0):,} Gold  💎 {player.get('diamond',0):,} Diamond\n"
        f"╚══════════════════════════════════╝\n\n"
        f"🌟 Selamat datang, petualang!\n"
        f"Pilih aksi dari tombol menu di bawah:"
    )

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Battle",    callback_data="menu_battle"),
            InlineKeyboardButton("🏰 Dungeon",   callback_data="menu_dungeon"),
            InlineKeyboardButton("🎒 Equipment", callback_data="menu_inventory"),
        ],
        [
            InlineKeyboardButton("🐾 Pet",       callback_data="inv_choose_pet"),
            InlineKeyboardButton("💠 Evolution", callback_data="pshop_evolution"),
            InlineKeyboardButton("⚒️ Enhance",   callback_data="enhance_main"),
        ],
        [
            InlineKeyboardButton("🛒 Shop",      callback_data="menu_shop"),
            InlineKeyboardButton("😴 Rest",      callback_data="menu_rest"),
            InlineKeyboardButton("🏅 Title",     callback_data="title_main"),
        ],
        [
            InlineKeyboardButton("📜 Profile",   callback_data="profile"),
            InlineKeyboardButton("📋 Quest",     callback_data="quest_main"),
            InlineKeyboardButton("❓ Help",      callback_data="menu_help"),
        ],
        [
            InlineKeyboardButton("🏪 Market",    callback_data="menu_market"),
            InlineKeyboardButton("📦 Transfer",  callback_data="menu_transfer"),
            InlineKeyboardButton("⚔️ War",       callback_data="war_menu"),
        ],
        [
            InlineKeyboardButton("📅 Daily",     callback_data="menu_daily"),
            InlineKeyboardButton("📖 Book",      callback_data="menu_book"),
            InlineKeyboardButton("🏆 Ranking",   callback_data="lb_level_all"),
        ],
        [
            InlineKeyboardButton("💬 Grup Official",   url=OFFICIAL_GROUP),
            InlineKeyboardButton("📢 Channel Official", url=OFFICIAL_CHANNEL),
        ],
    ]
    market_url = _get_market_channel_url()
    if market_url:
        keyboard.append([InlineKeyboardButton("🏪 Channel Market P2P", url=market_url)])

    try:
        if is_query and hasattr(update_or_query, "edit_message_text"):
            await update_or_query.edit_message_text(
                text, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif hasattr(update_or_query, "message") and update_or_query.message:
            await update_or_query.message.reply_text(
                text, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif hasattr(update_or_query, "reply_text"):
            await update_or_query.reply_text(
                text, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception:
        pass
