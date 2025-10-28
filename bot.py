#!/usr/bin/env python3
# bot.py - Telegram bot terintegrasi dengan Node.js Baileys cek-bio
# Compatible with python-telegram-bot v13 (Updater)

import os
import io
import json
import logging
import requests
from typing import List

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    CallbackContext,
)

# Optional: utils_premium should provide is_premium(user_id) and OWNER_ID
# Make sure you have utils_premium.py in same folder.
try:
    from utils_premium import is_premium, OWNER_ID
except Exception:
    # Fallback if utils_premium missing — treat nobody as premium except an OWNER_ID placeholder
    OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

    def is_premium(user_id):
        return int(user_id) == int(OWNER_ID)


# ========================= CONFIG =========================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")  # ganti token di sini atau set env BOT_TOKEN
NODE_WA_CEKBIO_URL = os.environ.get("NODE_WA_CEKBIO_URL", "http://localhost:5005/cekbio")
BANNER_URL = os.environ.get("BANNER_URL", "https://i.imgur.com/V8uDFY9.jpeg")
OWNER_USERNAME_URL = os.environ.get("OWNER_URL", "https://t.me/r4vnnx")

# Email config (jika mau pakai, jangan lupa isi accounts.json dan logic mengirim email)
ACCOUNTS_FILE = "accounts.json"  # optional, tidak dipakai di cek-bio

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========================= HELPERS =========================
def parse_numbers_from_text(text: str) -> List[str]:
    """
    Ambil semua deretan angka (nomor) dari teks, kembalikan tanpa tanda '+'.
    Contoh input: "/cekbio 62812, 0812-xxx" -> ["62812", "0812xxx"]
    """
    if not text:
        return []
    # Ambil semua digit-sequence
    import re

    nums = re.findall(r"\d+", text)
    # remove leading zeros? keep as-is since Node expects country code
    return [n.strip() for n in nums if n.strip()]


def call_node_cekbio(numbers: List[str], timeout: int = 60):
    """
    Kirim request ke Node.js API (POST JSON { numbers: [...] })
    Kembalikan response.json() atau raise Exception.
    """
    if not numbers:
        raise ValueError("No numbers provided")

    payload = {"numbers": numbers}
    try:
        r = requests.post(NODE_WA_CEKBIO_URL, json=payload, timeout=timeout)
    except requests.RequestException as e:
        logger.exception("Gagal konek ke Node WA API")
        raise RuntimeError(f"Gagal koneksi ke WA API: {e}")

    if r.status_code != 200:
        # coba parse body jika ada
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"WA API error {r.status_code}: {detail}")

    try:
        return r.json()
    except Exception as e:
        logger.exception("Respons dari WA API tidak valid JSON")
        raise RuntimeError("Respons dari WA API tidak valid JSON") from e


def build_result_text(data: dict) -> str:
    """
    Susun text ringkasan dan detail dari response WA API menjadi string.
    Mengasumsikan response: { withBio: [{nomor,bio,setAt}], noBio: [...], notRegistered: [...] }
    """
    lines = []
    with_bio = data.get("withBio") or data.get("withbio") or data.get("with_bio") or []
    no_bio = data.get("noBio") or data.get("nobio") or []
    not_reg = data.get("notRegistered") or data.get("notregistered") or data.get("not_registered") or []

    lines.append(f"✅ Total dicek: {len(with_bio) + len(no_bio) + len(not_reg)}")
    lines.append(f"📝 Dengan Bio: {len(with_bio)}")
    lines.append(f"📵 Tanpa Bio: {len(no_bio)}")
    lines.append(f"🚫 Tidak Terdaftar: {len(not_reg)}")
    lines.append("")
    if with_bio:
        lines.append("---- NOMOR DENGAN BIO ----")
        for item in with_bio:
            nomor = item.get("nomor") or item.get("number") or item.get("nomor_whatsapp") or ""
            bio = item.get("bio") or item.get("status") or ""
            setat = item.get("setAt") or item.get("set_at") or ""
            lines.append(f"{nomor} — \"{bio}\"")
            if setat:
                lines.append(f"   ⏰ {setat}")
        lines.append("")
    if no_bio:
        lines.append("---- NOMOR TANPA BIO ----")
        for n in no_bio:
            lines.append(str(n))
        lines.append("")
    if not_reg:
        lines.append("---- TIDAK TERDAFTAR ----")
        for n in not_reg:
            lines.append(str(n))
        lines.append("")
    return "\n".join(lines)


