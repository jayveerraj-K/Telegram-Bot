import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationMiddleware
)

# --- CONFIGURATION & LOGGING ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- DATABASE MOCKUP (Scalable for 2000 lines) ---
# In a large app, you would use SQLAlchemy here.
users_db = {}

# --- HELPER FUNCTIONS ---
def get_user_info(user_id):
    return users_db.get(user_id, {"join_date": "Unknown", "status": "Member"})

# --- COMMAND HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initializes the user and shows the main menu."""
    user = update.effective_user
    users_db[user.id] = {"join_date": datetime.now(), "status": "Active"}
    
    reply_keyboard = [['/help', '/profile'], ['/settings', '/about']]
    
    await update.message.reply_text(
        f"Hi {user.first_name}! I am your advanced assistant.\n"
        "I'm currently running on a scalable modular framework.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays user stats."""
    user_id = update.effective_user.id
    info = get_user_info(user_id)
    await update.message.reply_text(f"👤 Profile\nID: {user_id}\nStatus: {info['status']}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echoes messages or processes logic."""
    text = update.message.text
    logger.info(f"User sent: {text}")
    await update.message.reply_text(f"You said: {text}. I am processing this...")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by Updates."""
    logger.error(f"Exception while handling an update: {context.error}")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # Create the Application
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Add Error Handler
    application.add_error_handler(error_handler)
    
    print("Bot is starting...")
    application.run_polling()
