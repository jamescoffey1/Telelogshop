import random
import string
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for

def generate_order_number():
    """Generate a unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{timestamp}-{random_suffix}"

def format_currency(amount, currency='USD'):
    """Format currency amount"""
    if currency == 'USD':
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_cart_total(cart_items):
    """Calculate total amount for cart items"""
    total = 0
    for item in cart_items:
        total += float(item.product.price) * item.quantity
    return total

def get_order_status_color(status):
    """Get Bootstrap color class for order status"""
    color_map = {
        'pending': 'warning',
        'confirmed': 'info',
        'paid': 'success',
        'shipped': 'primary',
        'delivered': 'success',
        'cancelled': 'danger'
    }
    return color_map.get(status.lower(), 'secondary')

def get_payment_status_color(status):
    """Get Bootstrap color class for payment status"""
    color_map = {
        'waiting': 'warning',
        'confirming': 'info',
        'confirmed': 'success',
        'finished': 'success',
        'failed': 'danger',
        'expired': 'danger',
        'partially_paid': 'warning'
    }
    return color_map.get(status.lower(), 'secondary')

def truncate_text(text, length=50):
    """Truncate text to specified length"""
    if not text:
        return ''
    return text[:length] + '...' if len(text) > length else text
