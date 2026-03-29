# ─── CONSUMABLES ────────────────────────────────────────────────
CONSUMABLES = {
    "health_potion": {
        "name": "⚕️ Health Potion",
        "desc": "Pulihkan 60 HP",
        "price": 10000,
        "diamond_price": None,
        "type": "consumable",
        "effect": {"hp": 60},
        "class": None
    },
    "mana_potion": {
        "name": "🔵 Mana Potion",
        "desc": "Pulihkan 50 MP",
        "price": 10000,
        "diamond_price": None,
        "type": "consumable",
        "effect": {"mp": 50},
        "class": None
    },
    "elixir": {
        "name": "⚗️ Grand Elixir",
        "desc": "Pulihkan 150 HP & 120 MP",
        "price": 20000,
        "diamond_price": None,
        "type": "consumable",
        "effect": {"hp": 150, "mp": 120},
        "class": None
    },
    "revive_crystal": {
        "name": "💠 Revive Crystal",
        "desc": "Bangkit dengan 50% HP saat mati",
        "price": 35000,
        "diamond_price": None,
        "type": "consumable",
        "effect": {},
        "class": None
    },
    "mega_potion": {
        "name": "🌟 Mega Potion",
        "desc": "Pulihkan penuh HP",
        "price": 20000,
        "diamond_price": 3,
        "type": "consumable",
        "effect": {"hp": 9999},
        "class": None
    },
}

# ─── WEAPONS (per class) ─────────────────────────────────────────
WEAPONS = {
    # ── WARRIOR ──────────────────────────────────────────────────
    "iron_sword": {
        "name": "⚔️ Iron Sword",
        "desc": "+12 ATK",
        "price": 450000,
        "diamond_price": None,
        "type": "weapon",
        "class": "warrior",
        "rarity": "common",
        "req_level": 1,
        "stats": {"atk": 12},
        "sellable": True
    },
    "steel_blade": {
        "name": "⚔️ Steel Blade",
        "desc": "+22 ATK, +5 DEF",
        "price": 108000,
        "diamond_price": None,
        "type": "weapon",
        "class": "warrior",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"atk": 22, "def": 5},
        "sellable": True
    },
    "knights_greatsword": {
        "name": "🗡️ Knight's Greatsword",
        "desc": "+35 ATK, +10 DEF",
        "price": 216000,
        "diamond_price": None,
        "type": "weapon",
        "class": "warrior",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"atk": 35, "def": 10},
        "sellable": True
    },
    "war_hammer": {
        "name": "🔨 War Hammer",
        "desc": "+40 ATK, +20 HP",
        "price": 760000,
        "diamond_price": None,
        "type": "weapon",
        "class": "warrior",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"atk": 40, "max_hp": 20},
        "sellable": True
    },
    "titan_axe": {
        "name": "🪓 Titan Axe",
        "desc": "+55 ATK, +15 DEF, +30 HP",
        "price": 650000,
        "diamond_price": 30,
        "type": "weapon",
        "class": "warrior",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"atk": 55, "def": 15, "max_hp": 30},
        "sellable": True
    },

    # ── MAGE ─────────────────────────────────────────────────────
    "apprentice_staff": {
        "name": "🪄 Apprentice Staff",
        "desc": "+14 ATK, +20 MP",
        "price": 54000,
        "diamond_price": None,
        "type": "weapon",
        "class": "mage",
        "rarity": "common",
        "req_level": 1,
        "stats": {"atk": 14, "max_mp": 20},
        "sellable": True
    },
    "fire_staff": {
        "name": "🔥 Fire Staff",
        "desc": "+24 ATK, +40 MP",
        "price": 126000,
        "diamond_price": None,
        "type": "weapon",
        "class": "mage",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"atk": 24, "max_mp": 40},
        "sellable": True
    },
    "thunder_wand": {
        "name": "⚡ Thunder Wand",
        "desc": "+36 ATK, +60 MP",
        "price": 234000,
        "diamond_price": None,
        "type": "weapon",
        "class": "mage",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"atk": 36, "max_mp": 60},
        "sellable": True
    },
    "arcane_tome": {
        "name": "📖 Arcane Tome",
        "desc": "+42 ATK, +80 MP, +10 SPD",
        "price": 800000,
        "diamond_price": None,
        "type": "weapon",
        "class": "mage",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"atk": 42, "max_mp": 80, "spd": 10},
        "sellable": True
    },
    "crystal_scepter": {
        "name": "💎 Crystal Scepter",
        "desc": "+60 ATK, +120 MP",
        "price": 720000,
        "diamond_price": 35,
        "type": "weapon",
        "class": "mage",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"atk": 60, "max_mp": 120},
        "sellable": True
    },

    # ── ARCHER ───────────────────────────────────────────────────
    "wooden_bow": {
        "name": "🏹 Wooden Bow",
        "desc": "+10 ATK, +5 SPD",
        "price": 50400,
        "diamond_price": None,
        "type": "weapon",
        "class": "archer",
        "rarity": "common",
        "req_level": 1,
        "stats": {"atk": 10, "spd": 5},
        "sellable": True
    },
    "composite_bow": {
        "name": "🏹 Composite Bow",
        "desc": "+20 ATK, +10 SPD",
        "price": 117000,
        "diamond_price": None,
        "type": "weapon",
        "class": "archer",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"atk": 20, "spd": 10},
        "sellable": True
    },
    "elven_bow": {
        "name": "🌿 Elven Bow",
        "desc": "+32 ATK, +18 SPD",
        "price": 216000,
        "diamond_price": None,
        "type": "weapon",
        "class": "archer",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"atk": 32, "spd": 18},
        "sellable": True
    },
    "storm_crossbow": {
        "name": "⚡ Storm Crossbow",
        "desc": "+44 ATK, +22 SPD, +20 MP",
        "price": 780000,
        "diamond_price": None,
        "type": "weapon",
        "class": "archer",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"atk": 44, "spd": 22, "max_mp": 20},
        "sellable": True
    },
    "divine_longbow": {
        "name": "✨ Divine Longbow",
        "desc": "+58 ATK, +30 SPD",
        "price": 680000,
        "diamond_price": 32,
        "type": "weapon",
        "class": "archer",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"atk": 58, "spd": 30},
        "sellable": True
    },

    # ── ROGUE ────────────────────────────────────────────────────
    "rusty_dagger": {
        "name": "🔪 Rusty Dagger",
        "desc": "+11 ATK, +6 SPD",
        "price": 50400,
        "diamond_price": None,
        "type": "weapon",
        "class": "rogue",
        "rarity": "common",
        "req_level": 1,
        "stats": {"atk": 11, "spd": 6},
        "sellable": True
    },
    "shadow_dagger": {
        "name": "🌑 Shadow Dagger",
        "desc": "+22 ATK, +12 SPD",
        "price": 126000,
        "diamond_price": None,
        "type": "weapon",
        "class": "rogue",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"atk": 22, "spd": 12},
        "sellable": True
    },
    "serpent_blade": {
        "name": "🐍 Serpent Blade",
        "desc": "+34 ATK, +16 SPD",
        "price": 234000,
        "diamond_price": None,
        "type": "weapon",
        "class": "rogue",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"atk": 34, "spd": 16},
        "sellable": True
    },
    "phantom_knives": {
        "name": "👻 Phantom Knives",
        "desc": "+46 ATK, +20 SPD",
        "price": 820000,
        "diamond_price": None,
        "type": "weapon",
        "class": "rogue",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"atk": 46, "spd": 20},
        "sellable": True
    },
    "void_edge": {
        "name": "🌀 Void Edge",
        "desc": "+62 ATK, +28 SPD, +20 HP",
        "price": 700000,
        "diamond_price": 33,
        "type": "weapon",
        "class": "rogue",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"atk": 62, "spd": 28, "max_hp": 20},
        "sellable": True
    },

    # ── ASSASSIN ─────────────────────────────────────────────────
    "poison_needle": {
        "name": "💉 Poison Needle",
        "desc": "+13 ATK, +8 SPD | Serangan dasar punya 15% chance racun",
        "price": 54000,
        "diamond_price": None,
        "type": "weapon",
        "class": "assassin",
        "rarity": "common",
        "req_level": 1,
        "stats": {"atk": 13, "spd": 8},
        "special_effect": {"poison_chance": 0.15, "poison_dmg": 8, "poison_turns": 2},
        "sellable": True
    },
    "shadow_fang": {
        "name": "🦷 Shadow Fang",
        "desc": "+25 ATK, +14 SPD, +5 CRIT | Taring bayangan yang beracun",
        "price": 135000,
        "diamond_price": None,
        "type": "weapon",
        "class": "assassin",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"atk": 25, "spd": 14, "crit": 5},
        "special_effect": {"poison_chance": 0.20, "poison_dmg": 12, "poison_turns": 2},
        "sellable": True
    },
    "assassin_blade": {
        "name": "🗡️ Assassin Blade",
        "desc": "+38 ATK, +18 SPD, +8 CRIT | CRIT DMG +20%",
        "price": 252000,
        "diamond_price": None,
        "type": "weapon",
        "class": "assassin",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"atk": 38, "spd": 18, "crit": 8},
        "special_effect": {"crit_dmg_bonus": 0.20},
        "sellable": True
    },
    "nightshade_sickle": {
        "name": "🌙 Nightshade Sickle",
        "desc": "+52 ATK, +24 SPD, +12 CRIT | Serangan dari kegelapan, Bleed 3 ronde",
        "price": 840000,
        "diamond_price": None,
        "type": "weapon",
        "class": "assassin",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"atk": 52, "spd": 24, "crit": 12},
        "special_effect": {"bleed_on_hit": True, "bleed_dmg": 15, "bleed_turns": 3},
        "sellable": True
    },
    "death_scythe": {
        "name": "💀 Death Scythe",
        "desc": "+68 ATK, +32 SPD, +18 CRIT | Execute <30% HP → kill instan 20%",
        "price": 750000,
        "diamond_price": 38,
        "type": "weapon",
        "class": "assassin",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"atk": 68, "spd": 32, "crit": 18},
        "special_effect": {"execute_chance": 0.20, "execute_threshold": 0.30},
        "sellable": True
    },

    # ── REAPER ───────────────────────────────────────────────────
    "bone_staff": {
        "name": "🦴 Bone Staff",
        "desc": "+12 ATK, +25 MP",
        "price": 54000,
        "diamond_price": None,
        "type": "weapon",
        "class": "reaper",
        "rarity": "common",
        "req_level": 1,
        "stats": {"atk": 12, "max_mp": 25},
        "sellable": True
    },
    "cursed_tome": {
        "name": "📕 Cursed Tome",
        "desc": "+22 ATK, +50 MP",
        "price": 126000,
        "diamond_price": None,
        "type": "weapon",
        "class": "reaper",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"atk": 22, "max_mp": 50},
        "sellable": True
    },
    "soul_staff": {
        "name": "👁️ Soul Staff",
        "desc": "+36 ATK, +80 MP",
        "price": 243000,
        "diamond_price": None,
        "type": "weapon",
        "class": "reaper",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"atk": 36, "max_mp": 80},
        "sellable": True
    },
    "lich_scepter": {
        "name": "💜 Lich Scepter",
        "desc": "+48 ATK, +100 MP, +20 HP",
        "price": 860000,
        "diamond_price": None,
        "type": "weapon",
        "class": "reaper",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"atk": 48, "max_mp": 100, "max_hp": 20},
        "sellable": True
    },
    "doomsday_grimoire": {
        "name": "🌑 Doomsday Grimoire",
        "desc": "+64 ATK, +140 MP",
        "price": 780000,
        "diamond_price": 40,
        "type": "weapon",
        "class": "reaper",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"atk": 64, "max_mp": 140},
        "sellable": True
    },
}

