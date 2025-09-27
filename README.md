# Telegram Shop Bot with Crypto Payments

A comprehensive e-commerce Telegram bot that accepts cryptocurrency payments via NowPayments, featuring a complete product catalog, shopping cart, order management, and admin dashboard.

## Features

### 🛍️ Shop Features
- Product catalog organized by categories
- Shopping cart functionality
- Inventory management with stock tracking
- Order processing and status updates
- User account management

### 💳 Payment Integration
- Cryptocurrency payments via NowPayments API
- Support for Bitcoin, Ethereum, and 100+ cryptocurrencies
- Real-time payment status tracking
- Automatic order completion on payment confirmation
- Webhook integration for payment updates

### 🤖 Telegram Bot Interface
- Interactive product browsing
- Add/remove items from cart
- Secure checkout process
- Order history and tracking
- Admin commands for shop management

### 🔧 Admin Dashboard
- Web-based admin panel
- Product and category management
- Order tracking and fulfillment
- Sales analytics and reporting
- User management

### 🔐 Security Features
- Environment-based configuration
- Secure session management
- Input validation and sanitization
- Admin authentication
- Database connection pooling

## Quick Start

### 1. Environment Setup

Create a `.env` file with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/shopbot

# Flask Configuration
SECRET_KEY=your-secret-key-here
SESSION_SECRET=your-session-secret-here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://yourapp.replit.app/telegram/webhook

# NowPayments Configuration
NOWPAYMENTS_API_KEY=your-nowpayments-api-key
NOWPAYMENTS_IPN_SECRET=your-ipn-secret-key

# Admin Configuration
ADMIN_PASSWORD=your-admin-password
ADMIN_TELEGRAM_IDS=123456789,987654321

# Shop Configuration
SHOP_NAME=Your Shop Name
SHOP_DESCRIPTION=Your shop description
SUPPORT_CONTACT=@your_support_handle
```

### 2. Database Setup

The application automatically creates the database tables on first run. To populate with sample data:

```bash
python sample_data.py
```

### 3. Running the Application

```bash
python main.py
```

The application will start both the web server (port 5000) and Telegram bot simultaneously.

## API Configuration

### Telegram Bot Setup

1. Create a new bot via [@BotFather](https://t.me/botfather)
2. Get your bot token and add it to `TELEGRAM_BOT_TOKEN`
3. Set webhook URL to `https://yourapp.replit.app/telegram/webhook`

### NowPayments Setup

1. Sign up at [NowPayments](https://nowpayments.io)
2. Get your API key from the dashboard
3. Configure IPN (Instant Payment Notifications) with your webhook URL
4. Add the API key and IPN secret to your environment variables

## Usage Guide

### Admin Panel

Access the admin dashboard at `/admin` using the configured admin password.

**Features:**
- Product management (add, edit, delete)
- Category organization
- Order tracking and status updates
- Sales analytics and reporting

### Telegram Bot Commands

- `/start` - Welcome message and main menu
- `/products` - Browse product catalog
- `/cart` - View shopping cart
- `/orders` - View order history
- `/help` - Show available commands
- `/admin` - Admin panel (admin users only)

### Customer Flow

1. **Browse Products**: Users can explore products by category
2. **Add to Cart**: Select products and quantities
3. **Checkout**: Review order and proceed to payment
4. **Payment**: Pay using cryptocurrency via NowPayments
5. **Confirmation**: Receive order confirmation and tracking

## Project Structure

```
├── app.py              # Flask application factory
├── models.py           # Database models
├── bot.py              # Telegram bot implementation
├── routes.py           # Web routes
├── payments.py         # Payment processing
├── config.py           # Configuration management
├── utils.py            # Utility functions
├── main.py             # Application entry point
├── templates/          # HTML templates
│   ├── base.html
│   └── admin/
│       ├── dashboard.html
│       ├── products.html
│       ├── categories.html
│       ├── orders.html
│       └── login.html
└── static/
    └── js/
        └── admin.js
```

## Database Schema

### Core Models

- **User**: Customer information and admin status
- **Category**: Product categorization
- **Product**: Product details, pricing, and inventory
- **CartItem**: Shopping cart functionality
- **Order**: Order information and status
- **OrderItem**: Individual items within orders
- **Payment**: Payment tracking and status

### Order Statuses

- `pending` - Order created, awaiting payment
- `confirmed` - Order confirmed, processing
- `paid` - Payment received
- `shipped` - Order shipped to customer
- `delivered` - Order delivered
- `cancelled` - Order cancelled

### Payment Statuses

- `waiting` - Awaiting payment
- `confirming` - Payment being confirmed
- `confirmed` - Payment confirmed
- `finished` - Payment completed
- `failed` - Payment failed
- `expired` - Payment expired

## Deployment

### Environment Variables

Ensure all required environment variables are properly configured:

- Database connection string
- Telegram bot token
- NowPayments API credentials
- Admin credentials
- Security keys

### Production Considerations

1. **Database**: Use PostgreSQL for production
2. **Security**: Implement HTTPS for webhook endpoints
3. **Monitoring**: Set up logging and error tracking
4. **Backup**: Regular database backups
5. **Scaling**: Consider Redis for session storage

## Troubleshooting

### Common Issues

**Bot not responding:**
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Check webhook URL is accessible
- Ensure bot has proper permissions

**Payment not processing:**
- Verify NowPayments API key and IPN secret
- Check webhook endpoints are accessible
- Monitor payment logs for errors

**Database errors:**
- Ensure PostgreSQL is running
- Verify database credentials
- Check database permissions

### Logs and Debugging

Enable debug logging by setting `DEBUG=True` in your environment. Check application logs for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation for common solutions

---

Built with Flask, PostgreSQL, python-telegram-bot, and NowPayments API.