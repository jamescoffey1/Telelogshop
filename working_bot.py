#!/usr/bin/env python3
"""
Working Telegram bot implementation (Webhook mode)
"""

import logging
from decimal import Decimal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from app import app, db
from models import User, Product, Category, CartItem, Order, OrderItem, OrderStatus, PaymentStatus
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.application: Application | None = None

    # -----------------------------
    # ✅ Initialization
    # -----------------------------
    def get_application(self):
        return self.application

    async def init_for_webhook(self):
        """Initialize Application in webhook mode"""
        logger.info("Initializing Telegram bot...")

        # Build Application
        self.application = (
            ApplicationBuilder()
            .token(Config.TELEGRAM_BOT_TOKEN)
            .build()
        )

        # Register command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))

        # Register callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.browse_products, pattern="^browse_products$"))
        self.application.add_handler(CallbackQueryHandler(self.show_category_products, pattern="^category_"))
        self.application.add_handler(CallbackQueryHandler(self.show_product_details, pattern="^product_"))
        self.application.add_handler(CallbackQueryHandler(self.add_to_cart, pattern="^add_cart_"))
        self.application.add_handler(CallbackQueryHandler(self.view_cart, pattern="^view_cart$"))
        self.application.add_handler(CallbackQueryHandler(self.clear_cart, pattern="^clear_cart$"))
        self.application.add_handler(CallbackQueryHandler(self.checkout, pattern="^checkout$"))
        self.application.add_handler(CallbackQueryHandler(self.my_orders, pattern="^my_orders$"))
        self.application.add_handler(CallbackQueryHandler(self.show_order_details, pattern="^order_details_"))
        self.application.add_handler(CallbackQueryHandler(self.pay_crypto, pattern="^pay_crypto_"))

        # ✅ Start Application in webhook mode
        await self.application.initialize()
        await self.application.start()
        logger.info("Telegram bot started in webhook mode")

        return self.application

    # -----------------------------
    # ✅ Handlers
    # -----------------------------
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        with app.app_context():
            db_user = User.query.filter_by(telegram_id=user.id).first()
            if not db_user:
                db_user = User(
                    telegram_id=user.id,
                    username=user.username or "",
                    first_name=user.first_name or "",
                    last_name=user.last_name or "",
                    is_admin=user.id in Config.ADMIN_TELEGRAM_IDS,
                )
                db.session.add(db_user)
                db.session.commit()

        keyboard = [
            [InlineKeyboardButton("🛍️ Browse Products", callback_data="browse_products")],
            [InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")],
            [InlineKeyboardButton("📦 My Orders", callback_data="my_orders")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        ]
        if user.id in Config.ADMIN_TELEGRAM_IDS:
            keyboard.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel")])

        welcome_text = f"""
🤖 Welcome to {Config.SHOP_NAME}!

Hello {user.first_name}! I'm your crypto shopping assistant.

🛍️ Browse our products  
🛒 Add items to cart  
💳 Pay with crypto  
📦 Track your orders  
"""
        await update.message.reply_text(
            welcome_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML,
        )

    # 👉 keep all your existing handler methods (browse_products, show_category_products, etc.)
    # They don’t change — only difference is they are now registered above in init_for_webhook.
