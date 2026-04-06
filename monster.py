"""
monster.py — Data monster, boss, dan dungeon untuk Legends of Eternity
Berisi: MONSTERS, BOSSES, DUNGEONS + helper functions
"""

import random
import copy

# ════════════════════════════════════════════════════════════════
#  MONSTERS  (dipakai di battle biasa & book)
#  Fields wajib: name, emoji, hp, atk, def, exp, gold (tuple), tier
# ════════════════════════════════════════════════════════════════
MONSTERS = {
    # ── Tier 1 — Pemula (Level 1-9) ──────────────────────────────
    "Goblin": {
        "name": "Goblin", "emoji": "👺",
        "hp": 60,  "atk": 10, "def": 4,
        "exp": 18, "gold": (5, 15),
        "tier": 1,
    },
    "Slime": {
        "name": "Slime", "emoji": "🟢",
        "hp": 45,  "atk": 7,  "def": 2,
        "exp": 12, "gold": (3, 10),
        "tier": 1,
    },
    "Bat": {
        "name": "Bat", "emoji": "🦇",
        "hp": 40,  "atk": 9,  "def": 2,
        "exp": 14, "gold": (4, 12),
        "tier": 1,
    },
    "Zombie": {
        "name": "Zombie", "emoji": "🧟",
        "hp": 75,  "atk": 12, "def": 5,
        "exp": 20, "gold": (6, 18),
        "tier": 1,
    },
    "Skeleton": {
        "name": "Skeleton", "emoji": "💀",
        "hp": 55,  "atk": 11, "def": 3,
        "exp": 16, "gold": (5, 14),
        "tier": 1,
    },
    "Rat King": {
        "name": "Rat King", "emoji": "🐀",
        "hp": 65,  "atk": 8,  "def": 3,
        "exp": 15, "gold": (4, 13),
        "tier": 1,
    },

    # ── Tier 2 — Menengah (Level 10-19) ──────────────────────────
    "Orc Warrior": {
        "name": "Orc Warrior", "emoji": "👹",
        "hp": 140, "atk": 22, "def": 12,
        "exp": 48, "gold": (18, 40),
        "tier": 2,
    },
    "Dark Elf": {
        "name": "Dark Elf", "emoji": "🧝",
        "hp": 110, "atk": 28, "def": 8,
        "exp": 52, "gold": (20, 45),
        "tier": 2,
    },
    "Werewolf": {
        "name": "Werewolf", "emoji": "🐺",
        "hp": 160, "atk": 25, "def": 10,
        "exp": 55, "gold": (22, 48),
        "tier": 2,
    },
    "Vampire": {
        "name": "Vampire", "emoji": "🧛",
        "hp": 130, "atk": 30, "def": 9,
        "exp": 60, "gold": (25, 55),
        "tier": 2,
    },
    "Golem": {
        "name": "Golem", "emoji": "🗿",
        "hp": 200, "atk": 18, "def": 20,
        "exp": 58, "gold": (20, 42),
        "tier": 2,
    },
    "Forest Troll": {
        "name": "Forest Troll", "emoji": "🧌",
        "hp": 175, "atk": 24, "def": 14,
        "exp": 50, "gold": (19, 44),
        "tier": 2,
    },

    # ── Tier 3 — Kuat (Level 20-29) ──────────────────────────────
    "Demon Knight": {
        "name": "Demon Knight", "emoji": "😈",
        "hp": 280, "atk": 45, "def": 25,
        "exp": 120, "gold": (55, 110),
        "tier": 3,
    },
    "Shadow Assassin": {
        "name": "Shadow Assassin", "emoji": "🥷",
        "hp": 220, "atk": 55, "def": 18,
        "exp": 130, "gold": (60, 120),
        "tier": 3,
    },
    "Ice Witch": {
        "name": "Ice Witch", "emoji": "🧙",
        "hp": 200, "atk": 60, "def": 15,
        "exp": 135, "gold": (62, 125),
        "tier": 3,
    },
    "Stone Colossus": {
        "name": "Stone Colossus", "emoji": "🗽",
        "hp": 350, "atk": 40, "def": 35,
        "exp": 115, "gold": (50, 100),
        "tier": 3,
    },
    "Chaos Mage": {
        "name": "Chaos Mage", "emoji": "🔮",
        "hp": 210, "atk": 65, "def": 12,
        "exp": 140, "gold": (65, 130),
        "tier": 3,
    },
    "Lava Hound": {
        "name": "Lava Hound", "emoji": "🔥",
        "hp": 260, "atk": 50, "def": 22,
        "exp": 125, "gold": (58, 115),
        "tier": 3,
    },

    # ── Tier 4 — Epik (Level 30+) ─────────────────────────────────
    "Ancient Dragon": {
        "name": "Ancient Dragon", "emoji": "🐉",
        "hp": 600, "atk": 90, "def": 50,
        "exp": 320, "gold": (150, 300),
        "tier": 4,
    },
    "Lich Lord": {
        "name": "Lich Lord", "emoji": "☠️",
        "hp": 520, "atk": 100, "def": 40,
        "exp": 340, "gold": (160, 320),
        "tier": 4,
    },
    "Abyssal Titan": {
        "name": "Abyssal Titan", "emoji": "👾",
        "hp": 700, "atk": 85, "def": 60,
        "exp": 310, "gold": (140, 280),
        "tier": 4,
    },
    "Void Dragon": {
        "name": "Void Dragon", "emoji": "🌑",
        "hp": 580, "atk": 95, "def": 45,
        "exp": 330, "gold": (155, 310),
        "tier": 4,
    },
    "Infernal Overlord": {
        "name": "Infernal Overlord", "emoji": "🌋",
        "hp": 650, "atk": 105, "def": 55,
        "exp": 360, "gold": (170, 340),
        "tier": 4,
    },
}

