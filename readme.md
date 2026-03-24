# ⚔️ Legends of Eternity v5.0 — Telegram RPG Bot

> Bot RPG Telegram berbahasa Indonesia dengan sistem battle, dungeon, shop, leaderboard, VIP, dan panel admin lengkap.

---

## 🗂️ Struktur Proyek

```
Legends-of-Eternity-v5/
├── bot.py              # Entry point utama — daftarkan semua handler
├── database.py         # CRUD pemain, admin, ban, VIP, weekly/monthly stats
├── items.py            # Item, senjata, armor, VIP, skill shop
├── monster.py          # Monster, dungeon, boss
├── ui.py               # Helper tampilan (profil, hp bar, dll)
├── keep_alive.py       # Web server uptime (Replit/Railway)
├── requirements.txt    # Dependensi Python
├── data/               # (auto-generated) File JSON database
│   ├── players.json    # Data semua pemain
│   ├── market.json     # Listing pasar antar pemain
│   ├── admins.json     # Daftar admin (selain super admin)
│   ├── banned.json     # Daftar pemain yang di-ban
│   └── media.json      # URL gambar/gif entitas game
└── handlers/           # Handler per fitur
    ├── start.py        # Registrasi karakter & menu utama
    ├── profile.py      # Profil pemain
    ├── battle.py       # Pertempuran solo
    ├── dungeon.py      # Sistem dungeon & boss
    ├── shop.py         # Toko (item, senjata, armor, VIP, skill)
    ├── inventory.py    # Manajemen inventori
    ├── market.py       # Pasar antar pemain
    ├── transfer.py     # Transfer item
    ├── book.py         # Ensiklopedia monster
    ├── daily.py        # Login bonus harian
    ├── leaderboard.py  # Papan peringkat (weekly, monthly, all-time)
    ├── rest.py         # Istirahat & regen HP/MP
    ├── group_boss.py   # Boss raid tim di grup
    └── admin.py        # Panel admin lengkap
```

---

## 🚀 Cara Setup

### 1. Install Dependensi
```bash
pip install -r requirements.txt
```

### 2. Set Token Bot
```bash
export BOT_TOKEN="token_bot_telegram_kamu"
```
Atau langsung edit `bot.py` baris:
```python
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ISI_TOKEN_DI_SINI")
```

### 3. Set Super Admin ID
Buka `database.py` dan isi Telegram ID kamu:
```python
SUPER_ADMIN_IDS = [
    123456789,  # Ganti dengan Telegram ID kamu
]
```
> Cara cari Telegram ID: chat ke @userinfobot

### 4. Jalankan Bot
```bash
python bot.py
```

---

## 📋 Perintah Pemain

| Command | Fungsi |
|---|---|
| `/start` | Mulai bot & buat karakter |
| `/profile` | Lihat profil sendiri |
| `/profile` (reply) | Lihat profil pemain lain di grup |
| `/battle` | Lawan monster acak |
| `/dungeon` | Masuki dungeon & lawan boss |
| `/shop` | Beli item, senjata, armor, skill |
| `/inventory` | Kelola inventori & pakai item |
| `/market` | Jual & beli item antar pemain |
| `/transfer` | Kirim item ke pemain lain |
| `/book` | Ensiklopedia monster & boss |
| `/daily` | Klaim login bonus harian |
| `/leaderboard` | Papan peringkat (All Time / Weekly / Monthly) |
| `/rest` | Istirahat untuk regen HP & MP |
| `/menu` | Tampilkan menu utama |
| `/help` | Panduan bermain lengkap |

---

## 👑 Perintah Admin

> Akses via `/admin` atau command langsung. Gunakan `/adminhelp` untuk panduan admin.

