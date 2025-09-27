#!/usr/bin/env python3
"""
Working Telegram bot implementation
"""
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from app import app, db
from models import User, Product, Category, CartItem, Order, OrderItem, OrderStatus, PaymentStatus
from config import Config
from decimal import Decimal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        with app.app_context():
            # Get or create user
            db_user = User.query.filter_by(telegram_id=user.id).first()
            if not db_user:
                db_user = User(
                    telegram_id=user.id,
                    username=user.username or '',
                    first_name=user.first_name or '',
                    last_name=user.last_name or '',
                    is_admin=user.id in Config.ADMIN_TELEGRAM_IDS
                )
                db.session.add(db_user)
                db.session.commit()
        
        keyboard = [
            [InlineKeyboardButton("🛍️ Browse Products", callback_data="browse_products")],
            [InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")],
            [InlineKeyboardButton("📦 My Orders", callback_data="my_orders")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ]
        
        # Add admin button for admin users
        if user.id in Config.ADMIN_TELEGRAM_IDS:
            keyboard.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🤖 Welcome to {Config.SHOP_NAME}!

Hello {user.first_name}! I'm your crypto shopping assistant.

🛍️ Browse our products
🛒 Add items to cart  
💳 Pay with crypto
📦 Track your orders

What would you like to do?
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def browse_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show product categories"""
        query = update.callback_query
        await query.answer()
        
        with app.app_context():
            categories = Category.query.filter_by(is_active=True).all()
        
        if not categories:
            await query.edit_message_text("No categories available at the moment.")
            return
        
        keyboard = []
        for category in categories:
            keyboard.append([InlineKeyboardButton(
                f"📂 {category.name}", 
                callback_data=f"category_{category.id}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🛍️ <b>Product Categories</b>\n\nChoose a category to browse:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def show_category_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show products in a category"""
        query = update.callback_query
        await query.answer()
        
        category_id = int(query.data.split('_')[1])
        
        with app.app_context():
            category = Category.query.get(category_id)
            products = Product.query.filter_by(category_id=category_id, is_active=True).limit(10).all()
        
        if not products:
            await query.edit_message_text("No products available in this category.")
            return
        
        text = f"🛍️ <b>{category.name}</b>\n\n"
        keyboard = []
        
        for product in products:
            text += f"• {product.name} - ${product.price}\n"
            keyboard.append([InlineKeyboardButton(
                f"🛒 {product.name} (${product.price})",
                callback_data=f"product_{product.id}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data="browse_products")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def show_product_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed product information"""
        query = update.callback_query
        await query.answer()
        
        product_id = int(query.data.split('_')[1])
        
        with app.app_context():
            product = Product.query.get(product_id)
        
        if not product:
            await query.edit_message_text("Product not found.")
            return
        
        text = f"""
🛍️ <b>{product.name}</b>

💰 Price: ${product.price}
📦 Stock: {product.stock_quantity} available
📝 Description: {product.description or 'No description available'}
        """
        
        keyboard = [
            [InlineKeyboardButton("🛒 Add to Cart", callback_data=f"add_cart_{product.id}")],
            [InlineKeyboardButton("🔙 Back to Category", callback_data=f"category_{product.category_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def add_to_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add product to cart"""
        query = update.callback_query
        await query.answer()
        
        product_id = int(query.data.split('_')[2])
        user_id = update.effective_user.id
        
        with app.app_context():
            product = Product.query.get(product_id)
            user = User.query.filter_by(telegram_id=user_id).first()
            
            if not product or not user:
                await query.answer("Product or user not found.", show_alert=True)
                return
            
            if product.stock_quantity <= 0:
                await query.answer("Product out of stock.", show_alert=True)
                return
            
            # Check if item already in cart
            cart_item = CartItem.query.filter_by(user_id=user.id, product_id=product_id).first()
            if cart_item:
                cart_item.quantity += 1
                quantity_text = f"Quantity updated to {cart_item.quantity}"
            else:
                cart_item = CartItem(user_id=user.id, product_id=product_id, quantity=1)
                db.session.add(cart_item)
                quantity_text = "Added to cart"
            
            db.session.commit()
            
            # Show confirmation message with options
            text = f"✅ <b>{product.name}</b> {quantity_text}!\n\n"
            text += "What would you like to do next?"
            
            keyboard = [
                [InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")],
                [InlineKeyboardButton("➕ Add Another", callback_data=f"add_cart_{product_id}")],
                [InlineKeyboardButton("🛍️ Continue Shopping", callback_data=f"category_{product.category_id}")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )

    async def view_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's cart"""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            user_id = update.effective_user.id
        else:
            user_id = update.effective_user.id
        
        with app.app_context():
            user = User.query.filter_by(telegram_id=user_id).first()
            if not user:
                message = "User not found. Please start the bot with /start"
                keyboard = [[InlineKeyboardButton("🏠 Start", callback_data="main_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
            else:
                # Join with Product to avoid detached instance errors
                cart_items = db.session.query(CartItem).join(Product).filter(
                    CartItem.user_id == user.id
                ).all()
                
                if not cart_items:
                    message = "🛒 Your cart is empty!\n\nUse /start to browse products."
                    keyboard = [[InlineKeyboardButton("🛍️ Browse Products", callback_data="browse_products")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                else:
                    total = Decimal('0')
                    text = "🛒 <b>Your Cart</b>\n\n"
                    
                    for item in cart_items:
                        item_total = item.product.price * item.quantity
                        total += item_total
                        text += f"• {item.product.name}\n"
                        text += f"  ${item.product.price} x {item.quantity} = ${item_total}\n\n"
                    
                    text += f"💰 <b>Total: ${total}</b>"
                    
                    keyboard = [
                        [InlineKeyboardButton("💳 Checkout", callback_data="checkout")],
                        [InlineKeyboardButton("🛍️ Continue Shopping", callback_data="browse_products")],
                        [InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message = text
            
            # Send response within the app context
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )

    async def clear_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear user's cart"""
        query = update.callback_query
        await query.answer()
        user_id = update.effective_user.id
        
        with app.app_context():
            user = User.query.filter_by(telegram_id=user_id).first()
            if not user:
                await query.answer("User not found.", show_alert=True)
                return
            
            # Delete all cart items for this user
            CartItem.query.filter_by(user_id=user.id).delete()
            db.session.commit()
            
            text = "🗑️ Cart cleared successfully!\n\nWhat would you like to do next?"
            keyboard = [
                [InlineKeyboardButton("🛍️ Browse Products", callback_data="browse_products")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )

    async def checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process checkout"""
        query = update.callback_query
        await query.answer()
        user_id = update.effective_user.id
        
        with app.app_context():
            user = User.query.filter_by(telegram_id=user_id).first()
            if not user:
                await query.answer("User not found.", show_alert=True)
                return
            
            # Get cart items with products
            cart_items = db.session.query(CartItem).join(Product).filter(
                CartItem.user_id == user.id
            ).all()
            
            if not cart_items:
                await query.edit_message_text(
                    "🛒 Your cart is empty! Add some products first.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🛍️ Browse Products", callback_data="browse_products")
                    ]])
                )
                return
            
            # Calculate total
            total = Decimal('0')
            for item in cart_items:
                total += item.product.price * item.quantity
            
            # Create order
            from utils import generate_order_number
            order = Order(
                order_number=generate_order_number(),
                user_id=user.id,
                total_amount=total,
                status=OrderStatus.PENDING,
                payment_status=PaymentStatus.WAITING
            )
            db.session.add(order)
            db.session.flush()  # Get the order ID
            
            # Create order items
            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                db.session.add(order_item)
            
            # Clear cart
            CartItem.query.filter_by(user_id=user.id).delete()
            db.session.commit()
            
            # Show checkout confirmation
            text = f"📋 <b>Order Created!</b>\n\n"
            text += f"Order #: <code>{order.order_number}</code>\n"
            text += f"Total: <b>${total}</b>\n\n"
            text += "🔄 <i>Setting up payment...</i>\n\n"
            text += "Choose your payment method:"
            
            keyboard = [
                [InlineKeyboardButton("💰 Pay with Crypto", callback_data=f"pay_crypto_{order.id}")],
                [InlineKeyboardButton("📄 Order Details", callback_data=f"order_details_{order.id}")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )

    async def my_orders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's orders"""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            user_id = update.effective_user.id
        else:
            user_id = update.effective_user.id
        
        with app.app_context():
            user = User.query.filter_by(telegram_id=user_id).first()
            if not user:
                message = "User not found. Please start the bot with /start"
                keyboard = [[InlineKeyboardButton("🏠 Start", callback_data="main_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
            else:
                orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).limit(10).all()
                
                if not orders:
                    message = "📦 No orders found!\n\nStart shopping to create your first order."
                    keyboard = [[InlineKeyboardButton("🛍️ Browse Products", callback_data="browse_products")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                else:
                    text = "📦 <b>Your Orders</b>\n\n"
                    keyboard = []
                    
                    for order in orders:
                        status_emoji = "⏳" if order.status == OrderStatus.PENDING else "✅" if order.status == OrderStatus.DELIVERED else "🔄"
                        text += f"{status_emoji} Order #{order.order_number}\n"
                        text += f"   ${order.total_amount} - {order.status.value.title()}\n\n"
                        
                        keyboard.append([InlineKeyboardButton(
                            f"📋 Order #{order.order_number}", 
                            callback_data=f"order_details_{order.id}"
                        )])
                    
                    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message = text
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )

    async def show_order_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed order information"""
        query = update.callback_query
        await query.answer()
        
        order_id = int(query.data.split('_')[2])
        user_id = update.effective_user.id
        
        with app.app_context():
            user = User.query.filter_by(telegram_id=user_id).first()
            order = Order.query.filter_by(id=order_id, user_id=user.id).first()
            
            if not order:
                await query.answer("Order not found.", show_alert=True)
                return
            
            text = f"📋 <b>Order Details</b>\n\n"
            text += f"Order #: <code>{order.order_number}</code>\n"
            text += f"Status: <b>{order.status.value.title()}</b>\n"
            text += f"Payment: <b>{order.payment_status.value.title()}</b>\n"
            text += f"Total: <b>${order.total_amount}</b>\n"
            text += f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            text += "<b>Items:</b>\n"
            for item in order.items:
                text += f"• {item.product.name}\n"
                text += f"  ${item.price} x {item.quantity} = ${item.price * item.quantity}\n"
            
            keyboard = [
                [InlineKeyboardButton("📦 All Orders", callback_data="my_orders")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]
            
            # Add payment button if order is pending
            if order.payment_status == PaymentStatus.WAITING:
                keyboard.insert(0, [InlineKeyboardButton("💰 Pay Now", callback_data=f"pay_crypto_{order.id}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )

    async def pay_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle crypto payment"""
        query = update.callback_query
        await query.answer()
        
        order_id = int(query.data.split('_')[2])
        user_id = update.effective_user.id
        
        with app.app_context():
            user = User.query.filter_by(telegram_id=user_id).first()
            order = Order.query.filter_by(id=order_id, user_id=user.id).first()
            
            if not order:
                await query.answer("Order not found.", show_alert=True)
                return
            
            # Check if payment already exists
            if order.payment_id:
                # Get current payment details from NowPayments
                from payments import get_payment_status
                payment_details = get_payment_status(order.payment_id)
                
                text = f"💰 <b>Existing Payment</b>\n\n"
                text += f"Order #: <code>{order.order_number}</code>\n"
                text += f"Amount: <b>${order.total_amount} USD</b>\n"
                text += f"Status: <b>{order.payment_status.value.title()}</b>\n\n"
                
                if payment_details and order.payment_status == PaymentStatus.WAITING:
                    pay_currency = payment_details.get('pay_currency', 'BTC').upper()
                    pay_amount = payment_details.get('pay_amount', 'TBD')
                    pay_address = payment_details.get('pay_address')
                    
                    text += f"<b>💳 Payment Details:</b>\n"
                    text += f"Currency: <code>{pay_currency}</code>\n"
                    text += f"Amount: <code>{pay_amount}</code>\n\n"
                    
                    if pay_address:
                        text += f"<b>📍 Payment Address:</b>\n"
                        text += f"<code>{pay_address}</code>\n\n"
                        text += f"<b>📱 Send Payment:</b>\n"
                        text += f"Send exactly <code>{pay_amount} {pay_currency}</code>\n"
                        text += f"To: <code>{pay_address}</code>\n\n"
                
                if order.invoice_url:
                    text += f"🔗 <a href='{order.invoice_url}'>Open Payment Page</a>\n\n"
                
                text += "⏰ Payment expires in 30 minutes from creation"
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Check Payment Status", callback_data=f"check_payment_{order.id}")],
                    [InlineKeyboardButton("📋 Order Details", callback_data=f"order_details_{order.id}")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                ]
            else:
                # Create payment with NowPayments
                from payments import create_payment
                payment_result = await create_payment(order)
                
                if payment_result['success']:
                    # Update order with payment info
                    order.payment_id = payment_result['payment_id']
                    order.invoice_url = payment_result.get('invoice_url')
                    db.session.commit()
                    
                    text = f"💰 <b>Crypto Payment Ready</b>\n\n"
                    text += f"Order #: <code>{order.order_number}</code>\n"
                    text += f"Amount: <b>${order.total_amount} USD</b>\n\n"
                    
                    # Show payment details
                    pay_currency = payment_result.get('pay_currency', 'BTC').upper()
                    pay_amount = payment_result.get('pay_amount', 'TBD')
                    pay_address = payment_result.get('pay_address')
                    
                    text += f"<b>💳 Payment Details:</b>\n"
                    text += f"Currency: <code>{pay_currency}</code>\n"
                    text += f"Amount: <code>{pay_amount}</code>\n\n"
                    
                    if pay_address:
                        text += f"<b>📍 Payment Address:</b>\n"
                        text += f"<code>{pay_address}</code>\n\n"
                        text += f"<b>📱 Instructions:</b>\n"
                        text += f"1. Send exactly <code>{pay_amount} {pay_currency}</code>\n"
                        text += f"2. To address: <code>{pay_address}</code>\n"
                        text += f"3. Payment will be confirmed automatically\n\n"
                    
                    if payment_result.get('invoice_url'):
                        text += f"🔗 <a href='{payment_result['invoice_url']}'>Open Payment Page</a>\n\n"
                    
                    text += "⏰ <b>Important:</b> Payment expires in 30 minutes\n"
                    text += "🔄 Use 'Check Status' to see payment confirmation"
                    
                    keyboard = [
                        [InlineKeyboardButton("🔄 Check Payment Status", callback_data=f"check_payment_{order.id}")],
                        [InlineKeyboardButton("📋 Order Details", callback_data=f"order_details_{order.id}")],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                    ]
                else:
                    text = f"❌ <b>Payment Creation Failed</b>\n\n"
                    text += f"Error: {payment_result.get('error', 'Unknown error')}\n\n"
                    text += "Please try again or contact support."
                    
                    keyboard = [
                        [InlineKeyboardButton("🔄 Try Again", callback_data=f"pay_crypto_{order.id}")],
                        [InlineKeyboardButton("📋 Order Details", callback_data=f"order_details_{order.id}")],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
                    ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )

    async def check_payment_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check payment status from NowPayments"""
        query = update.callback_query
        await query.answer()
        
        order_id = int(query.data.split('_')[2])
        user_id = update.effective_user.id
        
        with app.app_context():
            user = User.query.filter_by(telegram_id=user_id).first()
            order = Order.query.filter_by(id=order_id, user_id=user.id).first()
            
            if not order or not order.payment_id:
                await query.answer("Payment not found.", show_alert=True)
                return
            
            # Get payment status from NowPayments
            from payments import get_payment_status
            payment_status = get_payment_status(order.payment_id)
            
            if payment_status:
                # Update local payment status
                try:
                    new_status = PaymentStatus(payment_status['payment_status'].lower())
                    order.payment_status = new_status
                    
                    if new_status == PaymentStatus.FINISHED:
                        order.status = OrderStatus.CONFIRMED
                    elif new_status in [PaymentStatus.FAILED, PaymentStatus.EXPIRED]:
                        order.status = OrderStatus.CANCELLED
                    
                    db.session.commit()
                    
                    text = f"🔄 <b>Payment Status Updated</b>\n\n"
                    text += f"Order #: <code>{order.order_number}</code>\n"
                    text += f"Payment Status: <b>{new_status.value.title()}</b>\n"
                    text += f"Order Status: <b>{order.status.value.title()}</b>\n\n"
                    
                    if new_status == PaymentStatus.FINISHED:
                        text += "🎉 Payment confirmed! Your order is being processed."
                    elif new_status == PaymentStatus.WAITING:
                        text += "⏰ Waiting for payment confirmation..."
                    elif new_status == PaymentStatus.CONFIRMING:
                        text += "🔄 Payment is being confirmed..."
                    elif new_status in [PaymentStatus.FAILED, PaymentStatus.EXPIRED]:
                        text += "❌ Payment failed or expired. Please try again."
                    
                except ValueError:
                    text = f"❌ <b>Unknown Payment Status</b>\n\n"
                    text += f"Status received: {payment_status.get('payment_status', 'unknown')}"
            else:
                text = f"❌ <b>Unable to Check Payment Status</b>\n\n"
                text += "Please try again later or contact support."
            
            keyboard = [
                [InlineKeyboardButton("📋 Order Details", callback_data=f"order_details_{order.id}")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]
            
            # Add payment retry option if failed
            if order.payment_status in [PaymentStatus.FAILED, PaymentStatus.EXPIRED]:
                keyboard.insert(0, [InlineKeyboardButton("💰 Try Payment Again", callback_data=f"pay_crypto_{order.id}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )

    async def simulate_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Simulate successful payment"""
        query = update.callback_query
        await query.answer()
        
        order_id = int(query.data.split('_')[2])
        user_id = update.effective_user.id
        
        with app.app_context():
            user = User.query.filter_by(telegram_id=user_id).first()
            order = Order.query.filter_by(id=order_id, user_id=user.id).first()
            
            if not order:
                await query.answer("Order not found.", show_alert=True)
                return
            
            # Update order status
            order.payment_status = PaymentStatus.CONFIRMED
            order.status = OrderStatus.CONFIRMED
            db.session.commit()
            
            text = f"🎉 <b>Payment Successful!</b>\n\n"
            text += f"Order #: <code>{order.order_number}</code>\n"
            text += f"Amount: <b>${order.total_amount}</b>\n"
            text += f"Status: <b>Confirmed & Paid</b>\n\n"
            text += "✅ Your order has been confirmed!\n"
            text += "📦 We'll process and ship your items soon.\n"
            text += "📧 You'll receive updates on your order status."
            
            keyboard = [
                [InlineKeyboardButton("📋 Order Details", callback_data=f"order_details_{order.id}")],
                [InlineKeyboardButton("📦 My Orders", callback_data="my_orders")],
                [InlineKeyboardButton("🛍️ Continue Shopping", callback_data="browse_products")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        help_text = f"""
🤖 <b>{Config.SHOP_NAME} Help</b>

<b>Available Commands:</b>
/start - Main menu
/cart - View your cart
/orders - View your orders
/help - Show this help

<b>How to shop:</b>
1. Browse products by category
2. Add items to your cart
3. Checkout and pay with crypto
4. Track your order status

<b>Support:</b> {Config.SUPPORT_CONTACT}
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                help_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                help_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )

    async def main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Return to main menu"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("🛍️ Browse Products", callback_data="browse_products")],
            [InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")],
            [InlineKeyboardButton("📦 My Orders", callback_data="my_orders")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🤖 <b>Welcome to {Config.SHOP_NAME}</b>\n\nWhat would you like to do?",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        
        if query.data == "browse_products":
            await self.browse_products(update, context)
        elif query.data.startswith("category_"):
            await self.show_category_products(update, context)
        elif query.data.startswith("product_"):
            await self.show_product_details(update, context)
        elif query.data.startswith("add_cart_"):
            await self.add_to_cart(update, context)
        elif query.data == "view_cart":
            await self.view_cart(update, context)
        elif query.data == "clear_cart":
            await self.clear_cart(update, context)
        elif query.data == "checkout":
            await self.checkout(update, context)
        elif query.data == "my_orders":
            await self.my_orders(update, context)
        elif query.data.startswith("order_details_"):
            await self.show_order_details(update, context)
        elif query.data.startswith("pay_crypto_"):
            await self.pay_crypto(update, context)
        elif query.data.startswith("check_payment_"):
            await self.check_payment_status(update, context)
        elif query.data.startswith("simulate_payment_"):
            await self.simulate_payment(update, context)
        elif query.data == "help":
            await self.help_command(update, context)
        elif query.data == "main_menu":
            await self.main_menu(update, context)
        elif query.data == "admin_panel":
            await self.admin_panel(update, context)
        elif query.data == "admin_add_product":
            await self.admin_add_product_start(update, context)
        elif query.data == "admin_manage_products":
            await self.admin_manage_products(update, context)
        elif query.data == "admin_manage_categories":
            await self.admin_manage_categories(update, context)

    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin panel"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        if user.id not in Config.ADMIN_TELEGRAM_IDS:
            await query.edit_message_text("⛔ Access denied. Admin only.")
            return
        
        keyboard = [
            [InlineKeyboardButton("➕ Add Product", callback_data="admin_add_product")],
            [InlineKeyboardButton("📦 Manage Products", callback_data="admin_manage_products")],
            [InlineKeyboardButton("📂 Manage Categories", callback_data="admin_manage_categories")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        with app.app_context():
            total_products = Product.query.count()
            active_products = Product.query.filter_by(is_active=True).count()
            total_categories = Category.query.count()
            total_orders = Order.query.count()
        
        admin_text = f"""
🔧 <b>Admin Panel</b>

📊 <b>Statistics:</b>
• Products: {active_products}/{total_products} active
• Categories: {total_categories}
• Orders: {total_orders}

What would you like to do?
        """
        
        await query.edit_message_text(
            admin_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def admin_add_product_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start adding a new product"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        if user.id not in Config.ADMIN_TELEGRAM_IDS:
            await query.edit_message_text("⛔ Access denied. Admin only.")
            return
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "➕ <b>Add New Product</b>\n\n"
            "Please send the product details in this format:\n\n"
            "<code>Name: Product Name\n"
            "Description: Product description\n"
            "Price: 99.99\n"
            "Stock: 100\n"
            "Category: Category Name</code>\n\n"
            "Send all the information in one message.",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        # Store the user's state for product creation
        context.user_data['admin_adding_product'] = True
    
    async def handle_product_addition(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text message for adding a new product"""
        user = update.effective_user
        if user.id not in Config.ADMIN_TELEGRAM_IDS:
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return
        
        # Check if message contains product format (Name:, Description:, etc.)
        text = update.message.text
        required_patterns = ['Name:', 'Description:', 'Price:', 'Stock:', 'Category:']
        if not all(pattern in text for pattern in required_patterns):
            # This is not a product addition message, ignore it
            return
        
        logger.info(f"Processing product addition text: {text}")
        
        try:
            # Parse the product details from the text
            lines = text.strip().split('\n')
            product_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    product_data[key] = value
            
            # Validate required fields
            required_fields = ['name', 'description', 'price', 'stock', 'category']
            missing_fields = [field for field in required_fields if field not in product_data]
            
            if missing_fields:
                await update.message.reply_text(
                    f"❌ <b>Missing fields:</b> {', '.join(missing_fields)}\n\n"
                    "Please use this format:\n\n"
                    "<code>Name: Product Name\n"
                    "Description: Product description\n"
                    "Price: 99.99\n"
                    "Stock: 100\n"
                    "Category: Category Name</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            
            # Validate and convert numeric fields
            try:
                price = float(product_data['price'])
                stock = int(product_data['stock'])
            except ValueError:
                await update.message.reply_text(
                    "❌ <b>Error:</b> Price must be a number and Stock must be an integer.\n\n"
                    "Example: Price: 99.99, Stock: 100",
                    parse_mode=ParseMode.HTML
                )
                return
            
            # Find or create category
            category_name = product_data['category']
            category = Category.query.filter_by(name=category_name).first()
            
            if not category:
                # Create new category
                category = Category(
                    name=category_name,
                    description=f"Auto-created category for {category_name}",
                    is_active=True
                )
                db.session.add(category)
                db.session.flush()  # Get the category ID
                logger.info(f"Created new category: {category_name}")
            
            # Create the product
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                price=price,
                stock_quantity=stock,
                category_id=category.id,
                is_active=True
            )
            
            db.session.add(product)
            db.session.commit()
            
            # Send success message
            keyboard = [
                [InlineKeyboardButton("➕ Add Another Product", callback_data="admin_add_product")],
                [InlineKeyboardButton("📦 View Products", callback_data="admin_manage_products")],
                [InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ <b>Product Added Successfully!</b>\n\n"
                f"📦 <b>{product.name}</b>\n"
                f"💰 Price: ${product.price}\n"
                f"📊 Stock: {product.stock_quantity}\n"
                f"📂 Category: {category.name}\n"
                f"📝 Description: {product.description}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            
            logger.info(f"Product added successfully: {product.name}")
            
        except Exception as e:
            logger.error(f"Error adding product: {str(e)}")
            await update.message.reply_text(
                f"❌ <b>Error adding product:</b>\n{str(e)}\n\n"
                "Please try again with the correct format.",
                parse_mode=ParseMode.HTML
            )
    
    async def admin_manage_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show product management interface"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        if user.id not in Config.ADMIN_TELEGRAM_IDS:
            await query.edit_message_text("⛔ Access denied. Admin only.")
            return
        
        with app.app_context():
            products = Product.query.order_by(Product.created_at.desc()).limit(10).all()
        
        if not products:
            keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📦 <b>Manage Products</b>\n\nNo products found.",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            return
        
        keyboard = []
        product_text = "📦 <b>Recent Products</b>\n\n"
        
        for product in products:
            status = "✅" if product.is_active else "❌"
            product_text += f"{status} <b>{product.name}</b>\n"
            product_text += f"   💰 ${product.price} | 📦 {product.stock_quantity} in stock\n\n"
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            product_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def admin_manage_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show category management interface"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        if user.id not in Config.ADMIN_TELEGRAM_IDS:
            await query.edit_message_text("⛔ Access denied. Admin only.")
            return
        
        with app.app_context():
            categories = Category.query.all()
        
        keyboard = []
        if categories:
            category_text = "📂 <b>Categories</b>\n\n"
            for category in categories:
                status = "✅" if category.is_active else "❌"
                product_count = Product.query.filter_by(category_id=category.id).count()
                category_text += f"{status} <b>{category.name}</b> ({product_count} products)\n"
        else:
            category_text = "📂 <b>Categories</b>\n\nNo categories found."
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            category_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages for admin product creation"""
        user = update.effective_user
        
        # Check if user is admin and in product creation mode
        if user.id in Config.ADMIN_TELEGRAM_IDS and context.user_data.get('admin_adding_product'):
            await self.process_product_creation(update, context)
            return
        
        # Default response for non-admin messages
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👋 Hi! Use the /start command to see the main menu.",
            reply_markup=reply_markup
        )
    
    async def process_product_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process product creation from admin message"""
        text = update.message.text
        
        try:
            # Parse product details from the message
            lines = text.strip().split('\n')
            product_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'name':
                        product_data['name'] = value
                    elif key == 'description':
                        product_data['description'] = value
                    elif key == 'price':
                        product_data['price'] = float(value)
                    elif key == 'stock':
                        product_data['stock'] = int(value)
                    elif key == 'category':
                        product_data['category'] = value
            
            # Validate required fields
            required_fields = ['name', 'description', 'price', 'stock', 'category']
            missing_fields = [field for field in required_fields if field not in product_data]
            
            if missing_fields:
                await update.message.reply_text(
                    f"❌ Missing required fields: {', '.join(missing_fields)}\n\n"
                    "Please send the product details again with all required fields."
                )
                return
            
            # Create or get category
            with app.app_context():
                category = Category.query.filter_by(name=product_data['category']).first()
                if not category:
                    category = Category(name=product_data['category'], is_active=True)
                    db.session.add(category)
                    db.session.flush()  # Get the ID
                
                # Create product
                product = Product(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    stock_quantity=product_data['stock'],
                    category_id=category.id,
                    is_active=True
                )
                
                db.session.add(product)
                db.session.commit()
                
                success_text = f"""
✅ <b>Product Created Successfully!</b>

📦 <b>{product.name}</b>
💰 Price: ${product.price}
📝 Description: {product.description}
📦 Stock: {product.stock_quantity}
📂 Category: {category.name}
                """
                
                keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    success_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
                
                # Clear the product creation state
                context.user_data['admin_adding_product'] = False
                
        except ValueError as e:
            await update.message.reply_text(
                f"❌ Error in price or stock format. Please use numbers.\n\n"
                "Example:\n"
                "Price: 99.99\n"
                "Stock: 100"
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error creating product: {str(e)}\n\n"
                "Please try again with the correct format."
            )

    def setup_handlers(self):
        """Setup bot handlers"""
        from telegram.ext import MessageHandler, filters
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("cart", self.view_cart))
        self.application.add_handler(CommandHandler("orders", self.my_orders))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def get_application(self):
        """Get the bot application for webhook mode"""
        if not self.application:
            self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
            self.setup_handlers()
        return self.application
        
    async def init_for_webhook(self):
        """Initialize the application for webhook mode"""
        if self.application:
            await self.application.initialize()
            await self.application.start()
        
    async def run_bot(self):
        """Run the bot in polling mode (for testing)"""
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
        
        await self.application.initialize()
        await self.application.start()
        
        # Use polling for development/testing
        await self.application.updater.start_polling()
        logger.info("Bot started with polling...")
        
        # Keep the bot running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped")
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

# Global bot instance for standalone mode
working_bot = TelegramBot()

def start_working_bot():
    """Start the working bot"""
    asyncio.run(working_bot.run_bot())

if __name__ == "__main__":
    start_working_bot()