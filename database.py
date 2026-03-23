import json
import os
import time
from typing import Optional

DB_PATH  = "data/players.json"
MKT_PATH = "data/market.json"

ADMIN_IDS = [
    # Tambahkan Telegram ID admin di sini
    577381,  # ganti dengan ID admin kamu
]

# ─── I/O ────────────────────────────────────────────────────────
def _load(path=DB_PATH) -> dict:
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def _save(data: dict, path=DB_PATH):
    os.makedirs("data", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─── PLAYER CRUD ────────────────────────────────────────────────
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

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ─── CHARACTER CREATION ─────────────────────────────────────────
CLASS_STATS = {
    "warrior": {
        "hp": 200, "max_hp": 200,
        "mp": 60,  "max_mp": 60,
        "atk": 22, "def": 18, "spd": 8,
        "crit": 10,
        "skill": "⚔️ Slash Storm",
        "skill_desc": "Serang musuh 3x berturut-turut",
        "emoji": "⚔️",
        "gender_m": "Pejuang", "gender_f": "Ksatria Wanita",
        "lore": "Petarung tangguh yang mengandalkan kekuatan fisik"
    },
    "mage": {
        "hp": 120, "max_hp": 120,
        "mp": 160, "max_mp": 160,
        "atk": 30, "def": 8, "spd": 10,
        "crit": 12,
        "skill": "🔥 Inferno",
        "skill_desc": "Ledakan api yang membakar musuh",
        "emoji": "🔮",
        "gender_m": "Penyihir", "gender_f": "Penyihir Wanita",
        "lore": "Pengguna sihir dengan kekuatan destruktif tertinggi"
    },
    "archer": {
        "hp": 150, "max_hp": 150,
        "mp": 90,  "max_mp": 90,
        "atk": 26, "def": 12, "spd": 20,
        "crit": 18,
        "skill": "🏹 Arrow Storm",
        "skill_desc": "Hujan anak panah yang menghujam musuh",
        "emoji": "🏹",
        "gender_m": "Pemanah", "gender_f": "Pemanah Wanita",
        "lore": "Pemburu cepat dengan ketepatan bidikan luar biasa"
    },
    "rogue": {
        "hp": 140, "max_hp": 140,
        "mp": 80,  "max_mp": 80,
        "atk": 32, "def": 10, "spd": 24,
        "crit": 25,
        "skill": "🌑 Shadow Strike",
        "skill_desc": "Serangan dari bayangan dengan critical tinggi",
        "emoji": "🗡️",
        "gender_m": "Pengembara", "gender_f": "Pembunuh Bayangan",
        "lore": "Pembunuh siluman yang selalu menyerang dari kegelapan"
    },
    "assassin": {
        "hp": 130, "max_hp": 130,
        "mp": 85,  "max_mp": 85,
        "atk": 36, "def": 9, "spd": 28,
        "crit": 30,
        "skill": "💀 Death Mark",
        "skill_desc": "Menandai musuh, serangan berikut x3 damage",
        "emoji": "💉",
        "gender_m": "Pembunuh Bayaran", "gender_f": "Pembunuh Bayaran Wanita",
        "lore": "Pembunuh terlatih yang mengakhiri target dalam sekejap"
    },
    "necromancer": {
        "hp": 115, "max_hp": 115,
        "mp": 180, "max_mp": 180,
        "atk": 28, "def": 7, "spd": 9,
        "crit": 14,
        "skill": "💜 Soul Drain",
        "skill_desc": "Menghisap jiwa musuh, memulihkan HP",
        "emoji": "💀",
        "gender_m": "Pemanggil Arwah", "gender_f": "Penyihir Gelap",
        "lore": "Penguasa kematian yang membangkitkan arwah sebagai senjata"
    },
}


def create_player(user_id: int, name: str, char_class: str, gender: str, telegram_username: str = "") -> dict:
    stats = CLASS_STATS.get(char_class, CLASS_STATS["warrior"])
    now = time.time()

    player = {
        "user_id": user_id,
        "telegram_id": user_id,
        "telegram_username": telegram_username,
        "name": name,
        "gender": gender,
        "class": char_class,
        "emoji": stats["emoji"],
        "level": 1,
        "exp": 0,
        "exp_needed": 120,
        "coin": 0,
        "diamond": 0,
        "hp": stats["hp"],
        "max_hp": stats["max_hp"],
        "mp": stats["mp"],
        "max_mp": stats["max_mp"],
        "atk": stats["atk"],
        "def": stats["def"],
        "spd": stats["spd"],
        "crit": stats["crit"],
        "skill": stats["skill"],
        "skill_desc": stats["skill_desc"],
        "skill_cooldown": 0,
        "kills": 0,
        "boss_kills": 0,
        "dungeon_clears": 0,
        "inventory": {
            "health_potion": 2,
            "mana_potion": 1,
        },
        "equipment": {
            "weapon": None,
            "armor": None,
        },
        "vip": {
            "active": False,
            "tier": None,
            "expires": 0,
        },
        "wins": 0,
        "losses": 0,
        "created_at": now,
        "last_daily": 0,
        "daily_streak": 0,
        "transfer_weekly": 0,
        "transfer_week_reset": now,
        "quest_progress": {},
        "skill_points": 0,
        "passive_skills": [],
        "achievements": [],
    }

    save_player(user_id, player)
    return player


# ─── LEVEL UP ───────────────────────────────────────────────────
def level_up(player: dict) -> tuple:
    leveled = False
    levels_gained = 0
    while player["exp"] >= player["exp_needed"]:
        player["exp"] -= player["exp_needed"]
        player["level"] += 1
        player["exp_needed"] = int(player["exp_needed"] * 1.35)
        levels_gained += 1

        # Kecil stat increase per level (no cap)
        player["max_hp"] += 8
        player["max_mp"] += 5
        player["atk"]    += 2
        player["def"]    += 1
        player["spd"]    += 1
        player["hp"] = player["max_hp"]
        player["mp"] = player["max_mp"]

        # Skill point setiap 3 level
        if player["level"] % 3 == 0:
            player["skill_points"] = player.get("skill_points", 0) + 1

        leveled = True

    return player, leveled, levels_gained


# ─── VIP SYSTEM ─────────────────────────────────────────────────
def apply_vip(player: dict, vip_tier: str, effects: dict, duration_days: int) -> dict:
    """Apply VIP effects to player."""
    # Remove old VIP effects if any
    if player["vip"].get("active") and player["vip"].get("tier"):
        remove_vip(player)

    player["vip"]["active"] = True
    player["vip"]["tier"] = vip_tier
    player["vip"]["expires"] = time.time() + duration_days * 86400
    player["vip"]["effects"] = effects

    player["max_hp"] += effects.get("max_hp_bonus", 0)
    player["max_mp"] += effects.get("max_mp_bonus", 0)
    player["atk"]    += effects.get("atk_bonus", 0)
    player["crit"]   = player.get("crit", 10) + effects.get("crit_bonus", 0)
    player["hp"] = min(player["hp"] + effects.get("max_hp_bonus", 0), player["max_hp"])

    return player


def remove_vip(player: dict) -> dict:
    effects = player["vip"].get("effects", {})
    player["max_hp"] -= effects.get("max_hp_bonus", 0)
    player["max_mp"] -= effects.get("max_mp_bonus", 0)
    player["atk"]    -= effects.get("atk_bonus", 0)
    player["crit"]   = max(5, player.get("crit", 10) - effects.get("crit_bonus", 0))
    player["hp"] = min(player["hp"], player["max_hp"])
    player["vip"] = {"active": False, "tier": None, "expires": 0}
    return player


def check_vip_expiry(player: dict) -> dict:
    if player["vip"].get("active") and time.time() > player["vip"].get("expires", 0):
        player = remove_vip(player)
    return player


# ─── MARKET ─────────────────────────────────────────────────────
def get_market() -> dict:
    return _load(MKT_PATH)

def save_market(data: dict):
    _save(data, MKT_PATH)

def add_market_listing(seller_id: int, seller_name: str, item_id: str, item_data: dict, price: int) -> str:
    market = get_market()
    listing_id = f"{seller_id}_{item_id}_{int(time.time())}"
    market[listing_id] = {
        "seller_id": seller_id,
        "seller_name": seller_name,
        "item_id": item_id,
        "item_data": item_data,
        "price": price,
        "listed_at": time.time(),
    }
    save_market(market)
    return listing_id

def remove_market_listing(listing_id: str) -> dict:
    market = get_market()
    listing = market.pop(listing_id, None)
    save_market(market)
    return listing
