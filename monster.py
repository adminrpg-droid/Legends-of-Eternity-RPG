import random

# ─── REGULAR MONSTERS ───────────────────────────────────────────
MONSTERS = {
    # Tier 1 (Lv 1-5) — Lebih keras dari sebelumnya
    "Slime":          {"emoji":"🟢","hp":180,  "atk":22, "def":12, "exp":12,"gold":(4,9),   "tier":1,"image":None},
    "Goblin":         {"emoji":"👺","hp":260,  "atk":32, "def":18, "exp":18,"gold":(6,14),  "tier":1,"image":None},
    "Bat":            {"emoji":"🦇","hp":160,  "atk":28, "def":10, "exp":10,"gold":(3,8),   "tier":1,"image":None},
    "Giant Rat":      {"emoji":"🐀","hp":220,  "atk":26, "def":15, "exp":14,"gold":(4,10),  "tier":1,"image":None},
    "Forest Spider":  {"emoji":"🕷️","hp":200, "atk":30, "def":14, "exp":16,"gold":(5,12),  "tier":1,"image":None},
    "Kobold":         {"emoji":"🦎","hp":240,  "atk":28, "def":16, "exp":15,"gold":(5,11),  "tier":1,"image":None},

    # Tier 2 (Lv 6-14) — Jauh lebih keras
    "Orc Warrior":    {"emoji":"👹","hp":520,  "atk":65, "def":45, "exp":45,"gold":(15,30),  "tier":2,"image":None},
    "Skeleton":       {"emoji":"💀","hp":440,  "atk":58, "def":30, "exp":38,"gold":(12,25),  "tier":2,"image":None},
    "Dark Elf":       {"emoji":"🧝","hp":480,  "atk":72, "def":35, "exp":48,"gold":(18,32),  "tier":2,"image":None},
    "Troll":          {"emoji":"🧌","hp":640,  "atk":68, "def":55, "exp":55,"gold":(20,38),  "tier":2,"image":None},
    "Harpy":          {"emoji":"🦅","hp":400,  "atk":78, "def":28, "exp":50,"gold":(16,30),  "tier":2,"image":None},
    "Minotaur":       {"emoji":"🐂","hp":720,  "atk":85, "def":52, "exp":65,"gold":(22,40),  "tier":2,"image":None},

    # Tier 3 (Lv 15-25) — Sangat keras
    "Werewolf":       {"emoji":"🐺","hp":880,  "atk":105,"def":62, "exp":90,"gold":(30,55),  "tier":3,"image":None},
    "Vampire Lord":   {"emoji":"🧛","hp":800,  "atk":120,"def":55, "exp":95,"gold":(35,60),  "tier":3,"image":None},
    "Demon Knight":   {"emoji":"😈","hp":1000, "atk":128,"def":78, "exp":105,"gold":(40,70), "tier":3,"image":None},
    "Ice Golem":      {"emoji":"🧊","hp":1120, "atk":98, "def":105,"exp":110,"gold":(42,72), "tier":3,"image":None},
    "Shadow Beast":   {"emoji":"🌑","hp":840,  "atk":135,"def":48, "exp":100,"gold":(38,65), "tier":3,"image":None},
    "Basilisk":       {"emoji":"🐍","hp":1040, "atk":112,"def":85, "exp":108,"gold":(40,68), "tier":3,"image":None},

    # Tier 4 (Lv 26+) — Brutal
    "Ancient Wyvern": {"emoji":"🐲","hp":1520, "atk":175,"def":115,"exp":160,"gold":(60,100),"tier":4,"image":None},
    "Death Knight":   {"emoji":"⚔️","hp":1680, "atk":188,"def":128,"exp":175,"gold":(65,110),"tier":4,"image":None},
    "Abyssal Demon":  {"emoji":"🌀","hp":1600, "atk":198,"def":108,"exp":180,"gold":(70,120),"tier":4,"image":None},
    "Chimera":        {"emoji":"🦁","hp":1840, "atk":170,"def":138,"exp":185,"gold":(72,125),"tier":4,"image":None},
}

