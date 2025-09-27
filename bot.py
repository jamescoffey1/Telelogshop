import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(name)

# Get bot token from environment
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respond to /start command"""
    await update.message.reply_text("Hello! Bot is running ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo any text message"""
    text = update.message.text
    logger.info(f"Received message: {text}")
    await update.message.reply_text(f"You said: {text}")

# --- Main Bot ---

class TelegramBot:
    def init(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.app.add_handler(CommandHandler("start", start))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    async def run_bot(self):
        logger.info("🤖 Bot started. Waiting for commands...")
        await self.app.run_polling()

# Optional standalone run
if name == "main":
    bot = TelegramBot()
    asyncio.run(bot.run_bot())