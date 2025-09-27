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

def initialize_bot():
    """Initialize the Telegram bot for webhook mode"""
    global bot_application
    
    try:
        from config import Config
        if not getattr(Config, "TELEGRAM_BOT_TOKEN", None):
            logger.warning("No Telegram bot token configured - bot will not start")
            return None
            
        from working_bot import TelegramBot
        bot = TelegramBot()
        bot_application = bot.get_application()
        
        logger.info("Telegram bot initialized for webhook mode")
        return bot_application
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {e}")
        import traceback
        traceback.print_exc()
        return None

# Import models and routes
from models import *

# Initialize bot application
initialize_bot()

from simple_routes import *

with app.app_context():
    db.create_all()  # ✅ Creates tele1.db if fallback