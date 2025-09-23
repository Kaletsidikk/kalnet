#!/usr/bin/env python3
"""
Enhanced Render Bot Deployment - Fixed Menu Handling
Uses a basic HTTP server approach that's compatible with Render
"""

import os
import sys
import logging
import time
from datetime import datetime
import signal
import traceback
import asyncio
import threading
from dotenv import load_dotenv

# Enhanced logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    """Handle shutdown gracefully"""
    logger.info("🛑 Bot shutdown signal received")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_environment():
    """Check required environment variables for bot"""
    logger.info("🔍 Checking bot environment variables...")
    
    required_vars = {
        'BOT_TOKEN': 'Telegram bot token',
        'ADMIN_CHAT_ID': 'Admin chat ID'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ Bot environment variables OK")
    return True

class SimpleBot:
    """Enhanced bot implementation with proper menu handling"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.admin_chat_id = os.getenv('ADMIN_CHAT_ID')
        self.business_name = os.getenv('BUSINESS_NAME', 'KalNetworks – Printing & Business Solutions')
        self.business_email = os.getenv('BUSINESS_EMAIL', 'gebeyatechnologies@gmail.com')
        self.business_phone = os.getenv('BUSINESS_PHONE', '0965552595')
        self.business_username = os.getenv('BUSINESS_USERNAME', '@ABISSINIANJA')
        self.running = False
        self.user_languages = {}  # Track user language preferences
        self.user_states = {}     # Track conversation states
        
        # Define menu options for both languages
        self.menu_options = {
            'en': ['🏪 Services', '🛒 Order', '💬 Contact', '❓ Help'],
            'am': ['🏪 አገልግሎቶች', '🛒 ትዕዛዝ', '💬 ያነጋግሩን', '❓ እርዳታ']
        }
        
    async def send_message(self, chat_id, text, parse_mode='HTML'):
        """Send message via Telegram API"""
        import aiohttp
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info(f"✅ Message sent to {chat_id}")
                        return True
                    else:
                        logger.error(f"❌ Failed to send message: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False

    async def get_updates(self, offset=0):
        """Get updates from Telegram"""
        import aiohttp
        
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {
            'offset': offset,
            'timeout': 30,
            'allowed_updates': ['message', 'callback_query']
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result', [])
                    else:
                        logger.error(f"❌ Failed to get updates: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"❌ Error getting updates: {e}")
            return []

    async def handle_message(self, message):
        """Handle incoming message with proper menu handling"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user = message.get('from', {})
            first_name = user.get('first_name', 'User')
            
            logger.info(f"📨 Message from {first_name} ({chat_id}): {text}")
            
            # Check if it's a menu button click first
            is_menu_option = False
            for lang_options in self.menu_options.values():
                if text in lang_options:
                    is_menu_option = True
                    break
            
            if is_menu_option:
                await self.handle_menu_selection(chat_id, text)
                return  # Important: return after handling menu selection
                
            if text.startswith('/start'):
                # Ask for language selection
                lang_text = (
                    f"🤖 Welcome to {self.business_name}!\n"
                    f"🇪🇹 ወደ {self.business_name} እንኳን በደህና መጡ!\n\n"
                    "🌐 Choose your language / ቋንቋ ይምረጡ:\n"
                    "• en - English\n"
                    "• am - አማርኛ\n\n"
                    "Reply with: en or am"
                )
                await self.send_message(chat_id, lang_text)
                self.user_states[chat_id] = 'awaiting_language'
                
            elif self.user_states.get(chat_id) == 'awaiting_language':
                if text.lower().startswith('en'):
                    self.user_languages[chat_id] = 'en'
                elif text.lower().startswith('am'):
                    self.user_languages[chat_id] = 'am'
                else:
                    await self.send_message(chat_id, "Please reply with 'en' or 'am' / እባክዎን 'en' ወይም 'am' ይላኩ")
                    return
                self.user_states[chat_id] = None
                await self.show_menu(chat_id)
                
            elif text.startswith('/help'):
                await self.show_help(chat_id)
                
            else:
                # Forward message to admin ONLY if it's not a menu option and not from admin
                if str(chat_id) != str(self.admin_chat_id):
                    forward_text = f"""<b>📨 New Message</b>

<b>From:</b> {first_name} (@{user.get('username', 'N/A')})
<b>Chat ID:</b> {chat_id}
<b>Message:</b> {text}

Reply with: /reply {chat_id} your_message"""
                    await self.send_message(self.admin_chat_id, forward_text)
                
                # Reply to user depending on language
                lang = self.user_languages.get(chat_id, 'en')
                if lang == 'am':
                    reply_text = (
                        "እናመሰግናለን! መልዕክትዎ ተቀብሏል። በተቻለ ፍጥነት እንመልስልዎታለን።\n\n"
                        f"የአደጋ ጊዜ መገናኛ: {self.business_phone}"
                    )
                else:
                    reply_text = (
                        f"Thank you for contacting {self.business_name}!\n\n"
                        "Your message has been received. We'll get back to you soon.\n\n"
                        f"For urgent matters, please call: {self.business_phone}"
                    )
                await self.send_message(chat_id, reply_text)
                
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
    
    async def show_menu(self, chat_id):
        """Show main menu based on user's language"""
        lang = self.user_languages.get(chat_id, 'en')
        
        if lang == 'am':
            menu_text = (
                f"🎉 ወደ {self.business_name} እንኳን በደህና መጡ!\n\n"
                "🎯 ዛሬ እንዴት ልረዳዎት ችላለሁ?\n\n"
                "መዝገብ:\n"
                "🏪 አገልግሎቶች - ያገልግሎቶቻችንን ይመልከቱ\n"
                "🛒 ትዕዛዝ - ትዕዛዝ ያድርጉ\n"
                "💬 ያነጋግሩን - እኛን ያነጋግሩ\n"
                "❓ እርዳታ - እርዳታ ይጠይቁ\n\n"
                "ከታች ያሉትን ምርጫዎች ተጠቀሙ:"
            )
        else:
            menu_text = (
                f"🎉 Welcome to {self.business_name}!\n\n"
                "🎯 How can I help you today?\n\n"
                "Menu:\n"
                "🏪 Services - View our printing services\n"
                "🛒 Order - Place an order\n"
                "💬 Contact - Get in touch with us\n"
                "❓ Help - Get help and information\n\n"
                "Use the options below:"
            )
        
        await self.send_message(chat_id, menu_text)
    
    async def handle_menu_selection(self, chat_id, text):
        """Handle menu button selections"""
        lang = self.user_languages.get(chat_id, 'en')
        
        if text in ['🏪 Services', '🏪 አገልግሎቶች']:
            await self.show_services(chat_id, lang)
        elif text in ['🛒 Order', '🛒 ትዕዛዝ']:
            await self.show_order_info(chat_id, lang)
        elif text in ['💬 Contact', '💬 ያነጋግሩን']:
            await self.show_contact(chat_id, lang)
        elif text in ['❓ Help', '❓ እርዳታ']:
            await self.show_help(chat_id, lang)
    
    async def show_services(self, chat_id, lang='en'):
        """Show available services with enhanced UI from test_bot.py"""
        if lang == 'am':
            services_text = f"""
🏪 <b>{self.business_name} - የእኛ አገልግሎቶች</b>

🖨️ <b>የንግድ ካርዶች</b>
   የሙያ ካርዶች፣ የተለያዩ አማራጮች
   💰 ከ25 birr ጀምሮ

📄 <b>ፍላየር እና ብሮሽሮች</b>
   የማርኬቲንግ ቁሳቁሶች፣ ሙሉ ቀለም
   💰 ከ50 birr ጀምሮ

🎯 <b>ባነሮች እና ፖስተሮች</b>
   ትላልቅ ህትመቶች፣ የውስጥ እና የውጭ አማራጮች
   💰 ከ75 birr ጀምሮ

📚 <b>መጽሔት እና ካታሎጎች</b>
   ብዙ ገፅ ሰነዶች፣ የማሰሪያ አማራጮች
   💰 ከ100 birr ጀምሮ

🏷️ <b>ስቲከሮች እና መለያዎች</b>
   ዝርዝር የተለያዩ ቅርጾች እና ስፋቶች
   💰 ከ30 birr ጀምሮ

⭐ <b>ልዩ ፕሮጀክቶች</b>
   ልዩ መስፈርቶች፣ የግል አገልግሎት
   💰 በጥያቄዎ መሰረት ዋጋ

📞 <i>ለዝርዝር ዋጋዎች እና ልዩ መስፈርቶች ያነጋግሩን!</i>
            """
        else:
            services_text = f"""
🏪 <b>{self.business_name} - Services</b>

🖨️ <b>Business Cards</b>
   Professional cards, various options
   💰 from 25 ETB

📄 <b>Flyers & Brochures</b>
   Marketing materials, full color
   💰 from 50 ETB

🎯 <b>Banners & Posters</b>
   Large prints, indoor & outdoor options
   💰 from 75 ETB

📚 <b>Booklets & Catalogs</b>
   Multi-page documents, binding options
   💰 from 100 ETB

🏷️ <b>Stickers & Labels</b>
   Detailed various shapes and sizes
   💰 from 30 ETB

⭐ <b>Custom Projects</b>
   Special requirements, personalized service
   💰 Quote on request

📞 <i>Contact us for detailed quotes and special requirements!</i>
            """
        
        await self.send_message(chat_id, services_text)
    
    async def show_order_info(self, chat_id, lang='en'):
        """Show order information with enhanced content"""
        if lang == 'am':
            order_text = f"""
🛒 <b>ትዕዛዝ ያድርጉ</b>

ትዕዛዝ ለማድረግ እባክዎን ያቅርቡ:
• የሚፈልጉት አገልግሎት ዓይነት
• የሚሹት መጠን  
• የእርስዎ የመገናኛ መረጃ
• ማናቸውንም ልዩ መስፈርቶች

📞 <b>ያነጋግሩን:</b>
📧 {self.business_email}
📱 {self.business_phone}
💬 {self.business_username}

ወይም እዚህ መልዕክት ይላኩልን!
            """
        else:
            order_text = f"""
🛒 <b>Place Your Order</b>

To place an order, please provide:
• Service type you need
• Quantity required
• Your contact information  
• Any special requirements

📞 <b>Contact us:</b>
📧 {self.business_email}
📱 {self.business_phone}
💬 {self.business_username}

Or just send us a message here!
            """
        
        await self.send_message(chat_id, order_text)
    
    async def show_contact(self, chat_id, lang='en'):
        """Show contact information"""
        if lang == 'am':
            contact_text = f"""
💬 <b>{self.business_name}ን ያነጋግሩ</b>

📧 ኢሜይል: {self.business_email}
📱 ስልክ: {self.business_phone}  
💬 ቴሌግራም: {self.business_username}

💡 እዚህ ቀጥተኛ መልዕክትም መላክ ይችላሉ!
            """
        else:
            contact_text = f"""
💬 <b>Contact {self.business_name}</b>

📧 Email: {self.business_email}
📱 Phone: {self.business_phone}
💬 Telegram: {self.business_username}

💡 You can also send us a message directly here!
            """
        
        await self.send_message(chat_id, contact_text)
    
    async def show_help(self, chat_id, lang=None):
        """Show help information with enhanced content"""
        if lang is None:
            lang = self.user_languages.get(chat_id, 'en')
        
        if lang == 'am':
            help_text = f"""
❓ <b>እርዳታ እና መረጃ</b>

🤖 <b>አቮቸብ ትዕዛዞች:</b>
/start - ቦቱን ጀምር
/help - ይህንን እርዳታ አሳይ

📋 <b>የመዝገብ አማራጮች:</b>
🏪 አገልግሎቶች - የማተሚያ አገልግሎቶቻችንን ይመልከቱ
🛒 ትዕዛዝ - ትዕዛዝ ያድርጉ  
💬 ያነጋግሩን - የእኛን የመገናኛ መረጃ ያግኙ
❓ እርዳታ - ይህንን እርዳታ አሳይ

📞 <b>የመገኛ መረጃ:</b>
📧 {self.business_email}
📱 {self.business_phone}
💬 {self.business_username}

💡 <b>ጠቃሚ ምክር:</b> መልዕክትዎን ብቻ ይተይቡ እና በቀጥታ እንቀበላለን!
            """
        else:
            help_text = f"""
❓ <b>Help & Information</b>

🤖 <b>Available Commands:</b>
/start - Start the bot
/help - Show this help

📋 <b>Menu Options:</b>
🏪 Services - View our printing services
🛒 Order - Place an order
💬 Contact - Get our contact information  
❓ Help - Show this help

📞 <b>Contact Information:</b>
📧 {self.business_email}
📱 {self.business_phone}
💬 {self.business_username}

💡 <b>Tip:</b> Just type your message and we'll get it directly!
            """
        
        await self.send_message(chat_id, help_text)

    async def run_bot(self):
        """Main bot polling loop"""
        logger.info("🤖 Starting enhanced bot polling...")
        self.running = True
        offset = 0
        
        while self.running:
            try:
                updates = await self.get_updates(offset)
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        await self.handle_message(update['message'])
                
                # Small delay to prevent overwhelming the API
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Bot polling error: {e}")
                await asyncio.sleep(5)  # Wait before retrying

def start_health_server():
    """Start Flask health check server"""
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'simple-telegram-bot',
            'timestamp': datetime.now().isoformat()
        }
    
    @app.route('/')
    def home():
        return {
            'service': 'KalNetworks Telegram Bot',
            'status': 'running',
            'timestamp': datetime.now().isoformat()
        }
    
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"✅ Health server starting on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def run_bot_async():
    """Run bot in async event loop"""
    try:
        bot = SimpleBot()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.run_bot())
    except Exception as e:
        logger.error(f"❌ Async bot error: {e}")

def main():
    """Main function for enhanced bot deployment"""
    start_time = time.time()
    logger.info("🤖 RENDER ENHANCED BOT DEPLOYMENT")
    logger.info("=" * 50)
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Environment check
        if not check_environment():
            logger.error("❌ Environment check failed")
            sys.exit(1)
        
        logger.info("🎯 Mode: ENHANCED BOT SERVICE (Fixed Menu Handling)")
        
        # Start bot in background thread
        logger.info("🤖 Starting bot thread...")
        bot_thread = threading.Thread(target=run_bot_async, daemon=True)
        bot_thread.start()
        
        # Start health server in main thread (required by Render)
        start_health_server()
    
    except KeyboardInterrupt:
        logger.info("🛑 Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        elapsed = time.time() - start_time
        logger.info(f"⏱️ Total runtime: {elapsed:.2f} seconds")

if __name__ == '__main__':
    main()