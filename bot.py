from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# گرفتن توکن از متغیر محیطی
BOT_TOKEN = os.getenv("BOT_TOKEN")

# تابع پاسخ به دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات فعاله و آماده دریافت دستورات شماست.")

# تابع اصلی برای اجرای ربات
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
