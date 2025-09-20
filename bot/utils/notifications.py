"""
Notification utilities for sending messages to admin and channel
"""
import logging
import asyncio
from typing import Optional
import requests
from config.bot_config import BOT_TOKEN, ADMIN_CHAT_ID, CHANNEL_USERNAME

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages notifications to admin and channel"""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.admin_chat_id = ADMIN_CHAT_ID
        self.channel_username = CHANNEL_USERNAME
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_to_admin(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send notification to admin"""
        if not self.admin_chat_id:
            logger.error("Admin chat ID not configured")
            return False
        
        try:
            data = {
                'chat_id': self.admin_chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(f"{self.api_url}/sendMessage", json=data)
            
            if response.status_code == 200:
                logger.info("Admin notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send admin notification: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
            return False
    
    async def send_to_channel(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send message to channel"""
        if not self.channel_username:
            logger.warning("Channel username not configured")
            return False
        
        try:
            data = {
                'chat_id': self.channel_username,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(f"{self.api_url}/sendMessage", json=data)
            
            if response.status_code == 200:
                logger.info("Channel message sent successfully")
                return True
            else:
                logger.error(f"Failed to send channel message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending channel message: {e}")
            return False
    
    async def notify_new_order(self, order_id: int, customer_name: str, company_name: Optional[str],
                             product_type: str, quantity: int, delivery_date: str, contact_info: str) -> bool:
        """Send new order notification to admin"""
        
        company_info = f" ({company_name})" if company_name else ""
        
        message = f"""
🆕 <b>NEW ORDER RECEIVED!</b>

📋 <b>Order ID:</b> #{order_id}
👤 <b>Customer:</b> {customer_name}{company_info}
🖨️ <b>Product:</b> {product_type}
📊 <b>Quantity:</b> {quantity}
📅 <b>Delivery Date:</b> {delivery_date}
📞 <b>Contact:</b> {contact_info}

⏰ <b>Received:</b> {self._get_current_time()}

Please review and process this order promptly.
        """
        
        return await self.send_to_admin(message.strip())
    
    async def notify_new_schedule(self, schedule_id: int, customer_name: str, contact_info: str,
                                preferred_datetime: str) -> bool:
        """Send new schedule notification to admin"""
        
        message = f"""
📅 <b>NEW CONSULTATION SCHEDULED!</b>

📋 <b>Schedule ID:</b> #{schedule_id}
👤 <b>Customer:</b> {customer_name}
🕒 <b>Preferred Time:</b> {preferred_datetime}
📞 <b>Contact:</b> {contact_info}

⏰ <b>Requested:</b> {self._get_current_time()}

Please confirm the appointment with the customer.
        """
        
        return await self.send_to_admin(message.strip())
    
    async def notify_new_message(self, message_id: int, customer_name: str, contact_info: str,
                               message_text: str) -> bool:
        """Send new direct message notification to admin"""
        
        # Truncate long messages
        display_message = message_text[:200] + "..." if len(message_text) > 200 else message_text
        
        message = f"""
💬 <b>NEW DIRECT MESSAGE!</b>

📋 <b>Message ID:</b> #{message_id}
👤 <b>From:</b> {customer_name}
📞 <b>Contact:</b> {contact_info}

💭 <b>Message:</b>
{display_message}

⏰ <b>Received:</b> {self._get_current_time()}

Please respond to the customer promptly.
        """
        
        return await self.send_to_admin(message.strip())
    
    async def broadcast_to_channel(self, title: str, content: str, include_business_info: bool = True) -> bool:
        """Broadcast an update to the channel"""
        
        message = f"📢 <b>{title}</b>\\n\\n{content}"
        
        if include_business_info:
            from config.bot_config import BUSINESS_NAME, BUSINESS_PHONE, BUSINESS_EMAIL
            message += f"""
            
🖨️ <b>{BUSINESS_NAME}</b>
📞 {BUSINESS_PHONE}
📧 {BUSINESS_EMAIL}
            """
        
        return await self.send_to_channel(message.strip())
    
    def _get_current_time(self) -> str:
        """Get current time formatted for display"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Sync versions for use in non-async contexts
    def send_to_admin_sync(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Synchronous version of send_to_admin"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is running, schedule the coroutine
                asyncio.create_task(self.send_to_admin(message, parse_mode))
                return True
            else:
                # If no event loop, run in new loop
                return loop.run_until_complete(self.send_to_admin(message, parse_mode))
        except:
            # Fallback: direct HTTP request
            try:
                data = {
                    'chat_id': self.admin_chat_id,
                    'text': message,
                    'parse_mode': parse_mode
                }
                response = requests.post(f"{self.api_url}/sendMessage", json=data)
                return response.status_code == 200
            except Exception as e:
                logger.error(f"Error in sync admin notification: {e}")
                return False