# ─── ARMOR (per class) ──────────────────────────────────────────
ARMORS = {
    # ── WARRIOR ──────────────────────────────────────────────────
    "iron_armor": {
        "name": "🛡️ Iron Armor",
        "desc": "+10 DEF, +20 HP",
        "price": 63000,
        "diamond_price": None,
        "type": "armor",
        "class": "warrior",
        "rarity": "common",
        "req_level": 1,
        "stats": {"def": 10, "max_hp": 20},
        "sellable": True
    },
    "chain_mail": {
        "name": "⛓️ Chain Mail",
        "desc": "+18 DEF, +40 HP",
        "price": 135000,
        "diamond_price": None,
        "type": "armor",
        "class": "warrior",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"def": 18, "max_hp": 40},
        "sellable": True
    },
    "knight_plate": {
        "name": "🛡️ Knight Plate",
        "desc": "+28 DEF, +60 HP",
        "price": 252000,
        "diamond_price": None,
        "type": "armor",
        "class": "warrior",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"def": 28, "max_hp": 60},
        "sellable": True
    },
    "battle_fortress": {
        "name": "🏰 Battle Fortress",
        "desc": "+38 DEF, +90 HP",
        "price": 900000,
        "diamond_price": None,
        "type": "armor",
        "class": "warrior",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"def": 38, "max_hp": 90},
        "sellable": True
    },
    "dragonscale_armor": {
        "name": "🐉 Dragonscale Armor",
        "desc": "+52 DEF, +130 HP",
        "price": 850000,
        "diamond_price": 40,
        "type": "armor",
        "class": "warrior",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"def": 52, "max_hp": 130},
        "sellable": True
    },

    # ── MAGE ─────────────────────────────────────────────────────
    "cloth_robe": {
        "name": "👘 Cloth Robe",
        "desc": "+5 DEF, +30 MP",
        "price": 54000,
        "diamond_price": None,
        "type": "armor",
        "class": "mage",
        "rarity": "common",
        "req_level": 1,
        "stats": {"def": 5, "max_mp": 30},
        "sellable": True
    },
    "arcane_robe": {
        "name": "🔮 Arcane Robe",
        "desc": "+10 DEF, +60 MP",
        "price": 126000,
        "diamond_price": None,
        "type": "armor",
        "class": "mage",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"def": 10, "max_mp": 60},
        "sellable": True
    },
    "starweave_mantle": {
        "name": "✨ Starweave Mantle",
        "desc": "+16 DEF, +90 MP",
        "price": 234000,
        "diamond_price": None,
        "type": "armor",
        "class": "mage",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"def": 16, "max_mp": 90},
        "sellable": True
    },
    "void_shroud": {
        "name": "🌀 Void Shroud",
        "desc": "+24 DEF, +130 MP, +10 ATK",
        "price": 920000,
        "diamond_price": None,
        "type": "armor",
        "class": "mage",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"def": 24, "max_mp": 130, "atk": 10},
        "sellable": True
    },
    "celestial_vestment": {
        "name": "🌟 Celestial Vestment",
        "desc": "+35 DEF, +180 MP",
        "price": 900000,
        "diamond_price": 45,
        "type": "armor",
        "class": "mage",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"def": 35, "max_mp": 180},
        "sellable": True
    },

    # ── ARCHER ───────────────────────────────────────────────────
    "leather_vest": {
        "name": "🥋 Leather Vest",
        "desc": "+7 DEF, +8 SPD",
        "price": 54000,
        "diamond_price": None,
        "type": "armor",
        "class": "archer",
        "rarity": "common",
        "req_level": 1,
        "stats": {"def": 7, "spd": 8},
        "sellable": True
    },
    "forest_cloak": {
        "name": "🌿 Forest Cloak",
        "desc": "+14 DEF, +14 SPD",
        "price": 126000,
        "diamond_price": None,
        "type": "armor",
        "class": "archer",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"def": 14, "spd": 14},
        "sellable": True
    },
    "ranger_mail": {
        "name": "🌲 Ranger Mail",
        "desc": "+22 DEF, +20 SPD",
        "price": 243000,
        "diamond_price": None,
        "type": "armor",
        "class": "archer",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"def": 22, "spd": 20},
        "sellable": True
    },
    "wind_dancer": {
        "name": "💨 Wind Dancer",
        "desc": "+30 DEF, +28 SPD",
        "price": 880000,
        "diamond_price": None,
        "type": "armor",
        "class": "archer",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"def": 30, "spd": 28},
        "sellable": True
    },
    "storm_warden": {
        "name": "⚡ Storm Warden",
        "desc": "+42 DEF, +38 SPD",
        "price": 870000,
        "diamond_price": 42,
        "type": "armor",
        "class": "archer",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"def": 42, "spd": 38},
        "sellable": True
    },

    # ── ROGUE ────────────────────────────────────────────────────
    "shadow_garb": {
        "name": "🌑 Shadow Garb",
        "desc": "+6 DEF, +10 SPD",
        "price": 54000,
        "diamond_price": None,
        "type": "armor",
        "class": "rogue",
        "rarity": "common",
        "req_level": 1,
        "stats": {"def": 6, "spd": 10},
        "sellable": True
    },
    "night_leather": {
        "name": "🌙 Night Leather",
        "desc": "+13 DEF, +16 SPD",
        "price": 126000,
        "diamond_price": None,
        "type": "armor",
        "class": "rogue",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"def": 13, "spd": 16},
        "sellable": True
    },
    "phantom_silk": {
        "name": "👻 Phantom Silk",
        "desc": "+20 DEF, +22 SPD",
        "price": 243000,
        "diamond_price": None,
        "type": "armor",
        "class": "rogue",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"def": 20, "spd": 22},
        "sellable": True
    },
    "void_wraps": {
        "name": "🌀 Void Wraps",
        "desc": "+28 DEF, +30 SPD, +10 ATK",
        "price": 940000,
        "diamond_price": None,
        "type": "armor",
        "class": "rogue",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"def": 28, "spd": 30, "atk": 10},
        "sellable": True
    },
    "shadow_sovereign": {
        "name": "🌑 Shadow Sovereign",
        "desc": "+40 DEF, +40 SPD",
        "price": 920000,
        "diamond_price": 45,
        "type": "armor",
        "class": "rogue",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"def": 40, "spd": 40},
        "sellable": True
    },

    # ── ASSASSIN ─────────────────────────────────────────────────
    "hunter_vest": {
        "name": "🎯 Hunter Vest",
        "desc": "+7 DEF, +10 SPD | Ringan dan gesit, dodge +5%",
        "price": 57600,
        "diamond_price": None,
        "type": "armor",
        "class": "assassin",
        "rarity": "common",
        "req_level": 1,
        "stats": {"def": 7, "spd": 10},
        "special_effect": {"dodge_bonus": 5},
        "sellable": True
    },
    "shade_armor": {
        "name": "🌑 Shade Armor",
        "desc": "+15 DEF, +18 SPD, +5 ATK | Armor bayangan yang meningkatkan refleks",
        "price": 144000,
        "diamond_price": None,
        "type": "armor",
        "class": "assassin",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"def": 15, "spd": 18, "atk": 5},
        "special_effect": {"dodge_bonus": 8},
        "sellable": True
    },
    "cursed_shroud": {
        "name": "🕸️ Cursed Shroud",
        "desc": "+24 DEF, +24 SPD, +8 ATK | Saat dodge, balik serang 0.5x DMG",
        "price": 270000,
        "diamond_price": None,
        "type": "armor",
        "class": "assassin",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"def": 24, "spd": 24, "atk": 8},
        "special_effect": {"dodge_bonus": 12, "counter_on_dodge": True, "counter_mult": 0.5},
        "sellable": True
    },
    "deathmark_cloak": {
        "name": "💀 Deathmark Cloak",
        "desc": "+35 DEF, +34 SPD, +14 ATK | CRIT rate +10%, musuh bertanda mati",
        "price": 960000,
        "diamond_price": None,
        "type": "armor",
        "class": "assassin",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"def": 35, "spd": 34, "atk": 14},
        "special_effect": {"crit_bonus": 10, "dodge_bonus": 18},
        "sellable": True
    },
    "reaper_mantle": {
        "name": "☠️ Shadow Reaper Mantle",
        "desc": "+48 DEF, +46 SPD, +20 ATK | Dodge +25%, CRIT DMG +30%",
        "price": 950000,
        "diamond_price": 48,
        "type": "armor",
        "class": "assassin",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"def": 48, "spd": 46, "atk": 20},
        "special_effect": {"dodge_bonus": 25, "crit_dmg_bonus": 0.30},
        "sellable": True
    },

    # ── REAPER ───────────────────────────────────────────────────
    "tattered_robe": {
        "name": "🧟 Tattered Robe",
        "desc": "+6 DEF, +35 MP",
        "price": 54000,
        "diamond_price": None,
        "type": "armor",
        "class": "reaper",
        "rarity": "common",
        "req_level": 1,
        "stats": {"def": 6, "max_mp": 35},
        "sellable": True
    },
    "death_shroud": {
        "name": "💜 Death Shroud",
        "desc": "+13 DEF, +70 MP",
        "price": 135000,
        "diamond_price": None,
        "type": "armor",
        "class": "reaper",
        "rarity": "uncommon",
        "req_level": 5,
        "stats": {"def": 13, "max_mp": 70},
        "sellable": True
    },
    "bone_armor": {
        "name": "🦴 Bone Armor",
        "desc": "+22 DEF, +100 MP",
        "price": 261000,
        "diamond_price": None,
        "type": "armor",
        "class": "reaper",
        "rarity": "rare",
        "req_level": 10,
        "stats": {"def": 22, "max_mp": 100},
        "sellable": True
    },
    "lich_vestment": {
        "name": "💀 Lich Vestment",
        "desc": "+32 DEF, +140 MP, +15 ATK",
        "price": 920000,
        "diamond_price": None,
        "type": "armor",
        "class": "reaper",
        "rarity": "epic",
        "req_level": 15,
        "stats": {"def": 32, "max_mp": 140, "atk": 15},
        "sellable": True
    },
    "void_phylactery": {
        "name": "🌑 Void Phylactery",
        "desc": "+44 DEF, +200 MP",
        "price": 980000,
        "diamond_price": 50,
        "type": "armor",
        "class": "reaper",
        "rarity": "legendary",
        "req_level": 20,
        "stats": {"def": 44, "max_mp": 200},
        "sellable": True
    },
}

# ─── VIP PACKAGES ───────────────────────────────────────────────
VIP_PACKAGES = {
    "vip_silver": {
        "name": "🥈 VIP Silver",
        "price_idr": 15000,
        "bank": "SEABANK",
        "account": "901919719088",
        "account_name": "Erik Martin",
        "duration_days": 30,
        "effects": {
            "crit_bonus": 4,
            "max_hp_bonus": 20,
            "max_mp_bonus": 15,
            "atk_bonus": 3,
        },
        "desc": "Crit +4%, HP +20, MP +15, ATK +3 selama 30 hari"
    },
    "vip_gold": {
        "name": "🥇 VIP Gold",
        "price_idr": 30000,
        "bank": "SEABANK",
        "account": "901919719088",
        "account_name": "Erik Martin",
        "duration_days": 30,
        "effects": {
            "crit_bonus": 8,
            "max_hp_bonus": 45,
            "max_mp_bonus": 30,
            "atk_bonus": 7,
        },
        "desc": "Crit +8%, HP +45, MP +30, ATK +7 selama 30 hari"
    },
    "vip_diamond": {
        "name": "💎 VIP Diamond",
        "price_idr": 75000,
        "bank": "SEABANK",
        "account": "901919719088",
        "account_name": "Erik Martin",
        "duration_days": 30,
        "effects": {
            "crit_bonus": 14,
            "max_hp_bonus": 85,
            "max_mp_bonus": 55,
            "atk_bonus": 13,
        },
        "desc": "Crit +14%, HP +85, MP +55, ATK +13 selama 30 hari"
    },
}

# ─── COIN & DIAMOND PACKAGES ────────────────────────────────────
COIN_PACKAGES = {
    "coins_small": {
        "name": "🪙 5.000.000 Gold",
        "coins": 5_000_000,
        "gold": 5_000_000,
        "price_idr": 25000,
        "bank": "SEABANK",
        "account": "901919719088",
        "account_name": "Erik Martin",
    },
    "coins_medium": {
        "name": "🪙 50.000.000 Gold",
        "coins": 50_000_000,
        "gold": 50_000_000,
        "price_idr": 50000,
        "bank": "SEABANK",
        "account": "901919719088",
        "account_name": "Erik Martin",
    },
    "coins_large": {
        "name": "🪙 150.000.000 Gold",
        "coins": 150_000_000,
        "gold": 150_000_000,
        "price_idr": 100000,
        "bank": "SEABANK",
        "account": "901919719088",
        "account_name": "Erik Martin",
    },
}

