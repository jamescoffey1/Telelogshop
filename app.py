import os
import logging
import threading
import asyncio
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Normalize URL for SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # ✅ Fallback to SQLite locally
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tele1.db"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Global bot application instance
bot_application = None

# Global bot loop for persistent async operations
bot_loop = None
bot_loop_thread = None

def initialize_bot():
    """Initialize the Telegram bot for webhook mode with persistent loop"""
    global bot_application, bot_loop, bot_loop_thread
    
    try:
        from config import Config
        if not getattr(Config, "TELEGRAM_BOT_TOKEN", None):
            logger.warning("No Telegram bot token configured - bot will not start")
            return None
            
        # Check WEBHOOK_SECRET security
        webhook_secret = getattr(Config, "WEBHOOK_SECRET", "")
        if not webhook_secret or webhook_secret == "dev-webhook-secret-123":
            logger.error("WEBHOOK_SECRET is not set or using default value. This is a security risk for production!")
            if os.environ.get("RAILWAY_STATIC_URL"):  # Production check
                raise ValueError("WEBHOOK_SECRET must be set to a secure value for production deployment")
            
        from working_bot import TelegramBot
        bot = TelegramBot()
        bot_application = bot.get_application()
        
        # Start persistent loop in background thread
        def run_bot_loop():
            global bot_loop
            import asyncio
            try:
                # Create and set the event loop for this thread
                bot_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(bot_loop)
                
                # Initialize the bot application
                bot_loop.run_until_complete(bot.init_for_webhook())
                logger.info("Telegram bot initialized for webhook mode")
                
                # Keep the loop running forever
                bot_loop.run_forever()
            except Exception as e:
                logger.error(f"Failed to run bot loop: {e}")
                import traceback
                traceback.print_exc()
        
        import threading
        bot_loop_thread = threading.Thread(target=run_bot_loop, daemon=True)
        bot_loop_thread.start()
        
        # Give the loop time to start
        import time
        time.sleep(1)
        
        return bot_application
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {e}")
        import traceback
        traceback.print_exc()
        return None

# Import models and routes
from models import *

# Initialize bot application
bot_application = initialize_bot()

from simple_routes import *

with app.app_context():
    db.create_all()  # ✅ Creates tele1.db if fallback
