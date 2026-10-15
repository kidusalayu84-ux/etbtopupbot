import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! እንኳን ወደ ቴሌግራም ቶፕ አፕ ቦት በደህና መጡ። 💎")

if __name__ == '__main__':
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    
    TOKEN = os.environ.get("BOT_TOKEN")
    if TOKEN:
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.run_polling()
      