DIAMOND_PACKAGES = {
    "diamond_small": {
        "name": "💎 1.500 Diamond",
        "diamonds": 1500,
        "price_idr": 100000,
        "bank": "SEABANK",
        "account": "901919719088",
        "account_name": "Erik Martin",
    },
    "diamond_medium": {
        "name": "💎 3.000 Diamond",
        "diamonds": 3000,
        "price_idr": 150000,
        "bank": "SEABANK",
        "account": "901919719088",
        "account_name": "Erik Martin",
    },
    "diamond_large": {
        "name": "💎 7.500 Diamond",
        "diamonds": 7500,
        "price_idr": 300000,
        "bank": "SEABANK",
        "account": "901919719088",
        "account_name": "Erik Martin",
    },
}

# ─── BOSS DROP POOL (per class) ──────────────────────────────────
BOSS_DROPS = {
    "warrior": ["war_hammer", "titan_axe", "battle_fortress", "dragonscale_armor"],
    "mage": ["arcane_tome", "crystal_scepter", "void_shroud", "celestial_vestment"],
    "archer": ["storm_crossbow", "divine_longbow", "wind_dancer", "storm_warden"],
    "rogue": ["phantom_knives", "void_edge", "void_wraps", "shadow_sovereign"],
    "assassin": ["nightshade_sickle", "death_scythe", "deathmark_cloak", "reaper_mantle"],
    "reaper": ["lich_scepter", "doomsday_grimoire", "lich_vestment", "void_phylactery"],
}

# ─── ALL ITEMS COMBINED ──────────────────────────────────────────
ALL_ITEMS = {**CONSUMABLES, **WEAPONS, **ARMORS}


def get_item(item_id: str) -> dict:
    return ALL_ITEMS.get(item_id, {})


def get_class_weapons(char_class: str) -> dict:
    return {k: v for k, v in WEAPONS.items() if v["class"] == char_class}


def get_class_armors(char_class: str) -> dict:
    return {k: v for k, v in ARMORS.items() if v["class"] == char_class}


RARITY_STARS = {
    "common": "⭐",
    "uncommon": "⭐⭐",
    "rare": "⭐⭐⭐",
    "epic": "⭐⭐⭐⭐",
    "legendary": "⭐⭐⭐⭐⭐",
}


# ─── SKILL SHOP (per class) ──────────────────────────────────────
# Masing-masing class punya 5 skill (3 lama + 2 baru)
SHOP_SKILLS = {
    # ── WARRIOR ──────────────────────────────────────────────────
    "warrior_skill_1": {
        "name": "🌪️ Whirlwind",
        "desc": "Serang semua musuh di sekitar, 2.5x DMG",
        "class": "warrior",
        "price": 252000,
        "rarity": "rare",
        "req_level": 10,
        "effect": {"dmg_mult": 2.5, "mp_cost": 35, "cooldown": 4},
        "lore": "Putaran angin yang menghancurkan semua yang ada di dekat Warrior.",
    },
    "warrior_skill_2": {
        "name": "🛡️ Iron Defense",
        "desc": "Tingkatkan DEF +30 selama 3 ronde",
        "class": "warrior",
        "price": 308000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"def_buff": 30, "duration": 3, "mp_cost": 40, "cooldown": 5},
        "lore": "Pertahanan baja yang tak tertembus oleh serangan apapun.",
    },
    "warrior_skill_3": {
        "name": "⚡ Thunder Charge",
        "desc": "Serangan kilat, 3.2x DMG + stun",
        "class": "warrior",
        "price": 420000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 3.2, "mp_cost": 55, "cooldown": 6},
        "lore": "Terjang dengan kecepatan petir, mengejutkan lawan sebelum mereka bereaksi.",
    },
    "warrior_skill_4": {
        "name": "🔥 Blazing Wrath",
        "desc": "Api amarah membakar musuh, 2.8x DMG + burn 3 ronde",
        "class": "warrior",
        "price": 266000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"dmg_mult": 2.8, "dot_dmg": 10, "dot_duration": 3, "mp_cost": 45, "cooldown": 5},
        "lore": "Amarah seorang Warrior yang meluap menjadi kobaran api mematikan.",
    },
    "warrior_skill_5": {
        "name": "🏔️ Titan Smash",
        "desc": "Hantaman raksasa, 4.0x DMG + stun 2 ronde",
        "class": "warrior",
        "price": 490000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 4.0, "mp_cost": 65, "cooldown": 7},
        "lore": "Serangan dahsyat sekuat titan yang mampu membelah batu karang.",
    },
    # ── MAGE ─────────────────────────────────────────────────────
    "mage_skill_1": {
        "name": "❄️ Blizzard",
        "desc": "Badai es membekukan musuh, 2.8x DMG",
        "class": "mage",
        "price": 266000,
        "rarity": "rare",
        "req_level": 10,
        "effect": {"dmg_mult": 2.8, "mp_cost": 40, "cooldown": 4},
        "lore": "Badai dingin yang membekukan siapa pun yang berani menantang sang Mage.",
    },
    "mage_skill_2": {
        "name": "⚡ Chain Lightning",
        "desc": "Petir berantai menyambar 2-3x, 2.0x DMG per sambaran",
        "class": "mage",
        "price": 322000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"dmg_mult": 2.0, "hits": 3, "mp_cost": 50, "cooldown": 5},
        "lore": "Petir yang melompat dari satu musuh ke musuh lainnya tanpa henti.",
    },
    "mage_skill_3": {
        "name": "🌌 Arcane Nova",
        "desc": "Ledakan arkana terbesar, 4x DMG",
        "class": "mage",
        "price": 490000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 4.0, "mp_cost": 80, "cooldown": 7},
        "lore": "Puncak kekuatan sihir — ledakan energi arkana yang bisa meruntuhkan gunung.",
    },
    "mage_skill_4": {
        "name": "🌊 Tidal Wave",
        "desc": "Ombak sihir menghantam musuh, 3.0x DMG + slow",
        "class": "mage",
        "price": 294000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"dmg_mult": 3.0, "mp_cost": 55, "cooldown": 5},
        "lore": "Gelombang energi magis yang menghempaskan semua yang ada di depannya.",
    },
    "mage_skill_5": {
        "name": "☄️ Meteor Strike",
        "desc": "Jatuhkan meteor dari langit, 5x DMG",
        "class": "mage",
        "price": 560000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 5.0, "mp_cost": 100, "cooldown": 8},
        "lore": "Menarik meteor dari luar angkasa untuk menghancurkan target.",
    },
    # ── ARCHER ───────────────────────────────────────────────────
    "archer_skill_1": {
        "name": "🎯 Snipe",
        "desc": "Bidikan tepat, 3x DMG + CRIT +20%",
        "class": "archer",
        "price": 252000,
        "rarity": "rare",
        "req_level": 10,
        "effect": {"dmg_mult": 3.0, "crit_bonus": 20, "mp_cost": 35, "cooldown": 4},
        "lore": "Bidikan mematikan yang tidak pernah meleset dari targetnya.",
    },
    "archer_skill_2": {
        "name": "🌀 Cyclone Shot",
        "desc": "Anak panah tornado, 2.5x DMG + dodge +15%",
        "class": "archer",
        "price": 308000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"dmg_mult": 2.5, "dodge_bonus": 15, "mp_cost": 45, "cooldown": 5},
        "lore": "Panah yang berputar bak angin topan, menembus pertahanan lawan.",
    },
    "archer_skill_3": {
        "name": "💥 Meteor Shot",
        "desc": "Panah setara meteor, 4.5x DMG",
        "class": "archer",
        "price": 525000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 4.5, "mp_cost": 70, "cooldown": 7},
        "lore": "Panah yang meledak seperti meteor saat mengenai target.",
    },
    "archer_skill_4": {
        "name": "🌿 Poison Arrow",
        "desc": "Panah beracun, 2.2x DMG + racun 4 ronde",
        "class": "archer",
        "price": 266000,
        "rarity": "rare",
        "req_level": 10,
        "effect": {"dmg_mult": 2.2, "dot_dmg": 12, "dot_duration": 4, "mp_cost": 38, "cooldown": 4},
        "lore": "Anak panah dilapisi racun mematikan yang terus menggerogoti musuh.",
    },
    "archer_skill_5": {
        "name": "🦅 Eagle Eye Barrage",
        "desc": "Hujan panah presisi tinggi, 3.8x DMG x2 tembakan",
        "class": "archer",
        "price": 532000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 3.8, "hits": 2, "mp_cost": 75, "cooldown": 7},
        "lore": "Mata elang memandu setiap panah tepat ke jantung musuh.",
    },
    # ── ROGUE ────────────────────────────────────────────────────
    "rogue_skill_1": {
        "name": "🌑 Smoke Bomb",
        "desc": "Kabur dan serang dari kegelapan, 2.5x DMG + dodge +30%",
        "class": "rogue",
        "price": 259000,
        "rarity": "rare",
        "req_level": 10,
        "effect": {"dmg_mult": 2.5, "dodge_bonus": 30, "mp_cost": 35, "cooldown": 4},
        "lore": "Bom asap menutupi gerak Rogue, memberi celah untuk serangan mematikan.",
    },
    "rogue_skill_2": {
        "name": "⚡ Backstab Chain",
        "desc": "Tikam beruntun dari belakang, 3x DMG x2",
        "class": "rogue",
        "price": 336000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"dmg_mult": 3.0, "hits": 2, "mp_cost": 50, "cooldown": 5},
        "lore": "Rentetan tikaman dari bayangan yang tak sempat diantisipasi lawan.",
    },
    "rogue_skill_3": {
        "name": "💀 Phantom Execution",
        "desc": "Eksekusi bayangan, 5x DMG jika musuh HP < 30%",
        "class": "rogue",
        "price": 560000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 5.0, "execute_threshold": 0.3, "mp_cost": 65, "cooldown": 8},
        "lore": "Eksekusi sempurna oleh sosok bayangan — hanya muncul saat musuh hampir mati.",
    },
    "rogue_skill_4": {
        "name": "🎭 Mirage Step",
        "desc": "Menciptakan bayangan palsu, dodge +50% selama 2 ronde + 2x ATK",
        "class": "rogue",
        "price": 308000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"dmg_mult": 2.0, "dodge_bonus": 50, "duration": 2, "mp_cost": 48, "cooldown": 5},
        "lore": "Ilusi yang membingungkan musuh, membuat serangan mereka mengenai bayangan kosong.",
    },
    "rogue_skill_5": {
        "name": "🌀 Void Slash",
        "desc": "Tebasan dimensi, 4.2x DMG + menembus DEF",
        "class": "rogue",
        "price": 532000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 4.2, "def_pierce": True, "mp_cost": 70, "cooldown": 7},
        "lore": "Serangan yang membelah ruang waktu, tidak ada pertahanan yang mampu menahannya.",
    },
    # ── ASSASSIN ─────────────────────────────────────────────────
    "assassin_skill_1": {
        "name": "🗡️ Poison Blade",
        "desc": "Balur racun pada bilah, 2.2x DMG + DoT 15/ronde selama 3 ronde",
        "class": "assassin",
        "price": 273000,
        "rarity": "rare",
        "req_level": 10,
        "effect": {"dmg_mult": 2.2, "dot_dmg": 15, "dot_duration": 3, "status": "poison", "mp_cost": 40, "cooldown": 4},
        "lore": "Racun mematikan yang terus menggerogoti target bahkan setelah serangan.",
    },
    "assassin_skill_2": {
        "name": "🌀 Vanish Strike",
        "desc": "Lenyap lalu tikam dari bayangan, 3.5x DMG + 100% evasion ronde ini",
        "class": "assassin",
        "price": 350000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"dmg_mult": 3.5, "evasion_next": True, "mp_cost": 55, "cooldown": 6},
        "lore": "Assassin menghilang dalam sekejap sebelum muncul kembali di belakang musuh.",
    },
    "assassin_skill_3": {
        "name": "💉 Soul Harvest",
        "desc": "Panen jiwa musuh, 4.8x DMG + lifesteal 20% dari DMG yang diberikan",
        "class": "assassin",
        "price": 595000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 4.8, "lifesteal": 0.20, "mp_cost": 70, "cooldown": 8},
        "lore": "Menuai jiwa musuh untuk memperpanjang kehidupan sang Assassin.",
    },
    "assassin_skill_4": {
        "name": "🕷️ Shadow Web",
        "desc": "Jebak musuh dalam jaring bayangan, 2.6x DMG + Stun 2 ronde",
        "class": "assassin",
        "price": 294000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"dmg_mult": 2.6, "stun_duration": 2, "status": "stun", "mp_cost": 50, "cooldown": 5},
        "lore": "Jaring kegelapan yang menahan pergerakan musuh, memudahkan serangan berikutnya.",
    },
    "assassin_skill_5": {
        "name": "☠️ Deathblow",
        "desc": "Serangan rahasia terkuat, 6x DMG + execute chance 30% jika musuh <50% HP",
        "class": "assassin",
        "price": 630000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 6.0, "execute_threshold": 0.5, "execute_chance": 0.30, "mp_cost": 85, "cooldown": 9},
        "lore": "Pukulan terakhir yang mengakhiri segalanya — satu serangan, satu kematian.",
    },
    # ── REAPER ───────────────────────────────────────────────────
    "death_scythe_skill_1": {
        "name": "💀 Corpse Explosion",
        "desc": "Ledakkan mayat musuh, 3x DMG + AoE",
        "class": "reaper",
        "price": 280000,
        "rarity": "rare",
        "req_level": 10,
        "effect": {"dmg_mult": 3.0, "aoe": True, "mp_cost": 45, "cooldown": 4},
        "lore": "Menggunakan mayat musuh sebagai bom — cara paling kejam untuk berperang.",
    },
    "death_scythe_skill_2": {
        "name": "🌑 Dark Ritual",
        "desc": "Ritual gelap, +50 HP + 3.2x DMG selanjutnya",
        "class": "reaper",
        "price": 364000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"heal": 50, "dmg_buff_mult": 3.2, "mp_cost": 60, "cooldown": 5},
        "lore": "Ritual pengorbanan yang memberi kekuatan luar biasa dari alam kematian.",
    },
    "death_scythe_skill_3": {
        "name": "👁️ Lich Awakening",
        "desc": "Bangkit sebagai Lich, semua stat +50% selama 4 ronde",
        "class": "reaper",
        "price": 630000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"stat_boost": 0.5, "duration": 4, "mp_cost": 90, "cooldown": 9},
        "lore": "Transformasi menjadi Lich sejati — kekuatan alam kematian mengalir penuh.",
    },
    "death_scythe_skill_4": {
        "name": "🦴 Bone Shield",
        "desc": "Perisai tulang menyerap 40% damage, bertahan 3 ronde",
        "class": "reaper",
        "price": 308000,
        "rarity": "epic",
        "req_level": 15,
        "effect": {"shield_pct": 0.4, "duration": 3, "mp_cost": 55, "cooldown": 5},
        "lore": "Tulang-tulang arwah yang dikumpulkan membentuk perisai tak tertembus.",
    },
    "death_scythe_skill_5": {
        "name": "🌑 Void Curse",
        "desc": "Kutukan kehampaan, 4.5x DMG + mengurangi DEF musuh 50%",
        "class": "reaper",
        "price": 588000,
        "rarity": "legendary",
        "req_level": 20,
        "effect": {"dmg_mult": 4.5, "def_debuff": 0.5, "mp_cost": 80, "cooldown": 8},
        "lore": "Kutukan yang merobek perlindungan musuh, membuat mereka rentan terhadap serangan apapun.",
    },
}