# ─── DUNGEON DEFINITIONS ─────────────────────────────────────────
DUNGEONS = {
    1: {
        "name": "Gua Goblin",
        "emoji": "🕳️",
        "min_level": 1,
        "monsters": ["Goblin", "Bat", "Giant Rat", "Forest Spider"],
        "boss": "goblin_king",
        "image": None,
        "floor_count": 5,
        "desc": "Sarang goblin yang gelap dan berbahaya"
    },
    2: {
        "name": "Hutan Tersesat",
        "emoji": "🌲",
        "min_level": 5,
        "monsters": ["Harpy", "Dark Elf", "Skeleton", "Troll"],
        "boss": "forest_witch",
        "image": None,
        "floor_count": 8,
        "desc": "Hutan misterius penuh kutukan"
    },
    3: {
        "name": "Istana Kegelapan",
        "emoji": "🏚️",
        "min_level": 12,
        "monsters": ["Vampire Lord", "Demon Knight", "Shadow Beast"],
        "boss": "dark_lord",
        "image": None,
        "floor_count": 10,
        "desc": "Istana terkutuk yang dihuni iblis"
    },
    4: {
        "name": "Labirin Bawah Tanah",
        "emoji": "🗺️",
        "min_level": 20,
        "monsters": ["Minotaur", "Ice Golem", "Basilisk", "Death Knight"],
        "boss": "labyrinth_guardian",
        "image": None,
        "floor_count": 12,
        "desc": "Labirin kuno penuh jebakan maut"
    },
    5: {
        "name": "Puncak Naga",
        "emoji": "🌋",
        "min_level": 30,
        "monsters": ["Ancient Wyvern", "Abyssal Demon", "Chimera"],
        "boss": "elder_dragon",
        "image": None,
        "floor_count": 15,
        "desc": "Sarang naga purba yang mengerikan"
    },
}

# ─── BOSS DEFINITIONS ───────────────────────────────────────────
BOSSES = {
    "goblin_king": {
        "name": "Goblin King",
        "emoji": "👑",
        "hp": 12000,
        "atk": 180,
        "def": 110,
        "exp": 800,
        "gold": (300, 560),
        "image": None,
        "desc": "Raja goblin yang kejam dan licik — hampir mustahil dikalahkan!",
        "special": "Memanggil bala bantuan goblin & serangan beruntun 3x!",
        "regen_pct": 0.03,   # Regen 3% HP tiap giliran
        "counter_pct": 0.30, # 30% chance balas serangan
    },
    "forest_witch": {
        "name": "Forest Witch",
        "emoji": "🧙",
        "hp": 18000,
        "atk": 230,
        "def": 140,
        "exp": 1100,
        "gold": (450, 750),
        "image": None,
        "desc": "Penyihir hutan yang menguasai racun — sangat berbahaya!",
        "special": "Kutukan racun mematikan + drain MP pemain!",
        "regen_pct": 0.04,
        "counter_pct": 0.35,
    },
    "dark_lord": {
        "name": "Dark Lord Malachar",
        "emoji": "👿",
        "hp": 28000,
        "atk": 295,
        "def": 175,
        "exp": 1600,
        "gold": (600, 950),
        "image": None,
        "desc": "Penguasa kegelapan abadi — hampir tak bisa dibunuh!",
        "special": "Soul Drain: hisap jiwa, heal 20% HP, + serangan chaos!",
        "regen_pct": 0.05,
        "counter_pct": 0.40,
    },
    "labyrinth_guardian": {
        "name": "Labyrinth Guardian",
        "emoji": "🏺",
        "hp": 42000,
        "atk": 360,
        "def": 215,
        "exp": 2200,
        "gold": (800, 1300),
        "image": None,
        "desc": "Penjaga labirin kuno — guardian terkuat yang pernah ada!",
        "special": "Serangan area + batu besar menghancurkan + regen masif!",
        "regen_pct": 0.06,
        "counter_pct": 0.45,
    },
    "elder_dragon": {
        "name": "Elder Dragon Ignaroth",
        "emoji": "🐉",
        "hp": 65000,
        "atk": 450,
        "def": 260,
        "exp": 3500,
        "gold": (1200, 2000),
        "image": None,
        "desc": "Naga purba dewa api — membakar seluruh peradaban!",
        "special": "Hellfire Breath: bakar semua + Berserker saat HP < 30%!",
        "regen_pct": 0.07,
        "counter_pct": 0.50,
        "berserk_threshold": 0.30,  # Berserk saat HP < 30%
        "berserk_atk_mult": 2.0,
    },
    # World Boss — SANGAT SANGAT SUSAH
    "world_boss_lich": {
        "name": "Lich King Zarthorak",
        "emoji": "☠️",
        "hp": 150000,
        "atk": 620,
        "def": 320,
        "exp": 8000,
        "gold": (3000, 6000),
        "image": None,
        "desc": "Raja Lich abadi — bahkan dewa pun gemetar di hadapannya!",
        "special": "Undead Army + Death Nova + Immortal Shield (regen 10% HP/turn)!",
        "world_boss": True,
        "regen_pct": 0.10,
        "counter_pct": 0.60,
        "berserk_threshold": 0.25,
        "berserk_atk_mult": 2.5,
    },
    "world_boss_demon_god": {
        "name": "Demon God Bael",
        "emoji": "🔴",
        "hp": 250000,
        "atk": 800,
        "def": 400,
        "exp": 12000,
        "gold": (5000, 9000),
        "image": None,
        "desc": "Dewa Iblis tertinggi — penghancur alam semesta!",
        "special": "Apocalypse Nova: serangan tak terbendung + Reality Collapse!",
        "world_boss": True,
        "regen_pct": 0.12,
        "counter_pct": 0.70,
        "berserk_threshold": 0.20,
        "berserk_atk_mult": 3.0,
    },
}


