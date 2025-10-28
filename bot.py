import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

TELEGRAM_TOKEN = "8266869214:AAFhzKVEaBRhIVxVKDZlwrS7u375bci_vqs"
ACCOUNTS_FILE = "accounts.json"

SUBJECT = "Questions Whatsapp for Android"

BODY_TEMPLATE = (
    """Құрметті WhatsApp 
Жеке нөмірімді тіркеу кезінде мәселе туындады, қызыл суреті бар хабарлама болды “Login not available” ол кезде менің жеке номерім болатын.
WhatsApp бұл мәселені тез қарап, дұрыс тіркеле аламын деп үміттенемін.
менің жеке нөмірім ({phone})
Мұның бәрі меннен [Junn] алғыс айту.
"""
)

# ---------------- CONFIG ----------------
def load_config(path=ACCOUNTS_FILE):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config()
CURRENT_INDEX = 0

def choose_account():
    global CURRENT_INDEX
    accounts = CONFIG["accounts"]
    account = accounts[CURRENT_INDEX % len(accounts)]
    CURRENT_INDEX += 1
    return account

# ---------------- EMAIL SENDER ----------------
def send_email(account, subject, body, to_email):
    msg = MIMEMultipart()
    msg["From"] = account["email"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(account.get("smtp", "smtp.gmail.com"), account.get("port", 587))
        server.starttls()
        server.login(account["email"], account["password"])
        server.sendmail(account["email"], to_email, msg.as_string())
        server.quit()
        return f"""✅ Sudah berhasil terkirim.
Tunggu 20 detik...
Kalau berhasil, doain yang bikin cepat kaya 😎
Kalau ada kendala, hubungi: @r4nvxx"""
    except Exception as e:
        return f"❌ Gagal mengirim: {e}"

# ---------------- HANDLERS ----------------

def start(update, context):
    # Tombol menu utama
    keyboard = [
        [InlineKeyboardButton("🧩 FIX MERAH", callback_data="fix_merah")],
        [
            InlineKeyboardButton("📱 Cek Nomor", callback_data="cek_num"),
            InlineKeyboardButton("👤 Cek ID", callback_data="cek_id"),
        ],
        [InlineKeyboardButton("💬 Cek Bio", callback_data="cek_bio")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # URL gambar banner (bisa kamu ganti pakai file lokal juga)
    photo_url = "https://i.imgur.com/V8uDFY9.jpeg"  # ganti sesuai gambar kamu

    # Kirim gambar + caption + tombol
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_url,
        caption=(
            "👋 *Selamat Datang di Email Bot Fix Merah!*\n\n"
            "Gunakan tombol di bawah untuk memilih aksi:\n"
            "🧩 *Fix Merah* — Kirim nomor merah kamu.\n"
            "📱 *Cek Nomor* — Cek format nomor kamu.\n"
            "👤 *Cek ID* — Lihat ID Telegram kamu.\n"
            "💬 *Cek Bio* — Info tambahan.\n\n"
            "_Dibuat oleh @r4nvxx_"
        ),
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
def handle_number(update, context):
    # Pastikan user di mode "fix merah"
    if context.user_data.get("mode") != "fix_merah":
        return

    phone_number = update.message.text.strip()
    if not phone_number.startswith("+"):
        update.message.reply_text("❗ Kirim Nomor Merah yang benar, contoh: +628123456789")
        return

    to_email = CONFIG.get("to_email")
    account = choose_account()
    body = BODY_TEMPLATE.format(phone=phone_number)
    result = send_email(account, SUBJECT, body, to_email)

    update.message.reply_text(f"{result}\n📱 Nomor: {phone_number}")
    context.user_data["mode"] = None  # reset mode

# ---------------- MAIN ----------------
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_number))

    updater.start_polling()
    print("🤖 Bot berjalan... tekan CTRL+C untuk berhenti.")
    updater.idle()

if __name__ == "__main__":
    main()