# ════════════════════════════════════════════════════════════════
#  BOSSES  (dipakai di dungeon, group boss, book)
#  Fields wajib: name, emoji, hp, atk, def, exp, gold (tuple),
#                desc, special, regen_pct, berserk_threshold,
#                berserk_atk_mult, counter_pct
# ════════════════════════════════════════════════════════════════
BOSSES = {
    "goblin_king": {
        "name": "Goblin King", "emoji": "👺",
        "hp": 500,  "atk": 35, "def": 18,
        "exp": 200, "gold": (80, 160),
        "desc": "Raja para goblin yang kejam dan rakus harta.",
        "special": "Memanggil 3 goblin tambahan setiap 5 ronde.",
        "regen_pct": 0.02,
        "berserk_threshold": 0.40,
        "berserk_atk_mult": 2.0,
        "counter_pct": 0.20,
        "world_boss": False,
    },
    "forest_witch": {
        "name": "Forest Witch", "emoji": "🧙",
        "hp": 800,  "atk": 55, "def": 22,
        "exp": 350, "gold": (130, 260),
        "desc": "Penyihir tua yang menguasai sihir hutan gelap.",
        "special": "Poison Storm — racun area yang menguras HP setiap ronde.",
        "regen_pct": 0.025,
        "berserk_threshold": 0.35,
        "berserk_atk_mult": 2.2,
        "counter_pct": 0.25,
        "world_boss": False,
    },
    "dark_lord": {
        "name": "Dark Lord", "emoji": "😈",
        "hp": 1400, "atk": 85, "def": 40,
        "exp": 650, "gold": (240, 480),
        "desc": "Penguasa kegelapan yang telah berkuasa selama ribuan tahun.",
        "special": "Dark Pulse — serangan gelap yang menembus armor.",
        "regen_pct": 0.03,
        "berserk_threshold": 0.45,
        "berserk_atk_mult": 2.5,
        "counter_pct": 0.35,
        "world_boss": False,
    },
    "labyrinth_guardian": {
        "name": "Labyrinth Guardian", "emoji": "🐂",
        "hp": 2200, "atk": 110, "def": 60,
        "exp": 1000, "gold": (380, 760),
        "desc": "Penjaga labirin bawah tanah yang tak pernah tidur.",
        "special": "Charge — men突破 pertahanan musuh, DEF diabaikan 50%.",
        "regen_pct": 0.03,
        "berserk_threshold": 0.50,
        "berserk_atk_mult": 2.8,
        "counter_pct": 0.40,
        "world_boss": False,
    },
    "fire_dragon": {
        "name": "Fire Dragon", "emoji": "🐲",
        "hp": 3500, "atk": 150, "def": 80,
        "exp": 1800, "gold": (650, 1300),
        "desc": "Naga api purba dari Gunung Api Abadi, penjaga puncak terkuat.",
        "special": "Dragon Breath — nafas api dahsyat yang membakar semua musuh.",
        "regen_pct": 0.04,
        "berserk_threshold": 0.55,
        "berserk_atk_mult": 3.0,
        "counter_pct": 0.45,
        "world_boss": True,
    },
}

