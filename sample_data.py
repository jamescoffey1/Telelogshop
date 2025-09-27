#!/usr/bin/env python3
"""
Sample data generator for the Telegram Shop Bot
Creates sample categories, products, and users for demonstration
"""

from app import app, db
from models import Category, Product, User, OrderStatus, PaymentStatus
import random

def create_sample_data():
    """Create sample data for the shop"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create sample categories
        categories = [
            Category(
                name="Electronics",
                description="Phones, laptops, gadgets and electronic devices",
                is_active=True
            ),
            Category(
                name="Clothing",
                description="Fashion items, shirts, pants, accessories",
                is_active=True
            ),
            Category(
                name="Books",
                description="Physical and digital books, educational materials",
                is_active=True
            ),
            Category(
                name="Home & Garden",
                description="Home improvement, gardening tools, furniture",
                is_active=True
            ),
            Category(
                name="Sports",
                description="Sports equipment, fitness gear, outdoor activities",
                is_active=True
            )
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        
        # Create sample products
        products_data = [
            # Electronics
            {
                "name": "iPhone 15 Pro",
                "description": "Latest Apple iPhone with A17 Pro chip, titanium design, and advanced camera system",
                "price": 999.99,
                "stock_quantity": 15,
                "category_name": "Electronics",
                "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-naturaltitanium-select?wid=470&hei=556&fmt=png-alpha&.v=1692920118732"
            },
            {
                "name": "MacBook Air M2",
                "description": "13-inch MacBook Air with M2 chip, 8GB RAM, 256GB SSD",
                "price": 1199.99,
                "stock_quantity": 8,
                "category_name": "Electronics",
                "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/macbook-air-midnight-select-20220606?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1653084303665"
            },
            {
                "name": "Sony WH-1000XM5",
                "description": "Wireless noise-canceling headphones with 30-hour battery life",
                "price": 349.99,
                "stock_quantity": 25,
                "category_name": "Electronics",
                "image_url": "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6505/6505727_sd.jpg"
            },
            
            # Clothing
            {
                "name": "Premium Cotton T-Shirt",
                "description": "100% organic cotton t-shirt in various colors and sizes",
                "price": 29.99,
                "stock_quantity": 50,
                "category_name": "Clothing",
                "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500"
            },
            {
                "name": "Denim Jeans",
                "description": "Classic fit denim jeans with stretch comfort",
                "price": 79.99,
                "stock_quantity": 30,
                "category_name": "Clothing",
                "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500"
            },
            {
                "name": "Winter Jacket",
                "description": "Waterproof winter jacket with insulation",
                "price": 159.99,
                "stock_quantity": 12,
                "category_name": "Clothing",
                "image_url": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=500"
            },
            
            # Books
            {
                "name": "Python Programming Guide",
                "description": "Complete guide to Python programming for beginners and advanced users",
                "price": 49.99,
                "stock_quantity": 100,
                "category_name": "Books",
                "image_url": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=500"
            },
            {
                "name": "Cryptocurrency Handbook",
                "description": "Understanding blockchain technology and digital currencies",
                "price": 34.99,
                "stock_quantity": 75,
                "category_name": "Books",
                "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=500"
            },
            
            # Home & Garden
            {
                "name": "Smart Home Hub",
                "description": "Central control hub for all your smart home devices",
                "price": 129.99,
                "stock_quantity": 20,
                "category_name": "Home & Garden",
                "image_url": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=500"
            },
            {
                "name": "Garden Tool Set",
                "description": "Complete 10-piece garden tool set with carrying case",
                "price": 89.99,
                "stock_quantity": 18,
                "category_name": "Home & Garden",
                "image_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=500"
            },
            
            # Sports
            {
                "name": "Yoga Mat Pro",
                "description": "Professional-grade yoga mat with extra cushioning",
                "price": 59.99,
                "stock_quantity": 35,
                "category_name": "Sports",
                "image_url": "https://images.unsplash.com/photo-1506629905607-c9d0c8d71b37?w=500"
            },
            {
                "name": "Running Shoes",
                "description": "Lightweight running shoes with advanced cushioning technology",
                "price": 139.99,
                "stock_quantity": 22,
                "category_name": "Sports",
                "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500"
            }
        ]
        
        # Add products to database
        for product_data in products_data:
            category = Category.query.filter_by(name=product_data["category_name"]).first()
            if category:
                product = Product(
                    name=product_data["name"],
                    description=product_data["description"],
                    price=product_data["price"],
                    stock_quantity=product_data["stock_quantity"],
                    category_id=category.id,
                    image_url=product_data["image_url"],
                    is_active=True
                )
                db.session.add(product)
        
        # Create sample users (would normally be created via Telegram)
        sample_users = [
            User(
                telegram_id=123456789,
                username="john_doe",
                first_name="John",
                last_name="Doe",
                is_admin=False
            ),
            User(
                telegram_id=987654321,
                username="jane_smith",
                first_name="Jane",
                last_name="Smith",
                is_admin=False
            ),
            User(
                telegram_id=555666777,
                username="admin_user",
                first_name="Admin",
                last_name="User",
                is_admin=True
            )
        ]
        
        for user in sample_users:
            db.session.add(user)
        
        db.session.commit()
        
        print("✅ Sample data created successfully!")
        print(f"📁 Created {len(categories)} categories")
        print(f"📦 Created {len(products_data)} products")
        print(f"👥 Created {len(sample_users)} users")
        print("\nYou can now:")
        print("1. Access the admin panel at /admin (password: admin123)")
        print("2. View the home page at /")
        print("3. Manage products and categories through the admin interface")

if __name__ == "__main__":
    create_sample_data()