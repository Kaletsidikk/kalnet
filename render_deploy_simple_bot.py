#!/usr/bin/env python3
"""
Simple Render Bot Deployment - No Updater Issues
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
    """Enhanced bot implementation with all features but no Updater issues"""
    
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
        """Handle incoming message"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user = message.get('from', {})
            first_name = user.get('first_name', 'User')
            
            logger.info(f"📨 Message from {first_name} ({chat_id}): {text}")
            
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
                
            elif text in ['🏪 Services', '🛒 Order', '💬 Contact', '❓ Help', '🏪 አገልግሎቶች', '🛒 ትዕዛዝ', '💬 ያነጋግሩን', '❓ እርዳታ']:
                await self.handle_menu_selection(chat_id, text)
                
            else:
                # Forward message to admin
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
        """Show available services"""
        if lang == 'am':
            services_text = (
                f"🏪 {self.business_name} - አገልግሎቶች\n\n"
                "🖨️ የንግድ ካርዶች - ከ 25 ብር ጀምሮ\n"
                "📄 ፍላየሮች እና ብሮሽዎች - ከ 50 ብር ጀምሮ\n"
                "🎯 ባነሮች እና ፖስተሮች - ከ 75 ብር ጀምሮ\n"
                "📚 መጽሐፍ እና ካታሎጎች - ከ 100 ብር ጀምሮ\n"
                "🏷️ ስቲከሮች እና ሌብሎች - ከ 30 ብር ጀምሮ\n"
                "⭐ ልዩ ፕሮጀክቶች - ዋጋ በጥያቄ መሰረት\n\n"
                "📞 ለዝርዝር ዋጋ ይደውሉልን!"
            )
        else:
            services_text = (
                f"🏪 {self.business_name} - Services\n\n"
                "🖨️ Business Cards - from 25 ETB\n"
                "📄 Flyers & Brochures - from 50 ETB\n"
                "🎯 Banners & Posters - from 75 ETB\n"
                "📚 Booklets & Catalogs - from 100 ETB\n"
                "🏷️ Stickers & Labels - from 30 ETB\n"
                "⭐ Custom Projects - Quote on request\n\n"
                "📞 Contact us for detailed quotes!"
            )
        
        await self.send_message(chat_id, services_text)
    
    async def show_order_info(self, chat_id, lang='en'):
        """Show order information"""
        if lang == 'am':
            order_text = (
                "🛒 ትዕዛዝ ያድርጉ\n\n"
                "ትዕዛዝ ለማድረግ እባክዎን ያቅርቡ:\n"
                "• የሚፈልጉት አገልግሎት ዓይነት\n"
                "• የሚሹት መጠን\n"
                "• የእርስዎ የመገናኛ መረጃ\n"
                "• ማናቸውንም ልዩ መስፈርቶች\n\n"
                "📞 ያነጋግሩን:\n"
                f"📧 {self.business_email}\n"
                f"📱 {self.business_phone}\n"
                f"💬 {self.business_username}\n\n"
                "ወይም እዚህ መልዕክት ይላኩልን!"
            )
        else:
            order_text = (
                "🛒 Place Your Order\n\n"
                "To place an order, please provide:\n"
                "• Service type you need\n"
                "• Quantity required\n"
                "• Your contact information\n"
                "• Any special requirements\n\n"
                "📞 Contact us:\n"
                f"📧 {self.business_email}\n"
                f"📱 {self.business_phone}\n"
                f"💬 {self.business_username}\n\n"
                "Or just send us a message here!"
            )
        
        await self.send_message(chat_id, order_text)
    
    async def show_contact(self, chat_id, lang='en'):
        """Show contact information"""
        if lang == 'am':
            contact_text = (
                f"💬 {self.business_name}ን ያነጋግሩ\n\n"
                f"📧 ኢሜይል: {self.business_email}\n"
                f"📱 ስልክ: {self.business_phone}\n"
                f"💬 ቴሌግራም: {self.business_username}\n\n"
                "💡 እዚህ ቀጥተኛ መልዕክትም መላክ ይችላሉ!"
            )
        else:
            contact_text = (
                f"💬 Contact {self.business_name}\n\n"
                f"📧 Email: {self.business_email}\n"
                f"📱 Phone: {self.business_phone}\n"
                f"💬 Telegram: {self.business_username}\n\n"
                "💡 You can also send us a message directly here!"
            )
        
        await self.send_message(chat_id, contact_text)
    
    async def show_help(self, chat_id, lang=None):
        """Show help information"""
        if lang is None:
            lang = self.user_languages.get(chat_id, 'en')
        
        if lang == 'am':
            help_text = (
                "❓ እርዳታ እና መረጃ\n\n"
                "🤖 አቮቸብ ትዕዛዞች:\n"
                "/start - ቦቱን ጀምር\n"
                "/help - ይህንን እርዳታ አሳይ\n\n"
                "📋 የመዝገብ አማራጮች:\n"
                "🏪 አገልግሎቶች - የማተሚያ አገልግሎቶቻችንን ይመልከቱ\n"
                "🛒 ትዕዛዝ - ትዕዛዝ ያድርጉ\n"
                "💬 ያነጋግሩን - የእኛን የመገናኛ መረጃ ያግኙ\n"
                "❓ እርዳታ - ይህንን እርዳታ አሳይ\n\n"
                "💡 ጠቃሚ ምክር: መልዕክትዎን ብቻ ይተይቡ እና በቀጥታ እንቀበላለን!"
            )
        else:
            help_text = (
                "❓ Help & Information\n\n"
                "🤖 Available Commands:\n"
                "/start - Start the bot\n"
                "/help - Show this help\n\n"
                "📋 Menu Options:\n"
                "🏪 Services - View our printing services\n"
                "🛒 Order - Place an order\n"
                "💬 Contact - Get our contact information\n"
                "❓ Help - Show this help\n\n"
                "💡 Tip: Just type your message and we'll get it directly!"
            )
        
        await self.send_message(chat_id, help_text)

    async def run_bot(self):
        """Main bot polling loop"""
        logger.info("🤖 Starting simple bot polling...")
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
    """Main function for simple bot deployment"""
    start_time = time.time()
    logger.info("🤖 RENDER SIMPLE BOT DEPLOYMENT")
    logger.info("=" * 50)
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Environment check
        if not check_environment():
            logger.error("❌ Environment check failed")
            sys.exit(1)
        
        logger.info("🎯 Mode: SIMPLE BOT SERVICE")
        
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
