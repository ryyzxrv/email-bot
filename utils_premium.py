import json
import time
from datetime import datetime

PREMIUM_FILE = "premium.json"
OWNER_ID = 7562165596  # 🧑‍💻 Ganti dengan user_id kamu (ID Telegram kamu)

def load_premium():
    try:
        with open(PREMIUM_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_premium(data):
    with open(PREMIUM_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_premium(user_id):
    if str(user_id) == str(OWNER_ID):  # 👑 Owner selalu premium
        return True
    data = load_premium()
    exp = data.get(str(user_id))
    return bool(exp and exp > time.time())

def add_premium(user_id, days):
    data = load_premium()
    expire_time = time.time() + (days * 86400)
    data[str(user_id)] = expire_time
    save_premium(data)
    return expire_time

def get_premium_status(user_id):
    if str(user_id) == str(OWNER_ID):
        return "👑 Kamu adalah *Owner* (akses premium permanen)."
    data = load_premium()
    exp = data.get(str(user_id))
    if not exp:
        return "🚫 Kamu belum premium."
    now = time.time()
    if exp < now:
        return "❌ Masa premium kamu sudah berakhir."
    sisa_hari = int((exp - now) / 86400)
    exp_str = datetime.fromtimestamp(exp).strftime("%d-%m-%Y %H:%M")
    return f"✅ Kamu *premium*.\n📅 Berlaku sampai: {exp_str}\n⏳ Sisa: {sisa_hari} hari"def get_premium_status(user_id):
    # Admin auto premium
    if str(user_id) == str(ADMIN_ID):
        return "👑 Kamu adalah *Owner/Admin*.\n💎 Akses premium aktif selamanya."

    data = load_premium()
    exp = data.get(str(user_id))
    if not exp:
        return "🚫 Kamu belum premium."
    now = time.time()
    if exp < now:
        return "❌ Masa premium kamu sudah berakhir."
    sisa_hari = int((exp - now) / 86400)
    exp_str = datetime.fromtimestamp(exp).strftime("%d-%m-%Y %H:%M")
    return f"✅ Kamu premium.\n📅 Berlaku sampai: {exp_str}\n⏳ Sisa: {sisa_hari} hari"def get_premium_status(user_id):
    data = load_premium()
    exp = data.get(str(user_id))

    if not exp:
        return "🚫 Kamu belum premium."

    now = time.time()
    if exp < now:
        return "❌ Masa premium kamu sudah berakhir."

    sisa_hari = int((exp - now) / 86400)
    exp_str = datetime.fromtimestamp(exp).strftime("%d-%m-%Y %H:%M")

    return (
        f"✅ Kamu premium.\n"
        f"📅 Berlaku sampai: {exp_str}\n"
        f"⏳ Sisa: {sisa_hari} hari"
    )
