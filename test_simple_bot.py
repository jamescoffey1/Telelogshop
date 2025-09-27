#!/usr/bin/env python3
"""
Simple bot test to verify Telegram connectivity
"""
import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Get token from environment
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hello! The bot is working!')
    logger.info(f"Received /start from {update.effective_user.first_name}")

async def test_bot():
    """Test bot functionality"""
    if not TOKEN:
        print("No token found")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    
    # Initialize and start
    await application.initialize()
    await application.start()
    
    # Clear any existing webhook
    await application.bot.delete_webhook()
    
    # Get bot info
    bot_info = await application.bot.get_me()
    print(f"Bot @{bot_info.username} is ready for polling")
    
    # Start polling
    await application.updater.start_polling()
    
    # Keep running for test
    try:
        for i in range(30):  # Run for 30 seconds
            await asyncio.sleep(1)
            if i % 10 == 0:
                print(f"Bot running... {30-i}s remaining")
    except KeyboardInterrupt:
        pass
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        print("Bot stopped")

if __name__ == "__main__":
    asyncio.run(test_bot())