def get_class_skills(char_class: str) -> dict:
    """Dapatkan semua skill shop yang tersedia untuk class tertentu."""
    return {k: v for k, v in SHOP_SKILLS.items() if v["class"] == char_class}


# ════════════════════════════════════════════════════════════════
#  CLASS SPECIAL ABILITIES (per class, status effect on battle)
# ════════════════════════════════════════════════════════════════
CLASS_SPECIALS = {
    "warrior": {
        "name": "🔥 Berserker Rage",
        "desc": "Saat HP < 30%, ATK +50% + Immune stun selama 3 ronde",
        "trigger": "low_hp",
        "effect": {"atk_bonus_pct": 0.5, "stun_immune": True, "duration": 3},
        "status": "berserker"
    },
    "mage": {
        "name": "⚡ Arcane Overload",
        "desc": "Setiap 3 serangan, tembak sihir otomatis 1.5x DMG + Burn",
        "trigger": "every_3_attacks",
        "effect": {"auto_dmg_mult": 1.5, "burn": True, "burn_dmg": 8, "burn_turns": 2},
        "status": "arcane_charged"
    },
    "archer": {
        "name": "🎯 Eagle Eye",
        "desc": "CRIT rate +30% + CRIT DMG x2.5 saat SPD > musuh",
        "trigger": "spd_advantage",
        "effect": {"crit_bonus": 30, "crit_dmg_mult": 2.5},
        "status": "eagle_eye"
    },
    "rogue": {
        "name": "🌑 Shadow Cloak",
        "desc": "Dodge +40% + tiap dodge balik serang 0.8x DMG",
        "trigger": "passive",
        "effect": {"dodge_bonus": 40, "counter_on_dodge": True, "counter_mult": 0.8},
        "status": "shadow_cloaked"
    },
    "assassin": {
        "name": "🩸 Shadow Execution",
        "desc": "Kill pertama tiap battle: restore 25% HP + next attack x3 DMG. CRIT selalu proc Bleed 3 ronde.",
        "trigger": "first_kill",
        "effect": {"heal_pct": 0.25, "next_dmg_mult": 3.0, "crit_bleed": True, "bleed_dmg": 15, "bleed_turns": 3},
        "status": "death_marked"
    },
    "reaper": {
        "name": "☠️ Soul Reap",
        "desc": "Tiap kill timbun Soul (max 5). 5 Soul → Harvest: semua musuh -50% HP + heal 15%",
        "trigger": "on_kill",
        "effect": {"soul_per_kill": 1, "max_souls": 5, "harvest_dmg_pct": 0.5, "heal_pct": 0.15},
        "status": "soul_charging"
    },
}

# Status Effect Definitions
STATUS_EFFECTS = {
    "burn":        {"name": "🔥 Terbakar",   "dmg_per_turn": 8,  "turns": 2, "effect": "dot"},
    "poison":      {"name": "☠️ Keracunan",  "dmg_per_turn": 12, "turns": 3, "effect": "dot"},
    "stun":        {"name": "⚡ Terstun",    "skip_turn": True,  "turns": 1, "effect": "skip"},
    "freeze":      {"name": "❄️ Membeku",    "skip_turn": True,  "turns": 2, "effect": "skip"},
    "bleed":       {"name": "🩸 Berdarah",   "dmg_per_turn": 15, "turns": 3, "effect": "dot"},
    "slow":        {"name": "🐌 Melambat",   "spd_reduce": 0.5,  "turns": 2, "effect": "debuff"},
    "curse":       {"name": "💜 Terkutuk",   "def_reduce": 0.5,  "turns": 3, "effect": "debuff"},
    "shield":      {"name": "🛡️ Terlindungi","dmg_reduce": 0.4,  "turns": 3, "effect": "buff"},
    "berserker":   {"name": "🔥 Berserk",    "atk_boost": 0.5,   "turns": 3, "effect": "buff"},
    "arcane_charged": {"name": "⚡ Overload", "auto_attack": True,"turns": 1, "effect": "buff"},
    "soul_charging":  {"name": "☠️ Soul Reap","souls": 0,         "turns": 99,"effect": "stack"},
}

