# 🤖 Telegram Bot — Fix Merah & WhatsApp Bio Checker

Bot Telegram ini memiliki dua fungsi utama:
1. **Fix Merah (Email Sender / Tool utama)**
2. **Cek Bio WhatsApp** — terhubung dengan **Node.js (Baileys API)** untuk mengambil bio/status dari nomor WhatsApp.

Dilengkapi dengan sistem **Premium Access**, **Owner Control**, dan **Inline Keyboard Menu** yang interaktif.

---

## 🧩 FITUR

- `/start` → menampilkan menu utama & banner interaktif.  
- **🧩 Fix Merah** → fitur utama (khusus pengguna premium).  
- **💬 Cek Bio WhatsApp**
  - `/cekbio <nomor,...>` → cek bio satu atau banyak nomor.
  - `/cekbiotxt` → reply file `.txt` berisi daftar nomor WhatsApp.
- **👑 Owner Panel**
  - `/addprem @username 10d` → tambah user premium (d = hari).
  - `/listprem` → tampilkan daftar premium.
- **Integrasi Node.js (Baileys)** untuk ambil bio WA.
- **Sistem Premium otomatis kadaluarsa.**

---

## 📁 STRUKTUR FOLDER

project-root/ │ ├── bot.py                # Bot utama (Telegram) ├── utils_premium.py      # Sistem premium ├── premium.json          # Data premium user ├── accounts.json         # (opsional) Email akun │ ├── config.js             # Konfigurasi Node.js ├── index.js              # Server Node.js (Cek Bio WhatsApp) ├── package.json          # Dependensi Node.js │ ├── requirements.txt      # Dependensi Python ├── hasil/                # Folder hasil bio ├── session/              # Folder session WhatsApp │ └── README.md             # Dokumentasi

---

## ⚙️ INSTALASI

## 🐍 1️⃣ Setup Python (Bot Telegram)
```bash
pip install -r requirements.txt
python3 bot.py
```

---

## Setup Node.js (Cek Bio WhatsApp)

```cd node_wa
npm install
node index.js
```
> Pastikan server Node.js berjalan di http://localhost:5005.



## 💡 CARA PAKAI

1. Jalankan bot.py dan index.js bersamaan.

2. Gunakan /start untuk membuka menu.

3. Fitur Fix Merah hanya bisa digunakan oleh pengguna premium.

4. Gunakan /addprem untuk memberikan akses premium ke user.

5. Untuk cek bio, kirim perintah /cekbio <nomor> atau /cekbiotxt dengan file .txt berisi daftar nomor.


## 👑 OWNER PANEL

Command	Fungsi

/addprem @user 10d	Tambah akses premium selama 10 hari
/listprem	Lihat daftar pengguna premium
/cekbio	Cek bio satu nomor
/cekbiotxt	Cek bio dari file .txt



## 🧠 TEKNOLOGI

Python 3.10+

Node.js 18+

python-telegram-bot

Baileys WhatsApp Library



---

📜 LISENSI

Proyek ini bersifat open-source untuk tujuan edukasi & pengembangan bot Telegram.
