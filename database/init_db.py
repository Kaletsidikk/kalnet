"""
Database initialization script for the printing business platform
"""
import sqlite3
import os
from datetime import datetime

def create_database():
    """Create the database and tables"""
    
    # Ensure database directory exists
    db_dir = os.path.dirname('database/printing_business.db')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Connect to database
    conn = sqlite3.connect('database/printing_business.db')
    cursor = conn.cursor()
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            company_name TEXT,
            product_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            delivery_date TEXT NOT NULL,
            contact_info TEXT NOT NULL,
            order_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            telegram_user_id INTEGER,
            notes TEXT
        )
    ''')
    
    # Create schedules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            contact_info TEXT NOT NULL,
            preferred_datetime TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            telegram_user_id INTEGER,
            notes TEXT
        )
    ''')
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            contact_info TEXT NOT NULL,
            message_text TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            telegram_user_id INTEGER,
            response TEXT
        )
    ''')
    
    # Create users table (for tracking telegram users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create services table (for managing available services)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            price_range TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default services (prices in Ethiopian Birr - ETB)
    default_services = [
        ('Business Cards', 'Professional business cards with various finishes', '2,500-10,000 ETB per 1000'),
        ('Flyers/Brochures', 'Marketing materials for promotions and information', '5,000-25,000 ETB'),
        ('Banners/Posters', 'Large format printing for events and advertising', '10,000-50,000 ETB'),
        ('Booklets/Catalogs', 'Multi-page printed materials with binding options', '15,000-75,000 ETB'),
        ('Stickers/Labels', 'Custom stickers and labels for branding', '5,000-20,000 ETB'),
        ('Custom Printing', 'Specialized printing services tailored to your needs', 'Quote on request')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO services (name, description, price_range)
        VALUES (?, ?, ?)
    ''', default_services)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("[SUCCESS] Database created successfully!")
    print("[INFO] Tables created:")
    print("  - orders")
    print("  - schedules") 
    print("  - messages")
    print("  - users")
    print("  - services")
    print("[INFO] Default services added")

def reset_database():
    """Reset the database by dropping all tables and recreating them"""
    if os.path.exists('database/printing_business.db'):
        os.remove('database/printing_business.db')
        print("[INFO] Existing database removed")
    
    create_database()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        create_database()