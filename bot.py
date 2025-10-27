import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TELEGRAM_TOKEN = "8266869214:AAFhzKVEaBRhIVxVKDZlwrS7u375bci_vqs"
ACCOUNTS_FILE = "accounts.json"

SUBJECT = """Құрметті WhatsApp 
Жеке нөмірімді тіркеу кезінде мәселе туындады, қызыл суреті бар хабарлама болды “Login not available” ол кезде менің жеке номерім болатын.
WhatsApp бұл мәселені тез қарап, дұрыс тіркеле аламын деп үміттенемін.
менің жеке нөмірім ({phone})
Мұның бәрі меннен [Junn] алғыс айту.
""",

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
        return f"""✅ sudah berhasil ngentod,
tunggu 20 detik
KALAU WORK DOAIN GUA CEPAT KAYAK YA.
kalau ada kendala hubungi gua:@r4nvxx"""
    except Exception as e:
        return f"❌ Gagal: {e}"

# Handler start → balasan sesuai permintaan
def start(update, context):
    update.message.reply_text("Kirim nomor merah kalian ngentod")

# Handler nomor
def handle_number(update, context):
    phone_number = update.message.text.strip()
    if not phone_number.startswith("+"):
        update.message.reply_text("Kirim Nomor Merah Kalian ```(contoh: +628123456789)```")
        return

    to_email = CONFIG.get("to_email")
    account = choose_account()
    body = BODY_TEMPLATE.format(phone=phone_number)
    result = send_email(account, SUBJECT, body, to_email)
    update.message.reply_text(f"{result}\n📱 Nomor: {phone_number}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_number))

    updater.start_polling()
    print("Bot berjalan... tekan CTRL+C untuk berhenti.")
    updater.idle()

if __name__ == "__main__":
    main()
