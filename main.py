import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USERNAME = "@KNIGHT5277"

# Replace this with your real Chapa checkout URL before accepting payments.
CHAPA_LINK = os.environ.get("CHAPA_LINK", "")

# Optional keep-alive web server
app_flask = Flask(__name__)


@app_flask.route("/")
def home():
    return "ETB TOP UP bot is running!"


def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))


# Product catalogue. Diamond packages have ETB 5 added to the original prices.
PRODUCTS = {
    "diamonds": {
        "buy_195": ("110+10 Diamonds", 195),
        "buy_405": ("210+21 Diamonds", 405),
        "buy_980": ("530+53 Diamonds", 980),
    },
    "membership": {
        "buy_485": ("Weekly Membership", 485),
        "buy_2155": ("Monthly Membership", 2155),
    },
    "levelup": {
        "buy_255": ("Level Up Pass", 255),
    },
}

# In-memory storage: pending orders are cleared if the bot process restarts.
orders = {}


def home_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Diamond Top-up", callback_data="diamonds_menu")],
        [InlineKeyboardButton("📦 Membership", callback_data="membership_menu")],
        [InlineKeyboardButton("⭐ Level Up Pass", callback_data="levelup_menu")],
        [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Welcome to ETB TOP UP! 🎮💎\n\n"
        "Choose a product below. Then enter your Free Fire Player ID "
        "and review your order before payment.\n\n"
        f"Support: {ADMIN_USERNAME}"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=home_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            text, reply_markup=home_keyboard()
        )


def product_keyboard(category):
    buttons = []
    for callback_data, (name, price) in PRODUCTS[category].items():
        buttons.append([
            InlineKeyboardButton(
                f"{name} — {price:,} ETB",
                callback_data=callback_data,
            )
        ])
    buttons.append([InlineKeyboardButton("◀️ Back", callback_data="back_home")])
    return InlineKeyboardMarkup(buttons)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "back_home":
        context.user_data.pop("waiting_for_id", None)
        await start(update, context)
        return

    if data == "diamonds_menu":
        await query.edit_message_text(
            "💎 Select Diamond Top-up Package:",
            reply_markup=product_keyboard("diamonds"),
        )
        return

    if data == "membership_menu":
        await query.edit_message_text(
            "📦 Select Membership:",
            reply_markup=product_keyboard("membership"),
        )
        return

    if data == "levelup_menu":
        await query.edit_message_text(
            "⭐ Select Level Up Pass:",
            reply_markup=product_keyboard("levelup"),
        )
        return

    if data == "contact_support":
        await query.edit_message_text(
            f"For help, contact the admin: {ADMIN_USERNAME}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Back", callback_data="back_home")]
            ]),
        )
        return

    product = None
    for category in PRODUCTS.values():
        if data in category:
            product = category[data]
            break

    if product:
        item_name, price = product
        orders[user_id] = {"item": item_name, "price": price}
        context.user_data["waiting_for_id"] = True
        await query.edit_message_text(
            f"Selected: {item_name}\nPrice: {price:,} ETB\n\n"
            "⌨️ Please enter your Free Fire Player ID:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Back", callback_data="back_home")]
            ]),
        )
        return

    if data == "confirm_order":
        order = orders.get(user_id)
        if not order or not order.get("player_id"):
            await query.edit_message_text(
                "Order details were not found. Please start again with /start."
            )
            return

        if not CHAPA_LINK or "..." in CHAPA_LINK:
            await query.edit_message_text(
                "⚠️ Payment is not configured yet.\n\n"
                "Your order details are saved in this session, but no payment "
                "has been taken. Please contact support to complete setup.\n\n"
                f"Product: {order['item']}\n"
                f"Amount: {order['price']:,} ETB\n"
                f"Player ID: {order['player_id']}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
                    [InlineKeyboardButton("◀️ Back", callback_data="back_home")],
                ]),
            )
            return

        await query.edit_message_text(
            f"Order: {order['item']}\n"
            f"Amount: {order['price']:,} ETB\n"
            f"Player ID: {order['player_id']}\n\n"
            "Open the payment link below and follow the payment provider's steps.\n"
            "Your top-up is not confirmed until payment is verified.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Pay with Chapa", url=CHAPA_LINK)],
                [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
            ]),
        )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if not context.user_data.get("waiting_for_id"):
        return

    player_id = update.message.text.strip()
    if not player_id.isdigit() or not (5 <= len(player_id) <= 20):
        await update.message.reply_text(
            "Please enter a valid numeric Free Fire Player ID (5–20 digits)."
        )
        return

    context.user_data["waiting_for_id"] = False
    user_id = update.effective_user.id
    order = orders.get(user_id)

    if not order:
        await update.message.reply_text(
            "Your selected product was not found. Please use /start and try again."
        )
        return

    order["player_id"] = player_id
    text = (
        "🧾 Confirm your order\n\n"
        f"Product: {order['item']}\n"
        f"Total: {order['price']:,} ETB\n"
        f"Free Fire Player ID: {player_id}\n\n"
        "Please check the Player ID carefully before confirming."
    )
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm order", callback_data="confirm_order")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_home")],
        ]),
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Please set the BOT_TOKEN environment variable.")

    threading.Thread(target=run_flask, daemon=True).start()

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    print("ETB TOP UP bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
        
