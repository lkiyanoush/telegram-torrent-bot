import os
import time
import libtorrent as lt
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def handle_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc or not doc.file_name.endswith(".torrent"):
        await update.message.reply_text("لطفاً فایل .torrent بفرست.")
        return

    await update.message.reply_text("📥 دریافت فایل تورنت...")

    # ذخیره فایل تورنت
    torrent_path = os.path.join(DOWNLOAD_DIR, doc.file_name)
    file = await doc.get_file()
    await file.download_to_drive(torrent_path)

    await update.message.reply_text("🚀 شروع دانلود تورنت...")

    # تنظیمات libtorrent
    ses = lt.session()
    ses.listen_on(6881, 6891)
    info = lt.torrent_info(torrent_path)
    params = {
        'save_path': DOWNLOAD_DIR,
        'storage_mode': lt.storage_mode_t(2),
        'ti': info
    }
    h = ses.add_torrent(params)

    # منتظر دانلود
    while not h.is_seed():
        s = h.status()
        percent = s.progress * 100
        update_text = f"⬇️ دانلود: {percent:.2f}%"
        await update.message.reply_text(update_text)
        time.sleep(5)

    await update.message.reply_text("✅ دانلود کامل شد. ارسال فایل...")

    # ارسال فایل‌ها
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
    app.add_handler(MessageHandler(filters.Document.MIME_TYPE("application/x-bittorrent"), handle_torrent))
    app.run_polling()

if __name__ == "__main__":
    main()
