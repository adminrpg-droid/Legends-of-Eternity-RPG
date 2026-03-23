# ⚔️ Legends of Eternity — Telegram RPG Bot

> **Versi: v4.0** | Python 3.10+ | python-telegram-bot 20.x

---

## 🗂️ Struktur Proyek

```
RPG-v3/
├── bot.py                  # Entry point utama
├── keep_alive.py           # Web server untuk uptime
├── requirements.txt        # Dependensi Python
├── data/
│   ├── items.py            # Item, senjata, armor, VIP, SKILL SHOP
│   ├── monsters.py         # Monster, dungeon, boss
│   └── players.json        # (auto-generated) Database pemain
├── handlers/
│   ├── start.py            # Registrasi karakter & menu utama
│   ├── profile.py          # Profil pemain (termasuk profil orang lain di grup)
│   ├── battle.py           # Pertempuran solo
│   ├── dungeon.py          # Sistem dungeon & boss
│   ├── shop.py             # Toko (konsumable, senjata, armor, VIP, SKILL)
│   ├── inventory.py        # Manajemen inventori
│   ├── market.py           # Pasar antar pemain
│   ├── transfer.py         # Transfer item
│   ├── book.py             # Ensiklopedia monster
│   ├── daily.py            # Login bonus harian
│   ├── leaderboard.py      # Papan peringkat (admin ikut serta)
│   ├── rest.py             # ✨ BARU: Sistem istirahat / regen HP & MP
│   ├── group_boss.py       # ✨ BARU: Boss raid tim di grup (maks 5 pemain)
│   └── admin.py            # Panel admin (termasuk respawn boss per dungeon)
├── models/
│   └── database.py         # CRUD database & model karakter
└── utils/
    └── ui.py               # Helper tampilan (profile, hp bar, dll)
```

---

## 🚀 Cara Setup

### 1. Clone & Install
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variable
```bash
export BOT_TOKEN="token_bot_telegram_kamu"
```

### 3. Atur Admin ID
Buka `models/database.py` dan ganti:
```python
ADMIN_IDS = [
    123456789,  # Ganti dengan Telegram ID kamu
]
```

### 4. Jalankan Bot
```bash
python bot.py
```

---

## 📋 Daftar Command

### Perintah Pemain
| Command | Fungsi |
|---|---|
| `/start` | Mulai bot & buat karakter |
| `/profile` | Lihat profil sendiri |
| `/profile @reply` | Lihat profil pemain lain di grup |
| `/battle` | Lawan monster acak |
| `/dungeon` | Masuki dungeon |
| `/shop` | Beli item, senjata, armor, skill |
| `/inventory` | Kelola inventori |
| `/market` | Pasar antar pemain |
| `/transfer` | Kirim item ke pemain lain |
| `/book` | Ensiklopedia monster & boss |
| `/daily` | Klaim login bonus harian |
| `/leaderboard` | Papan peringkat |
| `/rest` | ✨ Istirahat untuk regen HP & MP |
| `/help` | Panduan lengkap |

### Perintah Admin (Grup & Private)
| Command | Fungsi |
|---|---|
| `/admin` | Buka panel admin |
| `/addcoin <id> <jumlah>` | Tambah coin ke pemain |
| `/adddiamond <id> <jumlah>` | Tambah diamond ke pemain |
| `/setvip <id> <tier>` | Beri VIP ke pemain |
| `/setmedia <type> <id> <url>` | Set gambar/gif entitas |
| `/groupboss` | ✨ Spawn boss raid di grup (maks 5 pemain) |

---

## ✨ Fitur Baru v4.0

### 1. 👁️ Cek Profil di Grup
- Pemain bisa melihat profil admin dan pemain lain di grup
- Gunakan `/profile` dengan reply ke pesan pemain lain
- Atau `/profile <user_id>` untuk lihat profil berdasarkan ID
- Badge `👑ADMIN` ditampilkan di profil admin

### 2. 🏆 Admin Masuk Leaderboard
- Admin kini tercatat di papan peringkat seperti pemain biasa
- Badge `👑` ditampilkan di samping nama admin di leaderboard

### 3. 👹 Respawn Boss (Admin)
- Dari `/admin` → **Respawn Boss**
- Pilih dungeon yang ingin di-respawn bossnya
- Boss direset dan siap dilawan kembali
- Notifikasi dikirim ke admin sebagai konfirmasi

