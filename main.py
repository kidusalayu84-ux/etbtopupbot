import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# የተጠቃሚዎችን መረጃ ለጊዜው ለመያዝ (Player ID እና የተመረጠው ዕቃ)
user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Welcome to ETB TOP UP! 🎮💎\n\n"
        "Buy Free Fire Diamonds easily.\n"
        "Choose your diamond package, enter your Player ID, and follow the payment instructions.\n\n"
        "Support: Contact the admin for help."
    )
    keyboard = [
        [InlineKeyboardButton("🛒 Products", callback_data='products')],
        [InlineKeyboardButton("📞 Contact Support", callback_data='contact_support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'products':
        keyboard = [
            [InlineKeyboardButton("Free Fire Middle East", callback_data='ff_middle_east')],
            [InlineKeyboardButton("◀️ Back", callback_data='back_home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a game:", reply_markup=reply_markup)

    elif query.data == 'ff_middle_east':
        keyboard = [
            [InlineKeyboardButton("110+10 Diamonds - 185 ETB", callback_data='buy_185')],
            [InlineKeyboardButton("210+21 Diamonds - 395 ETB", callback_data='buy_395')],
            [InlineKeyboardButton("Weekly Membership - 480 ETB", callback_data='buy_480')],
            [InlineKeyboardButton("Booyah Pass - 650 ETB", callback_data='buy_650')],
            [InlineKeyboardButton("530+53 Diamonds - 970 ETB", callback_data='buy_970')],
            [InlineKeyboardButton("Monthly Membership - 2150 ETB", callback_data='buy_2150')],
            [InlineKeyboardButton("◀️ Back", callback_data='products')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Freefire Middle East", reply_markup=reply_markup)

    elif query.data.startswith('buy_'):
        price = query.data.split('_')[1]
        if price == '185':
            item_name = "110+10 Diamonds"
        elif price == '395':
            item_name = "210+21 Diamonds"
        elif price == '480':
            item_name = "Weekly Membership"
        elif price == '650':
            item_name = "Booyah Pass"
        elif price == '970':
            item_name = "530+53 Diamonds"
        else:
            item_name = "Monthly Membership"
            
        user_data_store[user_id] = {"item": item_name, "price": price}
        
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='ff_middle_east')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text("⌨️ Enter Game Id:", reply_markup=reply_markup)
        context.user_data['waiting_for_id'] = True

    elif query.data == 'pay_chapa':
        data = user_data_store.get(user_id, {})
        price = data.get("price", "185")
        
        chapa_link = "https://checkout.chapa.co/checkout/payment..."
        
        text = (
            "⚠️ Legal Warning / ህጋዊ ማሳሰቢያ ⚠️\n"
            "By paying, you confirm you are 18+ and agree to our Terms.\n\n"
            f"Total: {price} ETB\n\n"
            f"ክፍያ ለመፈጸም ከታች ያለውን ሊንክ ይጫኑ፦\n{chapa_link}"
        )
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='ff_middle_east')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)

    elif query.data == 'contact_support':
        await query.edit_message_text("ለማንኛውም ጥያቄ አድሚኑን ያናግሩ፦ @KNIGHT5277")

    elif query.data == 'back_home':
        await start(update, context)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if context.user_data.get('waiting_for_id'):
        player_id = update.message.text
        context.user_data['waiting_for_id'] = False
        
        user_data = user_data_store.get(user_id, {})
        item = user_data.get("item", "Diamonds")
        price = user_data.get("price", "185")
        
        text = (
            f"Confirm checkout\n"
            f"Items: {item} x 1\n"
            f"Total: {price} ETB\n"
            f"Player ID: {player_id}\n\n"
            f"ክፍያ ለመፈጸም እና Player ID ለመላክ አድሚኑን ያናግሩ፦ @KNIGHT5277\n\n"
            "Choose how to pay:"
        )
        keyboard = [
            [InlineKeyboardButton("Chapa", callback_data='pay_chapa')],
            [InlineKeyboardButton("◀️ Back", callback_data='ff_middle_east')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Bot is running...")
    app.run_polling()
        