# ════════════════════════════════════════════════════════════════
#  SSR / UR / GOD TIER WEAPONS (diamond shop)
# ════════════════════════════════════════════════════════════════
PREMIUM_WEAPONS = {
    # ── WARRIOR SSR/UR/GOD ───────────────────────────────────────
    "ssr_warrior_sword": {
        "name": "⚔️✨ Eternal Blade [SSR]",
        "desc": "+80 ATK, +40 DEF, +60 HP | Burn 3 ronde saat serang",
        "diamond_price": 80,
        "type": "weapon", "class": "warrior", "rarity": "SSR", "req_level": 25,
        "stats": {"atk": 144, "def": 72, "max_hp": 108},
        "special_effect": {"on_attack": "burn", "burn_dmg": 24, "burn_turns": 4},
        "sellable": False
    },
    "ur_warrior_axe": {
        "name": "🪓💜 Chaos Destroyer [UR]",
        "desc": "+120 ATK, +60 DEF, +100 HP | Ignore 30% DEF musuh",
        "diamond_price": 180,
        "type": "weapon", "class": "warrior", "rarity": "UR", "req_level": 35,
        "stats": {"atk": 264, "def": 132, "max_hp": 220},
        "special_effect": {"def_pierce_pct": 0.30, "on_crit": "bleed"},
        "sellable": False
    },
    "god_warrior_warhammer": {
        "name": "🔨🌟 Divine Wrath [GOD]",
        "desc": "+180 ATK, +90 DEF, +150 HP | Setiap 3 serangan Stun musuh",
        "diamond_price": 500,
        "type": "weapon", "class": "warrior", "rarity": "GOD", "req_level": 50,
        "stats": {"atk": 503, "def": 251, "max_hp": 420},
        "special_effect": {"every_3_atk_stun": True, "stun_turns": 5, "passive_regen": 25},
        "sellable": False
    },
    # ── MAGE SSR/UR/GOD ──────────────────────────────────────────
    "ssr_mage_staff": {
        "name": "🪄✨ Arcane Infinity [SSR]",
        "desc": "+85 ATK, +200 MP | Skill cost -30% MP",
        "diamond_price": 80,
        "type": "weapon", "class": "mage", "rarity": "SSR", "req_level": 25,
        "stats": {"atk": 153, "max_mp": 360},
        "special_effect": {"mp_cost_reduce": 0.30, "on_skill": "freeze"},
        "sellable": False
    },
    "ur_mage_tome": {
        "name": "📖💜 Grimoire of Doom [UR]",
        "desc": "+130 ATK, +300 MP, +20 CRIT | Skill DMG +50%",
        "diamond_price": 180,
        "type": "weapon", "class": "mage", "rarity": "UR", "req_level": 35,
        "stats": {"atk": 286, "max_mp": 660, "crit": 44},
        "special_effect": {"skill_dmg_bonus": 0.50, "on_skill": "burn", "burn_turns": 6},
        "sellable": False
    },
    "god_mage_scepter": {
        "name": "💎🌟 Cosmos Scepter [GOD]",
        "desc": "+200 ATK, +500 MP, +30 CRIT | Chain Lightning otomatis tiap 2 ronde",
        "diamond_price": 500,
        "type": "weapon", "class": "mage", "rarity": "GOD", "req_level": 50,
        "stats": {"atk": 560, "max_mp": 1400, "crit": 84},
        "special_effect": {"auto_chain_every": 2, "chain_dmg_mult": 4.5, "on_kill": "arcane_charged"},
        "sellable": False
    },
    # ── ARCHER SSR/UR/GOD ────────────────────────────────────────
    "ssr_archer_bow": {
        "name": "🏹✨ Starfall Bow [SSR]",
        "desc": "+75 ATK, +50 SPD, +25 CRIT | CRIT Poison 3 ronde",
        "diamond_price": 80,
        "type": "weapon", "class": "archer", "rarity": "SSR", "req_level": 25,
        "stats": {"atk": 135, "spd": 90, "crit": 45},
        "special_effect": {"on_crit": "poison", "poison_dmg": 28, "poison_turns": 4},
        "sellable": False
    },
    "ur_archer_crossbow": {
        "name": "⚡💜 Thunder Piercer [UR]",
        "desc": "+115 ATK, +70 SPD, +35 CRIT | Double shot 30% chance",
        "diamond_price": 180,
        "type": "weapon", "class": "archer", "rarity": "UR", "req_level": 35,
        "stats": {"atk": 253, "spd": 154, "crit": 77},
        "special_effect": {"double_shot_chance": 0.30, "on_crit": "stun"},
        "sellable": False
    },
    "god_archer_bow": {
        "name": "🌟✨ Celestial Longbow [GOD]",
        "desc": "+175 ATK, +100 SPD, +50 CRIT | Infinite CRIT = Full DMG",
        "diamond_price": 500,
        "type": "weapon", "class": "archer", "rarity": "GOD", "req_level": 50,
        "stats": {"atk": 489, "spd": 280, "crit": 140},
        "special_effect": {"crit_always": True, "crit_dmg_mult": 3.0, "on_kill": "eagle_eye"},
        "sellable": False
    },
    # ── ROGUE SSR/UR/GOD ─────────────────────────────────────────
    "ssr_rogue_blade": {
        "name": "🔪✨ Phantom Edge [SSR]",
        "desc": "+78 ATK, +45 SPD | Dodge +20%, Counter DMG x1.5",
        "diamond_price": 80,
        "type": "weapon", "class": "rogue", "rarity": "SSR", "req_level": 25,
        "stats": {"atk": 140, "spd": 81},
        "special_effect": {"dodge_bonus": 20, "counter_mult": 1.5, "on_dodge": "bleed"},
        "sellable": False
    },
    "ur_rogue_knives": {
        "name": "🌀💜 Void Ripper [UR]",
        "desc": "+118 ATK, +65 SPD | Triple strike 25% chance + Curse",
        "diamond_price": 180,
        "type": "weapon", "class": "rogue", "rarity": "UR", "req_level": 35,
        "stats": {"atk": 259, "spd": 143},
        "special_effect": {"triple_strike_chance": 0.25, "on_skill": "curse"},
        "sellable": False
    },
    "god_rogue_shadow": {
        "name": "👻🌟 Shadow Sovereign Blade [GOD]",
        "desc": "+178 ATK, +90 SPD | Invisible 1 ronde tiap 4 serangan",
        "diamond_price": 500,
        "type": "weapon", "class": "rogue", "rarity": "GOD", "req_level": 50,
        "stats": {"atk": 498, "spd": 251},
        "special_effect": {"every_4_atk_invisible": True, "invisible_dmg_mult": 4.0, "on_crit": "bleed"},
        "sellable": False
    },
    # ── ASSASSIN SSR/UR/GOD ──────────────────────────────────────
    "ssr_assassin_blade": {
        "name": "💀✨ Soul Carver [SSR]",
        "desc": "+82 ATK, +48 SPD | Life steal 15% dari tiap serangan",
        "diamond_price": 80,
        "type": "weapon", "class": "assassin", "rarity": "SSR", "req_level": 25,
        "stats": {"atk": 147, "spd": 86},
        "special_effect": {"lifesteal_pct": 0.15, "on_kill": "death_marked"},
        "sellable": False
    },
    "ur_assassin_scythe": {
        "name": "☠️💜 Deathbringer [UR]",
        "desc": "+125 ATK, +68 SPD | Execute <40% HP = instant kill 25%",
        "diamond_price": 180,
        "type": "weapon", "class": "assassin", "rarity": "UR", "req_level": 35,
        "stats": {"atk": 275, "spd": 149},
        "special_effect": {"execute_chance": 0.25, "execute_threshold": 0.40, "on_execute": "lifesteal"},
        "sellable": False
    },
    "god_assassin_reaper": {
        "name": "🌑🌟 Reaper of Souls [GOD]",
        "desc": "+185 ATK, +95 SPD | Kills heal 30% HP + next atk 5x DMG",
        "diamond_price": 500,
        "type": "weapon", "class": "assassin", "rarity": "GOD", "req_level": 50,
        "stats": {"atk": 518, "spd": 266},
        "special_effect": {"kill_heal_pct": 0.30, "kill_next_dmg": 5.0, "on_kill": "soul_charging"},
        "sellable": False
    },
    # ── DEATH SCYTHE SSR/UR/GOD ──────────────────────────────────
    "ssr_death_scythe_scythe": {
        "name": "☠️✨ Cursed Reaper [SSR]",
        "desc": "+80 ATK, +220 MP | Soul stack 2x lebih cepat",
        "diamond_price": 80,
        "type": "weapon", "class": "reaper", "rarity": "SSR", "req_level": 25,
        "stats": {"atk": 144, "max_mp": 396},
        "special_effect": {"soul_per_kill": 2, "on_skill": "curse", "curse_turns": 3},
        "sellable": False
    },
    "ur_death_scythe_grimoire": {
        "name": "📕💜 Tome of Eternal Death [UR]",
        "desc": "+125 ATK, +350 MP | Harvest DMG 75% + Drain HP musuh",
        "diamond_price": 180,
        "type": "weapon", "class": "reaper", "rarity": "UR", "req_level": 35,
        "stats": {"atk": 275, "max_mp": 770},
        "special_effect": {"harvest_dmg_pct": 0.75, "soul_drain_pct": 0.20, "on_kill": "soul_charging"},
        "sellable": False
    },
    "god_death_scythe_void": {
        "name": "🌑🌟 Void Reaper Absolute [GOD]",
        "desc": "+200 ATK, +600 MP | Harvest tiap 3 kill + invincible 1 ronde",
        "diamond_price": 500,
        "type": "weapon", "class": "reaper", "rarity": "GOD", "req_level": 50,
        "stats": {"atk": 560, "max_mp": 1680},
        "special_effect": {"harvest_every_3_kills": True, "invincible_on_harvest": True, "soul_per_kill": 3},
        "sellable": False
    },
}

# ════════════════════════════════════════════════════════════════
#  SSR / UR / GOD TIER ARMORS (diamond shop)
# ════════════════════════════════════════════════════════════════
PREMIUM_ARMORS = {
    "ssr_warrior_armor": {
        "name": "🛡️✨ Titan Guard [SSR]",
        "desc": "+70 DEF, +200 HP | Reflect 10% DMG ke musuh",
        "diamond_price": 80,
        "type": "armor", "class": "warrior", "rarity": "SSR", "req_level": 25,
        "stats": {"def": 126, "max_hp": 360},
        "special_effect": {"dmg_reflect_pct": 0.10},
        "sellable": False
    },
    "ur_warrior_armor": {
        "name": "🏰💜 Fortress Sovereign [UR]",
        "desc": "+110 DEF, +350 HP | Auto Shield saat HP < 50%",
        "diamond_price": 180,
        "type": "armor", "class": "warrior", "rarity": "UR", "req_level": 35,
        "stats": {"def": 242, "max_hp": 770},
        "special_effect": {"auto_shield_below": 0.50, "shield_turns": 2},
        "sellable": False
    },
    "god_warrior_armor": {
        "name": "🌟 Divine Bulwark [GOD]",
        "desc": "+170 DEF, +500 HP | Immune 1x per battle + HP regen 20/ronde",
        "diamond_price": 500,
        "type": "armor", "class": "warrior", "rarity": "GOD", "req_level": 50,
        "stats": {"def": 475, "max_hp": 1400},
        "special_effect": {"one_time_immune": True, "hp_regen_per_turn": 20},
        "sellable": False
    },
    "ssr_mage_robe": {
        "name": "🔮✨ Arcane Mantle [SSR]",
        "desc": "+45 DEF, +250 MP | MP regen 15/ronde",
        "diamond_price": 80,
        "type": "armor", "class": "mage", "rarity": "SSR", "req_level": 25,
        "stats": {"def": 81, "max_mp": 450},
        "special_effect": {"mp_regen_per_turn": 15},
        "sellable": False
    },
    "ur_mage_robe": {
        "name": "🌌💜 Void Vestment [UR]",
        "desc": "+70 DEF, +400 MP | Skill Cooldown -2",
        "diamond_price": 180,
        "type": "armor", "class": "mage", "rarity": "UR", "req_level": 35,
        "stats": {"def": 154, "max_mp": 880},
        "special_effect": {"cooldown_reduce": 2, "mp_regen_per_turn": 25},
        "sellable": False
    },
    "god_mage_robe": {
        "name": "☄️🌟 Celestial Cosmos Robe [GOD]",
        "desc": "+100 DEF, +700 MP | Skill gratis 1x per battle",
        "diamond_price": 500,
        "type": "armor", "class": "mage", "rarity": "GOD", "req_level": 50,
        "stats": {"def": 280, "max_mp": 1959},
        "special_effect": {"free_skill_once": True, "cooldown_reduce": 3, "mp_regen_per_turn": 40},
        "sellable": False
    },
    "ssr_archer_armor": {
        "name": "🏹✨ Wind Walker Vest [SSR]",
        "desc": "+55 DEF, +60 SPD | Dodge +15%",
        "diamond_price": 80,
        "type": "armor", "class": "archer", "rarity": "SSR", "req_level": 25,
        "stats": {"def": 99, "spd": 108},
        "special_effect": {"dodge_bonus": 15},
        "sellable": False
    },
    "ur_archer_armor": {
        "name": "⚡💜 Storm Walker [UR]",
        "desc": "+85 DEF, +90 SPD | First strike tiap battle",
        "diamond_price": 180,
        "type": "armor", "class": "archer", "rarity": "UR", "req_level": 35,
        "stats": {"def": 187, "spd": 198},
        "special_effect": {"first_strike": True, "dodge_bonus": 25},
        "sellable": False
    },
    "god_archer_armor": {
        "name": "🌟 Divine Wind Armor [GOD]",
        "desc": "+130 DEF, +130 SPD | Dodge reflect: counter 2x DMG",
        "diamond_price": 500,
        "type": "armor", "class": "archer", "rarity": "GOD", "req_level": 50,
        "stats": {"def": 364, "spd": 364},
        "special_effect": {"dodge_counter_mult": 2.0, "dodge_bonus": 40},
        "sellable": False
    },
    "ssr_rogue_armor": {
        "name": "🌑✨ Shadow Veil [SSR]",
        "desc": "+52 DEF, +55 SPD | Serang dari shadow +25% DMG",
        "diamond_price": 80,
        "type": "armor", "class": "rogue", "rarity": "SSR", "req_level": 25,
        "stats": {"def": 93, "spd": 99},
        "special_effect": {"shadow_attack_bonus": 0.25, "dodge_bonus": 15},
        "sellable": False
    },
    "ur_rogue_armor": {
        "name": "👻💜 Phantom Sovereign [UR]",
        "desc": "+82 DEF, +82 SPD | Phase shift: immune 1 serangan tiap 3 ronde",
        "diamond_price": 180,
        "type": "armor", "class": "rogue", "rarity": "UR", "req_level": 35,
        "stats": {"def": 180, "spd": 180},
        "special_effect": {"phase_immune_every": 3},
        "sellable": False
    },
    "god_rogue_armor": {
        "name": "🌀🌟 Void Sovereign Cloak [GOD]",
        "desc": "+125 DEF, +120 SPD | Permanent shadow mode saat HP < 50%",
        "diamond_price": 500,
        "type": "armor", "class": "rogue", "rarity": "GOD", "req_level": 50,
        "stats": {"def": 350, "spd": 336},
        "special_effect": {"shadow_mode_below": 0.50, "shadow_dodge": 60, "counter_mult": 2.0},
        "sellable": False
    },
    "ssr_assassin_armor": {
        "name": "💀✨ Death Walker Garb [SSR]",
        "desc": "+58 DEF, +58 SPD | +20% DMG saat musuh debuffed",
        "diamond_price": 80,
        "type": "armor", "class": "assassin", "rarity": "SSR", "req_level": 25,
        "stats": {"def": 104, "spd": 104},
        "special_effect": {"bonus_vs_debuffed": 0.20, "lifesteal_pct": 0.10},
        "sellable": False
    },
    "ur_assassin_armor": {
        "name": "☠️💜 Reaper's Embrace [UR]",
        "desc": "+90 DEF, +88 SPD | Life steal 20% + Immune poison/bleed",
        "diamond_price": 180,
        "type": "armor", "class": "assassin", "rarity": "UR", "req_level": 35,
        "stats": {"def": 198, "spd": 193},
        "special_effect": {"lifesteal_pct": 0.20, "immune_dot": True},
        "sellable": False
    },
    "god_assassin_armor": {
        "name": "🌑🌟 Eternal Reaper Mantle [GOD]",
        "desc": "+140 DEF, +135 SPD | Setelah kill: invisible + atk 4x next turn",
        "diamond_price": 500,
        "type": "armor", "class": "assassin", "rarity": "GOD", "req_level": 50,
        "stats": {"def": 392, "spd": 378},
        "special_effect": {"kill_invisible": True, "kill_next_atk_mult": 4.0, "lifesteal_pct": 0.25},
        "sellable": False
    },
    "ssr_death_scythe_armor": {
        "name": "☠️✨ Soul Harvester Robe [SSR]",
        "desc": "+50 DEF, +280 MP | Soul gained +1 dari tiap serangan",
        "diamond_price": 80,
        "type": "armor", "class": "reaper", "rarity": "SSR", "req_level": 25,
        "stats": {"def": 90, "max_mp": 504},
        "special_effect": {"soul_on_attack": 0.5, "mp_regen_per_turn": 20},
        "sellable": False
    },
    "ur_death_scythe_armor": {
        "name": "🌑💜 Void Phylactery Ascended [UR]",
        "desc": "+80 DEF, +450 MP | Saat Harvest, heal 40% HP",
        "diamond_price": 180,
        "type": "armor", "class": "reaper", "rarity": "UR", "req_level": 35,
        "stats": {"def": 176, "max_mp": 990},
        "special_effect": {"harvest_heal_pct": 0.40, "soul_per_kill": 2},
        "sellable": False
    },
    "god_death_scythe_armor": {
        "name": "🌟 Necro Sovereign Vestment [GOD]",
        "desc": "+120 DEF, +750 MP | Immortal 1x per battle (HP = 1 bukan mati)",
        "diamond_price": 500,
        "type": "armor", "class": "reaper", "rarity": "GOD", "req_level": 50,
        "stats": {"def": 336, "max_mp": 2100},
        "special_effect": {"immortal_once": True, "harvest_heal_pct": 0.50, "mp_regen_per_turn": 50},
        "sellable": False
    },
}

