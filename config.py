import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "devkey")

    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///tele1.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Telegram bot token
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    
    # Shop configuration
    SHOP_NAME = os.environ.get("SHOP_NAME", "TripleLog Shop")
    
    # Webhook configuration (REQUIRED for production)
    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
    
    # Admin configuration (add your Telegram user ID here)
    ADMIN_TELEGRAM_IDS = [int(x) for x in os.environ.get("ADMIN_TELEGRAM_IDS", "").split(",") if x.strip()]
    
    # NowPayments configuration
    NOWPAYMENTS_API_KEY = os.environ.get("NOWPAYMENTS_API_KEY", "")
    NOWPAYMENTS_BASE_URL = os.environ.get("NOWPAYMENTS_BASE_URL", "https://api.nowpayments.io/v1")
    NOWPAYMENTS_IPN_SECRET = os.environ.get("NOWPAYMENTS_IPN_SECRET", "")
    
    # Admin password for web interface
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    # Support configuration
    SUPPORT_CONTACT = os.environ.get("SUPPORT_CONTACT", "@your_support_handle")