def get_random_monster(player_level: int) -> dict:
    if player_level <= 5:
        tier = 1
    elif player_level <= 14:
        tier = random.choices([1, 2], weights=[15, 85])[0]
    elif player_level <= 25:
        tier = random.choices([2, 3], weights=[15, 85])[0]
    else:
        tier = random.choices([3, 4], weights=[20, 80])[0]

    pool = {k: v for k, v in MONSTERS.items() if v["tier"] == tier}
    if not pool:
        pool = {k: v for k, v in MONSTERS.items() if v["tier"] == 1}

    name = random.choice(list(pool.keys()))
    m = pool[name].copy()
    m["name"] = name

    # Scaling 0.15 per level — LEBIH BRUTAL
    scale = 1 + (player_level - 1) * 0.15
    m["hp"]  = int(m["hp"] * scale)
    m["atk"] = int(m["atk"] * scale)
    m["def"] = int(m["def"] * scale)
    m["current_hp"] = m["hp"]
    return m


def get_dungeon_monsters(dungeon_id: int, player_level: int, floor: int = 1) -> dict:
    """Semakin tinggi floor → monster makin keras (+10% per floor)."""
    dg = DUNGEONS.get(dungeon_id, DUNGEONS[1])
    available = dg["monsters"]
    pool = {k: v for k, v in MONSTERS.items() if k in available}
    if not pool:
        return get_random_monster(player_level)

    name = random.choice(list(pool.keys()))
    m = pool[name].copy()
    m["name"] = name

    # Base scaling per level + floor scaling (+10% per floor)
    level_scale = 1 + (player_level - 1) * 0.18
    floor_scale = 1 + (floor - 1) * 0.10
    scale = level_scale * floor_scale

    m["hp"]  = int(m["hp"]  * scale)
    m["atk"] = int(m["atk"] * scale)
    m["def"] = int(m["def"] * scale)
    m["current_hp"] = m["hp"]
    m["floor"] = floor
    return m


def get_boss(boss_id: str, scale_level: int = 1, floor: int = None) -> dict:
    """Boss scaling per level DAN floor (+15% per floor untuk boss)."""
    boss = BOSSES.get(boss_id, BOSSES["goblin_king"]).copy()
    boss["boss_id"] = boss_id

    level_scale = 1 + (scale_level - 1) * 0.20
    floor_scale = 1 + (floor - 1) * 0.15 if floor is not None else 1.0
    scale = level_scale * floor_scale

    boss["hp"]  = int(boss["hp"]  * scale)
    boss["atk"] = int(boss["atk"] * scale)
    boss["def"] = int(boss["def"] * scale)
    boss["current_hp"] = boss["hp"]
    boss["max_hp"]     = boss["hp"]
    return boss
