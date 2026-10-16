import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# 1. 24 ሰዓት ሰርቨሩ እንዳይተኛ የሚረዳ ዌብ ሰርቨር (Keep-Alive Server)
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=8080)

# የተጠቃሚዎችን መረጃ ለጊዜው ለመያዝ
user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Welcome to ETB TOP UP! 🎮💎\n\n"
        "Buy Free Fire Diamonds easily 24/7.\n"
        "Choose your product, enter your Player ID, and follow the payment instructions.\n\n"
        "Support: Contact the admin for help: @KNIGHT5277"
    )
    keyboard = [
        [InlineKeyboardButton("💎 Diamond Top-up", callback_data='diamonds_menu')],
        [InlineKeyboardButton("📦 Memberships", callback_data='membership_menu')],
        [InlineKeyboardButton("⭐ Level Up Pass", callback_data='levelup_menu')],
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

    if query.data == 'diamonds_menu':
        keyboard = [
            [InlineKeyboardButton("110+10 Diamonds - 190 ETB", callback_data='buy_190')],
            [InlineKeyboardButton("210+21 Diamonds - 400 ETB", callback_data='buy_400')],
            [InlineKeyboardButton("530+53 Diamonds - 975 ETB", callback_data='buy_975')],
            [InlineKeyboardButton("◀️ Back", callback_data='back_home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select Diamond Top-up Package:", reply_markup=reply_markup)

    elif query.data == 'membership_menu':
        keyboard = [
            [InlineKeyboardButton("Weekly Membership - 485 ETB", callback_data='buy_485')],
            [InlineKeyboardButton("Monthly Membership - 2155 ETB", callback_data='buy_2155')],
            [InlineKeyboardButton("◀️ Back", callback_data='back_home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select Membership:", reply_markup=reply_markup)

    elif query.data == 'levelup_menu':
        keyboard = [
            [InlineKeyboardButton("Level Up Pass - 255 ETB", callback_data='buy_255')],
            [InlineKeyboardButton("◀️ Back", callback_data='back_home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select Level Up Pass:", reply_markup=reply_markup)

    elif query.data.startswith('buy_'):
        price = query.data.split('_')[1]
        if price == '190':
            item_name = "110+10 Diamonds"
        elif price == '400':
            item_name = "210+21 Diamonds"
        elif price == '975':
            item_name = "530+53 Diamonds"
        elif price == '485':
            item_name = "Weekly Membership"
        elif price == '2155':
            item_name = "Monthly Membership"
        else:
            item_name = "Level Up Pass"
            
        user_data_store[user_id] = {"item": item_name, "price": price}
        
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='back_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text("⌨️ Enter Game ID (Player ID):", reply_markup=reply_markup)
        context.user_data['waiting_for_id'] = True

    elif query.data == 'confirm_order':
        data = user_data_store.get(user_id, {})
        price = data.get("price", "190")
        item = data.get("item", "Item")
        player_id = data.get("player_id", "000000")
        ign = data.get("ign", "Player")
        
        # ⬇️ እዚህ ጋር የራስዎን የቻፓ የክፍያ ሊንክ ያስገቡ ⬇️
        chapa_link = "https://checkout.chapa.co/checkout/payment..."
        
        text = (
            "⚠️ Legal Warning / ህጋዊ ማሳሰቢያ ⚠️\n"
            "By paying, you confirm you are 18+ and agree to our Terms.\n\n"
            f"Items: {item} x 1\n"
            f"Total: {price} ETB\n"
            f"Player ID: {player_id}\n"
            f"User: {ign}\n\n"
            f"ክፍያ ለመፈጸም ከታች ያለውን ሊንክ ይጫኑ፦\n{chapa_link}"
        )
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='back_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)

    elif query.data == 'contact_support':
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='back_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("ለማንኛውም ጥያቄ አድሚኑን ያናግሩ፦ @KNIGHT5277", reply_markup=reply_markup)

    elif query.data == 'back_home':
        await start(update, context)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if context.user_data.get('waiting_for_id'):
        player_id = update.message.text
        context.user_data['waiting_for_id'] = False
        
        verified_ign = f"FreeFire User ({player_id})"
        
        user_data = user_data_store.get(user_id, {})
        user_data["player_id"] = player_id
        user_data["ign"] = verified_ign
        user_data_store[user_id] = user_data
        
        item = user_data.get("item", "Diamonds")
        price = user_data.get("price", "190")
        
        text = (
            f"Confirm checkout\n"
            f"Items: {item} x 1\n"
            f"Total: {price} ETB\n"
            f"Player ID: {player_id}\n"
            f"User: {verified_ign}\n\n"
            "እባክዎ የተጠቃሚ ስሙ እና አይዲው ትክክል መሆናቸውን አረጋግጦ Confirm ይጫኑ!"
        )
        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data='confirm_order')],
            [InlineKeyboardButton("◀️ Back", callback_data='back_home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

if __name__ == '__main__':
    # ዌብ ሰርቨሩን በሌላ ትሬድ (Thread) ማስጀመር
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # የቴሌግራም ቦቱን ማስጀመር
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Bot is running 24/7...")
    app.run_polling()
