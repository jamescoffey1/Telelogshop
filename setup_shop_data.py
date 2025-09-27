#!/usr/bin/env python3
"""
Setup sample shop data for testing NowPayments integration
"""

from app import app, db
from models import Category, Product, User
from decimal import Decimal

def create_sample_categories():
    """Create sample product categories"""
    categories = [
        {
            'name': 'Clone Cards',
            'description': 'Credit Cards, Dumps card, and Debit cards'
        },
        {
            'name': 'Banks Logs',
            'description': 'US and Canada for all Logs'
        },
        {
            'name': 'RDP',
            'description': 'vaild and 30 days'
        },
        {
            'name': 'OTP Licence',
            'description': '7 days plans and monthly plans'
        },
        {
            'name': 'online orders',
            'description': 'Sports equipment and fitness gear'
        }
    ]
    
    created_categories = []
    for cat_data in categories:
        category = Category.query.filter_by(name=cat_data['name']).first()
        if not category:
            category = Category(
                name=cat_data['name'],
                description=cat_data['description']
            )
            db.session.add(category)
            created_categories.append(category)
        else:
            created_categories.append(category)
    
    db.session.commit()
    return created_categories

def create_sample_products(categories):
    """Create sample products for testing"""
    products_data = [
        # Electronics
        {
            'name': 'iPhone 15 Pro',
            'description': 'Latest iPhone with advanced camera and A17 Pro chip',
            'price': Decimal('999.00'),
            'stock_quantity': 50,
            'category': 'Electronics'
        },
        {
            'name': 'MacBook Air M2',
            'description': 'Ultra-thin laptop with M2 chip and all-day battery',
            'price': Decimal('1299.00'),
            'stock_quantity': 25,
            'category': 'Electronics'
        },
        {
            'name': 'AirPods Pro',
            'description': 'Wireless earbuds with active noise cancellation',
            'price': Decimal('249.00'),
            'stock_quantity': 100,
            'category': 'Electronics'
        },
        
        # Clothing
        {
            'name': 'Premium Cotton T-Shirt',
            'description': 'Comfortable 100% organic cotton t-shirt',
            'price': Decimal('29.99'),
            'stock_quantity': 200,
            'category': 'Clothing'
        },
        {
            'name': 'Denim Jeans',
            'description': 'Classic blue denim jeans with perfect fit',
            'price': Decimal('79.99'),
            'stock_quantity': 150,
            'category': 'Clothing'
        },
        
        # Books
        {
            'name': 'Programming with Python',
            'description': 'Complete guide to Python programming',
            'price': Decimal('39.99'),
            'stock_quantity': 75,
            'category': 'Books'
        },
        {
            'name': 'The Art of Trading',
            'description': 'Master cryptocurrency and financial trading',
            'price': Decimal('49.99'),
            'stock_quantity': 60,
            'category': 'Books'
        },
        
        # Home & Garden
        {
            'name': 'Smart Home Hub',
            'description': 'Control all your smart devices from one place',
            'price': Decimal('149.99'),
            'stock_quantity': 40,
            'category': 'Home & Garden'
        },
        {
            'name': 'Wireless Charger',
            'description': 'Fast wireless charging pad for all devices',
            'price': Decimal('35.99'),
            'stock_quantity': 80,
            'category': 'Electronics'
        },
        
        # Sports
        {
            'name': 'Yoga Mat Pro',
            'description': 'Premium non-slip yoga mat for all practices',
            'price': Decimal('59.99'),
            'stock_quantity': 90,
            'category': 'Sports'
        }
    ]
    
    # Create category lookup
    cat_lookup = {cat.name: cat for cat in categories}
    
    created_products = []
    for prod_data in products_data:
        product = Product.query.filter_by(name=prod_data['name']).first()
        if not product:
            category = cat_lookup.get(prod_data['category'])
            if category:
                product = Product(
                    name=prod_data['name'],
                    description=prod_data['description'],
                    price=prod_data['price'],
                    stock_quantity=prod_data['stock_quantity'],
                    category_id=category.id
                )
                db.session.add(product)
                created_products.append(product)
    
    db.session.commit()
    return created_products

def main():
    """Setup complete shop data"""
    with app.app_context():
        print("Setting up shop data...")
        
        # Create categories
        categories = create_sample_categories()
        print(f"Created {len(categories)} categories")
        
        # Create products
        products = create_sample_products(categories)
        print(f"Created {len(products)} products")
        
        print("Shop data setup complete!")
        print("\nAvailable categories:")
        for cat in categories:
            product_count = Product.query.filter_by(category_id=cat.id).count()
            print(f"  - {cat.name}: {product_count} products")

if __name__ == "__main__":
    main()