# ════════════════════════════════════════════════════════════════
#  DUNGEONS  (dipakai di dungeon handler, group boss, book)
#  Fields wajib: name, emoji, desc, min_level, floor_count,
#                boss (key ke BOSSES), monsters (list nama)
# ════════════════════════════════════════════════════════════════
DUNGEONS = {
    1: {
        "name": "Gua Goblin",
        "emoji": "🕳️",
        "desc": "Gua gelap yang penuh dengan goblin liar. Cocok untuk pemula.",
        "min_level": 1,
        "floor_count": 5,
        "boss": "goblin_king",
        "monsters": ["Goblin", "Slime", "Rat King", "Bat"],
    },
    2: {
        "name": "Hutan Tersesat",
        "emoji": "🌲",
        "desc": "Hutan misterius tempat para pengembara tersesat selamanya.",
        "min_level": 5,
        "floor_count": 7,
        "boss": "forest_witch",
        "monsters": ["Bat", "Werewolf", "Forest Troll", "Dark Elf"],
    },
    3: {
        "name": "Istana Kegelapan",
        "emoji": "🏚️",
        "desc": "Istana kuno yang dipenuhi undead dan iblis kegelapan.",
        "min_level": 12,
        "floor_count": 10,
        "boss": "dark_lord",
        "monsters": ["Zombie", "Skeleton", "Vampire", "Demon Knight"],
    },
    4: {
        "name": "Labirin Bawah Tanah",
        "emoji": "🗺️",
        "desc": "Labirin raksasa bawah tanah dengan monster-monster kuat.",
        "min_level": 20,
        "floor_count": 12,
        "boss": "labyrinth_guardian",
        "monsters": ["Golem", "Stone Colossus", "Shadow Assassin", "Orc Warrior"],
    },
    5: {
        "name": "Gunung Api Abadi",
        "emoji": "🌋",
        "desc": "Gunung api yang selalu menyala, tempat tinggal naga api purba.",
        "min_level": 30,
        "floor_count": 15,
        "boss": "fire_dragon",
        "monsters": ["Lava Hound", "Chaos Mage", "Ancient Dragon", "Infernal Overlord"],
    },
}


# ════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════

def _scale_monster(base: dict, player_level: int) -> dict:
    """
    Scale-up monster stats berdasarkan level pemain.
    Membuat pertarungan tetap menantang di level tinggi.
    """
    m = copy.deepcopy(base)
    # Mulai scale dari level 5 ke atas
    if player_level > 5:
        factor = 1.0 + (player_level - 5) * 0.08
        m["hp"]  = int(m["hp"]  * factor)
        m["atk"] = int(m["atk"] * max(1.0, factor * 0.7))
        m["def"] = int(m["def"] * max(1.0, factor * 0.5))
        m["exp"] = int(m["exp"] * factor)
        # Scale gold range
        g_min, g_max = m["gold"]
        m["gold"] = (int(g_min * factor), int(g_max * factor))
    m["current_hp"] = m["hp"]
    return m


