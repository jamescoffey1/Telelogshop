#!/usr/bin/env python3
"""
Setup sample data for the Telegram Shop Bot
"""
from app import app, db
from models import User, Category, Product, OrderStatus, PaymentStatus
from decimal import Decimal

def create_sample_data():
    """Create sample categories and products for the shop"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create categories
        categories = [
            Category(name="Electronics", description="Latest gadgets and electronic devices"),
            Category(name="Clothing", description="Fashion and apparel for all occasions"),
            Category(name="Books", description="Digital and physical books"),
            Category(name="Home & Garden", description="Items for your home and garden"),
            Category(name="Sports", description="Sports equipment and accessories")
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        
        # Create products
        products = [
            # Electronics
            Product(name="Wireless Headphones", description="Premium noise-cancelling wireless headphones with 30-hour battery life", 
                   price=Decimal("99.99"), stock_quantity=25, category_id=1, 
                   image_url="https://via.placeholder.com/300x300/0066cc/ffffff?text=Headphones"),
            
            Product(name="Smartphone", description="Latest flagship smartphone with advanced camera system", 
                   price=Decimal("699.99"), stock_quantity=15, category_id=1,
                   image_url="https://via.placeholder.com/300x300/0066cc/ffffff?text=Smartphone"),
            
            Product(name="Laptop", description="High-performance laptop for work and gaming", 
                   price=Decimal("1299.99"), stock_quantity=8, category_id=1,
                   image_url="https://via.placeholder.com/300x300/0066cc/ffffff?text=Laptop"),
            
            # Clothing
            Product(name="T-Shirt", description="Comfortable cotton t-shirt in various colors", 
                   price=Decimal("19.99"), stock_quantity=50, category_id=2,
                   image_url="https://via.placeholder.com/300x300/ff6600/ffffff?text=T-Shirt"),
            
            Product(name="Jeans", description="Classic denim jeans with modern fit", 
                   price=Decimal("59.99"), stock_quantity=30, category_id=2,
                   image_url="https://via.placeholder.com/300x300/ff6600/ffffff?text=Jeans"),
            
            Product(name="Sneakers", description="Comfortable running sneakers for daily wear", 
                   price=Decimal("89.99"), stock_quantity=20, category_id=2,
                   image_url="https://via.placeholder.com/300x300/ff6600/ffffff?text=Sneakers"),
            
            # Books
            Product(name="Programming Guide", description="Complete guide to modern programming languages", 
                   price=Decimal("29.99"), stock_quantity=40, category_id=3,
                   image_url="https://via.placeholder.com/300x300/009900/ffffff?text=Book"),
            
            Product(name="Science Fiction Novel", description="Bestselling sci-fi adventure novel", 
                   price=Decimal("14.99"), stock_quantity=35, category_id=3,
                   image_url="https://via.placeholder.com/300x300/009900/ffffff?text=Novel"),
            
            # Home & Garden
            Product(name="Coffee Maker", description="Automatic coffee maker with programmable timer", 
                   price=Decimal("79.99"), stock_quantity=12, category_id=4,
                   image_url="https://via.placeholder.com/300x300/cc6600/ffffff?text=Coffee"),
            
            Product(name="Plant Pot Set", description="Decorative ceramic plant pots in various sizes", 
                   price=Decimal("24.99"), stock_quantity=18, category_id=4,
                   image_url="https://via.placeholder.com/300x300/cc6600/ffffff?text=Plants"),
            
            # Sports
            Product(name="Yoga Mat", description="Non-slip exercise yoga mat with carrying strap", 
                   price=Decimal("34.99"), stock_quantity=25, category_id=5,
                   image_url="https://via.placeholder.com/300x300/9900cc/ffffff?text=Yoga"),
            
            Product(name="Dumbbells Set", description="Adjustable dumbbells for home workouts", 
                   price=Decimal("149.99"), stock_quantity=10, category_id=5,
                   image_url="https://via.placeholder.com/300x300/9900cc/ffffff?text=Weights")
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()
        
        print(f"Created {len(categories)} categories and {len(products)} products")
        print("Sample data setup completed successfully!")

if __name__ == "__main__":
    create_sample_data()