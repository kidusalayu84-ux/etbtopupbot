import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 Free Fire Diamonds", callback_data='ff_diamonds')],
        [InlineKeyboardButton("📞 Admin Contact", callback_data='contact_admin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "ሰላም! እንኳን ወደ ETB TOP UP በደህና መጡ! 💎\n\n"
        "እባክዎ የሚፈልጉትን አገልግሎት ይምረጡ፦"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'ff_diamonds':
        keyboard = [
            [InlineKeyboardButton("100 💎 - 150 ETB", callback_data='buy_100')],
            [InlineKeyboardButton("210 💎 - 300 ETB", callback_data='buy_210')],
            [InlineKeyboardButton("530 💎 - 700 ETB", callback_data='buy_530')],
            [InlineKeyboardButton("◀️ ወደ ኋላ", callback_data='back_home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("እባክዎ የሚፈልጉትን የዳይመንድ መጠን ይምረጡ፦", reply_markup=reply_markup)

    elif query.data.startswith('buy_'):
        diamond_amount = query.data.split('_')[1]
        await query.edit_message_text(
            f"የመረጡት መጠን፦ {diamond_amount} 💎\n\n"
            "ክፍያ ለመፈጸም እና Player ID ለመላክ አድሚኑን ያናግሩ፦ @your_admin_username"
        )

    elif query.data == 'contact_admin':
        await query.edit_message_text("ለማንኛውም ጥያቄ አድሚኑን ያናግሩ፦ @your_admin_username")

    elif query.data == 'back_home':
        await start(query, context)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is running...")
    app.run_polling()
    