def get_random_monster(player_level: int) -> dict:
    """
    Kembalikan monster acak yang sesuai level pemain.
    Monster tier dipilih berdasarkan level, lalu di-scale.
    """
    if player_level < 10:
        tier_weights = {1: 80, 2: 20, 3: 0,  4: 0}
    elif player_level < 20:
        tier_weights = {1: 20, 2: 60, 3: 20, 4: 0}
    elif player_level < 30:
        tier_weights = {1: 5,  2: 25, 3: 60, 4: 10}
    else:
        tier_weights = {1: 0,  2: 10, 3: 40, 4: 50}

    # Pilih tier berdasarkan bobot
    tiers  = list(tier_weights.keys())
    weights = list(tier_weights.values())
    chosen_tier = random.choices(tiers, weights=weights, k=1)[0]

    # Filter monster sesuai tier
    pool = [(name, m) for name, m in MONSTERS.items() if m["tier"] == chosen_tier]
    if not pool:
        # fallback: ambil tier 1
        pool = [(name, m) for name, m in MONSTERS.items() if m["tier"] == 1]

    name, base = random.choice(pool)
    monster = _scale_monster(base, player_level)
    monster["name"] = name  # pastikan name tersimpan
    return monster


def get_boss(boss_id: str, scale_level: int = 1, floor: int = 1) -> dict:
    """
    Kembalikan data boss berdasarkan boss_id, di-scale sesuai level & lantai.
    floor digunakan untuk scaling boss dungeon (lantai terakhir = lebih kuat).
    """
    base = BOSSES.get(boss_id)
    if not base:
        # fallback: goblin_king
        base = BOSSES["goblin_king"]

    boss = copy.deepcopy(base)

    # Scale berdasarkan level pemain
    if scale_level > 1:
        factor = 1.0 + (scale_level - 1) * 0.12
        boss["hp"]  = int(boss["hp"]  * factor)
        boss["atk"] = int(boss["atk"] * max(1.0, factor * 0.75))
        boss["def"] = int(boss["def"] * max(1.0, factor * 0.6))
        boss["exp"] = int(boss["exp"] * factor)
        g_min, g_max = boss["gold"]
        boss["gold"] = (int(g_min * factor), int(g_max * factor))

    # Bonus scaling per lantai dungeon (setiap lantai +5% stats)
    if floor > 1:
        floor_factor = 1.0 + (floor - 1) * 0.05
        boss["hp"]  = int(boss["hp"]  * floor_factor)
        boss["atk"] = int(boss["atk"] * floor_factor)

    boss["max_hp"]    = boss["hp"]
    boss["current_hp"] = boss["hp"]
    return boss


def get_dungeon_monsters(dungeon_id: int, player_level: int, floor: int = 1) -> dict:
    """
    Kembalikan monster acak dari dungeon tertentu, di-scale berdasarkan
    level pemain dan lantai dungeon.
    """
    dg = DUNGEONS.get(dungeon_id)
    if not dg:
        # fallback ke monster random biasa
        return get_random_monster(player_level)

    monster_names = dg.get("monsters", [])
    if not monster_names:
        return get_random_monster(player_level)

    name = random.choice(monster_names)
    base = MONSTERS.get(name)
    if not base:
        return get_random_monster(player_level)

    # Scale level + floor bonus
    monster = _scale_monster(base, player_level)

    # Bonus per lantai (setiap lantai +8% stats)
    if floor > 1:
        floor_factor = 1.0 + (floor - 1) * 0.08
        monster["hp"]         = int(monster["hp"]  * floor_factor)
        monster["atk"]        = int(monster["atk"] * floor_factor)
        monster["current_hp"] = monster["hp"]

    return monster