# ════════════════════════════════════════════════════════════════
#  SSR / UR / GOD SKILLS (diamond shop)
# ════════════════════════════════════════════════════════════════
PREMIUM_SKILLS = {
    # ── WARRIOR ──────────────────────────────────────────────────
    "ssr_warrior_skill": {
        "name": "🌋✨ Volcanic Rage [SSR]",
        "desc": "4.5x DMG + Burn 4 ronde + ATK +30% selama 2 ronde",
        "class": "warrior", "diamond_price": 100, "rarity": "SSR", "req_level": 25,
        "effect": {"dmg_mult": 7.2, "burn": True, "burn_turns": 6, "atk_boost": 0.30, "duration": 2, "mp_cost": 60, "cooldown": 6},
    },
    "ur_warrior_skill": {
        "name": "🔱💜 Titan's Judgment [UR]",
        "desc": "6x DMG + Stun 3 ronde + Immune damage 1 ronde",
        "class": "warrior", "diamond_price": 220, "rarity": "UR", "req_level": 35,
        "effect": {"dmg_mult": 12.0, "stun_turns": 6, "immune_turns": 1, "mp_cost": 90, "cooldown": 8},
    },
    "god_warrior_skill": {
        "name": "⚡🌟 Divine Thunder Smash [GOD]",
        "desc": "10x DMG + Stun 3 ronde + Semua stat +100% 3 ronde",
        "class": "warrior", "diamond_price": 600, "rarity": "GOD", "req_level": 50,
        "effect": {"dmg_mult": 25.0, "stun_turns": 7, "stat_boost": 1.0, "boost_duration": 3, "mp_cost": 130, "cooldown": 10},
    },
    # ── MAGE ─────────────────────────────────────────────────────
    "ssr_mage_skill": {
        "name": "🌌✨ Galaxy Burst [SSR]",
        "desc": "5x DMG + Chain Freeze 2 ronde + MP recover 50",
        "class": "mage", "diamond_price": 100, "rarity": "SSR", "req_level": 25,
        "effect": {"dmg_mult": 8.0, "freeze_turns": 2, "mp_recover": 50, "mp_cost": 70, "cooldown": 6},
    },
    "ur_mage_skill": {
        "name": "☄️💜 Supernova [UR]",
        "desc": "8x DMG + Burn 4 ronde + Skill CD reset",
        "class": "mage", "diamond_price": 220, "rarity": "UR", "req_level": 35,
        "effect": {"dmg_mult": 16.0, "burn_turns": 8, "reset_cd": True, "mp_cost": 110, "cooldown": 9},
    },
    "god_mage_skill": {
        "name": "🌟 Infinite Cosmos [GOD]",
        "desc": "15x DMG + All debuff + Serap 30% DMG dealt sebagai HP",
        "class": "mage", "diamond_price": 600, "rarity": "GOD", "req_level": 50,
        "effect": {"dmg_mult": 37.5, "all_debuff": True, "lifesteal": 0.75, "mp_cost": 160, "cooldown": 12},
    },
    # ── ARCHER ───────────────────────────────────────────────────
    "ssr_archer_skill": {
        "name": "🎯✨ Thousand Arrows [SSR]",
        "desc": "5x DMG x2 tembak + Poison 3 ronde + CRIT +40%",
        "class": "archer", "diamond_price": 100, "rarity": "SSR", "req_level": 25,
        "effect": {"dmg_mult": 8.0, "hits": 2, "poison_turns": 4, "crit_bonus": 40, "mp_cost": 65, "cooldown": 6},
    },
    "ur_archer_skill": {
        "name": "⚡💜 Storm Barrage [UR]",
        "desc": "6x DMG x3 + Stun + SPD +50% 3 ronde",
        "class": "archer", "diamond_price": 220, "rarity": "UR", "req_level": 35,
        "effect": {"dmg_mult": 12.0, "hits": 3, "stun_turns": 2, "spd_boost": 0.50, "duration": 3, "mp_cost": 95, "cooldown": 8},
    },
    "god_archer_skill": {
        "name": "🌟 Divine Arrow of Eternity [GOD]",
        "desc": "12x DMG + Ignore DEF + CRIT 100% + Slow 4 ronde",
        "class": "archer", "diamond_price": 600, "rarity": "GOD", "req_level": 50,
        "effect": {"dmg_mult": 30.0, "def_pierce": True, "crit_always": True, "slow_turns": 10, "mp_cost": 140, "cooldown": 11},
    },
    # ── ROGUE ────────────────────────────────────────────────────
    "ssr_rogue_skill": {
        "name": "🌑✨ Phantom Blitz [SSR]",
        "desc": "5x DMG + Dodge +60% 2 ronde + Bleed 3 ronde",
        "class": "rogue", "diamond_price": 100, "rarity": "SSR", "req_level": 25,
        "effect": {"dmg_mult": 8.0, "dodge_bonus": 60, "duration": 2, "bleed_turns": 4, "mp_cost": 65, "cooldown": 6},
    },
    "ur_rogue_skill": {
        "name": "👻💜 Void Assassination [UR]",
        "desc": "7x DMG + invisible 2 ronde + Curse musuh",
        "class": "rogue", "diamond_price": 220, "rarity": "UR", "req_level": 35,
        "effect": {"dmg_mult": 14.0, "invisible_turns": 2, "curse_turns": 3, "mp_cost": 100, "cooldown": 9},
    },
    "god_rogue_skill": {
        "name": "🌀🌟 Shadow Realm Execution [GOD]",
        "desc": "13x DMG + Execute <60% HP + Regen HP 15% per ronde 3 ronde",
        "class": "rogue", "diamond_price": 600, "rarity": "GOD", "req_level": 50,
        "effect": {"dmg_mult": 32.5, "execute_threshold": 0.60, "hp_regen_pct": 0.15, "regen_turns": 3, "mp_cost": 145, "cooldown": 11},
    },
    # ── ASSASSIN ─────────────────────────────────────────────────
    "ssr_assassin_skill": {
        "name": "💀✨ Soul Shatter [SSR]",
        "desc": "5.5x DMG + Life steal 25% + Death Mark stack",
        "class": "assassin", "diamond_price": 100, "rarity": "SSR", "req_level": 25,
        "effect": {"dmg_mult": 8.8, "lifesteal": 0.4, "death_mark": True, "mp_cost": 70, "cooldown": 6},
    },
    "ur_assassin_skill": {
        "name": "☠️💜 Reaper's Judgment [UR]",
        "desc": "8x DMG + Life steal 35% + Curse + Bleed",
        "class": "assassin", "diamond_price": 220, "rarity": "UR", "req_level": 35,
        "effect": {"dmg_mult": 16.0, "lifesteal": 0.7, "curse_turns": 3, "bleed_turns": 6, "mp_cost": 105, "cooldown": 9},
    },
    "god_assassin_skill": {
        "name": "🌑🌟 Absolute Death [GOD]",
        "desc": "15x DMG + Instant kill <50% HP + Heal 50% max HP",
        "class": "assassin", "diamond_price": 600, "rarity": "GOD", "req_level": 50,
        "effect": {"dmg_mult": 37.5, "execute_threshold": 0.50, "execute_heal_pct": 0.50, "mp_cost": 150, "cooldown": 12},
    },
    # ── DEATH SCYTHE ─────────────────────────────────────────────
    "ssr_death_scythe_skill": {
        "name": "☠️✨ Harvest Storm [SSR]",
        "desc": "5x DMG + Soul x3 + Drain 20% HP musuh",
        "class": "reaper", "diamond_price": 100, "rarity": "SSR", "req_level": 25,
        "effect": {"dmg_mult": 8.0, "soul_bonus": 3, "drain_pct": 0.20, "mp_cost": 75, "cooldown": 6},
    },
    "ur_death_scythe_skill": {
        "name": "🌑💜 Death's Embrace [UR]",
        "desc": "8x DMG + Instant Harvest + Heal 30% HP + Curse",
        "class": "reaper", "diamond_price": 220, "rarity": "UR", "req_level": 35,
        "effect": {"dmg_mult": 16.0, "instant_harvest": True, "heal_pct": 0.6, "curse_turns": 3, "mp_cost": 110, "cooldown": 9},
    },
    "god_death_scythe_skill": {
        "name": "🌟 Void Reaper Absolute [GOD]",
        "desc": "15x DMG + Harvest ALL souls + Semua musuh -60% HP + Immortal 1 ronde",
        "class": "reaper", "diamond_price": 600, "rarity": "GOD", "req_level": 50,
        "effect": {"dmg_mult": 37.5, "mass_harvest": True, "mass_drain_pct": 0.60, "immortal_turns": 1, "mp_cost": 160, "cooldown": 12},
    },
}

