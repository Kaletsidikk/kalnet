"""
Enhanced Database Models for KalNetworks Admin System
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'printing_business.db')
        self.db_path = db_path
        self.init_admin_tables()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_admin_tables(self):
        """Initialize admin-specific tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Services table with enhanced fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'general',
                base_price REAL DEFAULT 0.0,
                price_range TEXT,
                is_active BOOLEAN DEFAULT 1,
                image_url TEXT,
                processing_time TEXT DEFAULT '1-3 business days',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table for specific items under services
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                unit TEXT DEFAULT 'each',
                min_quantity INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                specifications TEXT, -- JSON string for additional specs
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services (id)
            )
        ''')
        
        # Admin settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Orders table enhancement
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_number TEXT UNIQUE NOT NULL,
                service_id INTEGER,
                product_id INTEGER,
                quantity INTEGER DEFAULT 1,
                custom_specifications TEXT,
                total_price REAL,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'normal',
                estimated_delivery TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Initialize default data
        self._insert_default_services(cursor)
        self._insert_default_admin_settings(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_default_services(self, cursor):
        """Insert default KalNetworks services"""
        default_services = [
            ('Banners', 'Custom banners for all occasions', 'marketing', 25.0, '$25-$200', 1, None, '2-3 business days'),
            ('Flyers', 'Professional flyers and leaflets', 'marketing', 15.0, '$15-$100', 1, None, '1-2 business days'),
            ('T-Shirts', 'Custom printed t-shirts', 'apparel', 20.0, '$20-$50', 1, None, '3-5 business days'),
            ('Mugs', 'Personalized mugs and drinkware', 'promotional', 12.0, '$12-$30', 1, None, '2-4 business days'),
            ('Hats', 'Custom embroidered hats and caps', 'apparel', 18.0, '$18-$45', 1, None, '3-5 business days'),
            ('Paper Bags', 'Branded paper bags', 'packaging', 8.0, '$8-$25', 1, None, '2-3 business days'),
            ('Packaging', 'Custom packaging solutions', 'packaging', 30.0, '$30-$500', 1, None, '3-7 business days'),
        ]
        
        # Check if services already exist
        cursor.execute("SELECT COUNT(*) FROM services")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.executemany('''
                INSERT INTO services (name, description, category, base_price, price_range, is_active, image_url, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', default_services)
    
    def _insert_default_admin_settings(self, cursor):
        """Insert default admin settings"""
        default_settings = [
            ('welcome_message', 'Welcome to KalNetworks – Your trusted printing solutions partner. Place an order, schedule a talk, or message me directly.', 'Bot welcome message'),
            ('business_hours', 'Monday-Friday: 9AM-6PM, Saturday: 10AM-4PM', 'Business operating hours'),
            ('min_order_value', '10.0', 'Minimum order value in USD'),
            ('max_order_value', '5000.0', 'Maximum order value in USD'),
            ('auto_quote_enabled', 'true', 'Enable automatic quote generation'),
            ('admin_notifications', 'true', 'Enable admin notifications for new orders'),
        ]
        
        for setting_key, setting_value, description in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO admin_settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', (setting_key, setting_value, description))


class ServiceManager:
    """Manager class for services"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_all_services(self, active_only: bool = False) -> List[Dict]:
        """Get all services"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM services"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        
        cursor.execute(query)
        services = []
        
        for row in cursor.fetchall():
            services.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category': row[3],
                'base_price': row[4],
                'price_range': row[5],
                'is_active': bool(row[6]),
                'image_url': row[7],
                'processing_time': row[8],
                'created_at': row[9],
                'updated_at': row[10]
            })
        
        conn.close()
        return services
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict]:
        """Get service by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category': row[3],
                'base_price': row[4],
                'price_range': row[5],
                'is_active': bool(row[6]),
                'image_url': row[7],
                'processing_time': row[8],
                'created_at': row[9],
                'updated_at': row[10]
            }
        return None
    
    def create_service(self, service_data: Dict) -> int:
        """Create a new service"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO services (name, description, category, base_price, price_range, is_active, image_url, processing_time, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            service_data.get('name'),
            service_data.get('description', ''),
            service_data.get('category', 'general'),
            service_data.get('base_price', 0.0),
            service_data.get('price_range', ''),
            service_data.get('is_active', 1),
            service_data.get('image_url', ''),
            service_data.get('processing_time', '1-3 business days')
        ))
        
        service_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return service_id
    
    def update_service(self, service_id: int, service_data: Dict) -> bool:
        """Update an existing service"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE services 
            SET name = ?, description = ?, category = ?, base_price = ?, 
                price_range = ?, is_active = ?, image_url = ?, processing_time = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            service_data.get('name'),
            service_data.get('description', ''),
            service_data.get('category', 'general'),
            service_data.get('base_price', 0.0),
            service_data.get('price_range', ''),
            service_data.get('is_active', 1),
            service_data.get('image_url', ''),
            service_data.get('processing_time', '1-3 business days'),
            service_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_service(self, service_id: int) -> bool:
        """Delete a service"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # First delete related products
        cursor.execute("DELETE FROM products WHERE service_id = ?", (service_id,))
        # Then delete the service
        cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success


