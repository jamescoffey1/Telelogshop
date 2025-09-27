import os
import threading
import logging
import asyncio
from app import app
from config import Config

logger = logging.getLogger(__name__)

def run_telegram_bot():
    """Run the Telegram bot in a separate thread"""
    try:
        # Create new event loop for the thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from working_bot import TelegramBot
        bot = TelegramBot()
        
        print(f"Starting Telegram bot @TRIPLELOGSHOP_BOT...")
        loop.run_until_complete(bot.run_bot())
    except Exception as e:
        logger.error(f"Telegram bot failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ensure bot token is available
    if not Config.TELEGRAM_BOT_TOKEN:
        print("No Telegram bot token configured")
    else:
        print(f"Bot token found, starting bot...")
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()
    
    # Start the Flask web server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
