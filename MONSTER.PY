# ═══════════════════════════════════════════════════════════════
#  LEGENDS OF ETERNITY — Monsters, Dungeons & Bosses
# ═══════════════════════════════════════════════════════════════
import random

# ─── REGULAR MONSTERS ───────────────────────────────────────────
MONSTERS = {
    # Tier 1 (Lv 1-5)
    "Slime":          {"emoji":"🟢","hp":50, "atk":8,  "def":3,  "exp":12,"gold":(4,9),   "tier":1,"image":None},
    "Goblin":         {"emoji":"👺","hp":70, "atk":12, "def":5,  "exp":18,"gold":(6,14),  "tier":1,"image":None},
    "Bat":            {"emoji":"🦇","hp":45, "atk":10, "def":2,  "exp":10,"gold":(3,8),   "tier":1,"image":None},
    "Giant Rat":      {"emoji":"🐀","hp":60, "atk":9,  "def":4,  "exp":14,"gold":(4,10),  "tier":1,"image":None},
    "Forest Spider":  {"emoji":"🕷️","hp":55, "atk":11, "def":3,  "exp":16,"gold":(5,12),  "tier":1,"image":None},
    "Kobold":         {"emoji":"🦎","hp":65, "atk":10, "def":4,  "exp":15,"gold":(5,11),  "tier":1,"image":None},

    # Tier 2 (Lv 6-14)
    "Orc Warrior":    {"emoji":"👹","hp":130,"atk":20, "def":12, "exp":45,"gold":(15,30),  "tier":2,"image":None},
    "Skeleton":       {"emoji":"💀","hp":110,"atk":18, "def":8,  "exp":38,"gold":(12,25),  "tier":2,"image":None},
    "Dark Elf":       {"emoji":"🧝","hp":120,"atk":22, "def":9,  "exp":48,"gold":(18,32),  "tier":2,"image":None},
    "Troll":          {"emoji":"🧌","hp":160,"atk":21, "def":15, "exp":55,"gold":(20,38),  "tier":2,"image":None},
    "Harpy":          {"emoji":"🦅","hp":100,"atk":24, "def":7,  "exp":50,"gold":(16,30),  "tier":2,"image":None},
    "Minotaur":       {"emoji":"🐂","hp":180,"atk":26, "def":14, "exp":65,"gold":(22,40),  "tier":2,"image":None},

    # Tier 3 (Lv 15-25)
    "Werewolf":       {"emoji":"🐺","hp":220,"atk":32, "def":16, "exp":90,"gold":(30,55),  "tier":3,"image":None},
    "Vampire Lord":   {"emoji":"🧛","hp":200,"atk":36, "def":14, "exp":95,"gold":(35,60),  "tier":3,"image":None},
    "Demon Knight":   {"emoji":"😈","hp":250,"atk":38, "def":20, "exp":105,"gold":(40,70), "tier":3,"image":None},
    "Ice Golem":      {"emoji":"🧊","hp":280,"atk":30, "def":28, "exp":110,"gold":(42,72), "tier":3,"image":None},
    "Shadow Beast":   {"emoji":"🌑","hp":210,"atk":40, "def":12, "exp":100,"gold":(38,65), "tier":3,"image":None},
    "Basilisk":       {"emoji":"🐍","hp":260,"atk":34, "def":22, "exp":108,"gold":(40,68), "tier":3,"image":None},

    # Tier 4 (Lv 26+)
    "Ancient Wyvern": {"emoji":"🐲","hp":380,"atk":52, "def":30, "exp":160,"gold":(60,100),"tier":4,"image":None},
    "Death Knight":   {"emoji":"⚔️","hp":420,"atk":55, "def":34, "exp":175,"gold":(65,110),"tier":4,"image":None},
    "Abyssal Demon":  {"emoji":"🌀","hp":400,"atk":58, "def":28, "exp":180,"gold":(70,120),"tier":4,"image":None},
    "Chimera":        {"emoji":"🦁","hp":460,"atk":50, "def":36, "exp":185,"gold":(72,125),"tier":4,"image":None},
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
        "hp": 800,
        "atk": 35,
        "def": 18,
        "exp": 400,
        "gold": (150, 280),
        "image": None,
        "desc": "Raja goblin yang kejam dan licik",
        "special": "Memanggil bala bantuan goblin kecil!"
    },
    "forest_witch": {
        "name": "Forest Witch",
        "emoji": "🧙",
        "hp": 950,
        "atk": 45,
        "def": 22,
        "exp": 520,
        "gold": (200, 350),
        "image": None,
        "desc": "Penyihir hutan yang menguasai racun",
        "special": "Mengutuk pemain dengan racun mematikan!"
    },
    "dark_lord": {
        "name": "Dark Lord Malachar",
        "emoji": "👿",
        "hp": 1200,
        "atk": 58,
        "def": 30,
        "exp": 700,
        "gold": (280, 450),
        "image": None,
        "desc": "Penguasa kegelapan yang tak terkalahkan",
        "special": "Menghisap jiwa dan memulihkan HP!"
    },
    "labyrinth_guardian": {
        "name": "Labyrinth Guardian",
        "emoji": "🏺",
        "hp": 1500,
        "atk": 70,
        "def": 38,
        "exp": 900,
        "gold": (350, 550),
        "image": None,
        "desc": "Penjaga labirin berusia ribuan tahun",
        "special": "Serangan area yang menghancurkan!"
    },
    "elder_dragon": {
        "name": "Elder Dragon Ignaroth",
        "emoji": "🐉",
        "hp": 2000,
        "atk": 88,
        "def": 45,
        "exp": 1400,
        "gold": (500, 800),
        "image": None,
        "desc": "Naga purba yang membakar seluruh kota",
        "special": "Napas api yang membakar segalanya!"
    },
    # World Boss
    "world_boss_lich": {
        "name": "Lich King Zarthorak",
        "emoji": "☠️",
        "hp": 5000,
        "atk": 120,
        "def": 60,
        "exp": 3000,
        "gold": (1000, 2000),
        "image": None,
        "desc": "Raja Lich yang membangkitkan seluruh orang mati",
        "special": "Mengaktifkan Undead Army yang mematikan!",
        "world_boss": True
    },
    "world_boss_demon_god": {
        "name": "Demon God Bael",
        "emoji": "🔴",
        "hp": 6000,
        "atk": 140,
        "def": 70,
        "exp": 4000,
        "gold": (1500, 2500),
        "image": None,
        "desc": "Dewa Iblis yang menghancurkan dunia",
        "special": "Ledakan energi hitam yang membelah langit!",
        "world_boss": True
    },
}


