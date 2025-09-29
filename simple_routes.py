import os
import logging
import asyncio
import json
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from app import app, db
from models import *
from config import Config
from utils import admin_required, format_currency
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main landing page"""
    with app.app_context():
        total_products = Product.query.filter_by(is_active=True).count()
        categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('base.html', 
                         total_products=total_products, 
                         categories=categories,
                         shop_name=Config.SHOP_NAME)

def register_routes(app)

@app.route(f'/telegram-webhook/{Config.WEBHOOK_SECRET}', methods=['POST'])
def telegram_webhook():
    """Handle Telegram webhook"""
    try:
        update_data = request.get_json()
        if not update_data:
            logger.error("No update data received")
            return '', 400
            
        logger.debug(f"Received webhook update: {update_data}")
        
        # Get the global bot application
        from app import bot_application
        if not bot_application:
            logger.error("Bot application not initialized")
            return '', 500
            
        # Process the update using the initialized bot application
        import asyncio
        from telegram import Update
        
        # Parse the update
        update = Update.de_json(update_data, bot_application.bot)
        
        if update:
            # Schedule the update processing on the bot's persistent loop
            from app import bot_loop
            if bot_loop and not bot_loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    bot_application.process_update(update), 
                    bot_loop
                )
                logger.debug("Successfully scheduled webhook update processing")
            else:
                logger.error("Bot loop is not available or closed")
                return '', 500
        else:
            logger.warning("Could not parse update")
        
        return '', 200
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return '', 500

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    # Get statistics
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
    paid_orders = Order.query.filter_by(payment_status=PaymentStatus.FINISHED).count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status=PaymentStatus.FINISHED).scalar() or 0
    
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    low_stock_products = Product.query.filter(Product.stock_quantity <= 5).count()
    
    total_users = User.query.count()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    # Sales data for last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    daily_sales = db.session.query(
        db.func.date(Order.created_at).label('date'),
        db.func.sum(Order.total_amount).label('revenue'),
        db.func.count(Order.id).label('orders')
    ).filter(
        Order.created_at >= week_ago,
        Order.payment_status == PaymentStatus.FINISHED
    ).group_by(db.func.date(Order.created_at)).all()
    
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         paid_orders=paid_orders,
                         total_revenue=total_revenue,
                         total_products=total_products,
                         active_products=active_products,
                         low_stock_products=low_stock_products,
                         total_users=total_users,
                         recent_orders=recent_orders,
                         daily_sales=daily_sales,
                         format_currency=format_currency)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        password = request.form.get('password')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        if password == admin_password:
            session['admin_authenticated'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/products')
def admin_products():
    """Admin products management"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    products = Product.query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    categories = Category.query.all()
    
    return render_template('admin/products.html', 
                         products=products, 
                         categories=categories,
                         format_currency=format_currency)

@app.route('/admin/products/add', methods=['POST'])
def admin_add_product():
    """Add new product"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            stock_quantity=int(request.form.get('stock_quantity', 0)),
            category_id=int(request.form.get('category_id')) if request.form.get('category_id') else None,
            image_url=request.form.get('image_url'),
            is_active=bool(request.form.get('is_active'))
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding product: {str(e)}', 'error')
        logger.error(f"Error adding product: {str(e)}")
    
    return redirect(url_for('admin_products'))

@app.route('/admin/categories')
def admin_categories():
    """Admin categories management"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['POST'])
def admin_add_category():
    """Add new category"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        category = Category(
            name=request.form.get('name'),
            description=request.form.get('description'),
            is_active=bool(request.form.get('is_active'))
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding category: {str(e)}', 'error')
        logger.error(f"Error adding category: {str(e)}")
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/orders')
def admin_orders():
    """Admin orders management"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    orders = Order.query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/orders.html', 
                         orders=orders,
                         format_currency=format_currency)

@app.route('/webhook/setup', methods=['POST'])
def setup_webhook():
    """Setup webhook with Telegram"""
    try:
        # Get the webhook URL
        webhook_url = request.json.get('webhook_url')
        if not webhook_url:
            # Auto-detect from environment
            domain = os.environ.get('RAILWAY_STATIC_URL') or os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
            if domain:
                webhook_url = f"https://{domain}/telegram-webhook/{Config.WEBHOOK_SECRET}"
            else:
                return jsonify({'error': 'No webhook URL provided or detected'}), 400
        
        # Setup webhook asynchronously
        import asyncio
        import threading
        from working_bot import working_bot
        
        result = {'success': False, 'error': None}
        
        def setup_webhook_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(working_bot.setup_webhook(webhook_url))
                result['success'] = success
                if not success:
                    result['error'] = 'Failed to set webhook'
            except Exception as e:
                result['error'] = str(e)
            finally:
                loop.close()
        
        thread = threading.Thread(target=setup_webhook_async)
        thread.start()
        thread.join(timeout=10)  # Wait up to 10 seconds
        
        if result['success']:
            return jsonify({'success': True, 'webhook_url': webhook_url})
        else:
            return jsonify({'error': result['error'] or 'Timeout setting webhook'}), 500
            
    except Exception as e:
        logger.error(f"Error setting up webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/delete', methods=['POST'])
def delete_webhook():
    """Delete webhook from Telegram"""
    try:
        import asyncio
        import threading
        from working_bot import working_bot
        
        result = {'success': False, 'error': None}
        
        def delete_webhook_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(working_bot.delete_webhook())
                result['success'] = success
                if not success:
                    result['error'] = 'Failed to delete webhook'
            except Exception as e:
                result['error'] = str(e)
            finally:
                loop.close()
        
        thread = threading.Thread(target=delete_webhook_async)
        thread.start()
        thread.join(timeout=10)  # Wait up to 10 seconds
        
        if result['success']:
            return jsonify({'success': True})
        else:
            return jsonify({'error': result['error'] or 'Timeout deleting webhook'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        return jsonify({'error': str(e)}), 500
