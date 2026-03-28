import random
import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_player, save_player, level_up, is_admin
from monster import DUNGEONS, get_boss, BOSSES
from items import BOSS_DROPS, get_item, ALL_ITEMS, GOD_SSSR_BOSS_DROPS, GOD_SSSR_WEAPONS, GOD_SSSR_ARMORS, GOD_SSSR_SKILLS, GOD_SSSR_PETS

# Penyimpanan sesi boss di grup (per chat_id)
# Format: {chat_id: {dungeon_id, boss, players, status, log, ...}}
_GROUP_BOSS_SESSIONS = {}

MAX_PLAYERS   = 5
JOIN_TIMEOUT  = 60   # detik untuk join sebelum mulai
BATTLE_DELAY  = 3    # detik antar ronde


def _get_session(chat_id: int) -> dict:
    return _GROUP_BOSS_SESSIONS.get(chat_id, {})

def _set_session(chat_id: int, s: dict):
    _GROUP_BOSS_SESSIONS[chat_id] = s

def _del_session(chat_id: int):
    _GROUP_BOSS_SESSIONS.pop(chat_id, None)


# ── Pilih dungeon untuk boss raid ────────────────────────────────
async def group_boss_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Pilih dungeon untuk spawn boss di grup. /groupboss"""
    user = update.effective_user
    chat = update.effective_chat

    if not is_admin(user.id):
        await update.message.reply_text("❌ Hanya admin yang bisa spawn boss grup!")
        return

    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❌ Command ini hanya untuk grup!")
        return

    sess = _get_session(chat.id)
    if sess and sess.get("status") in ("waiting", "running"):
        await update.message.reply_text(
            "⚠️ *Sudah ada boss raid aktif!*\nTunggu selesai dulu.",
            parse_mode="Markdown"
        )
        return

    buttons = []
    for did, dg in DUNGEONS.items():
        buttons.append([InlineKeyboardButton(
            f"{dg['emoji']} {dg['name']} (Lv.{dg['min_level']}+)",
            callback_data=f"gb_spawn_{did}"
        )])
    buttons.append([InlineKeyboardButton("❌ Batal", callback_data="gb_cancel")])

    await update.message.reply_text(
        "👑 *ADMIN — Pilih Dungeon Boss Raid*\n\n"
        "Pilih dungeon untuk spawn boss:\n"
        "_(Semua pemain bisa join setelah boss di-spawn)_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ── Callback handler utama grup boss ─────────────────────────────
async def group_boss_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    action = query.data
    user   = query.from_user
    chat   = query.message.chat

    if chat.type not in ("group", "supergroup"):
        await query.answer("Hanya untuk grup!", show_alert=True)
        return

    # ── Spawn boss (admin) ───────────────────────────────────────
    if action.startswith("gb_spawn_"):
        if not is_admin(user.id):
            await query.answer("❌ Hanya admin!", show_alert=True)
            return
        did = int(action.replace("gb_spawn_", ""))
        await _spawn_boss(query, context, chat.id, did)
        return

    # ── Join raid ────────────────────────────────────────────────
    if action == "gb_join":
        await _join_raid(query, user, chat.id, context)
        return

    # ── Start battle (admin trigger) ─────────────────────────────
    if action == "gb_start":
        if not is_admin(user.id):
            await query.answer("❌ Hanya admin!", show_alert=True)
            return
        await _start_raid(query, context, chat.id)
        return

    # ── Cancel ──────────────────────────────────────────────────
    if action == "gb_cancel":
        if not is_admin(user.id):
            await query.answer("❌ Hanya admin!", show_alert=True)
            return
        _del_session(chat.id)
        await query.edit_message_text("❌ *Boss Raid dibatalkan.*", parse_mode="Markdown")
        return


async def _spawn_boss(query, context, chat_id: int, dungeon_id: int):
    dg   = DUNGEONS.get(dungeon_id)
    if not dg:
        await query.answer("Dungeon tidak valid!", show_alert=True)
        return

    boss = get_boss(dg["boss"], scale_level=1)  # base level; di-scale ulang saat raid mulai
    boss["max_hp"]     = boss["hp"]
    boss["current_hp"] = boss["hp"]

    _set_session(chat_id, {
        "dungeon_id":  dungeon_id,
        "dungeon":     dg,
        "boss":        boss,
        "players":     {},   # {user_id: {name, hp, max_hp, atk, def, spd, crit, mp, max_mp, class, skill_cd, alive}}
        "status":      "waiting",
        "log":         [],
        "start_time":  time.time(),
        "msg_id":      query.message.message_id,
        "chat_id":     chat_id,
        "killer_id":   None,
    })

    text = (
        f"╔══════════════════════════════════╗\n"
        f"║  ⚔️  *BOSS RAID DIBUKA!*  ⚔️     ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🏰 Dungeon: *{dg['name']}*\n"
        f"║  📍 Total Lantai: {dg['floor_count']}\n"
        f"╚══════════════════════════════════╝\n\n"
        f"👹 *{boss['name']}* {boss['emoji']}\n"
        f"❤️ HP: `{boss['hp']:,}` | 💥 ATK: `{boss['atk']}` | 🛡️ DEF: `{boss['def']}`\n\n"
        f"👥 Pemain bergabung: 0/{MAX_PLAYERS}\n\n"
        f"⏳ *Waktu join: {JOIN_TIMEOUT} detik*\n"
        f"_Tekan tombol JOIN di bawah untuk ikut raid!_"
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ JOIN RAID", callback_data="gb_join")],
        [InlineKeyboardButton("▶️ Mulai Sekarang", callback_data="gb_start"),
         InlineKeyboardButton("❌ Batal", callback_data="gb_cancel")],
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)

    # Auto-start setelah timeout
    asyncio.create_task(_auto_start_after(context, chat_id, query.message.message_id, JOIN_TIMEOUT))


async def _auto_start_after(context, chat_id: int, msg_id: int, delay: int):
    await asyncio.sleep(delay)
    sess = _get_session(chat_id)
    if not sess or sess.get("status") != "waiting":
        return
    if not sess["players"]:
        _del_session(chat_id)
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id, message_id=msg_id,
                text="❌ *Boss Raid berakhir* — tidak ada pemain yang join.",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        return
    # Start otomatis
    await _run_raid(context, chat_id, msg_id)


async def _join_raid(query, user, chat_id: int, context):
    sess = _get_session(chat_id)
    if not sess or sess.get("status") != "waiting":
        await query.answer("Tidak ada raid aktif!", show_alert=True)
        return

    if len(sess["players"]) >= MAX_PLAYERS:
        await query.answer(f"❌ Penuh! Maks {MAX_PLAYERS} pemain.", show_alert=True)
        return

    if user.id in sess["players"]:
        await query.answer("Kamu sudah join!", show_alert=True)
        return

    player = get_player(user.id)
    if not player:
        await query.answer("❌ Belum punya karakter! /start dulu.", show_alert=True)
        return

    if player["hp"] <= 0:
        await query.answer("❌ HP 0! Pulihkan dulu.", show_alert=True)
        return

    # Snapshot stats pemain
    sess["players"][user.id] = {
        "name":     player["name"],
        "emoji":    player["emoji"],
        "hp":       player["hp"],
        "max_hp":   player["max_hp"],
        "atk":      player["atk"],
        "def":      player["def"],
        "spd":      player["spd"],
        "crit":     player.get("crit", 10),
        "mp":       player["mp"],
        "max_mp":   player["max_mp"],
        "class":    player.get("class", "warrior"),
        "skill":    player.get("skill", "Serangan"),
        "skill_cd": 0,
        "alive":    True,
        "dmg_dealt": 0,
    }
    _set_session(chat_id, sess)

    # Update pesan join
    dg   = sess["dungeon"]
    boss = sess["boss"]
    player_list = "\n".join(
        f"  {p['emoji']} *{p['name']}* — ❤️{p['hp']}/{p['max_hp']}"
        for p in sess["players"].values()
    )
    text = (
        f"⚔️ *BOSS RAID — JOIN PHASE*\n\n"
        f"🏰 {dg['name']} | 👹 *{boss['name']}* {boss['emoji']}\n"
        f"❤️ HP Boss: `{boss['hp']}`\n\n"
        f"👥 Pemain ({len(sess['players'])}/{MAX_PLAYERS}):\n{player_list}\n\n"
        f"⏳ Menunggu pemain lain atau admin start..."
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ JOIN RAID", callback_data="gb_join")],
        [InlineKeyboardButton("▶️ Mulai Sekarang", callback_data="gb_start"),
         InlineKeyboardButton("❌ Batal", callback_data="gb_cancel")],
    ])
    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        pass
    await query.answer(f"✅ {player['name']} bergabung ke raid!")


async def _start_raid(query, context, chat_id: int):
    sess = _get_session(chat_id)
    if not sess or sess.get("status") != "waiting":
        await query.answer("Tidak ada raid yang menunggu!", show_alert=True)
        return
    if not sess["players"]:
        await query.answer("Belum ada pemain yang join!", show_alert=True)
        return
    await _run_raid(context, chat_id, query.message.message_id)


async def _run_raid(context, chat_id: int, msg_id: int):
    """Main battle loop — auto play."""
    sess = _get_session(chat_id)
    if not sess:
        return

    sess["status"] = "running"
    _set_session(chat_id, sess)

    boss   = sess["boss"]
    player_count = len(sess["players"])

    # Scale boss HP berdasarkan jumlah pemain
    scale  = 1.0 + (player_count - 1) * 0.4
    boss["hp"]         = int(boss["hp"] * scale)
    boss["max_hp"]     = boss["hp"]
    boss["current_hp"] = boss["hp"]
    boss["atk"]        = int(boss["atk"] * (1.0 + (player_count - 1) * 0.15))

    round_num = 0
    max_rounds = 40

    while boss["current_hp"] > 0 and round_num < max_rounds:
        round_num += 1
        round_log  = [f"⚔️ *Ronde {round_num}*"]

        alive_players = {uid: p for uid, p in sess["players"].items() if p["alive"]}
        if not alive_players:
            break

        # ── Setiap pemain menyerang boss ─────────────────────────
        for uid, p in alive_players.items():
            if not p["alive"]:
                continue

            # Skill atau serangan biasa
            use_skill = p["mp"] >= 25 and p["skill_cd"] == 0 and random.randint(1, 3) == 1
            if use_skill:
                mult     = random.uniform(2.0, 2.8)
                dmg      = max(1, int(p["atk"] * mult - boss["def"] * 0.3))
                p["mp"] -= 25
                p["skill_cd"] = 3
                round_log.append(f"  ✨ *{p['name']}* pakai {p['skill']}! `-{dmg}` HP boss")
            else:
                crit  = random.randint(1, 100) <= p["crit"]
                mult  = 1.6 if crit else 1.0
                dmg   = max(1, int(p["atk"] * mult - boss["def"] * 0.6))
                crit_txt = " 💥CRIT!" if crit else ""
                round_log.append(f"  ⚔️ *{p['name']}* menyerang `-{dmg}` HP boss{crit_txt}")

            boss["current_hp"] -= dmg
            p["dmg_dealt"]      += dmg

            if p["skill_cd"] > 0:
                p["skill_cd"] -= 1

            if boss["current_hp"] <= 0:
                boss["current_hp"] = 0
                sess["killer_id"]  = uid
                break

        if boss["current_hp"] <= 0:
            break

        # ── Boss menyerang pemain hidup ──────────────────────────
        alive_now = [uid for uid, p in sess["players"].items() if p["alive"]]

        # Aktifkan berserk jika HP boss < threshold
        berserk_th = boss.get("berserk_threshold", 0)
        if berserk_th > 0 and boss["current_hp"] / boss["max_hp"] <= berserk_th:
            if not sess.get("berserk_active"):
                sess["berserk_active"] = True
                round_log.append(f"  🔥 *{boss['name']} BERSERK!* ATK meningkat drastis!")

        if alive_now:
            target_uid = random.choice(alive_now)
            t = sess["players"][target_uid]

            # Boss bisa multi-hit acak
            hits = random.randint(1, 2) if boss.get("special") else 1
            total_boss_dmg = 0
            boss_atk = boss["atk"]
            if sess.get("berserk_active"):
                boss_atk = int(boss_atk * boss.get("berserk_atk_mult", 2.0))
            for _ in range(hits):
                dodge = min(50, t["spd"] * 2)
                if random.randint(1, 100) <= dodge:
                    round_log.append(f"  💨 *{t['name']}* menghindar dari {boss['emoji']} {boss['name']}!")
                else:
                    bdmg = max(1, int(boss_atk * random.uniform(0.8, 1.2) - t["def"] * 0.6))
                    t["hp"] = max(0, t["hp"] - bdmg)
                    total_boss_dmg += bdmg

            if total_boss_dmg > 0:
                berserk_tag = " 🔥BERSERK!" if sess.get("berserk_active") else ""
                round_log.append(
                    f"  {boss['emoji']} Boss menyerang *{t['name']}* `-{total_boss_dmg}` HP"
                    f" (tersisa ❤️{t['hp']}){berserk_tag}"
                )

            if t["hp"] <= 0:
                t["alive"] = False
                round_log.append(f"  💀 *{t['name']}* telah GUGUR!")

        # ── Boss counter attack acak ke pemain hidup ────────────
        counter_pct = int(boss.get("counter_pct", 0) * 100)
        if counter_pct > 0 and random.randint(1, 100) <= counter_pct:
            alive_now2 = [p for p in sess["players"].values() if p["alive"]]
            if alive_now2:
                ct = random.choice(alive_now2)
                c_dmg = max(1, int(boss["atk"] * 0.4) - int(ct["def"] * 0.3))
                ct["hp"] = max(0, ct["hp"] - c_dmg)
                round_log.append(f"  ⚡ *COUNTER!* {boss['emoji']} balas serang *{ct['name']}*! `-{c_dmg}` HP")
                if ct["hp"] <= 0:
                    ct["alive"] = False
                    round_log.append(f"  💀 *{ct['name']}* gugur karena counter!")

        sess["log"].extend(round_log)
        _set_session(chat_id, sess)

        # Update pesan setiap ronde
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=_build_battle_text(sess, round_num),
                parse_mode="Markdown"
            )
        except Exception:
            pass

        await asyncio.sleep(BATTLE_DELAY)

    # ── Battle selesai ───────────────────────────────────────────
    await _finish_raid(context, chat_id, msg_id, sess)


def _build_battle_text(sess: dict, round_num: int) -> str:
    boss   = sess["boss"]
    dg     = sess["dungeon"]
    from ui import hp_bar

    # Boss HP bar
    b_bar  = hp_bar(max(0, boss["current_hp"]), boss["max_hp"], 10)

    # Player status
    p_lines = []
    for p in sess["players"].values():
        status = "💀" if not p["alive"] else "✅"
        p_lines.append(f"  {status} {p['emoji']} *{p['name']}* ❤️{p['hp']}/{p['max_hp']}")
    player_status = "\n".join(p_lines)

    # Last 5 log
    recent_log = "\n".join(sess["log"][-8:]) if sess["log"] else "⚔️ Pertempuran dimulai!"

    # Hitung % HP boss
    hp_pct = int((max(0, boss["current_hp"]) / boss["max_hp"]) * 100) if boss["max_hp"] > 0 else 0
    if hp_pct > 60:
        hp_color = "🟢"
    elif hp_pct > 30:
        hp_color = "🟡"
    else:
        hp_color = "🔴"

    alive_count = sum(1 for p in sess["players"].values() if p["alive"])
    total_count = len(sess["players"])

    return (
        f"╔══════════════════════════════════╗\n"
        f"║  ⚔️  *BOSS RAID AKTIF!*  ⚔️      ║\n"
        f"╠══════════════════════════════════╣\n"
        f"║  🏰 {dg['name']} | Ronde {round_num}\n"
        f"╚══════════════════════════════════╝\n\n"
        f"{boss['emoji']} *{boss['name']}*\n"
        f"{hp_color} ❤️ {b_bar} `{max(0,boss['current_hp']):,}/{boss['max_hp']:,}` ({hp_pct}%)\n\n"
        f"👥 *Tim Petarung* ({alive_count}/{total_count} hidup):\n{player_status}\n\n"
        f"📜 *Log Pertempuran:*\n{recent_log}"
    )


async def _finish_raid(context, chat_id: int, msg_id: int, sess: dict):
    """Beri reward dan tampilkan hasil akhir."""
    boss       = sess["boss"]
    dg         = sess["dungeon"]
    killer_id  = sess.get("killer_id")
    boss_dead  = boss["current_hp"] <= 0

    result_lines = []

    for uid, p in sess["players"].items():
        player_db = get_player(uid)
        if not player_db:
            continue

        # Update HP dari battle
        player_db["hp"] = max(1, p["hp"]) if p["hp"] > 0 else player_db["max_hp"] // 4

        if boss_dead:
            # Semua yang ikut dapat XP dan gold
            base_exp  = int(boss.get("exp", 500) / max(1, len(sess["players"])))
            base_gold = int(random.randint(*boss.get("gold", (100, 300))) / max(1, len(sess["players"])))
            player_db["exp"]  += base_exp
            player_db["coin"] = player_db.get("coin", 0) + base_gold
            player_db["boss_kills"] = player_db.get("boss_kills", 0) + 1
            player_db["weekly_boss_kills"]  = player_db.get("weekly_boss_kills", 0) + 1
            player_db["monthly_boss_kills"] = player_db.get("monthly_boss_kills", 0) + 1
            # BUG FIX: weekly_kills dan monthly_kills juga harus diincrement saat boss raid mati
            player_db["kills"]          = player_db.get("kills", 0) + 1
            player_db["weekly_kills"]   = player_db.get("weekly_kills", 0) + 1
            player_db["monthly_kills"]  = player_db.get("monthly_kills", 0) + 1
            player_db["weekly_coin_earned"]  = player_db.get("weekly_coin_earned", 0) + base_gold
            player_db["monthly_coin_earned"] = player_db.get("monthly_coin_earned", 0) + base_gold

            reward_txt = f"✨ +{base_exp} EXP | 🪙 +{base_gold} Gold"

            # Hadiah khusus pembunuh bos
            if uid == killer_id:
                char_class = player_db.get("class", "warrior")
                drops = BOSS_DROPS.get(char_class, [])
                drop_txt = ""
                if drops:
                    drop_id   = random.choice(drops)
                    drop_item = get_item(drop_id)
                    if drop_item:
                        equip = player_db.setdefault("equipment", {})
                        old   = equip.get(drop_item["type"])
                        if old:
                            old_i = ALL_ITEMS.get(old, {})
                            for s, v in old_i.get("stats", {}).items():
                                player_db[s] = max(1, player_db.get(s, 0) - v)
                        equip[drop_item["type"]] = drop_id
                        for s, v in drop_item.get("stats", {}).items():
                            player_db[s] = player_db.get(s, 0) + v
                        drop_txt = f"\n   🎁 *DROP ITEM: {drop_item['name']}* ✅ Terpasang!"
                # 0.1% chance Evolution Stone for killer
                if random.randint(1, 1000) == 1:
                    inv = player_db.setdefault("inventory", {})
                    inv["evolution_stone"] = inv.get("evolution_stone", 0) + 1
                    drop_txt += "\n   💠 *EVOLUTION STONE DIDAPAT!* (0.1% rate!)"
                # 0.1% chance GOD SSSR drop for killer
                if random.randint(1, 1000) == 1:
                    sssr_pool = GOD_SSSR_BOSS_DROPS.get(char_class, [])
                    if sssr_pool:
                        sssr_id = random.choice(sssr_pool)
                        if sssr_id in GOD_SSSR_WEAPONS:
                            sssr_item = GOD_SSSR_WEAPONS[sssr_id]
                            equip = player_db.setdefault("equipment", {})
                            slot  = sssr_item["type"]
                            old   = equip.get(slot)
                            if old:
                                oi = ALL_ITEMS.get(old, {})
                                for s, v in oi.get("stats", {}).items():
                                    player_db[s] = max(1, player_db.get(s, 0) - v)
                            equip[slot] = sssr_id
                            for s, v in sssr_item.get("stats", {}).items():
                                player_db[s] = player_db.get(s, 0) + v
                            drop_txt += f"\n   🔱✨ *GOD SSSR DROP: {sssr_item['name']}!* (0.1%)"
                        elif sssr_id in GOD_SSSR_ARMORS:
                            sssr_item = GOD_SSSR_ARMORS[sssr_id]
                            equip = player_db.setdefault("equipment", {})
                            slot  = sssr_item["type"]
                            old   = equip.get(slot)
                            if old:
                                oi = ALL_ITEMS.get(old, {})
                                for s, v in oi.get("stats", {}).items():
                                    player_db[s] = max(1, player_db.get(s, 0) - v)
                            equip[slot] = sssr_id
                            for s, v in sssr_item.get("stats", {}).items():
                                player_db[s] = player_db.get(s, 0) + v
                            drop_txt += f"\n   🔱✨ *GOD SSSR DROP: {sssr_item['name']}!* (0.1%)"
                        elif sssr_id in GOD_SSSR_SKILLS:
                            sssr_item = GOD_SSSR_SKILLS[sssr_id]
                            player_db.setdefault("bought_skills", [])
                            if sssr_id not in [s if isinstance(s, str) else s.get("id","") for s in player_db["bought_skills"]]:
                                player_db["bought_skills"].append({"id": sssr_id, "name": sssr_item["name"]})
                            drop_txt += f"\n   🔱✨ *GOD SSSR SKILL: {sssr_item['name']}!* (0.1%)"
                        elif sssr_id in GOD_SSSR_PETS:
                            sssr_item = GOD_SSSR_PETS[sssr_id]
                            player_db["pet"] = sssr_id
                            player_db["pet_tier"] = 10
                            drop_txt += f"\n   🔱✨ *GOD SSSR PET: {sssr_item['name']}!* (0.1%)"
                # Bonus gold x2 untuk killer
                bonus_gold = base_gold
                player_db["coin"] = player_db.get("coin", 0) + bonus_gold
                player_db["weekly_coin_earned"]  = player_db.get("weekly_coin_earned", 0) + bonus_gold
                player_db["monthly_coin_earned"] = player_db.get("monthly_coin_earned", 0) + bonus_gold
                reward_txt = f"✨ +{base_exp} EXP | 🪙 +{base_gold * 2} Gold (x2 Killer!){drop_txt}"

            # Level up check
            from handlers.quest import update_quest_progress
            from handlers.title import check_and_award_titles
            player_db = update_quest_progress(player_db, "boss_kills", 1)
            player_db = update_quest_progress(player_db, "weekly_boss_kills", 1)
            player_db = update_quest_progress(player_db, "dungeon_clears", 1)
            player_db = update_quest_progress(player_db, "dungeon_clears_weekly", 1)
            # BUG FIX: daily kill quests (kills) dan weekly kill quest (weekly_kills) harus
            # diupdate saat boss group raid mati — sebelumnya hanya boss_kills yang di-track
            player_db = update_quest_progress(player_db, "kills", 1)
            player_db = update_quest_progress(player_db, "weekly_kills", 1)
            # BUG FIX: weekly_coin_earned sudah diincrement manual di atas (base_gold + bonus_gold untuk killer)
            # Gunakan nilai yang sama persis agar tidak double-count
            total_gold_earned = base_gold + (base_gold if uid == killer_id else 0)
            player_db = update_quest_progress(player_db, "weekly_coin_earned", total_gold_earned)
            player_db, _ = check_and_award_titles(player_db)
            player_db, leveled, lv_gained = level_up(player_db)
            lv_txt = f" 🎊 LEVEL UP! → Lv.{player_db['level']}" if leveled else ""
            result_lines.append(
                f"  {'🗡️ KILLER → ' if uid == killer_id else ''}"
                f"{p['emoji']} *{p['name']}*: {reward_txt}{lv_txt}"
            )
        else:
            # Boss tidak mati — pemain hanya dapat XP kecil
            consolation_exp  = 50
            consolation_gold = 20
            player_db["exp"]  += consolation_exp
            player_db["coin"] = player_db.get("coin", 0) + consolation_gold
            player_db["weekly_coin_earned"]  = player_db.get("weekly_coin_earned", 0) + consolation_gold
            player_db["monthly_coin_earned"] = player_db.get("monthly_coin_earned", 0) + consolation_gold
            player_db, leveled_c, _ = level_up(player_db)
            lv_c_txt = f" 🎊 LEVEL UP! → Lv.{player_db['level']}" if leveled_c else ""
            result_lines.append(
                f"  {p['emoji']} *{p['name']}*: +{consolation_exp} EXP | +{consolation_gold} Gold _(Boss lolos)_{lv_c_txt}"
            )

        save_player(uid, player_db)

    results_txt = "\n".join(result_lines) if result_lines else "_Tidak ada data._"

    if boss_dead:
        killer_name = sess["players"].get(killer_id, {}).get("name", "???")
        header = (
            f"🏆 *BOSS RAID SELESAI — BOSS DIKALAHKAN!*\n\n"
            f"⚔️ {boss['emoji']} *{boss['name']}* telah dikalahkan!\n"
            f"🗡️ *Pembunuh Terakhir: {killer_name}* — Mendapat item langka!\n\n"
        )
    else:
        header = (
            f"💀 *BOSS RAID GAGAL — Tim Kalah!*\n\n"
            f"{boss['emoji']} *{boss['name']}* masih berdiri...\n\n"
        )

    final_text = (
        f"{header}"
        f"📊 *Hasil Pertempuran:*\n{results_txt}\n\n"
        f"_Terima kasih telah berpartisipasi!_"
    )

    _del_session(chat_id)

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=final_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚔️ Battle Solo", callback_data="battle_start"),
                 InlineKeyboardButton("🏰 Dungeon", callback_data="dungeon_list")]
            ])
        )
    except Exception:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=final_text,
                parse_mode="Markdown"
            )
        except Exception:
            pass
