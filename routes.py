import os
import hmac
import hashlib
import json
import logging
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from app import app, db
from models import *
from payments import process_payment_webhook
from bot import handle_telegram_webhook
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

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Handle Telegram webhook"""
    try:
        update = request.get_json()
        if update:
            # Process the update asynchronously
            import asyncio
            asyncio.create_task(handle_telegram_webhook(update))
        return '', 200
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {str(e)}")
        return '', 500

@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    """Handle NowPayments webhook"""
    try:
        # Verify webhook signature if secret is provided
        if Config.NOWPAYMENTS_IPN_SECRET:
            signature = request.headers.get('x-nowpayments-sig')
            if not signature:
                logger.error("Missing webhook signature")
                return '', 400
            
            payload = request.get_data()
            expected_sig = hmac.new(
                Config.NOWPAYMENTS_IPN_SECRET.encode(),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_sig):
                logger.error("Invalid webhook signature")
                return '', 400
        
        webhook_data = request.get_json()
        if process_payment_webhook(webhook_data):
            return '', 200
        else:
            return '', 400
            
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        return '', 500

@app.route('/payment-success')
def payment_success():
    """Payment success page"""
    return render_template('payment_success.html')

@app.route('/payment-cancel')
def payment_cancel():
    """Payment cancel page"""
    return render_template('payment_cancel.html')

# Admin routes
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

@app.route('/admin/products/<int:product_id>/edit', methods=['POST'])
def admin_edit_product(product_id):
    """Edit product"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        product = Product.query.get_or_404(product_id)
        
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock_quantity = int(request.form.get('stock_quantity', 0))
        product.category_id = int(request.form.get('category_id')) if request.form.get('category_id') else None
        product.image_url = request.form.get('image_url')
        product.is_active = bool(request.form.get('is_active'))
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating product: {str(e)}', 'error')
        logger.error(f"Error updating product: {str(e)}")
    
    return redirect(url_for('admin_products'))

@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
def admin_delete_product(product_id):
    """Delete product"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
        logger.error(f"Error deleting product: {str(e)}")
    
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
def admin_orders():
    """Admin orders management"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')
    per_page = 20
    
    query = Order.query
    
    if status_filter and status_filter != 'all':
        try:
            status_enum = OrderStatus(status_filter)
            query = query.filter_by(status=status_enum)
        except ValueError:
            pass
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/orders.html', 
                         orders=orders, 
                         current_status=status_filter,
                         order_statuses=OrderStatus,
                         format_currency=format_currency)

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
def admin_update_order_status(order_id):
    """Update order status"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        order = Order.query.get_or_404(order_id)
        new_status = request.form.get('status')
        
        order.status = OrderStatus(new_status)
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Order status updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating order status: {str(e)}', 'error')
        logger.error(f"Error updating order status: {str(e)}")
    
    return redirect(url_for('admin_orders'))

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

@app.route('/api/orders/<int:order_id>')
def api_order_details(order_id):
    """API endpoint for order details"""
    if not session.get('admin_authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    order = Order.query.get_or_404(order_id)
    
    return jsonify({
        'id': order.id,
        'order_number': order.order_number,
        'customer': {
            'name': f"{order.customer.first_name or ''} {order.customer.last_name or ''}".strip(),
            'username': order.customer.username,
            'telegram_id': order.customer.telegram_id
        },
        'total_amount': float(order.total_amount),
        'status': order.status.value,
        'payment_status': order.payment_status.value,
        'created_at': order.created_at.isoformat(),
        'items': [{
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': float(item.price),
            'total': float(item.price) * item.quantity
        } for item in order.items]
    })
