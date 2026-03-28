import json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_player, save_player, check_vip_expiry, is_admin
from ui import format_profile


def _load_media() -> dict:
    path = "data/media.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _profile_action_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚔️ Battle",      callback_data="menu_battle"),
            InlineKeyboardButton("🏰 Dungeon",     callback_data="menu_dungeon"),
            InlineKeyboardButton("🎒 Equipment",   callback_data="menu_inventory"),
        ],
        [
            InlineKeyboardButton("🐾 Pet",         callback_data="menu_evolution"),
            InlineKeyboardButton("💠 Evolution",   callback_data="pshop_evolution"),
            InlineKeyboardButton("⚒️ Enhance",     callback_data="enhance_main"),
        ],
        [
            InlineKeyboardButton("🛒 Shop",        callback_data="menu_shop"),
            InlineKeyboardButton("😴 Rest",        callback_data="menu_rest"),
            InlineKeyboardButton("🏅 Title",       callback_data="title_main"),
        ],
        [
            InlineKeyboardButton("🖼️ Lihat Media", callback_data="profile_media"),
            InlineKeyboardButton("🔄 Refresh",     callback_data="profile"),
            InlineKeyboardButton("🏠 Menu",        callback_data="menu"),
        ],
    ])


async def _send_profile_media(msg, player: dict):
    """Kirim semua foto/gif terkait karakter pemain dalam 1 tempat."""
    media      = _load_media()
    equip      = player.get("equipment", {})
    char_class = player.get("class", "warrior")
    wpn_id     = equip.get("weapon", "")
    arm_id     = equip.get("armor", "")
    pet_id     = player.get("pet", "")
    skill_id   = equip.get("skill", "")

    from items import get_item, SHOP_SKILLS, PREMIUM_SKILLS, GOD_SSSR_SKILLS, PET_SHOP, GOD_SSSR_PETS

    items_to_show = []

    # Class / Special
    cls_media = media.get(f"class:{char_class}") or media.get(f"special:{char_class}")
    if cls_media:
        items_to_show.append((f"⚔️ Class: {char_class.replace('_',' ').title()}", cls_media))

    # Senjata
    if wpn_id:
        wpn_media = media.get(f"weapon:{wpn_id}") or media.get(f"item:{wpn_id}")
        if wpn_media:
            wpn_item = get_item(wpn_id)
            lbl = wpn_item["name"] if wpn_item else wpn_id
            items_to_show.append((f"🗡️ Senjata: {lbl}", wpn_media))

    # Armor
    if arm_id:
        arm_media = media.get(f"armor:{arm_id}") or media.get(f"item:{arm_id}")
        if arm_media:
            arm_item = get_item(arm_id)
            lbl = arm_item["name"] if arm_item else arm_id
            items_to_show.append((f"🛡️ Armor: {lbl}", arm_media))

    # Pet
    if pet_id:
        pet_media = media.get(f"pet:{pet_id}")
        if pet_media:
            pet_item = PET_SHOP.get(pet_id) or GOD_SSSR_PETS.get(pet_id)
            lbl = pet_item["name"] if pet_item else pet_id
            items_to_show.append((f"🐾 Pet: {lbl}", pet_media))

    # Skill
    if skill_id:
        skl_media = media.get(f"skill:{skill_id}") or media.get(f"special:{char_class}")
        if skl_media:
            skl_item = SHOP_SKILLS.get(skill_id) or PREMIUM_SKILLS.get(skill_id) or GOD_SSSR_SKILLS.get(skill_id)
            lbl = skl_item["name"] if skl_item else skill_id
            items_to_show.append((f"🔮 Skill: {lbl}", skl_media))

    if not items_to_show:
        await msg.reply_text(
            "📭 Belum ada foto/GIF yang diset untuk item kamu.\n"
            "_Admin perlu mengatur media terlebih dahulu._",
            parse_mode="Markdown"
        )
        return

    header = await msg.reply_text(
        f"🖼️ *GALERI MEDIA — {player['name']}*\n"
        f"_{len(items_to_show)} item ditemukan_",
        parse_mode="Markdown"
    )

    for label, file_id in items_to_show:
        try:
            try:
                await msg.reply_animation(animation=file_id, caption=f"*{label}*", parse_mode="Markdown")
            except Exception:
                await msg.reply_photo(photo=file_id, caption=f"*{label}*", parse_mode="Markdown")
        except Exception:
            pass


async def profile_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback profile_media — tampilkan semua foto/gif karakter."""
    query  = update.callback_query
    await query.answer()
    user   = query.from_user
    player = get_player(user.id)
    if not player:
        await query.answer("❌ Belum ada karakter!", show_alert=True)
        return
    await _send_profile_media(query.message, player)


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ── Callback (profil sendiri via inline button) ───────────────
    if hasattr(update, "callback_query") and update.callback_query:
        query  = update.callback_query
        await query.answer()
        user   = query.from_user
        player = get_player(user.id)
        if not player:
            await query.edit_message_text("❌ Belum ada karakter. /start")
            return
        player = check_vip_expiry(player)
        save_player(user.id, player)
        await query.edit_message_text(
            format_profile(player, user.id),
            parse_mode="Markdown",
            reply_markup=_profile_action_keyboard()
        )
        return

    # ── /profile command ──────────────────────────────────────────
    msg  = update.message
    user = update.effective_user

    target_user   = None
    target_player = None

    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
    elif context.args:
        try:
            uid           = int(context.args[0])
            target_player = get_player(uid)
            if target_player:
                target_user = type("U", (), {"id": uid})()
        except ValueError:
            pass

    if target_user and target_user.id != user.id:
        if is_admin(target_user.id):
            await msg.reply_text(
                "🚫 *Profil admin tidak dapat dilihat.*",
                parse_mode="Markdown"
            )
            return
        tp = target_player or get_player(target_user.id)
        if not tp:
            await msg.reply_text("❌ Pemain tersebut belum punya karakter.")
            return
        tp = check_vip_expiry(tp)
        save_player(target_user.id, tp)
        await msg.reply_text(
            format_profile(tp, target_user.id, viewer_id=user.id),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="menu")]])
        )
        return

    # ── Profil sendiri ────────────────────────────────────────────
    player = get_player(user.id)
    if not player:
        await msg.reply_text("❌ Belum ada karakter. Ketik /start")
        return
    player = check_vip_expiry(player)
    save_player(user.id, player)
    await msg.reply_text(
        format_profile(player, user.id),
        parse_mode="Markdown",
        reply_markup=_profile_action_keyboard()
    )