| Command | Fungsi |
|---|---|
| `/admin` | Buka panel admin |
| `/adminhelp` | Panduan khusus admin |
| `/addcoin <id> <jml>` | Tambah coin ke pemain |
| `/adddiamond <id> <jml>` | Tambah diamond ke pemain |
| `/setvip <id> <silver\|gold\|diamond>` | Beri VIP ke pemain |
| `/ban <id> [alasan]` | Ban pemain |
| `/unban <id>` | Unban pemain |
| `/addadmin <id>` | Tambah admin baru _(Super Admin only)_ |
| `/removeadmin <id>` | Hapus admin _(Super Admin only)_ |
| `/setmedia <type> <id> <url>` | Set gambar/gif entitas |
| `/groupboss` | Spawn boss raid di grup |

### Ketentuan Admin
- ✅ Admin gratis semua item & tidak kena biaya apapun
- 🚫 Admin tidak muncul di Leaderboard
- 🔒 Profil admin tidak bisa dilihat pemain biasa
- 🛡️ Admin tidak bisa di-ban oleh admin lain
- ⭐ Super Admin tidak bisa dihapus via command

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
| 🥈 Silver | Rp 15.000/bulan | Crit +6%, HP +30, MP +20, ATK +5 |
| 🥇 Gold | Rp 30.000/bulan | Crit +12%, HP +60, MP +40, ATK +10 |
| 💎 Diamond | Rp 75.000/bulan | Crit +20%, HP +120, MP +75, ATK +18 |

> VIP tidak memberikan keuntungan berlebihan — hanya bonus ringan untuk kenyamanan bermain.

---

## 🏆 Sistem Leaderboard

- **🏆 All Time** — Peringkat sepanjang masa
- **📅 Mingguan** — Reset setiap Senin pukul 00.00 UTC
- **📆 Bulanan** — Reset setiap tanggal 1 pukul 00.00 UTC
- **Admin tidak tampil** di leaderboard manapun
- Diurutkan berdasarkan: Level, Kills, Boss Kills

---

## 🔮 Skill Shop

Buka `/shop` → **🔮 Beli Skill** untuk membeli skill tambahan sesuai kelas.

| Kelas | Skill Rare | Skill Epic | Skill Legendary |
|---|---|---|---|
| Warrior | 🌪️ Whirlwind | 🛡️ Iron Defense | ⚡ Thunder Charge |
| Mage | ❄️ Blizzard | ⚡ Chain Lightning | 🌌 Arcane Nova |
| Archer | 🎯 Snipe | 🌀 Cyclone Shot | 💥 Meteor Shot |
| Rogue | 🌑 Smoke Bomb | ⚡ Backstab Chain | 💀 Phantom Execution |
| Assassin | 🗡️ Poison Blade | 🌀 Vanish Strike | 💉 Soul Harvest |
| Necromancer | 💀 Corpse Explosion | 🌑 Dark Ritual | 👁️ Lich Awakening |

> Harga skill mulai dari 7.000 hingga 18.000 Coin.

---

## 👹 Group Boss Raid

1. Admin jalankan `/groupboss` di grup
2. Pilih dungeon (boss sesuai dungeon)
3. Pemain join dengan tombol **JOIN RAID** (maks 5 pemain)
4. Battle berjalan **otomatis** setiap 3 detik
5. **Pembunuh boss** mendapat item drop eksklusif + gold ×2
6. Pemain lain tetap dapat XP & gold

---

## 😴 Sistem Istirahat (/rest)

- Regen **+15 HP** & **+12 MP** per 10 detik
- Tekan ❌ Batal untuk lanjut bermain kapan saja
- Cooldown 60 detik setelah berhenti
- Maks durasi 5 menit per sesi
- HP/MP penuh → istirahat otomatis berhenti

---

## ⚙️ Requirements

```
python-telegram-bot==20.7
```

---

## 📝 Catatan Teknis

- Database: JSON flat-file di `data/` (mudah di-backup)
- Untuk skala besar: migrasi ke SQLite atau PostgreSQL
- Group boss session disimpan di memory (reset saat bot restart)
- Log tersimpan di `data/bot.log`
- Semua waktu menggunakan `time.time()` (Unix timestamp)
- Weekly reset: Senin 00:00 UTC | Monthly reset: Tanggal 1 00:00 UTC

---

*Legends of Eternity v5.0 — Dibuat dengan ❤️ untuk komunitas RPG Indonesia*