# ════════════════════════════════════════════════════════════════
#  PET SHOP (Standard → GOD rarity)
# ════════════════════════════════════════════════════════════════
PET_SHOP = {
    # ── COMMON (Gold) ─────────────────────────────────────────────
    "pet_slime": {
        "name": "🟢 Slime",
        "desc": "Pet dasar, +5 ATK saat battle",
        "rarity": "common", "price": 50000, "diamond_price": None,
        "tier": 1,
        "effect": {"atk_bonus": 5},
        "passive": "Slime Bounce: 5% chance miss serangan musuh"
    },
    "pet_wolf_pup": {
        "name": "🐺 Wolf Pup",
        "desc": "+8 ATK, +5 SPD saat battle",
        "rarity": "common", "price": 80000, "diamond_price": None,
        "tier": 1,
        "effect": {"atk_bonus": 8, "spd_bonus": 5},
        "passive": "Pack Instinct: +3% CRIT"
    },
    "pet_fire_cat": {
        "name": "🐱‍🔥 Fire Cat",
        "desc": "+10 ATK + Burn 10% chance saat serang",
        "rarity": "uncommon", "price": 150000, "diamond_price": None,
        "tier": 2,
        "effect": {"atk_bonus": 10, "on_attack_burn_chance": 0.10},
        "passive": "Flame Aura: +2 DMG tiap ronde dari api"
    },
    "pet_stone_golem": {
        "name": "🪨 Stone Golem",
        "desc": "+15 DEF, +50 HP saat battle",
        "rarity": "uncommon", "price": 180000, "diamond_price": None,
        "tier": 2,
        "effect": {"def_bonus": 15, "hp_bonus": 50},
        "passive": "Stone Skin: Reduce DMG received by 8%"
    },
    "pet_thunder_hawk": {
        "name": "⚡ Thunder Hawk",
        "desc": "+15 ATK, +10 SPD, +10% CRIT",
        "rarity": "rare", "price": 300000, "diamond_price": None,
        "tier": 3,
        "effect": {"atk_bonus": 15, "spd_bonus": 10, "crit_bonus": 10},
        "passive": "Thunder Strike: Tiap 3 serangan, petir otomatis 1.2x DMG"
    },
    "pet_poison_serpent": {
        "name": "🐍 Poison Serpent",
        "desc": "+12 ATK + Poison 20% tiap serangan (3 ronde)",
        "rarity": "rare", "price": 320000, "diamond_price": None,
        "tier": 3,
        "effect": {"atk_bonus": 12, "poison_chance": 0.20, "poison_turns": 3},
        "passive": "Venom Aura: Musuh -5 DEF saat battle"
    },
    "pet_shadow_fox": {
        "name": "🦊 Shadow Fox",
        "desc": "+18 ATK, +15 SPD, Dodge +10%",
        "rarity": "epic", "price": 600000, "diamond_price": None,
        "tier": 4,
        "effect": {"atk_bonus": 18, "spd_bonus": 15, "dodge_bonus": 10},
        "passive": "Shadow Dance: Setelah dodge, next atk +50% DMG"
    },
    "pet_ice_dragon": {
        "name": "🐲❄️ Ice Dragon",
        "desc": "+22 ATK, +20 DEF, Freeze 15% tiap serangan",
        "rarity": "epic", "price": 700000, "diamond_price": None,
        "tier": 4,
        "effect": {"atk_bonus": 22, "def_bonus": 20, "freeze_chance": 0.15},
        "passive": "Frost Breath: -10 SPD musuh permanen saat battle"
    },
    # ── SSR (Diamond) ─────────────────────────────────────────────
    "pet_celestial_wolf": {
        "name": "🐺✨ Celestial Wolf [SSR]",
        "desc": "+40 ATK, +30 SPD, +15 CRIT | Howl: +20% DMG 2 ronde tiap 4 serangan",
        "rarity": "SSR", "price": None, "diamond_price": 150,
        "tier": 5,
        "effect": {"atk_bonus": 64, "spd_bonus": 30, "crit_bonus": 15},
        "passive": "Moon Howl: Setiap 4 serangan, +20% DMG selama 2 ronde"
    },
    "pet_phoenix": {
        "name": "🔥✨ Phoenix [SSR]",
        "desc": "+35 ATK, +80 HP, Burn 30% tiap atk | Rebirth: 1x per battle +30% HP",
        "rarity": "SSR", "price": None, "diamond_price": 150,
        "tier": 5,
        "effect": {"atk_bonus": 56, "hp_bonus": 80, "burn_chance": 0.30},
        "passive": "Rebirth: 1x per battle saat HP < 20%, pulihkan 30% HP"
    },
    "pet_storm_dragon": {
        "name": "🐲⚡ Storm Dragon [SSR]",
        "desc": "+45 ATK, +30 DEF, +20 SPD | Lightning Breath tiap 3 ronde 1.8x DMG",
        "rarity": "SSR", "price": None, "diamond_price": 150,
        "tier": 5,
        "effect": {"atk_bonus": 72, "def_bonus": 48, "spd_bonus": 20},
        "passive": "Lightning Breath: Tiap 3 ronde, 1.8x DMG otomatis + Stun"
    },
    # ── UR (Diamond) ──────────────────────────────────────────────
    "pet_divine_unicorn": {
        "name": "🦄💜 Divine Unicorn [UR]",
        "desc": "+60 ATK, +60 DEF, +40 SPD | Heal 10% HP tiap ronde + Bless +20% DMG",
        "rarity": "UR", "price": None, "diamond_price": 350,
        "tier": 6,
        "effect": {"atk_bonus": 120, "def_bonus": 120, "spd_bonus": 40},
        "passive": "Sacred Aura: Heal 10% HP tiap ronde + Semua stat +20%"
    },
    "pet_shadow_leviathan": {
        "name": "🌊💜 Shadow Leviathan [UR]",
        "desc": "+70 ATK, +50 DEF, +100 HP | Tentacle: 2 serangan tambahan 1.5x DMG",
        "rarity": "UR", "price": None, "diamond_price": 350,
        "tier": 6,
        "effect": {"atk_bonus": 140, "def_bonus": 100, "hp_bonus": 100},
        "passive": "Abyss Tide: 2 serangan otomatis 1.5x DMG tiap ronde monster serang"
    },
    "pet_chaos_hydra": {
        "name": "🐉💜 Chaos Hydra [UR]",
        "desc": "+80 ATK, +40 DEF, Poison+Burn+Bleed tiap serang",
        "rarity": "UR", "price": None, "diamond_price": 350,
        "tier": 6,
        "effect": {"atk_bonus": 160, "def_bonus": 80, "multi_dot": True},
        "passive": "Triple Venom: Tiap serangan apply Poison+Burn+Bleed sekaligus"
    },
    # ── GOD (Diamond) ─────────────────────────────────────────────
    "pet_god_of_war": {
        "name": "⚔️🌟 God of War Beast [GOD]",
        "desc": "+120 ATK, +80 DEF, +60 SPD | War Cry: +50% DMG + Immune 1 ronde tiap 5 serangan",
        "rarity": "GOD", "price": None, "diamond_price": 999,
        "tier": 7,
        "effect": {"atk_bonus": 300, "def_bonus": 200, "spd_bonus": 60},
        "passive": "Eternal War Cry: Tiap 5 serangan, +50% DMG + Immune 1 ronde"
    },
    "pet_void_dragon_god": {
        "name": "🌌🌟 Void Dragon God [GOD]",
        "desc": "+150 ATK, +100 DEF, +200 HP | Void Breath: 3x DMG tiap 3 ronde + Drain HP",
        "rarity": "GOD", "price": None, "diamond_price": 999,
        "tier": 7,
        "effect": {"atk_bonus": 375, "def_bonus": 250, "hp_bonus": 200},
        "passive": "Void Breath: Tiap 3 ronde, 3x DMG + Drain 20% HP musuh"
    },
    "pet_eternal_phoenix_god": {
        "name": "🔥🌟 Eternal Phoenix God [GOD]",
        "desc": "+130 ATK, +90 DEF, +150 HP | Immortal: Bangkit 3x per battle dengan 50% HP",
        "rarity": "GOD", "price": None, "diamond_price": 999,
        "tier": 7,
        "effect": {"atk_bonus": 325, "def_bonus": 225, "hp_bonus": 150},
        "passive": "Eternal Rebirth: Bangkit 3x per battle dengan 50% HP, next atk 4x DMG"
    },
}

# ════════════════════════════════════════════════════════════════
#  CLASS & PET EVOLUTION SYSTEM (10 Tiers)
# ════════════════════════════════════════════════════════════════
EVOLUTION_TIERS = {
    1:  {"name": "Novice",       "emoji": "⚪", "stat_mult": 1.0,  "evolution_stone_needed": 0},
    2:  {"name": "Apprentice",   "emoji": "🟢", "stat_mult": 1.1,  "evolution_stone_needed": 1},
    3:  {"name": "Journeyman",   "emoji": "🔵", "stat_mult": 1.22, "evolution_stone_needed": 2},
    4:  {"name": "Adept",        "emoji": "🟡", "stat_mult": 1.36, "evolution_stone_needed": 3},
    5:  {"name": "Expert",       "emoji": "🟠", "stat_mult": 1.52, "evolution_stone_needed": 5},
    6:  {"name": "Master",       "emoji": "🔴", "stat_mult": 1.70, "evolution_stone_needed": 8},
    7:  {"name": "Grandmaster",  "emoji": "🟣", "stat_mult": 1.90, "evolution_stone_needed": 12},
    8:  {"name": "Legend",       "emoji": "⚡", "stat_mult": 2.15, "evolution_stone_needed": 18},
    9:  {"name": "Mythic",       "emoji": "💜", "stat_mult": 2.45, "evolution_stone_needed": 25},
    10: {"name": "GOD",          "emoji": "🌟", "stat_mult": 3.0,  "evolution_stone_needed": 40},
}

PET_EVOLUTION_TIERS = {
    1:  {"name": "Baby",         "emoji": "🥚", "stat_mult": 1.0,  "evolution_stone_needed": 0},
    2:  {"name": "Juvenile",     "emoji": "🐣", "stat_mult": 1.15, "evolution_stone_needed": 1},
    3:  {"name": "Young",        "emoji": "🐤", "stat_mult": 1.30, "evolution_stone_needed": 2},
    4:  {"name": "Grown",        "emoji": "🌱", "stat_mult": 1.50, "evolution_stone_needed": 3},
    5:  {"name": "Matured",      "emoji": "🌿", "stat_mult": 1.75, "evolution_stone_needed": 5},
    6:  {"name": "Champion",     "emoji": "⚔️", "stat_mult": 2.0,  "evolution_stone_needed": 8},
    7:  {"name": "Elite",        "emoji": "💫", "stat_mult": 2.3,  "evolution_stone_needed": 12},
    8:  {"name": "Ancient",      "emoji": "🏆", "stat_mult": 2.7,  "evolution_stone_needed": 20},
    9:  {"name": "Divine",       "emoji": "💎", "stat_mult": 3.2,  "evolution_stone_needed": 30},
    10: {"name": "LEGENDARY",    "emoji": "🌟", "stat_mult": 4.0,  "evolution_stone_needed": 50},
}

# Evolution Stone - boss drop rarity 0.1%
EVOLUTION_STONE = {
    "evolution_stone": {
        "name": "💠 Evolution Stone",
        "desc": "Batu langka untuk evolusi Class/Pet. Drop dari Boss rate 0.1%!",
        "type": "evolution_material",
        "rarity": "legendary",
        "diamond_price": 500,  # bisa dibeli dengan diamond jika mau
        "price": None,
        "class": None,
        "sellable": False,
    }
}

# Rarity display
RARITY_STARS.update({
    "SSR":      "💎💎💎💎💎✨",
    "UR":       "💜💜💜💜💜💜",
    "GOD":      "🌟🌟🌟🌟🌟🌟🌟",
    "GOD SSSR": "🔱🔱🔱🔱🔱🔱🔱🔱🔱🔱",
})

# ════════════════════════════════════════════════════════════════
#  GOD SSSR — Item Langka Terkuat (rate 0.1% dari Boss Kill)
# ════════════════════════════════════════════════════════════════
GOD_SSSR_WEAPONS = {
    # ── WARRIOR ──────────────────────────────────────────────────
    "god_sssr_warrior_weapon": {
        "name": "🔱💥 Sovereign Annihilator [GOD SSSR]",
        "desc": "Pedang dewa tertinggi. Hanya sang terpilih yang layak memegangnya.",
        "type": "weapon", "class": "warrior", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"atk": 3496, "crit": 105, "spd": 70},
    },
    # ── MAGE ─────────────────────────────────────────────────────
    "god_sssr_mage_weapon": {
        "name": "🌌💫 Eternity Grimoire [GOD SSSR]",
        "desc": "Kitab sihir purba yang mengandung seluruh hukum alam semesta.",
        "type": "weapon", "class": "mage", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"atk": 3850, "max_mp": 1750, "crit": 87},
    },
    # ── ARCHER ───────────────────────────────────────────────────
    "god_sssr_archer_weapon": {
        "name": "⚡🏹 Void Arrow of Eternity [GOD SSSR]",
        "desc": "Busur yang menembus dimensi. Panahnya tak pernah meleset.",
        "type": "weapon", "class": "archer", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"atk": 3325, "crit": 140, "spd": 140},
    },
    # ── ROGUE ────────────────────────────────────────────────────
    "god_sssr_rogue_weapon": {
        "name": "🌑☠️ Shadow God's Fang [GOD SSSR]",
        "desc": "Pisau bayangan sang dewa malam. Tak terlihat, tak terhindar.",
        "type": "weapon", "class": "rogue", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"atk": 3675, "crit": 175, "spd": 122},
    },
    # ── ASSASSIN ─────────────────────────────────────────────────
    "god_sssr_assassin_weapon": {
        "name": "💀🔱 Reaper's Divine Scythe [GOD SSSR]",
        "desc": "Sabit pencabut nyawa para dewa. Satu tebasan = kematian abadi.",
        "type": "weapon", "class": "assassin", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"atk": 4200, "crit": 157, "spd": 105},
    },
    # ── DEATH SCYTHE ─────────────────────────────────────────────
    "god_sssr_death_scythe_weapon": {
        "name": "🌑🔮 Void Apocalypse [GOD SSSR]",
        "desc": "Staf neraka dari kegelapan absolut. Meluruhkan jiwa siapapun.",
        "type": "weapon", "class": "reaper", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"atk": 3500, "max_mp": 2100, "crit": 122},
    },
}

