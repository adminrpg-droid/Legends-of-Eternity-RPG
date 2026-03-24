import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, level_up
from monster import DUNGEONS, get_dungeon_monsters, get_boss
from items import BOSS_DROPS, get_item
from ui import hp_bar


def _ds(ctx, uid):  return ctx.user_data.get(f"dg_{uid}", {})
def _sds(ctx, uid, s): ctx.user_data[f"dg_{uid}"] = s
def _cds(ctx, uid): ctx.user_data.pop(f"dg_{uid}", None)


async def dungeon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user   = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Ketik /start dulu!")
        return
    if player["hp"] <= 0:
        await update.message.reply_text("💀 HP 0! Pulihkan di /inventory")
        return
    await _show_dungeon_list(update.message, player, is_msg=True)


async def _show_dungeon_list(target, player: dict, is_msg=False):
    text = (
        f"╔══════════════════════════════════╗\n"
        f"║    🏰  *PILIH DUNGEON*            ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  ❤️ {player['hp']}/{player['max_hp']}  Lv.{player['level']}\n"
        f"╚══════════════════════════════════╝\n\n"
        f"Pilih dungeon yang ingin dijelajahi:\n"
        f"_(Min. level tercantum di setiap dungeon)_"
    )
    buttons = []
    for did, dg in DUNGEONS.items():
        min_lv = dg["min_level"]
        unlocked = player["level"] >= min_lv
        lock = "🔓" if unlocked else f"🔒 (Lv.{min_lv}+)"
        label = f"{dg['emoji']} {dg['name']} {lock}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"dungeon_enter_{did}")])

    markup = InlineKeyboardMarkup(buttons)
    if is_msg:
        await target.reply_text(text, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)


async def dungeon_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data.replace("dungeon_", "")
    user   = query.from_user
    player = get_player(user.id)

    if not player:
        await query.edit_message_text("❌ Ketik /start dulu!")
        return

    # ── Enter dungeon ────────────────────────────────────────────
    if action.startswith("enter_"):
        did = int(action.replace("enter_", ""))
        dg  = DUNGEONS.get(did)
        if not dg:
            await query.answer("Dungeon tidak ada!", show_alert=True)
            return
        if player["level"] < dg["min_level"]:
            await query.answer(
                f"❌ Perlu Lv.{dg['min_level']}! Kamu Lv.{player['level']}",
                show_alert=True
            )
            return

        _sds(context, user.id, {
            "dungeon_id": did,
            "floor": 1,
            "total_floors": dg["floor_count"],
            "monster": None,
            "turn": 1,
            "log": [],
            "is_boss": False,
        })
        await _show_dungeon_room(query, player, _ds(context, user.id))
        return

    if action == "exit":
        _cds(context, user.id)
        await query.edit_message_text(
            "🚪 *Kamu keluar dari dungeon.*\nSampai jumpa petualang!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Menu", callback_data="menu")
            ]])
        )
        return

    if action == "dungeonlist":
        await _show_dungeon_list(query, player)
        return

    if action == "explore":
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Masuk dungeon dulu!")
            return
        await _dungeon_explore(query, player, dstate, context, user.id)
        return

    if action == "boss":
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Masuk dungeon dulu!")
            return
        did  = dstate["dungeon_id"]
        dg   = DUNGEONS[did]
        boss = get_boss(dg["boss"], player["level"])
        dstate.update({"monster": boss, "is_boss": True, "turn": 1, "log": []})
        _sds(context, user.id, dstate)
        await _show_dg_battle(query, player, dstate, is_boss=True)
        return

    if action in ("attack", "skill", "potion", "dflee"):
        dstate = _ds(context, user.id)
        if not dstate:
            await query.edit_message_text("❌ Tidak ada battle aktif.")
            return
        await _process_dg_action(query, player, dstate, action, context, user.id)
        return


async def _show_dungeon_room(target, player: dict, dstate: dict):
    did  = dstate["dungeon_id"]
    dg   = DUNGEONS[did]
    fl   = dstate["floor"]
    total = dstate["total_floors"]

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  {dg['emoji']} *{dg['name']}*               ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  📍 Lantai {fl}/{total}\n"
        f"║  ❤️ {player['hp']}/{player['max_hp']}\n"
        f"║  💰 {player.get('coin',0)} Coin\n"
        f"╚══════════════════════════════════╝\n\n"
        f"_{dg['desc']}_\n\n"
        f"Apa yang akan kamu lakukan?"
    )
    keyboard = [
        [InlineKeyboardButton("⚔️ Jelajahi Lantai",  callback_data="dungeon_explore")],
        [InlineKeyboardButton("👹 Tantang Boss",       callback_data="dungeon_boss")],
        [InlineKeyboardButton("🚪 Keluar Dungeon",    callback_data="dungeon_exit")],
    ]
    await target.edit_message_text(text, parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(keyboard))


