"""
database.py — Model & CRUD untuk Legends of Eternity v5
"""
import json
import os
import time
from typing import Optional

# ─── Paths ──────────────────────────────────────────────────────
DB_PATH    = "data/players.json"
MKT_PATH   = "data/market.json"
ADMIN_PATH = "data/admins.json"
BAN_PATH   = "data/banned.json"

# ─── Super Admin (tidak bisa dihapus/di-ban via command) ─────────
SUPER_ADMIN_IDS = [
    577381,   # ← Ganti dengan Telegram ID kamu
]

# ════════════════════════════════════════════════════════════════
#  I/O
# ════════════════════════════════════════════════════════════════
def _load(path: str = DB_PATH) -> dict:
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data: dict, path: str = DB_PATH):
    os.makedirs("data", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ════════════════════════════════════════════════════════════════
#  ADMIN MANAGEMENT
# ════════════════════════════════════════════════════════════════
def _load_admins() -> list:
    return _load(ADMIN_PATH).get("admin_ids", [])

def _save_admins(ids: list):
    _save({"admin_ids": ids}, ADMIN_PATH)

def is_admin(user_id: int) -> bool:
    return user_id in SUPER_ADMIN_IDS or user_id in _load_admins()

def is_super_admin(user_id: int) -> bool:
    return user_id in SUPER_ADMIN_IDS

def add_admin(user_id: int) -> bool:
    if is_admin(user_id):
        return False
    ids = _load_admins()
    ids.append(user_id)
    _save_admins(ids)
    return True

def remove_admin(user_id: int) -> bool:
    if user_id in SUPER_ADMIN_IDS:
        return False
    ids = _load_admins()
    if user_id not in ids:
        return False
    ids.remove(user_id)
    _save_admins(ids)
    return True

def get_all_admins() -> list:
    extra = [a for a in _load_admins() if a not in SUPER_ADMIN_IDS]
    return SUPER_ADMIN_IDS + extra


# ════════════════════════════════════════════════════════════════
#  BAN MANAGEMENT
# ════════════════════════════════════════════════════════════════
def _load_bans() -> dict:
    return _load(BAN_PATH)

def is_banned(user_id: int) -> bool:
    return str(user_id) in _load_bans()

def ban_player(user_id: int, reason: str = "Melanggar aturan", banned_by: int = 0) -> bool:
    if is_admin(user_id):
        return False   # Admin tidak bisa di-ban
    bans = _load_bans()
    bans[str(user_id)] = {
        "reason":    reason,
        "banned_by": banned_by,
        "banned_at": time.time(),
    }
    _save(bans, BAN_PATH)
    return True

def unban_player(user_id: int) -> bool:
    bans = _load_bans()
    key  = str(user_id)
    if key not in bans:
        return False
    del bans[key]
    _save(bans, BAN_PATH)
    return True

def get_ban_info(user_id: int) -> Optional[dict]:
    return _load_bans().get(str(user_id))


# ════════════════════════════════════════════════════════════════
#  PLAYER CRUD
# ════════════════════════════════════════════════════════════════
def get_player(user_id: int) -> Optional[dict]:
    return _load().get(str(user_id))

def save_player(user_id: int, player: dict):
    data = _load()
    data[str(user_id)] = player
    _save(data)

def player_exists(user_id: int) -> bool:
    return get_player(user_id) is not None

def get_all_players() -> dict:
    return _load()


# ════════════════════════════════════════════════════════════════
#  WEEKLY / MONTHLY TRACKING
# ════════════════════════════════════════════════════════════════
def _get_week_start() -> float:
    t = time.gmtime()
    monday = time.mktime(time.struct_time((
        t.tm_year, t.tm_mon, t.tm_mday - t.tm_wday,
        0, 0, 0, 0, 0, -1
    )))
    return monday

def _get_month_start() -> float:
    t = time.gmtime()
    return time.mktime(time.struct_time((t.tm_year, t.tm_mon, 1, 0, 0, 0, 0, 0, -1)))

def reset_weekly_if_needed(player: dict) -> dict:
    week = _get_week_start()
    if player.get("weekly_reset", 0) < week:
        player["weekly_kills"]      = 0
        player["weekly_boss_kills"] = 0
        player["weekly_coin_earned"]= 0
        player["weekly_reset"]      = week
    return player

def reset_monthly_if_needed(player: dict) -> dict:
    month = _get_month_start()
    if player.get("monthly_reset", 0) < month:
        player["monthly_kills"]      = 0
        player["monthly_boss_kills"] = 0
        player["monthly_coin_earned"]= 0
        player["monthly_reset"]      = month
    return player

def refresh_periods(player: dict) -> dict:
    player = reset_weekly_if_needed(player)
    player = reset_monthly_if_needed(player)
    return player


# ════════════════════════════════════════════════════════════════
#  CHARACTER CREATION
# ════════════════════════════════════════════════════════════════
CLASS_STATS = {
    "warrior": {
        "hp": 200, "max_hp": 200, "mp": 60,  "max_mp": 60,
        "atk": 22, "def": 18, "spd": 8, "crit": 10,
        "skill": "⚔️ Slash Storm",
        "skill_desc": "Serang musuh 3x berturut-turut",
        "emoji": "⚔️",
        "gender_m": "Pejuang", "gender_f": "Ksatria Wanita",
        "lore": "Petarung tangguh yang mengandalkan kekuatan fisik"
    },
    "mage": {
        "hp": 120, "max_hp": 120, "mp": 160, "max_mp": 160,
        "atk": 30, "def": 8, "spd": 10, "crit": 12,
        "skill": "🔥 Inferno",
        "skill_desc": "Ledakan api yang membakar musuh",
        "emoji": "🔮",
        "gender_m": "Penyihir", "gender_f": "Penyihir Wanita",
        "lore": "Pengguna sihir dengan kekuatan destruktif tertinggi"
    },
    "archer": {
        "hp": 150, "max_hp": 150, "mp": 90,  "max_mp": 90,
        "atk": 26, "def": 12, "spd": 20, "crit": 18,
        "skill": "🏹 Arrow Storm",
        "skill_desc": "Hujan anak panah yang menghujam musuh",
        "emoji": "🏹",
        "gender_m": "Pemanah", "gender_f": "Pemanah Wanita",
        "lore": "Pemburu cepat dengan ketepatan bidikan luar biasa"
    },
    "rogue": {
        "hp": 140, "max_hp": 140, "mp": 80,  "max_mp": 80,
        "atk": 32, "def": 10, "spd": 24, "crit": 25,
        "skill": "🌑 Shadow Strike",
        "skill_desc": "Serangan dari bayangan dengan critical tinggi",
        "emoji": "🗡️",
        "gender_m": "Pengembara", "gender_f": "Pembunuh Bayangan",
        "lore": "Pembunuh siluman yang selalu menyerang dari kegelapan"
    },
    "assassin": {
        "hp": 130, "max_hp": 130, "mp": 85,  "max_mp": 85,
        "atk": 36, "def": 9, "spd": 28, "crit": 30,
        "skill": "💀 Death Mark",
        "skill_desc": "Menandai musuh, serangan berikut x3 damage",
        "emoji": "💉",
        "gender_m": "Pembunuh Bayaran", "gender_f": "Pembunuh Bayaran Wanita",
        "lore": "Pembunuh terlatih yang mengakhiri target dalam sekejap"
    },
    "necromancer": {
        "hp": 115, "max_hp": 115, "mp": 180, "max_mp": 180,
        "atk": 28, "def": 7, "spd": 9, "crit": 14,
        "skill": "💜 Soul Drain",
        "skill_desc": "Menghisap jiwa musuh, memulihkan HP",
        "emoji": "💀",
        "gender_m": "Pemanggil Arwah", "gender_f": "Penyihir Gelap",
        "lore": "Penguasa kematian yang membangkitkan arwah sebagai senjata"
    },
}


def create_player(user_id: int, name: str, char_class: str,
                  gender: str, telegram_username: str = "") -> dict:
    stats = CLASS_STATS.get(char_class, CLASS_STATS["warrior"])
    now   = time.time()
    player = {
        # Identity
        "user_id":           user_id,
        "telegram_id":       user_id,
        "telegram_username": telegram_username,
        "name":              name,
        "gender":            gender,
        "class":             char_class,
        "emoji":             stats["emoji"],
        # Core stats
        "level":        1,
        "exp":          0,
        "exp_needed":   120,
        "coin":         0,
        "diamond":      0,
        "hp":           stats["hp"],
        "max_hp":       stats["max_hp"],
        "mp":           stats["mp"],
        "max_mp":       stats["max_mp"],
        "atk":          stats["atk"],
        "def":          stats["def"],
        "spd":          stats["spd"],
        "crit":         stats["crit"],
        # Skills
        "skill":          stats["skill"],
        "skill_desc":     stats["skill_desc"],
        "skill_cooldown": 0,
        "skill_points":   0,
        "passive_skills": [],
        "bought_skills":  [],
        # Records
        "kills":         0,
        "boss_kills":    0,
        "dungeon_clears":0,
        "wins":          0,
        "losses":        0,
        # Inventory & equipment
        "inventory":  {"health_potion": 2, "mana_potion": 1},
        "equipment":  {"weapon": None, "armor": None},
        # VIP
        "vip": {"active": False, "tier": None, "expires": 0},
        # Time & misc
        "created_at":         now,
        "last_daily":         0,
        "daily_streak":       0,
        "transfer_weekly":    0,
        "transfer_week_reset":now,
        "quest_progress":     {},
        "achievements":       [],
        # Weekly stats
        "weekly_kills":       0,
        "weekly_boss_kills":  0,
        "weekly_coin_earned": 0,
        "weekly_reset":       _get_week_start(),
        # Monthly stats
        "monthly_kills":       0,
        "monthly_boss_kills":  0,
        "monthly_coin_earned": 0,
        "monthly_reset":       _get_month_start(),
    }
    save_player(user_id, player)
    return player


# ════════════════════════════════════════════════════════════════
#  LEVEL UP
# ════════════════════════════════════════════════════════════════
def level_up(player: dict) -> tuple:
    leveled, levels_gained = False, 0
    while player["exp"] >= player["exp_needed"]:
        player["exp"]        -= player["exp_needed"]
        player["level"]      += 1
        player["exp_needed"]  = int(player["exp_needed"] * 1.35)
        levels_gained         += 1
        player["max_hp"] += 8
        player["max_mp"] += 5
        player["atk"]    += 2
        player["def"]    += 1
        player["spd"]    += 1
        player["hp"]  = player["max_hp"]
        player["mp"]  = player["max_mp"]
        if player["level"] % 3 == 0:
            player["skill_points"] = player.get("skill_points", 0) + 1
        leveled = True
    return player, leveled, levels_gained


# ════════════════════════════════════════════════════════════════
#  VIP SYSTEM
# ════════════════════════════════════════════════════════════════
def apply_vip(player: dict, vip_tier: str, effects: dict, duration_days: int) -> dict:
    if player["vip"].get("active") and player["vip"].get("tier"):
        player = remove_vip(player)
    player["vip"].update({
        "active":  True,
        "tier":    vip_tier,
        "expires": time.time() + duration_days * 86400,
        "effects": effects,
    })
    player["max_hp"] += effects.get("max_hp_bonus", 0)
    player["max_mp"] += effects.get("max_mp_bonus", 0)
    player["atk"]    += effects.get("atk_bonus", 0)
    player["crit"]    = player.get("crit", 10) + effects.get("crit_bonus", 0)
    player["hp"]      = min(player["hp"] + effects.get("max_hp_bonus", 0), player["max_hp"])
    return player

def remove_vip(player: dict) -> dict:
    fx = player["vip"].get("effects", {})
    player["max_hp"] -= fx.get("max_hp_bonus", 0)
    player["max_mp"] -= fx.get("max_mp_bonus", 0)
    player["atk"]    -= fx.get("atk_bonus", 0)
    player["crit"]    = max(5, player.get("crit", 10) - fx.get("crit_bonus", 0))
    player["hp"]      = min(player["hp"], player["max_hp"])
    player["vip"]     = {"active": False, "tier": None, "expires": 0}
    return player

def check_vip_expiry(player: dict) -> dict:
    if player["vip"].get("active") and time.time() > player["vip"].get("expires", 0):
        player = remove_vip(player)
    return player


# ════════════════════════════════════════════════════════════════
#  MARKET
# ════════════════════════════════════════════════════════════════
def get_market() -> dict:
    return _load(MKT_PATH)

def save_market(data: dict):
    _save(data, MKT_PATH)

def add_market_listing(seller_id: int, seller_name: str,
                       item_id: str, item_data: dict, price: int) -> str:
    market     = get_market()
    listing_id = f"{seller_id}_{item_id}_{int(time.time())}"
    market[listing_id] = {
        "seller_id":   seller_id,
        "seller_name": seller_name,
        "item_id":     item_id,
        "item_data":   item_data,
        "price":       price,
        "listed_at":   time.time(),
    }
    save_market(market)
    return listing_id

def remove_market_listing(listing_id: str) -> Optional[dict]:
    market  = get_market()
    listing = market.pop(listing_id, None)
    save_market(market)
    return listing
