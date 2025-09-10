import os
import subprocess
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")  # توکن ربات از محیط اجرا گرفته میشه

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

ARIA2_PATH = "aria2c"  # فرض می‌کنیم aria2c در محیط اجرا نصب شده

async def handle_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc or not doc.file_name.endswith(".torrent"):
        await update.message.reply_text("لطفاً فایل .torrent بفرست.")
        return

    await update.message.reply_text("📥 دریافت فایل تورنت...")

    # دانلود فایل تورنت از تلگرام
    torrent_path = os.path.join(DOWNLOAD_DIR, doc.file_name)
    file = await doc.get_file()
    await file.download_to_drive(torrent_path)

    await update.message.reply_text("🚀 شروع دانلود تورنت...")

    # اجرای aria2c برای دانلود فایل تورنت
    subprocess.run([
        ARIA2_PATH,
        "--seed-time=0",
        "-d", DOWNLOAD_DIR,
        torrent_path
    ])

    # پیدا کردن فایل دانلود شده
    sent_any = False
    for fname in os.listdir(DOWNLOAD_DIR):
        fpath = os.path.join(DOWNLOAD_DIR, fname)
        if os.path.isfile(fpath) and not fname.endswith(".torrent"):
            size = os.path.getsize(fpath)
            if size <= 2 * 1024 * 1024 * 1024:
                await update.message.reply_document(open(fpath, "rb"))
                sent_any = True
            else:
                await update.message.reply_text(f"⚠️ فایل {fname} بزرگ‌تر از ۲ گیگ است و نمی‌توانم ارسال کنم.")

    if not sent_any:
        await update.message.reply_text("❌ فایلی برای ارسال پیدا نشد یا همه بالای ۲ گیگ بودند.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.FILE_EXTENSION("torrent"), handle_torrent))
    app.run_polling()

if __name__ == "__main__":
    main()
