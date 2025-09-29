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

# Database base class
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tele1.db"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}
db.init_app(app)

# --------------------
# Telegram bot globals
# --------------------
bot_application = None
bot_loop = None
bot_ready_event = threading.Event()  # Will signal when bot is ready

def initialize_bot():
    """Initialize Telegram bot in webhook mode and persistent loop"""
    global bot_application, bot_loop, bot_ready_event

    from config import Config
    if not getattr(Config, "TELEGRAM_BOT_TOKEN", None):
        logger.warning("No Telegram bot token configured - bot will not start")
        return None

    from working_bot import TelegramBot
    bot = TelegramBot()
    bot_application = bot.get_application()

    def run_bot_loop():
        global bot_loop
        bot_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(bot_loop)
        try:
            bot_loop.run_until_complete(bot.init_for_webhook())
            logger.info("Telegram bot initialized for webhook mode")
            bot_ready_event.set()  # Signal that bot is ready
            bot_loop.run_forever()
        except Exception as e:
            logger.error(f"Failed to run bot loop: {e}")
            import traceback
            traceback.print_exc()

    t = threading.Thread(target=run_bot_loop, daemon=True)
    t.start()

    # Wait up to 10 seconds for bot to be ready
    if not bot_ready_event.wait(timeout=10):
        logger.error("Bot failed to initialize within 10 seconds")
    return bot_application, bot_loop

# Initialize bot
bot_application, bot_loop = initialize_bot()

# --------------------
# Import models and routes
# --------------------
from models import *

# Instead of importing the app inside routes (circular import), pass everything
import simple_routes
simple_routes.register_routes(app, bot_application, bot_loop)

# Create database tables if not exist
with app.app_context():
    db.create_all()
