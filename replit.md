# Telegram Shop Bot with Crypto Payments

## Overview

This is a comprehensive e-commerce Telegram bot that accepts cryptocurrency payments via NowPayments. The system features a complete product catalog, shopping cart functionality, order management, and an admin dashboard. Users can browse products, add items to their cart, and pay using Bitcoin and other cryptocurrencies. The bot provides an interactive Telegram interface for customers while offering administrators a web-based dashboard for managing products, orders, and analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Architecture
The system uses the Python Telegram Bot library with an asynchronous event-driven architecture. The bot operates in webhook mode for production deployment, handling user interactions through inline keyboards and callback queries. The main bot logic is separated into distinct handlers for commands, product browsing, cart management, and order processing.

### Backend Framework
Built on Flask with SQLAlchemy ORM for database operations. The application follows a modular structure with separate files for models, routes, bot functionality, and utilities. The system supports both SQLite for development and PostgreSQL for production environments.

### Database Design
Uses SQLAlchemy with enum-based status tracking for orders and payments. The schema includes user management, product catalog with categories, shopping cart persistence, order tracking, and payment history. Relationships are properly defined with foreign keys and cascading deletes where appropriate.

### Payment Processing
Integrates with NowPayments API for cryptocurrency payments supporting Bitcoin, Ethereum, and 100+ other cryptocurrencies. The system handles payment webhooks for real-time status updates, automatic order completion on payment confirmation, and secure payment verification using IPN secrets.

### Admin Interface
Web-based admin dashboard with session-based authentication. Provides comprehensive product and category management, real-time order tracking and fulfillment, sales analytics and reporting, and user management capabilities.

### Security Implementation
Environment-based configuration management keeps sensitive data secure. Input validation and sanitization prevent injection attacks. Admin authentication uses session management with password protection. Database connections use connection pooling for performance and security.

## External Dependencies

### Core Services
- **NowPayments API**: Cryptocurrency payment processing with support for 100+ cryptocurrencies, real-time payment tracking, and webhook notifications
- **Telegram Bot API**: Bot interactions, message handling, and webhook integration
- **PostgreSQL**: Production database for data persistence (SQLite fallback for development)

### Python Libraries
- **Flask**: Web framework for admin dashboard and webhook endpoints
- **SQLAlchemy**: ORM for database operations and model management
- **python-telegram-bot**: Async Telegram bot framework with webhook support
- **requests**: HTTP client for NowPayments API integration
- **psycopg2-binary**: PostgreSQL adapter for database connectivity

### Infrastructure
- **Replit**: Hosting platform with environment variable management
- **Bootstrap**: Frontend framework for responsive admin dashboard
- **Font Awesome**: Icon library for UI components