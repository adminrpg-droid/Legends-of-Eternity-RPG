# ═══════════════════════════════════════════════════════════════
#  LEGENDS OF ETERNITY — Daily Login Bonus
# ═══════════════════════════════════════════════════════════════
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models.database import get_player, save_player

DAILY_REWARDS = [
    {"coin": 50,  "hp_pot": 2, "mp_pot": 1,               "day": 1},
    {"coin": 80,  "hp_pot": 2, "mp_pot": 1,               "day": 2},
    {"coin": 100, "hp_pot": 3, "mp_pot": 2,               "day": 3},
    {"coin": 130, "hp_pot": 3, "mp_pot": 2, "diamond": 2, "day": 4},
    {"coin": 160, "hp_pot": 4, "mp_pot": 3,               "day": 5},
    {"coin": 200, "hp_pot": 4, "mp_pot": 3, "diamond": 3, "day": 6},
    {"coin": 300, "hp_pot": 5, "mp_pot": 4, "diamond": 5, "day": 7},
]


async def daily_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return

    now      = time.time()
    last     = player.get("last_daily", 0)
    elapsed  = now - last
    cooldown = 86400  # 24 jam

    if elapsed < cooldown:
        remaining = int(cooldown - elapsed)
        h = remaining // 3600
        m = (remaining % 3600) // 60
        streak = player.get("daily_streak", 0)
        await update.message.reply_text(
            f"⏳ *Daily sudah diklaim!*\n\n"
            f"Kembali dalam: *{h}j {m}m*\n"
            f"🔥 Streak sekarang: {streak} hari",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Menu", callback_data="menu")
            ]])
        )
        return

    # Reset streak jika lebih dari 48 jam tidak login
    if elapsed > 172800:
        player["daily_streak"] = 0

    streak  = player.get("daily_streak", 0)
    day_idx = streak % 7
    reward  = DAILY_REWARDS[day_idx]

    # Apply rewards
    player["coin"]    = player.get("coin", 0) + reward.get("coin", 0)
    player["diamond"] = player.get("diamond", 0) + reward.get("diamond", 0)
    inv = player.setdefault("inventory", {})
    inv["health_potion"] = inv.get("health_potion", 0) + reward.get("hp_pot", 0)
    inv["mana_potion"]   = inv.get("mana_potion", 0) + reward.get("mp_pot", 0)

    player["daily_streak"] = streak + 1
    player["last_daily"]   = now
    save_player(user.id, player)

    new_streak = player["daily_streak"]
    next_day   = (day_idx + 1) % 7
    next_reward = DAILY_REWARDS[next_day]

    stars = "🌟" * (day_idx + 1)
    is_7  = (day_idx + 1) == 7
    streak_line = "🎊 *STREAK 7 HARI! Bonus maksimal!*" if is_7 else f"🔥 Streak: *{new_streak}* hari"

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║   📅  *DAILY LOGIN BONUS!*       ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"{stars}\n"
        f"{streak_line}\n\n"
        f"🎁 *Reward Hari ke-{day_idx + 1}:*\n"
        f"💰 +{reward.get('coin', 0)} Coin\n"
        f"🧪 +{reward.get('hp_pot', 0)} Health Potion\n"
        f"💧 +{reward.get('mp_pot', 0)} Mana Potion\n"
    )

    if reward.get("diamond"):
        text += f"💎 +{reward['diamond']} Diamond\n"

    text += (
        f"\n📊 *Total Kamu:*\n"
        f"💰 {player.get('coin', 0)} Coin  💎 {player.get('diamond', 0)} Diamond\n\n"
        f"⏭️ *Besok (Hari ke-{next_day + 1}):* 💰 {next_reward.get('coin', 0)} Coin"
    )

    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Menu Utama", callback_data="menu")
        ]])
    )