async def _dungeon_explore(query, player: dict, dstate: dict, context, user_id: int):
    events = ["monster"] * 5 + ["treasure", "trap", "rest", "monster"]
    event  = random.choice(events)
    did    = dstate["dungeon_id"]

    if event == "treasure":
        gold = random.randint(30, 80)
        player["coin"] = player.get("coin", 0) + gold
        save_player(user_id, player)
        await query.edit_message_text(
            f"💰 *HARTA KARUN!*\n\nKamu menemukan peti berisi *{gold} Coin*!\n"
            f"Total Coin: {player.get('coin',0)}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚔️ Lanjut", callback_data="dungeon_explore"),
                 InlineKeyboardButton("👹 Boss",    callback_data="dungeon_boss")],
                [InlineKeyboardButton("🚪 Keluar", callback_data="dungeon_exit")],
            ])
        )
        return

    if event == "trap":
        dmg = random.randint(15, 35)
        player["hp"] = max(1, player["hp"] - dmg)
        save_player(user_id, player)
        await query.edit_message_text(
            f"🪤 *JEBAKAN!*\n\nKamu terkena jebakan! -{dmg} HP\n"
            f"HP tersisa: {player['hp']}/{player['max_hp']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚔️ Lanjut", callback_data="dungeon_explore"),
                 InlineKeyboardButton("🚪 Keluar", callback_data="dungeon_exit")],
            ])
        )
        return

    if event == "rest":
        heal = random.randint(25, 50)
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        save_player(user_id, player)
        await query.edit_message_text(
            f"🛖 *TEMPAT ISTIRAHAT*\n\nKamu menemukan api unggun!\n"
            f"+{heal} HP | HP: {player['hp']}/{player['max_hp']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚔️ Lanjut", callback_data="dungeon_explore"),
                 InlineKeyboardButton("👹 Boss",    callback_data="dungeon_boss")],
            ])
        )
        return

    # Monster encounter
    monster = get_dungeon_monsters(did, player["level"])
    dstate.update({"monster": monster, "is_boss": False, "turn": 1, "log": []})
    _sds(context, user_id, dstate)
    await _show_dg_battle(query, player, dstate)


async def _show_dg_battle(query, player: dict, dstate: dict, is_boss=False):
    monster = dstate["monster"]
    log_txt = "\n".join(dstate["log"][-3:]) if dstate["log"] else "⚔️ Pertempuran dimulai!"
    p_bar   = hp_bar(player["hp"], player["max_hp"], 9)
    m_bar   = hp_bar(monster["current_hp"], monster["hp"], 9)
    boss_tag = "👹 *BOSS BATTLE!*\n" if is_boss else ""
    boss_special = f"\n💥 _{monster.get('special', '')}_" if is_boss else ""

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║    🏰  *DUNGEON BATTLE*  🏰      ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"{boss_tag}"
        f"🟢 *{player['name']}* Lv.{player['level']}\n"
        f"❤️ {p_bar}\n"
        f"💙 MP: {player['mp']}/{player['max_mp']}\n\n"
        f"{monster['emoji']} *{monster['name']}*{boss_special}\n"
        f"❤️ {m_bar}\n\n"
        f"📜 {log_txt}\n\n"
        f"🎮 Giliran #{dstate['turn']}:"
    )

    cd     = player.get("skill_cooldown", 0)
    s_lbl  = player["skill"] if cd == 0 else f"{player['skill']} ⏳{cd}"
    pot    = player.get("inventory", {}).get("health_potion", 0)
    flee_txt = "🚫 Boss" if is_boss else "🏃 Kabur"

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Serang", callback_data="dungeon_attack"),
            InlineKeyboardButton(s_lbl,       callback_data="dungeon_skill"),
        ],
        [
            InlineKeyboardButton(f"🧪 Potion ({pot})", callback_data="dungeon_potion"),
            InlineKeyboardButton(flee_txt,              callback_data="dungeon_dflee"),
        ],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


