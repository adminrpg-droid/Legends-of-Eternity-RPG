# ⚔️ Legends of Eternity — Telegram RPG Bot

> Bot RPG Telegram berbahasa Indonesia dengan sistem battle, dungeon, market, book, leaderboard, VIP, dan panel admin lengkap.

---

## 🗂️ Struktur Proyek

```
Legends-of-Eternity/
├── bot.py              # Entry point utama
├── database.py         # CRUD pemain, admin, ban, VIP, market
├── items.py            # Item, senjata, armor, skill, pet, GOD SSSR
├── monster.py          # Monster, dungeon, boss
├── ui.py               # Helper tampilan (profil, hp bar, dll)
├── keep_alive.py       # Web server uptime (Replit/Railway)
├── requirements.txt    # Dependensi Python
├── data/               # (auto-generated) File JSON database
│   ├── players.json    # Data semua pemain
│   ├── market.json     # Listing pasar antar pemain
│   ├── admins.json     # Daftar admin
│   ├── banned.json     # Daftar pemain yang di-ban
│   └── media.json      # URL gambar/gif entitas game
└── handlers/           # Handler per fitur
    ├── start.py        # Registrasi karakter & menu utama
    ├── profile.py      # Profil pemain
    ├── battle.py       # Pertempuran solo
    ├── dungeon.py      # Sistem dungeon & boss
    ├── shop.py         # Toko (item, senjata, armor, VIP, skill)
    ├── inventory.py    # Manajemen inventori & equipment
    ├── market.py       # Pasar antar pemain (Gold & Diamond)
    ├── transfer.py     # Transfer item ke pemain lain
    ├── book.py         # Ensiklopedia (monster, boss, item per kelas)
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
Atau edit `bot.py`:
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
| `/shop` | Beli item, senjata, armor, skill, VIP |
| `/inventory` | Kelola equipment & item |
| `/market` | Jual & beli item antar pemain (Gold/Diamond) |
| `/transfer` | Kirim item ke pemain lain |
| `/book` | Ensiklopedia monster, boss, dan item per kelas |
| `/daily` | Klaim login bonus harian |
| `/leaderboard` | Papan peringkat |
| `/rest` | Istirahat untuk regen HP & MP |
| `/menu` | Tampilkan menu utama |
| `/help` | Panduan bermain lengkap |

---

## 🎮 Sistem Kelas

| Kelas | HP | MP | ATK | DEF | SPD | CRIT | Skill Utama |
|---|---|---|---|---|---|---|---|
| ⚔️ Warrior | 200 | 60 | 22 | 18 | 8 | 10% | Slash Storm |
| 🔮 Mage | 120 | 160 | 30 | 8 | 10 | 12% | Inferno |
| 🏹 Archer | 150 | 90 | 26 | 12 | 20 | 18% | Arrow Storm |
| 🗡️ Rogue | 140 | 80 | 32 | 10 | 24 | 25% | Shadow Strike |
| 💉 Assassin | 130 | 85 | 36 | 9 | 28 | 30% | Death Mark |
| 💀 Reaper | 115 | 180 | 28 | 7 | 9 | 14% | Soul Drain |

Setiap kelas memiliki **Class Special** unik yang aktif otomatis saat kondisi terpenuhi.

---

## ⭐ Sistem Rarity Item

| Rarity | Icon | Cara Mendapat |
|---|---|---|
| Common | ⭐ | Toko Gold |
| Uncommon | ⭐⭐ | Toko Gold |
| Rare | ⭐⭐⭐ | Toko Gold |
| Epic | ⭐⭐⭐⭐ | Toko Gold |
| Legendary | ⭐⭐⭐⭐⭐ | Toko Gold / Drop |
| SSR | 💎💎💎💎💎✨ | Toko Diamond |
| UR | 💜💜💜💜💜💜 | Toko Diamond |
| GOD | 🌟🌟🌟🌟🌟🌟🌟 | Toko Diamond |
| **GOD SSSR** | 🔱🔱🔱🔱🔱🔱🔱🔱🔱🔱 | **Drop Boss 0.1%** |

> ⚠️ **GOD SSSR** adalah item terlangka dalam game. Rate drop hanya **0.1%** dari boss dengan tier 3+.
> Hanya ada **1 dari 1000 kesempatan** untuk mendapatkannya!

---

## 🏪 Sistem Market (Antar Pemain)

Market memungkinkan pemain untuk jual-beli item secara langsung.

### Item yang Bisa Dijual:
- ⚔️ **Weapon** (semua rarity termasuk GOD SSSR)
- 🛡️ **Armor** (semua rarity termasuk GOD SSSR)
- 🔮 **Skill** (semua rarity, dibayar dengan Diamond jika SSR+)
- 🐾 **Pet** (semua rarity, dibayar dengan Diamond jika SSR+)
- 💠 **Evolution Stone** (dibayar dengan Diamond)

### Cara Jual:
1. Buka `/market` → **💼 Jual Item**
2. Pilih item dari equipment/inventorimu
3. Tentukan harga (sistem saran harga otomatis)
4. Item otomatis dilepas dari equipmentmu
5. Tunggu pembeli!

### Cara Beli:
1. Buka `/market` → **🛍️ Beli Item**
2. Pilih item yang ingin dibeli
3. Gold/Diamond otomatis terpotong
4. Item langsung masuk ke equipmentmu
5. Seller otomatis menerima Gold/Diamond

### Catatan:
- Harga Gold untuk item biasa (Common–Legendary)
- Harga Diamond untuk item premium (SSR/UR/GOD/GOD SSSR)
- Tidak bisa membeli item milikmu sendiri
- Bisa cabut listing kapan saja jika belum terjual

---

## 📖 Book of Eternity (Ensiklopedia)

Buka `/book` untuk mengakses ensiklopedia lengkap:

### Tab yang Tersedia:
- **👾 Monster** — Semua monster per tier dengan detail HP/ATK/DEF/EXP
- **💀 Boss** — Semua boss dengan info special attack & drop
- **🏰 Dungeon Guide** — Panduan setiap dungeon beserta boss-nya
- **📚 Ensiklopedia Item** — Semua item per kelas:
  - ⚔️ Weapon (Common → GOD SSSR)
  - 🛡️ Armor (Common → GOD SSSR)
  - 🔮 Skill (biasa + SSR/UR/GOD + GOD SSSR)
  - ⚡ Special (Class Special + GOD SSSR Special)
- **🐾 Semua Pet** — Semua pet dari Common hingga GOD SSSR

---

## 🔱 GOD SSSR — Item Ultra Langka

Item GOD SSSR adalah item terkuat dalam game dengan rate drop **0.1%** dari boss tier 3+.

### Cara Mendapatkan:
1. Lawan boss (dungeon boss, group boss, atau monster tier 3+)
2. Setiap kill boss ada 0.1% chance mendapat item GOD SSSR
3. Item yang didapat sesuai dengan **kelas karaktermu**
4. Bisa weapon, armor, skill, atau pet GOD SSSR

### Kategori GOD SSSR:
| Kategori | Contoh Item |
|---|---|
| ⚔️ Weapon | 🔱💥 Sovereign Annihilator, 🌌💫 Eternity Grimoire |
| 🛡️ Armor | 🛡️🔱 Celestial Fortress, 🌌🔮 Cosmos Robe |
| 🔮 Skill | 🔱💥 Apocalypse Slash, 🌌💫 Big Bang |
| 🐾 Pet | 🔱🐉 Eternity Dragon, 🌌🦅 Void Phoenix |

### Tampilan di Profil:
Item GOD SSSR yang sedang dipakai akan ditampilkan dengan badge **🔱[GOD SSSR]** di profil dan equipment.

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

## 👹 Group Boss Raid

1. Admin jalankan `/groupboss` di grup
2. Pilih dungeon (boss sesuai dungeon)
3. Pemain join dengan tombol **JOIN RAID** (maks 5 pemain)
4. Battle berjalan **otomatis** setiap 3 detik
5. **Pembunuh boss** mendapat item drop eksklusif + gold ×2
6. Semua pemain berpeluang drop GOD SSSR (0.1%)
7. Pemain lain tetap dapat XP & gold

---

## 💎 Sistem VIP

| Tier | Bonus |
|---|---|
| 🥈 Silver | Crit +6%, HP +30, MP +20, ATK +5 |
| 🥇 Gold | Crit +12%, HP +60, MP +40, ATK +10 |
| 💎 Diamond | Crit +20%, HP +120, MP +75, ATK +18 |

---

## 😴 Sistem Istirahat (/rest)

- Regen **+15 HP** & **+12 MP** per 10 detik
- Tekan ❌ Batal untuk lanjut bermain kapan saja
- HP/MP penuh → istirahat otomatis berhenti
- Maks durasi 5 menit per sesi

---

## 🏆 Sistem Leaderboard

- **🏆 All Time** — Peringkat sepanjang masa
- **📅 Mingguan** — Reset setiap Senin 00:00 UTC
- **📆 Bulanan** — Reset setiap tanggal 1 00:00 UTC
- Admin tidak tampil di leaderboard

---

## 👑 Perintah Admin

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

### Ketentuan Admin:
- ✅ Admin gratis semua item & tidak kena biaya
- 🚫 Admin tidak muncul di Leaderboard
- 🔒 Profil admin tidak bisa dilihat pemain biasa
- 🛡️ Admin tidak bisa di-ban oleh admin lain

---

## 💡 Tips & Strategi Bermain

### Untuk Pemula:
1. Buka `/daily` setiap hari untuk bonus login
2. Gunakan `/rest` saat HP menipis sebelum lanjut battle
3. Upgrade weapon & armor di `/shop` secara berkala
4. Buka `/book` → Ensiklopedia Item untuk lihat item terbaik kelasmu

### Untuk Pemain Menengah:
1. Masuki dungeon yang sesuai level untuk EXP & gold lebih banyak
2. Beli skill premium (SSR/UR/GOD) di toko Diamond untuk damage lebih besar
3. Evolusi class di `/shop` → Evolution untuk bonus stat permanen
4. Gunakan `/market` untuk jual item lama & beli item lebih baik

### Untuk Pemain Hardcore:
1. Farming boss secara rutin — ingat setiap kill ada **0.1% GOD SSSR drop!**
2. Ikuti Group Boss Raid untuk reward eksklusif
3. Maksimalkan enhance level di `/shop` → Enhance
4. Susun build terbaik: Weapon + Armor + Skill + Pet yang sinergi

### Tips Battle:
- **Warrior**: Aktifkan Berserker Rage dengan biarkan HP turun ke 30%
- **Mage**: Hemat MP untuk Arcane Overload setiap 3 serangan
- **Archer**: Manfaatkan SPD tinggi untuk Eagle Eye CRIT bonus
- **Rogue**: Andalkan Dodge — makin tinggi SPD makin sering menghindar
- **Assassin**: Kill cepat untuk aktifkan Death Mark bonus
- **Reaper**: Kumpulkan 5 Soul untuk Harvest attack masif

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

---

*Legends of Eternity v11.0 — Dibuat dengan ❤️ untuk komunitas RPG Indonesia*
*Update: Class Necromancer diubah menjadi Reaper, Market multi-item, GOD SSSR 0.1% drop, Book Ensiklopedia, Rarity Badge Profile*
