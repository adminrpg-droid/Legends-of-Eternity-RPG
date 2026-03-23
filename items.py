# ─── CONSUMABLES ────────────────────────────────────────────────
CONSUMABLES = {
    "health_potion": {
        "name": "⚕️ Health Potion",
        "desc": "Pulihkan 60 HP",
        "price": 80,
        "diamond_price": None,
        "type": "consumable",
        "effect": {"hp": 60},
        "class": None
    },
    "mana_potion": {
        "name": "🔵 Mana Potion",
        "desc": "Pulihkan 50 MP",
        "price": 80,
        "diamond_price": None,
        "type": "consumable",
        "effect": {"mp": 50},
        "class": None
    },
    "elixir": {
        "name": "⚗️ Grand Elixir",
        "desc": "Pulihkan 150 HP & 120 MP",
        "price": 250,
        "diamond_price": None,
        "type": "consumable",
        "effect": {"hp": 150, "mp": 120},
        "class": None
    },
    "revive_crystal": {
        "name": "💠 Revive Crystal",
        "desc": "Bangkit dengan 50% HP saat mati",
        "price": 350,
        "diamond_price": None,
        "type": "consumable",
        "effect": {},
        "class": None
    },
    "mega_potion": {
        "name": "🌟 Mega Potion",
        "desc": "Pulihkan penuh HP",
        "price": 500,
        "diamond_price": 5,
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
        "price": 600,
        "diamond_price": None,
        "type": "weapon",
        "class": "warrior",
        "rarity": "common",
        "stats": {"atk": 12},
        "sellable": True
    },
    "steel_blade": {
        "name": "⚔️ Steel Blade",
        "desc": "+22 ATK, +5 DEF",
        "price": 1200,
        "diamond_price": None,
        "type": "weapon",
        "class": "warrior",
        "rarity": "uncommon",
        "stats": {"atk": 22, "def": 5},
        "sellable": True
    },
    "knights_greatsword": {
        "name": "🗡️ Knight's Greatsword",
        "desc": "+35 ATK, +10 DEF",
        "price": 2500,
        "diamond_price": None,
        "type": "weapon",
        "class": "warrior",
        "rarity": "rare",
        "stats": {"atk": 35, "def": 10},
        "sellable": True
    },
    "war_hammer": {
        "name": "🔨 War Hammer",
        "desc": "+40 ATK, +20 HP",
        "price": 3200,
        "diamond_price": None,
        "type": "weapon",
        "class": "warrior",
        "rarity": "epic",
        "stats": {"atk": 40, "max_hp": 20},
        "sellable": True
    },
    "titan_axe": {
        "name": "🪓 Titan Axe",
        "desc": "+55 ATK, +15 DEF, +30 HP",
        "price": 5000,
        "diamond_price": 30,
        "type": "weapon",
        "class": "warrior",
        "rarity": "legendary",
        "stats": {"atk": 55, "def": 15, "max_hp": 30},
        "sellable": True
    },

    # ── MAGE ─────────────────────────────────────────────────────
    "apprentice_staff": {
        "name": "🪄 Apprentice Staff",
        "desc": "+14 ATK, +20 MP",
        "price": 600,
        "diamond_price": None,
        "type": "weapon",
        "class": "mage",
        "rarity": "common",
        "stats": {"atk": 14, "max_mp": 20},
        "sellable": True
    },
    "fire_staff": {
        "name": "🔥 Fire Staff",
        "desc": "+24 ATK, +40 MP",
        "price": 1400,
        "diamond_price": None,
        "type": "weapon",
        "class": "mage",
        "rarity": "uncommon",
        "stats": {"atk": 24, "max_mp": 40},
        "sellable": True
    },
    "thunder_wand": {
        "name": "⚡ Thunder Wand",
        "desc": "+36 ATK, +60 MP",
        "price": 2600,
        "diamond_price": None,
        "type": "weapon",
        "class": "mage",
        "rarity": "rare",
        "stats": {"atk": 36, "max_mp": 60},
        "sellable": True
    },
    "arcane_tome": {
        "name": "📖 Arcane Tome",
        "desc": "+42 ATK, +80 MP, +10 SPD",
        "price": 3500,
        "diamond_price": None,
        "type": "weapon",
        "class": "mage",
        "rarity": "epic",
        "stats": {"atk": 42, "max_mp": 80, "spd": 10},
        "sellable": True
    },
    "crystal_scepter": {
        "name": "💎 Crystal Scepter",
        "desc": "+60 ATK, +120 MP",
        "price": 5500,
        "diamond_price": 35,
        "type": "weapon",
        "class": "mage",
        "rarity": "legendary",
        "stats": {"atk": 60, "max_mp": 120},
        "sellable": True
    },

    # ── ARCHER ───────────────────────────────────────────────────
    "wooden_bow": {
        "name": "🏹 Wooden Bow",
        "desc": "+10 ATK, +5 SPD",
        "price": 550,
        "diamond_price": None,
        "type": "weapon",
        "class": "archer",
        "rarity": "common",
        "stats": {"atk": 10, "spd": 5},
        "sellable": True
    },
    "composite_bow": {
        "name": "🏹 Composite Bow",
        "desc": "+20 ATK, +10 SPD",
        "price": 1300,
        "diamond_price": None,
        "type": "weapon",
        "class": "archer",
        "rarity": "uncommon",
        "stats": {"atk": 20, "spd": 10},
        "sellable": True
    },
    "elven_bow": {
        "name": "🌿 Elven Bow",
        "desc": "+32 ATK, +18 SPD",
        "price": 2400,
        "diamond_price": None,
        "type": "weapon",
        "class": "archer",
        "rarity": "rare",
        "stats": {"atk": 32, "spd": 18},
        "sellable": True
    },
    "storm_crossbow": {
        "name": "⚡ Storm Crossbow",
        "desc": "+44 ATK, +22 SPD, +20 MP",
        "price": 3600,
        "diamond_price": None,
        "type": "weapon",
        "class": "archer",
        "rarity": "epic",
        "stats": {"atk": 44, "spd": 22, "max_mp": 20},
        "sellable": True
    },
    "divine_longbow": {
        "name": "✨ Divine Longbow",
        "desc": "+58 ATK, +30 SPD",
        "price": 5200,
        "diamond_price": 32,
        "type": "weapon",
        "class": "archer",
        "rarity": "legendary",
        "stats": {"atk": 58, "spd": 30},
        "sellable": True
    },

    # ── ROGUE ────────────────────────────────────────────────────
    "rusty_dagger": {
        "name": "🔪 Rusty Dagger",
        "desc": "+11 ATK, +6 SPD",
        "price": 550,
        "diamond_price": None,
        "type": "weapon",
        "class": "rogue",
        "rarity": "common",
        "stats": {"atk": 11, "spd": 6},
        "sellable": True
    },
    "shadow_dagger": {
        "name": "🌑 Shadow Dagger",
        "desc": "+22 ATK, +12 SPD",
        "price": 1400,
        "diamond_price": None,
        "type": "weapon",
        "class": "rogue",
        "rarity": "uncommon",
        "stats": {"atk": 22, "spd": 12},
        "sellable": True
    },
    "serpent_blade": {
        "name": "🐍 Serpent Blade",
        "desc": "+34 ATK, +16 SPD",
        "price": 2600,
        "diamond_price": None,
        "type": "weapon",
        "class": "rogue",
        "rarity": "rare",
        "stats": {"atk": 34, "spd": 16},
        "sellable": True
    },
    "phantom_knives": {
        "name": "👻 Phantom Knives",
        "desc": "+46 ATK, +20 SPD",
        "price": 3800,
        "diamond_price": None,
        "type": "weapon",
        "class": "rogue",
        "rarity": "epic",
        "stats": {"atk": 46, "spd": 20},
        "sellable": True
    },
    "void_edge": {
        "name": "🌀 Void Edge",
        "desc": "+62 ATK, +28 SPD, +20 HP",
        "price": 5400,
        "diamond_price": 33,
        "type": "weapon",
        "class": "rogue",
        "rarity": "legendary",
        "stats": {"atk": 62, "spd": 28, "max_hp": 20},
        "sellable": True
    },

    # ── ASSASSIN ─────────────────────────────────────────────────
    "poison_needle": {
        "name": "💉 Poison Needle",
        "desc": "+13 ATK, +8 SPD",
        "price": 600,
        "diamond_price": None,
        "type": "weapon",
        "class": "assassin",
        "rarity": "common",
        "stats": {"atk": 13, "spd": 8},
        "sellable": True
    },
    "shadow_fang": {
        "name": "🦷 Shadow Fang",
        "desc": "+25 ATK, +14 SPD",
        "price": 1500,
        "diamond_price": None,
        "type": "weapon",
        "class": "assassin",
        "rarity": "uncommon",
        "stats": {"atk": 25, "spd": 14},
        "sellable": True
    },
    "assassin_blade": {
        "name": "⚰️ Assassin Blade",
        "desc": "+38 ATK, +18 SPD",
        "price": 2800,
        "diamond_price": None,
        "type": "weapon",
        "class": "assassin",
        "rarity": "rare",
        "stats": {"atk": 38, "spd": 18},
        "sellable": True
    },
    "nightshade_sickle": {
        "name": "🌙 Nightshade Sickle",
        "desc": "+50 ATK, +22 SPD",
        "price": 4000,
        "diamond_price": None,
        "type": "weapon",
        "class": "assassin",
        "rarity": "epic",
        "stats": {"atk": 50, "spd": 22},
        "sellable": True
    },
    "death_scythe": {
        "name": "💀 Death Scythe",
        "desc": "+65 ATK, +30 SPD",
        "price": 5800,
        "diamond_price": 38,
        "type": "weapon",
        "class": "assassin",
        "rarity": "legendary",
        "stats": {"atk": 65, "spd": 30},
        "sellable": True
    },

    # ── NECROMANCER ──────────────────────────────────────────────
    "bone_staff": {
        "name": "🦴 Bone Staff",
        "desc": "+12 ATK, +25 MP",
        "price": 600,
        "diamond_price": None,
        "type": "weapon",
        "class": "necromancer",
        "rarity": "common",
        "stats": {"atk": 12, "max_mp": 25},
        "sellable": True
    },
    "cursed_tome": {
        "name": "📕 Cursed Tome",
        "desc": "+22 ATK, +50 MP",
        "price": 1400,
        "diamond_price": None,
        "type": "weapon",
        "class": "necromancer",
        "rarity": "uncommon",
        "stats": {"atk": 22, "max_mp": 50},
        "sellable": True
    },
    "soul_staff": {
        "name": "👁️ Soul Staff",
        "desc": "+36 ATK, +80 MP",
        "price": 2700,
        "diamond_price": None,
        "type": "weapon",
        "class": "necromancer",
        "rarity": "rare",
        "stats": {"atk": 36, "max_mp": 80},
        "sellable": True
    },
    "lich_scepter": {
        "name": "💜 Lich Scepter",
        "desc": "+48 ATK, +100 MP, +20 HP",
        "price": 4200,
        "diamond_price": None,
        "type": "weapon",
        "class": "necromancer",
        "rarity": "epic",
        "stats": {"atk": 48, "max_mp": 100, "max_hp": 20},
        "sellable": True
    },
    "doomsday_grimoire": {
        "name": "🌑 Doomsday Grimoire",
        "desc": "+64 ATK, +140 MP",
        "price": 6000,
        "diamond_price": 40,
        "type": "weapon",
        "class": "necromancer",
        "rarity": "legendary",
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
        "price": 700,
        "diamond_price": None,
        "type": "armor",
        "class": "warrior",
        "rarity": "common",
        "stats": {"def": 10, "max_hp": 20},
        "sellable": True
    },
    "chain_mail": {
        "name": "⛓️ Chain Mail",
        "desc": "+18 DEF, +40 HP",
        "price": 1500,
        "diamond_price": None,
        "type": "armor",
        "class": "warrior",
        "rarity": "uncommon",
        "stats": {"def": 18, "max_hp": 40},
        "sellable": True
    },
    "knight_plate": {
        "name": "🛡️ Knight Plate",
        "desc": "+28 DEF, +60 HP",
        "price": 2800,
        "diamond_price": None,
        "type": "armor",
        "class": "warrior",
        "rarity": "rare",
        "stats": {"def": 28, "max_hp": 60},
        "sellable": True
    },
    "battle_fortress": {
        "name": "🏰 Battle Fortress",
        "desc": "+38 DEF, +90 HP",
        "price": 4000,
        "diamond_price": None,
        "type": "armor",
        "class": "warrior",
        "rarity": "epic",
        "stats": {"def": 38, "max_hp": 90},
        "sellable": True
    },
    "dragonscale_armor": {
        "name": "🐉 Dragonscale Armor",
        "desc": "+52 DEF, +130 HP",
        "price": 6500,
        "diamond_price": 40,
        "type": "armor",
        "class": "warrior",
        "rarity": "legendary",
        "stats": {"def": 52, "max_hp": 130},
        "sellable": True
    },

    # ── MAGE ─────────────────────────────────────────────────────
    "cloth_robe": {
        "name": "👘 Cloth Robe",
        "desc": "+5 DEF, +30 MP",
        "price": 600,
        "diamond_price": None,
        "type": "armor",
        "class": "mage",
        "rarity": "common",
        "stats": {"def": 5, "max_mp": 30},
        "sellable": True
    },
    "arcane_robe": {
        "name": "🔮 Arcane Robe",
        "desc": "+10 DEF, +60 MP",
        "price": 1400,
        "diamond_price": None,
        "type": "armor",
        "class": "mage",
        "rarity": "uncommon",
        "stats": {"def": 10, "max_mp": 60},
        "sellable": True
    },
    "starweave_mantle": {
        "name": "✨ Starweave Mantle",
        "desc": "+16 DEF, +90 MP",
        "price": 2600,
        "diamond_price": None,
        "type": "armor",
        "class": "mage",
        "rarity": "rare",
        "stats": {"def": 16, "max_mp": 90},
        "sellable": True
    },
    "void_shroud": {
        "name": "🌀 Void Shroud",
        "desc": "+24 DEF, +130 MP, +10 ATK",
        "price": 4200,
        "diamond_price": None,
        "type": "armor",
        "class": "mage",
        "rarity": "epic",
        "stats": {"def": 24, "max_mp": 130, "atk": 10},
        "sellable": True
    },
    "celestial_vestment": {
        "name": "🌟 Celestial Vestment",
        "desc": "+35 DEF, +180 MP",
        "price": 7000,
        "diamond_price": 45,
        "type": "armor",
        "class": "mage",
        "rarity": "legendary",
        "stats": {"def": 35, "max_mp": 180},
        "sellable": True
    },

    # ── ARCHER ───────────────────────────────────────────────────
    "leather_vest": {
        "name": "🥋 Leather Vest",
        "desc": "+7 DEF, +8 SPD",
        "price": 600,
        "diamond_price": None,
        "type": "armor",
        "class": "archer",
        "rarity": "common",
        "stats": {"def": 7, "spd": 8},
        "sellable": True
    },
    "forest_cloak": {
        "name": "🌿 Forest Cloak",
        "desc": "+14 DEF, +14 SPD",
        "price": 1400,
        "diamond_price": None,
        "type": "armor",
        "class": "archer",
        "rarity": "uncommon",
        "stats": {"def": 14, "spd": 14},
        "sellable": True
    },
    "ranger_mail": {
        "name": "🌲 Ranger Mail",
        "desc": "+22 DEF, +20 SPD",
        "price": 2700,
        "diamond_price": None,
        "type": "armor",
        "class": "archer",
        "rarity": "rare",
        "stats": {"def": 22, "spd": 20},
        "sellable": True
    },
    "wind_dancer": {
        "name": "💨 Wind Dancer",
        "desc": "+30 DEF, +28 SPD",
        "price": 4200,
        "diamond_price": None,
        "type": "armor",
        "class": "archer",
        "rarity": "epic",
        "stats": {"def": 30, "spd": 28},
        "sellable": True
    },
    "storm_warden": {
        "name": "⚡ Storm Warden",
        "desc": "+42 DEF, +38 SPD",
        "price": 6800,
        "diamond_price": 42,
        "type": "armor",
        "class": "archer",
        "rarity": "legendary",
        "stats": {"def": 42, "spd": 38},
        "sellable": True
    },

    # ── ROGUE ────────────────────────────────────────────────────
    "shadow_garb": {
        "name": "🌑 Shadow Garb",
        "desc": "+6 DEF, +10 SPD",
        "price": 600,
        "diamond_price": None,
        "type": "armor",
        "class": "rogue",
        "rarity": "common",
        "stats": {"def": 6, "spd": 10},
        "sellable": True
    },
    "night_leather": {
        "name": "🌙 Night Leather",
        "desc": "+13 DEF, +16 SPD",
        "price": 1400,
        "diamond_price": None,
        "type": "armor",
        "class": "rogue",
        "rarity": "uncommon",
        "stats": {"def": 13, "spd": 16},
        "sellable": True
    },
    "phantom_silk": {
        "name": "👻 Phantom Silk",
        "desc": "+20 DEF, +22 SPD",
        "price": 2700,
        "diamond_price": None,
        "type": "armor",
        "class": "rogue",
        "rarity": "rare",
        "stats": {"def": 20, "spd": 22},
        "sellable": True
    },
    "void_wraps": {
        "name": "🌀 Void Wraps",
        "desc": "+28 DEF, +30 SPD, +10 ATK",
        "price": 4500,
        "diamond_price": None,
        "type": "armor",
        "class": "rogue",
        "rarity": "epic",
        "stats": {"def": 28, "spd": 30, "atk": 10},
        "sellable": True
    },
    "shadow_sovereign": {
        "name": "🌑 Shadow Sovereign",
        "desc": "+40 DEF, +40 SPD",
        "price": 7200,
        "diamond_price": 45,
        "type": "armor",
        "class": "rogue",
        "rarity": "legendary",
        "stats": {"def": 40, "spd": 40},
        "sellable": True
    },

    # ── ASSASSIN ─────────────────────────────────────────────────
    "hunter_vest": {
        "name": "🎯 Hunter Vest",
        "desc": "+7 DEF, +10 SPD",
        "price": 650,
        "diamond_price": None,
        "type": "armor",
        "class": "assassin",
        "rarity": "common",
        "stats": {"def": 7, "spd": 10},
        "sellable": True
    },
    "shade_armor": {
        "name": "🌑 Shade Armor",
        "desc": "+15 DEF, +18 SPD",
        "price": 1600,
        "diamond_price": None,
        "type": "armor",
        "class": "assassin",
        "rarity": "uncommon",
        "stats": {"def": 15, "spd": 18},
        "sellable": True
    },
    "cursed_shroud": {
        "name": "⚰️ Cursed Shroud",
        "desc": "+24 DEF, +24 SPD",
        "price": 3000,
        "diamond_price": None,
        "type": "armor",
        "class": "assassin",
        "rarity": "rare",
        "stats": {"def": 24, "spd": 24},
        "sellable": True
    },
    "deathmark_cloak": {
        "name": "💀 Deathmark Cloak",
        "desc": "+34 DEF, +32 SPD, +12 ATK",
        "price": 4800,
        "diamond_price": None,
        "type": "armor",
        "class": "assassin",
        "rarity": "epic",
        "stats": {"def": 34, "spd": 32, "atk": 12},
        "sellable": True
    },
    "reaper_mantle": {
        "name": "🌑 Reaper Mantle",
        "desc": "+46 DEF, +44 SPD",
        "price": 7500,
        "diamond_price": 48,
        "type": "armor",
        "class": "assassin",
        "rarity": "legendary",
        "stats": {"def": 46, "spd": 44},
        "sellable": True
    },

    # ── NECROMANCER ──────────────────────────────────────────────
    "tattered_robe": {
        "name": "🧟 Tattered Robe",
        "desc": "+6 DEF, +35 MP",
        "price": 600,
        "diamond_price": None,
        "type": "armor",
        "class": "necromancer",
        "rarity": "common",
        "stats": {"def": 6, "max_mp": 35},
        "sellable": True
    },
    "death_shroud": {
        "name": "💜 Death Shroud",
        "desc": "+13 DEF, +70 MP",
        "price": 1500,
        "diamond_price": None,
        "type": "armor",
        "class": "necromancer",
        "rarity": "uncommon",
        "stats": {"def": 13, "max_mp": 70},
        "sellable": True
    },
    "bone_armor": {
        "name": "🦴 Bone Armor",
        "desc": "+22 DEF, +100 MP",
        "price": 2900,
        "diamond_price": None,
        "type": "armor",
        "class": "necromancer",
        "rarity": "rare",
        "stats": {"def": 22, "max_mp": 100},
        "sellable": True
    },
    "lich_vestment": {
        "name": "💀 Lich Vestment",
        "desc": "+32 DEF, +140 MP, +15 ATK",
        "price": 4600,
        "diamond_price": None,
        "type": "armor",
        "class": "necromancer",
        "rarity": "epic",
        "stats": {"def": 32, "max_mp": 140, "atk": 15},
        "sellable": True
    },
    "void_phylactery": {
        "name": "🌑 Void Phylactery",
        "desc": "+44 DEF, +200 MP",
        "price": 7800,
        "diamond_price": 50,
        "type": "armor",
        "class": "necromancer",
        "rarity": "legendary",
        "stats": {"def": 44, "max_mp": 200},
        "sellable": True
    },
}

