"""
Database models and operations for the printing business bot
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class DatabaseManager:
    """Database manager for handling all database operations"""
    
    def __init__(self, db_path: str = "database/printing_business.db"):
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure the database and directory exist"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        if not os.path.exists(self.db_path):
            # Run database initialization
            from database.init_db import create_database
            create_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last row ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

class UserModel:
    """Model for handling user operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_or_update_user(self, telegram_user_id: int, username: Optional[str] = None,
                             first_name: Optional[str] = None, last_name: Optional[str] = None) -> int:
        """Create or update a user record"""
        existing_user = self.get_user(telegram_user_id)
        
        if existing_user:
            # Update existing user
            query = """
                UPDATE users 
                SET username = ?, first_name = ?, last_name = ?, last_active = CURRENT_TIMESTAMP
                WHERE telegram_user_id = ?
            """
            self.db.execute_update(query, (username, first_name, last_name, telegram_user_id))
            return existing_user['id']
        else:
            # Create new user
            query = """
                INSERT INTO users (telegram_user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            """
            return self.db.execute_insert(query, (telegram_user_id, username, first_name, last_name))
    
    def get_user(self, telegram_user_id: int) -> Optional[sqlite3.Row]:
        """Get user by Telegram user ID"""
        query = "SELECT * FROM users WHERE telegram_user_id = ?"
        results = self.db.execute_query(query, (telegram_user_id,))
        return results[0] if results else None

class OrderModel:
    """Model for handling order operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_order(self, customer_name: str, company_name: Optional[str], product_type: str,
                    quantity: int, delivery_date: str, contact_info: str,
                    telegram_user_id: Optional[int] = None, notes: Optional[str] = None) -> int:
        """Create a new order"""
        query = """
            INSERT INTO orders 
            (customer_name, company_name, product_type, quantity, delivery_date, 
             contact_info, telegram_user_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_insert(query, (
            customer_name, company_name, product_type, quantity,
            delivery_date, contact_info, telegram_user_id, notes
        ))
    
    def get_order(self, order_id: int) -> Optional[sqlite3.Row]:
        """Get order by ID"""
        query = "SELECT * FROM orders WHERE id = ?"
        results = self.db.execute_query(query, (order_id,))
        return results[0] if results else None
    
    def get_orders_by_status(self, status: str) -> List[sqlite3.Row]:
        """Get orders by status"""
        query = "SELECT * FROM orders WHERE order_status = ? ORDER BY created_at DESC"
        return self.db.execute_query(query, (status,))
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """Update order status"""
        query = "UPDATE orders SET order_status = ? WHERE id = ?"
        affected = self.db.execute_update(query, (status, order_id))
        return affected > 0
    
    def get_recent_orders(self, limit: int = 10) -> List[sqlite3.Row]:
        """Get recent orders"""
        query = "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?"
        return self.db.execute_query(query, (limit,))

class ScheduleModel:
    """Model for handling schedule operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_schedule(self, customer_name: str, contact_info: str, preferred_datetime: str,
                       telegram_user_id: Optional[int] = None, notes: Optional[str] = None) -> int:
        """Create a new schedule"""
        query = """
            INSERT INTO schedules 
            (customer_name, contact_info, preferred_datetime, telegram_user_id, notes)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute_insert(query, (
            customer_name, contact_info, preferred_datetime, telegram_user_id, notes
        ))
    
    def get_schedule(self, schedule_id: int) -> Optional[sqlite3.Row]:
        """Get schedule by ID"""
        query = "SELECT * FROM schedules WHERE id = ?"
        results = self.db.execute_query(query, (schedule_id,))
        return results[0] if results else None
    
    def get_pending_schedules(self) -> List[sqlite3.Row]:
        """Get pending schedules"""
        query = "SELECT * FROM schedules WHERE status = 'Pending' ORDER BY created_at DESC"
        return self.db.execute_query(query)
    
    def update_schedule_status(self, schedule_id: int, status: str) -> bool:
        """Update schedule status"""
        query = "UPDATE schedules SET status = ? WHERE id = ?"
        affected = self.db.execute_update(query, (status, schedule_id))
        return affected > 0

class MessageModel:
    """Model for handling message operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_message(self, customer_name: str, contact_info: str, message_text: str,
                      telegram_user_id: Optional[int] = None) -> int:
        """Create a new message"""
        query = """
            INSERT INTO messages 
            (customer_name, contact_info, message_text, telegram_user_id)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute_insert(query, (
            customer_name, contact_info, message_text, telegram_user_id
        ))
    
    def get_message(self, message_id: int) -> Optional[sqlite3.Row]:
        """Get message by ID"""
        query = "SELECT * FROM messages WHERE id = ?"
        results = self.db.execute_query(query, (message_id,))
        return results[0] if results else None
    
    def get_pending_messages(self) -> List[sqlite3.Row]:
        """Get pending messages"""
        query = "SELECT * FROM messages WHERE status = 'Pending' ORDER BY created_at DESC"
        return self.db.execute_query(query)
    
    def update_message_status(self, message_id: int, status: str, response: Optional[str] = None) -> bool:
        """Update message status and response"""
        query = "UPDATE messages SET status = ?, response = ? WHERE id = ?"
        affected = self.db.execute_update(query, (status, response, message_id))
        return affected > 0

class ServiceModel:
    """Model for handling service operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_active_services(self) -> List[sqlite3.Row]:
        """Get all active services"""
        query = "SELECT * FROM services WHERE is_active = 1 ORDER BY name"
        return self.db.execute_query(query)
    
    def get_service(self, service_id: int) -> Optional[sqlite3.Row]:
        """Get service by ID"""
        query = "SELECT * FROM services WHERE id = ?"
        results = self.db.execute_query(query, (service_id,))
        return results[0] if results else None
    
    def get_service_by_name(self, name: str) -> Optional[sqlite3.Row]:
        """Get service by name"""
        query = "SELECT * FROM services WHERE name = ?"
        results = self.db.execute_query(query, (name,))
        return results[0] if results else None

# Global database manager instance
db_manager = DatabaseManager()

# Model instances
user_model = UserModel(db_manager)
order_model = OrderModel(db_manager)
schedule_model = ScheduleModel(db_manager)
message_model = MessageModel(db_manager)
service_model = ServiceModel(db_manager)