# ========================= HANDLERS =========================
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    keyboard = [
        [InlineKeyboardButton("🧩 FIX MERAH", callback_data="fix_merah")],
        [
            InlineKeyboardButton("📱 Cek Nomor", callback_data="cek_num"),
            InlineKeyboardButton("👤 Cek ID", callback_data="cek_id"),
        ],
        [InlineKeyboardButton("💬 Cek Bio", callback_data="cek_bio")],
        [InlineKeyboardButton("👑 Owner", url=OWNER_USERNAME_URL)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        "👋 *Selamat Datang di Bot Fix Merah!*\n\n"
        "Gunakan tombol di bawah untuk memilih aksi:\n"
        "🧩 *Fix Merah* — Kirim nomor merah kamu.\n"
        "📱 *Cek Nomor* — Cek format nomor kamu.\n"
        "👤 *Cek ID* — Lihat ID Telegram kamu.\n"
        "💬 *Cek Bio* — Cek bio WhatsApp (butuh Node.js Baileys berjalan).\n\n"
        "_Dibuat oleh @r4nvxx_"
    )

    # send_photo may raise some errors (e.g. chat not allowed to send media) -> fallback to text
    try:
        context.bot.send_photo(chat_id=chat_id, photo=BANNER_URL, caption=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    except Exception:
        context.bot.send_message(chat_id=chat_id, text=caption, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)


def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    # keep original behavior of FIX MERAH untouched
    if data == "fix_merah":
        # call original handler or reply prompt
        query.answer()
        query.message.reply_text("🧩 Untuk FIX MERAH: Kirim nomor merah kamu (fitur tetap sama).")
        return

    if data == "cek_num":
        query.answer()
        query.message.reply_text("📱 Masukkan nomor yang mau dicek, contoh: `/cekbio 628123456789,62811...`")
        return

    if data == "cek_id":
        query.answer()
        uid = query.from_user.id
        query.message.reply_text(f"👤 ID Telegram kamu: `{uid}`", parse_mode=ParseMode.MARKDOWN)
        return

    if data == "cek_bio":
        query.answer()
        # instruct user how to use /cekbio
        text = (
            "💬 *Cek Bio WhatsApp*\n\n"
            "Kamu bisa:\n"
            "• Ketik `/cekbio 628123456789,62822...` untuk cek langsung.\n"
            "• Atau reply file .txt (list nomor) dengan perintah `/cekbiotxt`.\n\n"
            "_Note: fitur ini memerlukan Node.js Baileys API berjalan di server._"
        )
        query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        return

    query.answer()


def cmd_cekbio(update: Update, context: CallbackContext):
    """Handler for /cekbio command that accepts numbers as args"""
    user = update.effective_user
    user_id = user.id

    # premium restriction: only premium or owner can use
    if not is_premium(user_id) and user_id != int(OWNER_ID):
        return update.message.reply_text("🚫 Fitur ini hanya untuk pengguna *Premium*.", parse_mode=ParseMode.MARKDOWN)

    # parse arguments
    text = update.message.text or ""
    parts = text.split(" ", 1)
    if len(parts) < 2 or not parts[1].strip():
        return update.message.reply_text("Kirim contoh: `/cekbio 628123456789,62822...`", parse_mode=ParseMode.MARKDOWN)

    numbers = parse_numbers_from_text(parts[1])
    if not numbers:
        return update.message.reply_text("Tidak menemukan nomor di pesanmu. Pastikan format benar.", parse_mode=ParseMode.MARKDOWN)

    msg = update.message.reply_text(f"🔎 Mengecek {len(numbers)} nomor... Mohon tunggu.", parse_mode=ParseMode.MARKDOWN)
    try:
        data = call_node_cekbio(numbers, timeout=120)
        result_text = build_result_text(data)
        # kirim sebagai file txt (lebih rapi)
        bio_file_name = f"hasil_cekbio_{user_id}.txt"
        bio_bytes = result_text.encode("utf-8")
        bio_stream = io.BytesIO(bio_bytes)
        bio_stream.name = bio_file_name
        update.message.reply_document(document=bio_stream, filename=bio_file_name, caption="📄 Hasil cek bio")
    except Exception as e:
        logger.exception("Error saat cekbio")
        update.message.reply_text(f"❌ Gagal cek bio: {e}")


def cmd_cekbiotxt(update: Update, context: CallbackContext):
    """Handler for /cekbiotxt — user must reply to a .txt file containing numbers"""
    user = update.effective_user
    user_id = user.id
    if not is_premium(user_id) and user_id != int(OWNER_ID):
        return update.message.reply_text("🚫 Fitur ini hanya untuk pengguna *Premium*.", parse_mode=ParseMode.MARKDOWN)

    # check reply_to_message
    if not update.message.reply_to_message or not update.message.reply_to_message.document:
        return update.message.reply_text("Reply file .txt yang berisi nomor, lalu ketik /cekbiotxt", parse_mode=ParseMode.MARKDOWN)

    doc = update.message.reply_to_message.document
    # ensure mime-type is plain text (some clients may report different types)
    # we'll still try to download and parse
    try:
        file_obj = context.bot.get_file(doc.file_id)
        fpath = f"/tmp/cekbio_{user_id}.txt"
        file_obj.download(custom_path=fpath)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        numbers = parse_numbers_from_text(content)
        if not numbers:
            return update.message.reply_text("Tidak menemukan nomor di file .txt tersebut.", parse_mode=ParseMode.MARKDOWN)
        msg = update.message.reply_text(f"🔎 Mengecek {len(numbers)} nomor dari file... Mohon tunggu.", parse_mode=ParseMode.MARKDOWN)
        try:
            data = call_node_cekbio(numbers, timeout=180)
            result_text = build_result_text(data)
            bio_file_name = f"hasil_cekbio_{user_id}.txt"
            bio_stream = io.BytesIO(result_text.encode("utf-8"))
            bio_stream.name = bio_file_name
            update.message.reply_document(document=bio_stream, filename=bio_file_name, caption="📄 Hasil cek bio")
        except Exception as e:
            logger.exception("Error saat cekbio dari file")
            update.message.reply_text(f"❌ Gagal cek bio: {e}")
        finally:
            # cleanup
            try:
                os.remove(fpath)
            except Exception:
                pass
    except Exception as e:
        logger.exception("Gagal download file")
        update.message.reply_text(f"❌ Gagal ambil file: {e}")


# Optional small helper command to check node API status
def cmd_status_node(update: Update, context: CallbackContext):
    try:
        r = requests.get(NODE_WA_CEKBIO_URL.replace("/cekbio", "/status"), timeout=6)
        if r.status_code == 200:
            update.message.reply_text("✅ Node WA API terhubung.")
        else:
            update.message.reply_text(f"⚠️ Node WA API respons: {r.status_code}")
    except Exception as e:
        update.message.reply_text(f"❌ Node WA API tidak tersedia: {e}")


# Basic echo for text messages (can be constrained)
def echo_text(update: Update, context: CallbackContext):
    # not used for cekbio; keep minimal to avoid accidental captures
    pass


# ========================= MAIN =========================
def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN belum di-set. Edit bot.py atau set env BOT_TOKEN.")
        return

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("cekbio", cmd_cekbio))
    dp.add_handler(CommandHandler("cekbiotxt", cmd_cekbiotxt))
    dp.add_handler(CommandHandler("statusnode", cmd_status_node))  # optional

    # Callback Query (buttons)
    dp.add_handler(CallbackQueryHandler(button_callback))

    # Text handler (keperluan lain) - disabled to avoid clash with cekbio flow
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_text))

    logger.info("Bot started. Listening...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
