import requests
import logging
import os
from config import Config
from models import Payment, PaymentStatus
from app import app, db

logger = logging.getLogger(__name__)

class NowPaymentsAPI:
    def __init__(self):
        self.api_key = Config.NOWPAYMENTS_API_KEY
        self.base_url = Config.NOWPAYMENTS_BASE_URL
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

    def get_available_currencies(self):
        """Get list of available currencies"""
        try:
            response = requests.get(f"{self.base_url}/currencies", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting currencies: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exception getting currencies: {str(e)}")
            return None

    def get_minimum_payment_amount(self, currency_from, currency_to):
        """Get minimum payment amount for currency pair"""
        try:
            url = f"{self.base_url}/min-amount"
            params = {
                'currency_from': currency_from,
                'currency_to': currency_to
            }
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting min amount: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exception getting min amount: {str(e)}")
            return None

    def create_payment(self, order):
        """Create a payment"""
        try:
            payment_data = {
                'price_amount': float(order.total_amount),
                'price_currency': 'USD',
                'pay_currency': 'btc',  # Default to Bitcoin, can be made configurable
                'order_id': order.order_number,
                'order_description': f'Order #{order.order_number} from {Config.SHOP_NAME}',
                'ipn_callback_url': f"https://{os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')}/payment-webhook",
                'success_url': f"https://{os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')}/payment-success",
                'cancel_url': f"https://{os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')}/payment-cancel"
            }
            
            response = requests.post(
                f"{self.base_url}/payment",
                headers=self.headers,
                json=payment_data
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Error creating payment: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception creating payment: {str(e)}")
            return None

    def get_payment_status(self, payment_id):
        """Get payment status"""
        try:
            response = requests.get(
                f"{self.base_url}/payment/{payment_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting payment status: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception getting payment status: {str(e)}")
            return None

# Initialize the API client
nowpayments = NowPaymentsAPI()

async def create_payment(order):
    """Create a payment for an order"""
    try:
        # Create payment with NowPayments
        payment_response = nowpayments.create_payment(order)
        
        if not payment_response:
            return {
                'success': False,
                'error': 'Failed to create payment with NowPayments'
            }
        
        # Save payment record
        payment = Payment(
            payment_id=payment_response['payment_id'],
            order_id=order.id,
            amount=order.total_amount,
            currency='USD',
            pay_currency=payment_response.get('pay_currency', 'btc'),
            status=PaymentStatus.WAITING,
            invoice_url=payment_response.get('invoice_url')
        )
        
        with app.app_context():
            db.session.add(payment)
            db.session.commit()
        
        return {
            'success': True,
            'payment_id': payment_response['payment_id'],
            'invoice_url': payment_response.get('invoice_url'),
            'pay_address': payment_response.get('pay_address'),
            'pay_amount': payment_response.get('pay_amount'),
            'pay_currency': payment_response.get('pay_currency')
        }
        
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def process_payment_webhook(webhook_data):
    """Process payment webhook from NowPayments"""
    try:
        payment_id = webhook_data.get('payment_id')
        payment_status = webhook_data.get('payment_status')
        order_id = webhook_data.get('order_id')
        
        logger.info(f"Processing webhook for payment {payment_id}, status: {payment_status}")
        
        # Find the payment record
        payment = Payment.query.filter_by(payment_id=payment_id).first()
        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return False
        
        # Update payment status
        try:
            payment.status = PaymentStatus(payment_status.lower())
        except ValueError:
            logger.error(f"Unknown payment status: {payment_status}")
            return False
        
        # Update order status based on payment status
        from models import OrderStatus
        order = payment.order
        if payment.status == PaymentStatus.FINISHED:
            order.payment_status = PaymentStatus.FINISHED
            order.status = OrderStatus.CONFIRMED if order.status == OrderStatus.PENDING else order.status
            
            # Reduce stock for order items
            for item in order.items:
                if item.product.stock_quantity >= item.quantity:
                    item.product.stock_quantity -= item.quantity
                else:
                    logger.warning(f"Insufficient stock for product {item.product.name}")
        
        elif payment.status in [PaymentStatus.FAILED, PaymentStatus.EXPIRED]:
            order.payment_status = payment.status
            if order.status == OrderStatus.PENDING:
                order.status = OrderStatus.CANCELLED
        
        elif payment.status == PaymentStatus.PARTIALLY_PAID:
            order.payment_status = PaymentStatus.PARTIALLY_PAID
        
        with app.app_context():
            db.session.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        return False

def get_payment_status(payment_id):
    """Get current payment status from NowPayments"""
    return nowpayments.get_payment_status(payment_id)