class ProductManager:
    """Manager class for products"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_products_by_service(self, service_id: int, active_only: bool = False) -> List[Dict]:
        """Get products by service ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM products WHERE service_id = ?"
        params = [service_id]
        
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY name"
        
        cursor.execute(query, params)
        products = []
        
        for row in cursor.fetchall():
            specs = {}
            try:
                if row[9]:  # specifications
                    specs = json.loads(row[9])
            except:
                pass
                
            products.append({
                'id': row[0],
                'service_id': row[1],
                'name': row[2],
                'description': row[3],
                'price': row[4],
                'unit': row[5],
                'min_quantity': row[6],
                'is_active': bool(row[7]),
                'specifications': specs,
                'created_at': row[10],
                'updated_at': row[11]
            })
        
        conn.close()
        return products
    
    def create_product(self, product_data: Dict) -> int:
        """Create a new product"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        specifications = json.dumps(product_data.get('specifications', {}))
        
        cursor.execute('''
            INSERT INTO products (service_id, name, description, price, unit, min_quantity, is_active, specifications, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            product_data.get('service_id'),
            product_data.get('name'),
            product_data.get('description', ''),
            product_data.get('price'),
            product_data.get('unit', 'each'),
            product_data.get('min_quantity', 1),
            product_data.get('is_active', 1),
            specifications
        ))
        
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def update_product(self, product_id: int, product_data: Dict) -> bool:
        """Update an existing product"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        specifications = json.dumps(product_data.get('specifications', {}))
        
        cursor.execute('''
            UPDATE products 
            SET name = ?, description = ?, price = ?, unit = ?, min_quantity = ?, 
                is_active = ?, specifications = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            product_data.get('name'),
            product_data.get('description', ''),
            product_data.get('price'),
            product_data.get('unit', 'each'),
            product_data.get('min_quantity', 1),
            product_data.get('is_active', 1),
            specifications,
            product_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success


class AdminSettingsManager:
    """Manager class for admin settings"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Get a setting value"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT setting_value FROM admin_settings WHERE setting_key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else default
    
    def set_setting(self, key: str, value: str, description: str = None) -> bool:
        """Set a setting value"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO admin_settings (setting_key, setting_value, description, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (key, value, description))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_all_settings(self) -> Dict[str, Dict]:
        """Get all settings"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT setting_key, setting_value, description FROM admin_settings ORDER BY setting_key")
        settings = {}
        
        for row in cursor.fetchall():
            settings[row[0]] = {
                'value': row[1],
                'description': row[2] or ''
            }
        
        conn.close()
        return settings


# Initialize global managers
db_manager = DatabaseManager()
service_manager = ServiceManager(db_manager)
product_manager = ProductManager(db_manager)
settings_manager = AdminSettingsManager(db_manager)