# ─── VIP PACKAGES ───────────────────────────────────────────────
VIP_PACKAGES = {
    "vip_silver": {
        "name": "🥈 VIP Silver",
        "price_idr": 15000,
        "bank": "BCA",
        "account": "1234567890",
        "account_name": "Legends of Eternity",
        "duration_days": 30,
        "effects": {
            "crit_bonus": 10,
            "max_hp_bonus": 50,
            "max_mp_bonus": 30,
            "atk_bonus": 8,
        },
        "desc": "Crit +10%, HP +50, MP +30, ATK +8 selama 30 hari"
    },
    "vip_gold": {
        "name": "🥇 VIP Gold",
        "price_idr": 30000,
        "bank": "BCA",
        "account": "1234567890",
        "account_name": "Legends of Eternity",
        "duration_days": 30,
        "effects": {
            "crit_bonus": 20,
            "max_hp_bonus": 100,
            "max_mp_bonus": 60,
            "atk_bonus": 18,
        },
        "desc": "Crit +20%, HP +100, MP +60, ATK +18 selama 30 hari"
    },
    "vip_diamond": {
        "name": "💎 VIP Diamond",
        "price_idr": 75000,
        "bank": "BCA",
        "account": "1234567890",
        "account_name": "Legends of Eternity",
        "duration_days": 30,
        "effects": {
            "crit_bonus": 35,
            "max_hp_bonus": 200,
            "max_mp_bonus": 120,
            "atk_bonus": 35,
        },
        "desc": "Crit +35%, HP +200, MP +120, ATK +35 selama 30 hari"
    },
}