def get_random_monster(player_level: int) -> dict:
    if player_level <= 5:
        tier = 1
    elif player_level <= 14:
        tier = random.choices([1, 2], weights=[25, 75])[0]
    elif player_level <= 25:
        tier = random.choices([2, 3], weights=[25, 75])[0]
    else:
        tier = random.choices([3, 4], weights=[35, 65])[0]

    pool = {k: v for k, v in MONSTERS.items() if v["tier"] == tier}
    if not pool:
        pool = {k: v for k, v in MONSTERS.items() if v["tier"] == 1}

    name = random.choice(list(pool.keys()))
    m = pool[name].copy()
    m["name"] = name

    scale = 1 + (player_level - 1) * 0.06
    m["hp"]  = int(m["hp"] * scale)
    m["atk"] = int(m["atk"] * scale)
    m["def"] = int(m["def"] * scale)
    m["current_hp"] = m["hp"]
    return m


def get_dungeon_monsters(dungeon_id: int, player_level: int) -> list:
    dg = DUNGEONS.get(dungeon_id, DUNGEONS[1])
    available = dg["monsters"]
    pool = {k: v for k, v in MONSTERS.items() if k in available}
    if not pool:
        return [get_random_monster(player_level)]

    name = random.choice(list(pool.keys()))
    m = pool[name].copy()
    m["name"] = name

    scale = 1 + (player_level - 1) * 0.06
    m["hp"]  = int(m["hp"] * scale)
    m["atk"] = int(m["atk"] * scale)
    m["def"] = int(m["def"] * scale)
    m["current_hp"] = m["hp"]
    return m


def get_boss(boss_id: str, scale_level: int = 1) -> dict:
    boss = BOSSES.get(boss_id, BOSSES["goblin_king"]).copy()
    boss["boss_id"] = boss_id
    scale = 1 + (scale_level - 1) * 0.08
    boss["hp"]  = int(boss["hp"] * scale)
    boss["atk"] = int(boss["atk"] * scale)
    boss["def"] = int(boss["def"] * scale)
    boss["current_hp"] = boss["hp"]
    boss["max_hp"] = boss["hp"]
    return boss