GOD_SSSR_ARMORS = {
    # ── WARRIOR ──────────────────────────────────────────────────
    "god_sssr_warrior_armor": {
        "name": "🛡️🔱 Celestial Fortress [GOD SSSR]",
        "desc": "Zirah dewa perang. Tidak ada senjata yang bisa menembusnya.",
        "type": "armor", "class": "warrior", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"def": 2800, "max_hp": 7000, "spd": 35},
    },
    # ── MAGE ─────────────────────────────────────────────────────
    "god_sssr_mage_armor": {
        "name": "🌌🔮 Cosmos Robe [GOD SSSR]",
        "desc": "Jubah yang ditenun dari bintang-bintang. MP tak pernah habis.",
        "type": "armor", "class": "mage", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"def": 1750, "max_hp": 4200, "max_mp": 2800},
    },
    # ── ARCHER ───────────────────────────────────────────────────
    "god_sssr_archer_armor": {
        "name": "⚡🌪️ Storm Sovereign Vest [GOD SSSR]",
        "desc": "Rompi secepat kilat. Bergerak lebih cepat dari cahaya.",
        "type": "armor", "class": "archer", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"def": 1925, "max_hp": 5250, "spd": 280},
    },
    # ── ROGUE ────────────────────────────────────────────────────
    "god_sssr_rogue_armor": {
        "name": "🌑💨 Void Shadow Cloak [GOD SSSR]",
        "desc": "Jubah yang membuat pemakainya menjadi bayangan murni.",
        "type": "armor", "class": "rogue", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"def": 2100, "max_hp": 4900, "spd": 210},
    },
    # ── ASSASSIN ─────────────────────────────────────────────────
    "god_sssr_assassin_armor": {
        "name": "💀🌑 Death Sovereign Mantle [GOD SSSR]",
        "desc": "Jubah sang dewa kematian. Membuat musuh gemetar ketakutan.",
        "type": "armor", "class": "assassin", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"def": 2275, "max_hp": 4550, "spd": 175},
    },
    # ── DEATH SCYTHE ─────────────────────────────────────────────
    "god_sssr_death_scythe_armor": {
        "name": "☠️🌌 Lich God's Phylactery [GOD SSSR]",
        "desc": "Perisai jiwa dari raja lich tertinggi. Abadi dan tak tergoyahkan.",
        "type": "armor", "class": "reaper", "rarity": "GOD SSSR",
        "req_level": 1, "price": None, "diamond_price": None, "sellable": True,
        "stats": {"def": 2450, "max_hp": 3850, "max_mp": 3500},
    },
}

GOD_SSSR_SKILLS = {
    "god_sssr_warrior_skill": {
        "name": "🔱💥 Apocalypse Slash [GOD SSSR]",
        "desc": "25x DMG + Semua musuh terhancurkan + HP recover 50% + Invincible 5 ronde",
        "class": "warrior", "diamond_price": None, "rarity": "GOD SSSR", "req_level": 1,
        "effect": {"dmg_mult": 75.0, "heal_pct": 1.5, "immune_turns": 5, "mp_cost": 200, "cooldown": 15},
    },
    "god_sssr_mage_skill": {
        "name": "🌌💫 Big Bang [GOD SSSR]",
        "desc": "30x DMG + Hapus semua buff musuh + Absorb 50% DMG sebagai HP",
        "class": "mage", "diamond_price": None, "rarity": "GOD SSSR", "req_level": 1,
        "effect": {"dmg_mult": 90.0, "all_debuff": True, "lifesteal": 1.5, "mp_cost": 250, "cooldown": 18},
    },
    "god_sssr_archer_skill": {
        "name": "⚡🏹 Void Snipe [GOD SSSR]",
        "desc": "20x DMG x5 peluru + Crit selalu 100% + Ignore DEF + Slow 10 ronde",
        "class": "archer", "diamond_price": None, "rarity": "GOD SSSR", "req_level": 1,
        "effect": {"dmg_mult": 60.0, "hits": 5, "crit_always": True, "def_pierce": True, "slow_turns": 30, "mp_cost": 220, "cooldown": 16},
    },
    "god_sssr_rogue_skill": {
        "name": "🌑☠️ Shadow God's Domain [GOD SSSR]",
        "desc": "22x DMG + Dodge 100% 5 ronde + Poison 10 ronde",
        "class": "rogue", "diamond_price": None, "rarity": "GOD SSSR", "req_level": 1,
        "effect": {"dmg_mult": 66.0, "dodge_turns": 5, "poison_turns": 30, "mp_cost": 200, "cooldown": 15},
    },
    "god_sssr_assassin_skill": {
        "name": "💀🔱 Divine Death Mark [GOD SSSR]",
        "desc": "28x DMG + Instant KO chance 30% + Next 3 serangan x5 DMG",
        "class": "assassin", "diamond_price": None, "rarity": "GOD SSSR", "req_level": 1,
        "effect": {"dmg_mult": 84.0, "instant_ko_chance": 0.9, "next_atk_mult": 15.0, "next_atk_count": 3, "mp_cost": 230, "cooldown": 17},
    },
    "god_sssr_death_scythe_skill": {
        "name": "🌑🔮 Void Apocalypse Ritual [GOD SSSR]",
        "desc": "35x DMG + Drain semua HP musuh 10% per ronde + Resurrect sekali",
        "class": "reaper", "diamond_price": None, "rarity": "GOD SSSR", "req_level": 1,
        "effect": {"dmg_mult": 105.0, "hp_drain_pct": 0.3, "resurrect": True, "mp_cost": 280, "cooldown": 20},
    },
}

GOD_SSSR_PETS = {
    "pet_god_sssr_eternity_dragon": {
        "name": "🔱🐉 Eternity Dragon [GOD SSSR]",
        "desc": "Naga abadi yang menjaga batas waktu dan ruang. ATK +500, DEF +300, semua stat +50%",
        "rarity": "GOD SSSR", "price": None, "diamond_price": None,
        "tier": 10,
        "effect": {"atk_bonus": 1500, "def_bonus": 900, "all_stat_pct": 1.5},
        "passive": "Eternal Roar: Setiap 3 ronde, serangan otomatis 5x DMG ke semua musuh"
    },
    "pet_god_sssr_void_phoenix": {
        "name": "🌌🦅 Void Phoenix [GOD SSSR]",
        "desc": "Phoenix dari kekosongan absolut. Bangkit kembali jika mati, restore HP penuh.",
        "rarity": "GOD SSSR", "price": None, "diamond_price": None,
        "tier": 10,
        "effect": {"atk_bonus": 1200, "max_hp_bonus": 6000, "resurrect": True},
        "passive": "Void Rebirth: Bangkit dengan HP penuh sekali per battle"
    },
}

GOD_SSSR_SPECIALS = {
    "warrior": {
        "name": "🔱 Sovereign Rage [GOD SSSR]",
        "desc": "ATK +200% permanen saat HP < 50%, immune semua debuff, setiap serangan ada 15% chance instant kill",
        "trigger": "passive",
        "rarity": "GOD SSSR",
        "effect": {"atk_bonus_pct": 2.0, "debuff_immune": True, "instant_kill_chance": 0.15},
        "status": "sovereign_rage"
    },
    "mage": {
        "name": "🌌 Cosmos Overflow [GOD SSSR]",
        "desc": "Setiap 2 serangan, tembak meteor 20x DMG otomatis, MP tidak pernah habis",
        "trigger": "every_2_attacks",
        "rarity": "GOD SSSR",
        "effect": {"auto_dmg_mult": 20.0, "mp_infinite": True},
        "status": "cosmos_overflow"
    },
    "archer": {
        "name": "⚡ Void Eye [GOD SSSR]",
        "desc": "CRIT rate 100% permanen, CRIT DMG x10, serangan tembus DEF sepenuhnya",
        "trigger": "passive",
        "rarity": "GOD SSSR",
        "effect": {"crit_always": True, "crit_dmg_mult": 10.0, "def_pierce": True},
        "status": "void_eye"
    },
    "rogue": {
        "name": "🌑 Shadow Absolute [GOD SSSR]",
        "desc": "Dodge 60% permanen, tiap dodge balik serang 5x DMG, invisible 3 ronde tiap battle",
        "trigger": "passive",
        "rarity": "GOD SSSR",
        "effect": {"dodge_bonus": 60, "counter_on_dodge": True, "counter_mult": 5.0, "invisible_turns": 3},
        "status": "shadow_absolute"
    },
    "assassin": {
        "name": "💀 Divine Death Sentence [GOD SSSR]",
        "desc": "Kill pertama restore HP penuh, next 5 serangan x10 DMG, Instant KO chance 20%",
        "trigger": "first_kill",
        "rarity": "GOD SSSR",
        "effect": {"heal_full": True, "next_dmg_mult": 30.0, "next_atk_count": 5, "instant_ko_chance": 0.6},
        "status": "death_sentence"
    },
    "reaper": {
        "name": "☠️ Void Soul Reap [GOD SSSR]",
        "desc": "Tiap kill tambah Soul tak terbatas, Harvest: musuh -80% HP + heal 50% HP",
        "trigger": "on_kill",
        "rarity": "GOD SSSR",
        "effect": {"soul_per_kill": 2, "max_souls": 999, "harvest_dmg_pct": 0.8, "heal_pct": 1.5},
        "status": "void_soul_reap"
    },
}

# Boss Drop table for GOD SSSR (rate 0.1%)
GOD_SSSR_BOSS_DROPS = {
    "warrior":     ["god_sssr_warrior_weapon", "god_sssr_warrior_armor", "god_sssr_warrior_skill", "pet_god_sssr_eternity_dragon", "pet_god_sssr_void_phoenix"],
    "mage":        ["god_sssr_mage_weapon", "god_sssr_mage_armor", "god_sssr_mage_skill", "pet_god_sssr_eternity_dragon", "pet_god_sssr_void_phoenix"],
    "archer":      ["god_sssr_archer_weapon", "god_sssr_archer_armor", "god_sssr_archer_skill", "pet_god_sssr_eternity_dragon", "pet_god_sssr_void_phoenix"],
    "rogue":       ["god_sssr_rogue_weapon", "god_sssr_rogue_armor", "god_sssr_rogue_skill", "pet_god_sssr_eternity_dragon", "pet_god_sssr_void_phoenix"],
    "assassin":    ["god_sssr_assassin_weapon", "god_sssr_assassin_armor", "god_sssr_assassin_skill", "pet_god_sssr_eternity_dragon", "pet_god_sssr_void_phoenix"],
    "reaper":["god_sssr_death_scythe_weapon", "god_sssr_death_scythe_armor", "god_sssr_death_scythe_skill", "pet_god_sssr_eternity_dragon", "pet_god_sssr_void_phoenix"],
}

# Update ALL_ITEMS
ALL_ITEMS.update(PREMIUM_WEAPONS)
ALL_ITEMS.update(PREMIUM_ARMORS)
ALL_ITEMS.update(EVOLUTION_STONE)
ALL_ITEMS.update(GOD_SSSR_WEAPONS)
ALL_ITEMS.update(GOD_SSSR_ARMORS)


def get_premium_weapons(char_class: str) -> dict:
    return {k: v for k, v in PREMIUM_WEAPONS.items() if v.get("class") == char_class}

def get_premium_armors(char_class: str) -> dict:
    return {k: v for k, v in PREMIUM_ARMORS.items() if v.get("class") == char_class}

def get_premium_skills(char_class: str) -> dict:
    return {k: v for k, v in PREMIUM_SKILLS.items() if v.get("class") == char_class}

def get_class_tier_name(tier: int) -> dict:
    return EVOLUTION_TIERS.get(tier, EVOLUTION_TIERS[1])

def get_pet_tier_name(tier: int) -> dict:
    return PET_EVOLUTION_TIERS.get(tier, PET_EVOLUTION_TIERS[1])

def get_pet_shop_by_rarity(rarity: str) -> dict:
    if rarity == "all":
        return PET_SHOP
    return {k: v for k, v in PET_SHOP.items() if v["rarity"] == rarity}