# ─── COIN & DIAMOND PACKAGES ────────────────────────────────────
COIN_PACKAGES = {
    "coins_small": {
        "name": "💰 500 Coin",
        "coins": 500,
        "price_idr": 10000,
        "bank": "BCA",
        "account": "1234567890",
        "account_name": "Legends of Eternity",
    },
    "coins_medium": {
        "name": "💰 1500 Coin",
        "coins": 1500,
        "price_idr": 25000,
        "bank": "BCA",
        "account": "1234567890",
        "account_name": "Legends of Eternity",
    },
    "coins_large": {
        "name": "💰 5000 Coin",
        "coins": 5000,
        "price_idr": 75000,
        "bank": "BCA",
        "account": "1234567890",
        "account_name": "Legends of Eternity",
    },
}

DIAMOND_PACKAGES = {
    "diamond_small": {
        "name": "💎 50 Diamond",
        "diamonds": 50,
        "price_idr": 15000,
        "bank": "BCA",
        "account": "1234567890",
        "account_name": "Legends of Eternity",
    },
    "diamond_medium": {
        "name": "💎 150 Diamond",
        "diamonds": 150,
        "price_idr": 40000,
        "bank": "BCA",
        "account": "1234567890",
        "account_name": "Legends of Eternity",
    },
    "diamond_large": {
        "name": "💎 500 Diamond",
        "diamonds": 500,
        "price_idr": 120000,
        "bank": "BCA",
        "account": "1234567890",
        "account_name": "Legends of Eternity",
    },
}

