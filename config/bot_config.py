"""
Bot Configuration Settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')

# Validate required environment variables
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")
if not ADMIN_CHAT_ID:
    raise ValueError("ADMIN_CHAT_ID environment variable is required")

# Business Information
BUSINESS_NAME = os.getenv('BUSINESS_NAME', 'Printing Business')
BUSINESS_EMAIL = os.getenv('BUSINESS_EMAIL', 'contact@printingbusiness.com')
BUSINESS_PHONE = os.getenv('BUSINESS_PHONE', '+1234567890')
BUSINESS_ADDRESS = os.getenv('BUSINESS_ADDRESS', 'Business Address')

# Bot Messages
WELCOME_MESSAGE = f"""
🖨️ Welcome to {BUSINESS_NAME}! 

I'm here to help you with:
• 📋 Viewing our printing services
• 🛒 Placing orders for printing services
• 📅 Scheduling consultations
• 💬 Direct messaging with our team
• 📢 Accessing our updates channel

What would you like to do today?
"""

MAIN_MENU_KEYBOARD = [
    ['📋 View Services', '🛒 Place Order'],
    ['📅 Schedule a Talk', '💬 Message Me Directly'],
    ['📢 View Channel']
]

# Service Categories
SERVICES = [
    'Business Cards',
    'Flyers/Brochures', 
    'Banners/Posters',
    'Booklets/Catalogs',
    'Stickers/Labels',
    'Custom Printing'
]

# Order Status Options
ORDER_STATUSES = ['Pending', 'Processing', 'Completed', 'Cancelled']

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_URL', 'database/printing_business.db')

# Conversation States
(WAITING_NAME, WAITING_COMPANY, WAITING_PRODUCT, WAITING_QUANTITY, 
 WAITING_DELIVERY, WAITING_CONTACT, WAITING_SCHEDULE_NAME, 
 WAITING_SCHEDULE_CONTACT, WAITING_SCHEDULE_DATETIME, 
 WAITING_MESSAGE_NAME, WAITING_MESSAGE_CONTACT, WAITING_MESSAGE_TEXT) = range(12)

# Error Messages
ERROR_MESSAGES = {
    'invalid_date': '❌ Please enter a valid date in DD/MM/YYYY format',
    'invalid_quantity': '❌ Please enter a valid number for quantity',
    'invalid_contact': '❌ Please provide valid contact information (phone or email)',
    'general_error': '❌ Something went wrong. Please try again or contact support.',
    'admin_notification_failed': '⚠️ Failed to send notification to admin'
}

# Success Messages
SUCCESS_MESSAGES = {
    'order_placed': '✅ Your order has been placed successfully! We will contact you soon.',
    'schedule_booked': '✅ Your consultation has been scheduled! We will confirm the details with you.',
    'message_sent': '✅ Your message has been sent successfully! We will get back to you soon.'
}