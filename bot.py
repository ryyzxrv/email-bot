import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from utils_premium import is_premium, add_premium, get_premium_status

# ========== CONFIG ==========
TELEGRAM_TOKEN = "8266869214:AAFhzKVEaBRhIVxVKDZlwrS7u375bci_vqs"
ACCOUNTS_FILE = "accounts.json"
ADMIN_ID = 7562165596  # Ganti dengan ID Telegram kamu

SUBJECT = "Questions Whatsapp for Android"
BODY_TEMPLATE = """Құрметті WhatsApp 
Жеке нөмірімді тіркеу кезінде мәселе туындады, қызыл суреті бар хабарлама болды “Login not available” ол кезде менің жеке номерім болатын.
WhatsApp бұл мәселені тез қарап, дұрыс тіркеле аламын деп үміттенемін.
менің жеке нөмірім [{phone}]
Мұның бәрі меннен [Junn] алғыс айту.
"""

# ========== EMAIL FUNCTIONS ==========
def load_config():
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config()
CURRENT_INDEX = 0

def choose_account():
    global CURRENT_INDEX
    accounts = CONFIG["accounts"]
    account = accounts[CURRENT_INDEX % len(accounts)]
    CURRENT_INDEX += 1
    return account

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
        return "✅ Email berhasil dikirim!"
    except Exception as e:
        return f"❌ Gagal mengirim: {e}"

# ========== COMMAND HANDLERS ==========
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🧩 FIX MERAH (Premium Only)", callback_data="fix_merah")],
        [InlineKeyboardButton("⭐ Check Premium", callback_data="check_prem")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    photo_url = "https://i.imgur.com/V8uDFY9.jpeg"

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_url,
        caption=(
            "👋 *Selamat Datang di Email Bot Fix Merah!*\n\n"
            "Gunakan tombol di bawah:\n"
            "🧩 *Fix Merah* — Kirim nomor merah kamu (khusus premium)\n"
            "⭐ *Check Premium* — Lihat status premium kamu.\n\n"
            "_Dibuat oleh @r4nvxx_"
        ),
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

def button_callback(update, context):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == "fix_merah":
        if not is_premium(user_id):
            query.answer("❌ Fitur ini khusus pengguna premium.", show_alert=True)
            return
        query.answer()
        context.user_data["mode"] = "fix_merah"
        query.edit_message_caption(caption="🧩 Kirim nomor merah kamu (contoh: +628123456789)")

    elif data == "check_prem":
        query.answer()
        status = get_premium_status(user_id)
        query.edit_message_caption(caption=f"⭐ *Status Premium Kamu:*\n\n{status}", parse_mode="Markdown")

def handle_number(update, context):
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
    context.user_data["mode"] = None

# ========== ADMIN COMMANDS ==========
def addprem_command(update, context):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ Kamu bukan admin.")
        return

    if len(context.args) < 2:
        update.message.reply_text("Gunakan format: /addprem @user 10d (balas pesan user)")
        return

    duration = context.args[1]
    if not duration.endswith("d"):
        update.message.reply_text("Gunakan format hari, contoh: 10d")
        return

    days = int(duration[:-1])
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not user:
        update.message.reply_text("Balas pesan user yang ingin ditambahkan premium.")
        return

    exp_time = add_premium(user.id, days)
    exp_str = datetime.fromtimestamp(exp_time).strftime("%d-%m-%Y %H:%M")
    update.message.reply_text(f"✅ @{user.username} jadi premium {days} hari.\n📅 Hingga: {exp_str}")

def checkprem_command(update, context):
    status = get_premium_status(update.effective_user.id)
    update.message.reply_text(status)

# ========== MAIN ==========
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("addprem", addprem_command))
    dp.add_handler(CommandHandler("checkprem", checkprem_command))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_number))

    updater.start_polling()
    print("🤖 Bot berjalan...")
    updater.idle()

if __name__ == "__main__":
    main()th("+"):
        update.message.reply_text("❗ Nomor harus diawali dengan '+'. Contoh: +628123456789")
        return

    to_email = CONFIG.get("to_email")
    account = choose_account()
    body = BODY_TEMPLATE.format(phone=phone_number)
    result = send_email(account, SUBJECT, body, to_email)
    update.message.reply_text(result)
    context.user_data["mode"] = None

# ---------------- COMMAND: ADDPREM ----------------
def addprem(update: Update, context: CallbackContext):
    # Hanya admin bot (ganti ID kamu di bawah)
    ADMIN_ID = 7562165596  # GANTI DENGAN ID TELEGRAM KAMU
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("🚫 Kamu tidak punya izin untuk perintah ini.")
        return

    try:
        username = context.args[0]
        days_arg = context.args[1]

        # Ambil ID user dari mention (atau numeric)
        user_id = username.replace("@", "").strip()
        if days_arg.endswith("d"):
            days = int(days_arg[:-1])
        else:
            days = int(days_arg)

        expiry = add_premium(user_id, days)
        update.message.reply_text(
            f"✅ {username} telah menjadi *Premium* selama {days} hari.\n"
            f"🕓 Kadaluarsa: {expiry.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except Exception as e:
        update.message.reply_text(f"❌ Format salah!\nGunakan: `/addprem @user 10d`\nError: {e}")

# ---------------- MAIN ----------------
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("addprem", addprem))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_number))

    updater.start_polling()
    print("🤖 Bot berjalan... tekan CTRL+C untuk berhenti.")
    updater.idle()

if __name__ == "__main__":
    main()# ---------------- EMAIL SENDER ----------------
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
    keyboard = [
        [InlineKeyboardButton("🧩 FIX MERAH", callback_data="fix_merah")],
        [
            InlineKeyboardButton("📱 Cek Nomor", callback_data="cek_num"),
            InlineKeyboardButton("👤 Cek ID", callback_data="cek_id"),
        ],
        [InlineKeyboardButton("💬 Cek Bio", callback_data="cek_bio")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    photo_url = "https://i.imgur.com/V8uDFY9.jpeg"

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

# ---- Callback tombol ----
def button_callback(update, context):
    query = update.callback_query
    query.answer()

    if query.data == "fix_merah":
        context.user_data["mode"] = "fix_merah"
        query.edit_message_caption(
            caption="🔴 Kirim *Nomor Merah* kamu di sini (contoh: +628123456789)",
            parse_mode="Markdown",
        )

    elif query.data == "cek_num":
        query.edit_message_caption(
            caption="📱 Masukkan nomor kamu untuk dicek formatnya!",
            parse_mode="Markdown",
        )

    elif query.data == "cek_id":
        user_id = query.from_user.id
        query.edit_message_caption(
            caption=f"👤 ID Telegram kamu: `{user_id}`",
            parse_mode="Markdown",
        )

    elif query.data == "cek_bio":
        query.edit_message_caption(
            caption="💬 Bot ini dibuat untuk bantu kirim email fix merah otomatis.\n\nKontak dev: @r4nvxx",
            parse_mode="Markdown",
        )

# ---- Handler nomor ----
def handle_number(update, context):
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
    main()# ---------------- EMAIL SENDER ----------------
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