# ─── BOSS DROP POOL (per class) ──────────────────────────────────
BOSS_DROPS = {
    "warrior": ["war_hammer", "titan_axe", "battle_fortress", "dragonscale_armor"],
    "mage": ["arcane_tome", "crystal_scepter", "void_shroud", "celestial_vestment"],
    "archer": ["storm_crossbow", "divine_longbow", "wind_dancer", "storm_warden"],
    "rogue": ["phantom_knives", "void_edge", "void_wraps", "shadow_sovereign"],
    "assassin": ["nightshade_sickle", "death_scythe", "deathmark_cloak", "reaper_mantle"],
    "necromancer": ["lich_scepter", "doomsday_grimoire", "lich_vestment", "void_phylactery"],
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
# Skill yang bisa dibeli di shop (harga mahal, sesuai class)
SHOP_SKILLS = {
    # ── WARRIOR ──────────────────────────────────────────────────
    "warrior_skill_1": {
        "name": "🌪️ Whirlwind",
        "desc": "Serang semua musuh di sekitar, 2.5x DMG",
        "class": "warrior",
        "price": 3500,
        "rarity": "rare",
        "effect": {"dmg_mult": 2.5, "mp_cost": 35, "cooldown": 4},
        "lore": "Putaran angin yang menghancurkan semua yang ada di dekat Warrior.",
    },
    "warrior_skill_2": {
        "name": "🛡️ Iron Defense",
        "desc": "Tingkatkan DEF +30 selama 3 ronde",
        "class": "warrior",
        "price": 4200,
        "rarity": "epic",
        "effect": {"def_buff": 30, "duration": 3, "mp_cost": 40, "cooldown": 5},
        "lore": "Pertahanan baja yang tak tertembus oleh serangan apapun.",
    },
    "warrior_skill_3": {
        "name": "⚡ Thunder Charge",
        "desc": "Serangan kilat, 3.2x DMG + stun",
        "class": "warrior",
        "price": 6000,
        "rarity": "legendary",
        "effect": {"dmg_mult": 3.2, "mp_cost": 55, "cooldown": 6},
        "lore": "Terjang dengan kecepatan petir, mengejutkan lawan sebelum mereka bereaksi.",
    },
    # ── MAGE ─────────────────────────────────────────────────────
    "mage_skill_1": {
        "name": "❄️ Blizzard",
        "desc": "Badai es membekukan musuh, 2.8x DMG",
        "class": "mage",
        "price": 3800,
        "rarity": "rare",
        "effect": {"dmg_mult": 2.8, "mp_cost": 40, "cooldown": 4},
        "lore": "Badai dingin yang membekukan siapa pun yang berani menantang sang Mage.",
    },
    "mage_skill_2": {
        "name": "⚡ Chain Lightning",
        "desc": "Petir berantai menyambar 2-3x, 2.0x DMG per sambaran",
        "class": "mage",
        "price": 4500,
        "rarity": "epic",
        "effect": {"dmg_mult": 2.0, "hits": 3, "mp_cost": 50, "cooldown": 5},
        "lore": "Petir yang melompat dari satu musuh ke musuh lainnya tanpa henti.",
    },
    "mage_skill_3": {
        "name": "🌌 Arcane Nova",
        "desc": "Ledakan arkana terbesar, 4x DMG",
        "class": "mage",
        "price": 7000,
        "rarity": "legendary",
        "effect": {"dmg_mult": 4.0, "mp_cost": 80, "cooldown": 7},
        "lore": "Puncak kekuatan sihir — ledakan energi arkana yang bisa meruntuhkan gunung.",
    },
    # ── ARCHER ───────────────────────────────────────────────────
    "archer_skill_1": {
        "name": "🎯 Snipe",
        "desc": "Bidikan tepat, 3x DMG + CRIT +20%",
        "class": "archer",
        "price": 3600,
        "rarity": "rare",
        "effect": {"dmg_mult": 3.0, "crit_bonus": 20, "mp_cost": 35, "cooldown": 4},
        "lore": "Bidikan mematikan yang tidak pernah meleset dari targetnya.",
    },
    "archer_skill_2": {
        "name": "🌀 Cyclone Shot",
        "desc": "Anak panah tornado, 2.5x DMG + dodge +15%",
        "class": "archer",
        "price": 4300,
        "rarity": "epic",
        "effect": {"dmg_mult": 2.5, "dodge_bonus": 15, "mp_cost": 45, "cooldown": 5},
        "lore": "Panah yang berputar bak angin topan, menembus pertahanan lawan.",
    },
    "archer_skill_3": {
        "name": "💥 Meteor Shot",
        "desc": "Panah setara meteor, 4.5x DMG",
        "class": "archer",
        "price": 7500,
        "rarity": "legendary",
        "effect": {"dmg_mult": 4.5, "mp_cost": 70, "cooldown": 7},
        "lore": "Panah yang meledak seperti meteor saat mengenai target.",
    },
    # ── ROGUE ────────────────────────────────────────────────────
    "rogue_skill_1": {
        "name": "🌑 Smoke Bomb",
        "desc": "Kabur dan serang dari kegelapan, 2.5x DMG + dodge +30%",
        "class": "rogue",
        "price": 3700,
        "rarity": "rare",
        "effect": {"dmg_mult": 2.5, "dodge_bonus": 30, "mp_cost": 35, "cooldown": 4},
        "lore": "Bom asap menutupi gerak Rogue, memberi celah untuk serangan mematikan.",
    },
    "rogue_skill_2": {
        "name": "⚡ Backstab Chain",
        "desc": "Tikam beruntun dari belakang, 3x DMG x2",
        "class": "rogue",
        "price": 4800,
        "rarity": "epic",
        "effect": {"dmg_mult": 3.0, "hits": 2, "mp_cost": 50, "cooldown": 5},
        "lore": "Rentetan tikaman dari bayangan yang tak sempat diantisipasi lawan.",
    },
    "rogue_skill_3": {
        "name": "💀 Phantom Execution",
        "desc": "Eksekusi bayangan, 5x DMG jika musuh HP < 30%",
        "class": "rogue",
        "price": 8000,
        "rarity": "legendary",
        "effect": {"dmg_mult": 5.0, "execute_threshold": 0.3, "mp_cost": 65, "cooldown": 8},
        "lore": "Eksekusi sempurna oleh sosok bayangan — hanya muncul saat musuh hampir mati.",
    },
    # ── ASSASSIN ─────────────────────────────────────────────────
    "assassin_skill_1": {
        "name": "🗡️ Poison Blade",
        "desc": "Racun pada bilah, 2.2x DMG + DoT selama 3 ronde",
        "class": "assassin",
        "price": 3900,
        "rarity": "rare",
        "effect": {"dmg_mult": 2.2, "dot_dmg": 15, "dot_duration": 3, "mp_cost": 40, "cooldown": 4},
        "lore": "Racun mematikan yang terus menggerogoti target bahkan setelah serangan.",
    },
    "assassin_skill_2": {
        "name": "🌀 Vanish Strike",
        "desc": "Lenyap lalu serang balik, 3.5x DMG + evasion 100%",
        "class": "assassin",
        "price": 5000,
        "rarity": "epic",
        "effect": {"dmg_mult": 3.5, "evasion_next": True, "mp_cost": 55, "cooldown": 6},
        "lore": "Assassin menghilang dalam sekejap sebelum muncul kembali di belakang musuh.",
    },
    "assassin_skill_3": {
        "name": "💉 Soul Harvest",
        "desc": "Panen jiwa musuh, 4.8x DMG + heal 20% dari DMG",
        "class": "assassin",
        "price": 8500,
        "rarity": "legendary",
        "effect": {"dmg_mult": 4.8, "lifesteal": 0.20, "mp_cost": 70, "cooldown": 8},
        "lore": "Menuai jiwa musuh untuk memperpanjang kehidupan sang Assassin.",
    },
    # ── NECROMANCER ──────────────────────────────────────────────
    "necromancer_skill_1": {
        "name": "💀 Corpse Explosion",
        "desc": "Ledakkan mayat musuh, 3x DMG + AoE",
        "class": "necromancer",
        "price": 4000,
        "rarity": "rare",
        "effect": {"dmg_mult": 3.0, "aoe": True, "mp_cost": 45, "cooldown": 4},
        "lore": "Menggunakan mayat musuh sebagai bom — cara paling kejam untuk berperang.",
    },
    "necromancer_skill_2": {
        "name": "🌑 Dark Ritual",
        "desc": "Ritual gelap, +50 HP + 3.2x DMG selanjutnya",
        "class": "necromancer",
        "price": 5200,
        "rarity": "epic",
        "effect": {"heal": 50, "dmg_buff_mult": 3.2, "mp_cost": 60, "cooldown": 5},
        "lore": "Ritual pengorbanan yang memberi kekuatan luar biasa dari alam kematian.",
    },
    "necromancer_skill_3": {
        "name": "👁️ Lich Awakening",
        "desc": "Bangkit sebagai Lich, semua stat +50% selama 4 ronde",
        "class": "necromancer",
        "price": 9000,
        "rarity": "legendary",
        "effect": {"stat_boost": 0.5, "duration": 4, "mp_cost": 90, "cooldown": 9},
        "lore": "Transformasi menjadi Lich sejati — kekuatan alam kematian mengalir penuh.",
    },
}


def get_class_skills(char_class: str) -> dict:
    """Dapatkan semua skill shop yang tersedia untuk class tertentu."""
    return {k: v for k, v in SHOP_SKILLS.items() if v["class"] == char_class}