async def _process_dg_action(query, player: dict, dstate: dict, action: str, context, user_id: int):
    monster = dstate["monster"]
    log     = dstate["log"]
    is_boss = dstate.get("is_boss", False)

    if action == "dflee":
        if is_boss:
            await query.answer("⛔ Tidak bisa kabur dari Boss!", show_alert=True)
            return
        log.append("🏃 Kamu kabur dari dungeon!")
        _cds(context, user_id)
        save_player(user_id, player)
        await query.edit_message_text("🏃 *Kamu kabur!*", parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup([[
                                          InlineKeyboardButton("🏠 Menu", callback_data="menu")
                                      ]]))
        return

    if action == "potion":
        pot = player.get("inventory", {}).get("health_potion", 0)
        if pot <= 0:
            await query.answer("❌ Potion habis!", show_alert=True)
            return
        heal = 60
        player["hp"] = min(player["max_hp"], player["hp"] + heal)
        player["inventory"]["health_potion"] -= 1
        log.append(f"🧪 Potion +{heal} HP!")
        player_dmg = 0

    elif action == "skill":
        if player.get("skill_cooldown", 0) > 0:
            await query.answer(f"⏳ Cooldown!", show_alert=True)
            return
        if player["mp"] < 25:
            await query.answer("❌ MP kurang!", show_alert=True)
            return
        player["mp"] -= 25
        mult = random.uniform(2.0, 3.0)
        player_dmg = max(1, int(player["atk"] * mult - monster["def"] * 0.4))
        if player["class"] == "necromancer":
            player["hp"] = min(player["max_hp"], player["hp"] + player_dmg // 3)
        player["skill_cooldown"] = 3
        log.append(f"✨ {player['skill']}! -{player_dmg} HP 💥")

    else:  # attack
        crit_chance = player.get("crit", 10)
        crit = random.randint(1, 100) <= crit_chance
        mult = 1.6 if crit else 1.0
        player_dmg = max(1, int(player["atk"] * mult - monster["def"] * 0.7))
        log.append(f"⚔️ Serang! -{player_dmg} HP{'  💥CRIT!' if crit else ''}")

    if action not in ("potion",):
        monster["current_hp"] -= player_dmg
    if action != "skill" and player.get("skill_cooldown", 0) > 0:
        player["skill_cooldown"] -= 1

    # ── Monster dies ─────────────────────────────────────────────
    if monster["current_hp"] <= 0:
        gold  = int(random.randint(*monster.get("gold", (20, 50))) * 0.75)
        exp   = int(monster.get("exp", 50) * 0.8)

        player["coin"]  = player.get("coin", 0) + (gold * 2 if is_boss else gold)
        player["exp"]   += exp
        player["kills"] += 1
        if is_boss:
            player["boss_kills"] = player.get("boss_kills", 0) + 1
            player["dungeon_clears"] = player.get("dungeon_clears", 0) + 1
            dstate["floor"] = dstate.get("floor", 1) + 1

        player, leveled, lv_gained = level_up(player)
        lv_txt = f"\n🎊 *LEVEL UP!* → Lv.{player['level']}" if leveled else ""

        # Boss drops rare item
        drop_txt = ""
        if is_boss:
            char_class = player.get("class", "warrior")
            drops = BOSS_DROPS.get(char_class, [])
            if drops and random.randint(1, 100) <= 60:
                drop_id   = random.choice(drops)
                drop_item = get_item(drop_id)
                if drop_item:
                    equip = player.setdefault("equipment", {})
                    old   = equip.get(drop_item["type"])
                    from items import ALL_ITEMS
                    if old:
                        old_i = ALL_ITEMS.get(old, {})
                        for s, v in old_i.get("stats", {}).items():
                            player[s] = max(1, player.get(s, 0) - v)
                    equip[drop_item["type"]] = drop_id
                    for s, v in drop_item.get("stats", {}).items():
                        player[s] = player.get(s, 0) + v
                    drop_txt = f"\n🎁 *DROP ITEM!* {drop_item['name']} ✅ Terpasang!"

        _cds(context, user_id)
        save_player(user_id, player)

        boss_txt = "🎊 *BOSS DIKALAHKAN!* Floor naik!\n" if is_boss else ""
        await query.edit_message_text(
            f"🏆 *MENANG!*\n\n"
            f"{boss_txt}"
            f"💀 *{monster['name']}* dikalahkan!\n"
            f"💰 +{gold * (2 if is_boss else 1)} Coin\n"
            f"✨ +{exp} EXP{lv_txt}{drop_txt}\n\n"
            f"❤️ HP: {player['hp']}/{player['max_hp']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏰 Lanjut Dungeon", callback_data="dungeon_explore"),
                 InlineKeyboardButton("🚪 Keluar",         callback_data="dungeon_exit")],
            ])
        )
        return

    # ── Monster attacks ─────────────────────────────────────────
    dodge = min(50, player.get("spd", 10) * 2)
    if random.randint(1, 100) <= dodge:
        log.append("💨 Menghindar!")
    else:
        mdmg = max(1, monster["atk"] - int(player["def"] * 0.75))
        player["hp"] = max(0, player["hp"] - mdmg)
        log.append(f"{monster['emoji']} -{mdmg} HP")

    dstate["turn"] += 1

    if player["hp"] <= 0:
        revives = player.get("inventory", {}).get("revive_crystal", 0)
        if revives > 0:
            player["hp"] = player["max_hp"] // 2
            player["inventory"]["revive_crystal"] -= 1
            log.append("💠 Revive Crystal aktif!")
        else:
            gold_lost = player.get("coin", 0) // 15
            player["coin"]   = max(0, player.get("coin", 0) - gold_lost)
            player["hp"]     = player["max_hp"] // 3
            player["losses"] += 1
            _cds(context, user_id)
            save_player(user_id, player)
            await query.edit_message_text(
                f"💀 *GAME OVER*\n\n"
                f"Dikalahkan oleh {monster['emoji']} *{monster['name']}*!\n"
                f"Kehilangan {gold_lost} Coin",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Kembali", callback_data="dungeon_exit")
                ]])
            )
            return

    save_player(user_id, player)
    _sds(context, user_id, dstate)
    await _show_dg_battle(query, player, dstate, is_boss=is_boss)