### 4. ⚔️ Group Boss Raid
- Admin jalankan `/groupboss` di grup
- Pilih dungeon (boss sesuai dungeon yang dipilih)
- Pemain join dengan tombol **JOIN RAID** (maks 5 pemain)
- Battle berjalan **otomatis** setiap 3 detik
- Notifikasi real-time: siapa yang mati, siapa yang hit boss
- **Pembunuh boss** mendapat item drop eksklusif + gold x2
- Pemain yang tidak membunuh boss tetap dapat XP & gold

### 5. 😴 Sistem Istirahat (/rest)
- Ketik `/rest` untuk mulai istirahat
- **Regen otomatis**: +15 HP & +12 MP per 10 detik
- Cooldown `10 detik` antar tick (update pesan real-time)
- **Batal kapan saja** dengan tombol ❌ — lanjut main
- Cooldown 60 detik setelah berhenti istirahat
- Maks durasi 5 menit per sesi istirahat
- HP/MP penuh → istirahat otomatis berhenti

### 6. 🔮 Skill Shop
- Buka `/shop` → **🔮 Beli Skill**
- Skill eksklusif per kelas (3 skill: Rare, Epic, Legendary)
- Harga: **3.500 – 9.000 Coin** (lebih mahal dari item biasa)
- Skill yang dibeli tersimpan permanen di karakter
- Tampil di profil karakter

#### Daftar Skill per Kelas:
| Kelas | Skill Rare | Skill Epic | Skill Legendary |
|---|---|---|---|
| Warrior | 🌪️ Whirlwind | 🛡️ Iron Defense | ⚡ Thunder Charge |
| Mage | ❄️ Blizzard | ⚡ Chain Lightning | 🌌 Arcane Nova |
| Archer | 🎯 Snipe | 🌀 Cyclone Shot | 💥 Meteor Shot |
| Rogue | 🌑 Smoke Bomb | ⚡ Backstab Chain | 💀 Phantom Execution |
| Assassin | 🗡️ Poison Blade | 🌀 Vanish Strike | 💉 Soul Harvest |
| Necromancer | 💀 Corpse Explosion | 🌑 Dark Ritual | 👁️ Lich Awakening |

---

## 🎮 Sistem Kelas

| Kelas | HP | MP | ATK | DEF | SPD | CRIT | Skill Utama |
|---|---|---|---|---|---|---|---|
| ⚔️ Warrior | 200 | 60 | 22 | 18 | 8 | 10% | Slash Storm |
| 🔮 Mage | 120 | 160 | 30 | 8 | 10 | 12% | Inferno |
| 🏹 Archer | 150 | 90 | 26 | 12 | 20 | 18% | Arrow Storm |
| 🗡️ Rogue | 140 | 80 | 32 | 10 | 24 | 25% | Shadow Strike |
| 💉 Assassin | 130 | 85 | 36 | 9 | 28 | 30% | Death Mark |
| 💀 Necromancer | 115 | 180 | 28 | 7 | 9 | 14% | Soul Drain |

---

## 🏰 Dungeon & Boss

| Dungeon | Min Level | Boss |
|---|---|---|
| 🕳️ Gua Goblin | 1 | 👺 Goblin King |
| 🌲 Hutan Tersesat | 5 | 🧙 Forest Witch |
| 🏚️ Istana Kegelapan | 12 | 😈 Dark Lord |
| 🗺️ Labirin Bawah Tanah | 20 | 🐂 Labyrinth Guardian |
| 🌋 Gunung Api Abadi | 30 | 🐲 Fire Dragon |

---

## 💎 Sistem VIP

| Tier | Harga | Bonus |
|---|---|---|
| 🥈 Silver | Rp 15.000/bulan | +10% Crit, +50 HP, +30 MP, +8 ATK |
| 🥇 Gold | Rp 30.000/bulan | +20% Crit, +100 HP, +60 MP, +18 ATK |
| 💎 Diamond | Rp 75.000/bulan | +35% Crit, +200 HP, +120 MP, +35 ATK |

---

## ⚙️ Requirements

```
python-telegram-bot==20.7
```

---

## 📝 Catatan Developer

- Database disimpan di `data/players.json` (JSON sederhana)
- Untuk produksi, pertimbangkan migrasi ke SQLite/PostgreSQL
- Group boss session disimpan di memory (reset saat bot restart)
- Rest loop menggunakan `asyncio.create_task` — pastikan event loop tidak berhenti
- Semua waktu menggunakan `time.time()` (Unix timestamp)

---

*Legends of Eternity v4.0 — Dibuat dengan ❤️ untuk komunitas RPG Indonesia*
