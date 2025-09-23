#!/usr/bin/env python3
"""
Enhanced Render Bot Deployment - Fixed Version for 24/7 Operation
Uses Flask's built-in server (no waitress dependency)
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
        
        # Define ALL menu options from your test_bot.py
        self.menu_options = [
            # English menu options
            '🏪 View Services', '🛒 Place Order', '📅 Schedule Consultation', 
            '💬 Contact Us', '📢 Updates Channel', '❓ Help & Info',
            # Amharic menu options  
            '🏪 አገልግሎቶች', '🛒 ትዕዛዝ ይስጡ', '📅 ቀጠሮ ይያዙ',
            '💬 ያነጋግሩን', '📢 መረጃ ቻናል', '❓ እርዳታ'
        ]
        
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
                        error_text = await response.text()
                        logger.error(f"❌ Failed to send message: {response.status} - {error_text}")
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
                    elif response.status == 409:
                        logger.error("❌ 409 Conflict: Another bot instance is running")
                        # Try to clear webhook
                        await self.clear_webhook()
                        return []
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to get updates: {response.status} - {error_text}")
                        return []
        except Exception as e:
            logger.error(f"❌ Error getting updates: {e}")
            return []

    async def clear_webhook(self):
        """Clear any existing webhook - FIXED VERSION"""
        import aiohttp
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/deleteWebhook"
            # Fixed: Remove problematic boolean parameter
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    if response.status == 200:
                        logger.info("✅ Webhook cleared successfully")
                    else:
                        logger.warning("⚠️ Could not clear webhook")
        except Exception as e:
            logger.warning(f"⚠️ Webhook clear attempt failed: {e}")

    async def handle_message(self, message):
        """Handle incoming message with proper menu handling"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user = message.get('from', {})
            first_name = user.get('first_name', 'User')
            
            logger.info(f"📨 Message from {first_name} ({chat_id}): {text}")
            
            # Check if it's a menu button click first
            if text in self.menu_options:
                logger.info(f"🎯 Menu option detected: {text}")
                await self.handle_menu_selection(chat_id, text)
                return  # Important: return after handling menu selection
                
            if text.startswith('/start'):
                await self.handle_start(chat_id, first_name)
                
            elif text.startswith('/help'):
                await self.show_help(chat_id)
                
            elif text.startswith('/reply') and str(chat_id) == str(self.admin_chat_id):
                await self.handle_admin_reply(text)
                
            elif self.user_states.get(chat_id) == 'awaiting_language':
                await self.handle_language_selection(chat_id, text)
                
            else:
                await self.handle_regular_message(chat_id, text, user, first_name)
                
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            logger.error(traceback.format_exc())
    
    async def handle_start(self, chat_id, first_name):
        """Handle /start command"""
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
    
    async def handle_language_selection(self, chat_id, text):
        """Handle language selection"""
        if text.lower().startswith('en'):
            self.user_languages[chat_id] = 'en'
            await self.send_message(chat_id, "🇺🇸 English selected! Showing main menu...")
        elif text.lower().startswith('am'):
            self.user_languages[chat_id] = 'am'
            await self.send_message(chat_id, "🇪🇹 አማርኛ መርጠዋል! ዋና ሜኑ እያሳየ ነው...")
        else:
            await self.send_message(chat_id, "Please reply with 'en' or 'am' / እባክዎን 'en' ወይም 'am' ይላኩ")
            return
        
        self.user_states[chat_id] = None
        await self.show_main_menu(chat_id)
    
    async def handle_regular_message(self, chat_id, text, user, first_name):
        """Handle regular user messages"""
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
    
    async def handle_admin_reply(self, text):
        """Handle admin reply command"""
        try:
            parts = text.split(' ', 2)
            if len(parts) >= 3:
                target_chat_id = parts[1]
                reply_message = parts[2]
                
                await self.send_message(target_chat_id, f"📩 <b>Reply from {self.business_name}:</b>\n\n{reply_message}")
                await self.send_message(self.admin_chat_id, f"✅ Reply sent to {target_chat_id}")
            else:
                await self.send_message(self.admin_chat_id, "❌ Usage: /reply CHAT_ID your_message")
        except Exception as e:
            logger.error(f"❌ Error handling admin reply: {e}")
            await self.send_message(self.admin_chat_id, f"❌ Error sending reply: {e}")
                
    async def show_main_menu(self, chat_id):
        """Show main menu based on user's language"""
        lang = self.user_languages.get(chat_id, 'en')
        
        if lang == 'am':
            menu_text = (
                f"🎉 ወደ {self.business_name} እንኳን በደህና መጡ!\n\n"
                "🎯 ዛሬ እንዴት ልረዳዎት ችላለሁ?\n\n"
                "ከታች ያሉትን አማራጮች ይጠቀሙ:"
            )
        else:
            menu_text = (
                f"🎉 Welcome to {self.business_name}!\n\n"
                "🎯 How can I help you today?\n\n"
                "Use the options below:"
            )
        
        await self.send_message(chat_id, menu_text)
    
    async def handle_menu_selection(self, chat_id, text):
        """Handle menu button selections"""
        logger.info(f"🔄 Handling menu selection: {text}")
        
        lang = self.user_languages.get(chat_id, 'en')
        
        # Map menu options to handlers
        menu_handlers = {
            # English handlers
            '🏪 View Services': self.show_services,
            '🛒 Place Order': self.show_order_info,
            '📅 Schedule Consultation': self.show_schedule_info,
            '💬 Contact Us': self.show_contact_info,
            '📢 Updates Channel': self.show_channel_info,
            '❓ Help & Info': self.show_help,
            # Amharic handlers
            '🏪 አገልግሎቶች': self.show_services,
            '🛒 ትዕዛዝ ይስጡ': self.show_order_info,
            '📅 ቀጠሮ ይያዙ': self.show_schedule_info,
            '💬 ያነጋግሩን': self.show_contact_info,
            '📢 መረጃ ቻናል': self.show_channel_info,
            '❓ እርዳታ': self.show_help
        }
        
        handler = menu_handlers.get(text)
        if handler:
            await handler(chat_id, lang)
        else:
            logger.warning(f"❌ No handler found for menu option: {text}")
            await self.send_message(chat_id, "Sorry, I didn't understand that option. Please try again.")
    
    async def show_services(self, chat_id, lang='en'):
        """Show available services"""
        if lang == 'am':
            services_text = f"""
🏪 <b>{self.business_name} - የእኛ አገልግሎቶች</b>

🖨️ <b>የንግድ ካርዶች</b>
• የሙያ ካርዶች፣ የተለያዩ አማራጮች
• 💰 ከ25 ብር ጀምሮ

📄 <b>ፍላየሮች እና ብሮሽሮች</b>
• የማርኬቲንግ ቁሳቁሶች፣ ሙሉ ቀለም
• 💰 ከ50 ብር ጀምሮ

🎯 <b>ባነሮች እና ፖስተሮች</b>
• ትላልቅ ህትመቶች፣ የውስጥ እና የውጭ አማራጮች
• 💰 ከ75 ብር ጀምሮ

📚 <b>መጽሐፍት እና ካታሎጎች</b>
• ብዙ ገፅ ሰነዶች፣ የማሰሪያ አማራጮች
• 💰 ከ100 ብር ጀምሮ

🏷️ <b>ስቲከሮች እና ሌብሎች</b>
• ዝርዝር የተለያዩ ቅርጾች እና ስፋቶች
• 💰 ከ30 ብር ጀምሮ

⭐ <b>ልዩ ፕሮጀክቶች</b>
• ልዩ መስፈርቶች፣ የግል አገልግሎት
• 💰 በጥያቄዎ መሰረት ዋጋ

📞 <i>ለዝርዝር ዋጋዎች እና ልዩ መስፈርቶች ያነጋግሩን!</i>
            """
        else:
            services_text = f"""
🏪 <b>{self.business_name} - Services</b>

🖨️ <b>Business Cards</b>
• Professional cards, various options
• 💰 from 25 ETB

📄 <b>Flyers & Brochures</b>
• Marketing materials, full color
• 💰 from 50 ETB

🎯 <b>Banners & Posters</b>
• Large prints, indoor & outdoor options
• 💰 from 75 ETB

📚 <b>Booklets & Catalogs</b>
• Multi-page documents, binding options
• 💰 from 100 ETB

🏷️ <b>Stickers & Labels</b>
• Various shapes and sizes
• 💰 from 30 ETB

⭐ <b>Custom Projects</b>
• Special requirements, personalized service
• 💰 Quote on request

📞 <i>Contact us for detailed quotes and special requirements!</i>
            """
        
        await self.send_message(chat_id, services_text)
    
    async def show_order_info(self, chat_id, lang='en'):
        """Show order information"""
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
    
    async def show_schedule_info(self, chat_id, lang='en'):
        """Show schedule consultation information"""
        if lang == 'am':
            schedule_text = f"""
📅 <b>ቀጠሮ ያስይዙ</b>

የእርስዎን የህትመት ፍላጎቶች ለመወያየት ዝግጁ ነኝ!

እባክዎን ያቅርቡ:
• የሚመርጡትን ቀን/ሰአት
• የመገኛ መረጃ
• የእርስዎ ፕሮጀክት አጭር መግለጫ

💬 ይህንን መረጃ በመልእክት መላክ ይቻላል!
            """
        else:
            schedule_text = f"""
📅 <b>Schedule Consultation</b>

I'd love to discuss your printing needs!

Please provide:
• Your preferred date/time
• Contact information
• Brief description of your project

💬 You can send this info as a message!
            """
        
        await self.send_message(chat_id, schedule_text)
    
    async def show_contact_info(self, chat_id, lang='en'):
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
    
    async def show_channel_info(self, chat_id, lang='en'):
        """Show updates channel information"""
        if lang == 'am':
            channel_text = f"""
📢 <b>የመረጃ ቻናል</b>

ተዘጋጅተው ይቆዩ ለ:
• 🆕 አዲስ የአገልግሎቶች ማሳወቂያዎች
• 💰 ልዩ ቅናሾች እና ቅናሾች
• 📸 የቅርብ ጊዜ ስራዎች ማሻያ
• 💡 የህትመት ምክሮች እና ዘዴዎች

🔔 <i>ልዩ ቅናሾችን አያምለጡ!</i>
            """
        else:
            channel_text = f"""
📢 <b>Updates Channel</b>

Stay tuned for:
• 🆕 New service announcements
• 💰 Special discounts and offers
• 📸 Recent work showcases
• 💡 Printing tips and techniques

🔔 <i>Don't miss special discounts!</i>
            """
        
        await self.send_message(chat_id, channel_text)
    
    async def show_help(self, chat_id, lang=None):
        """Show help information"""
        if lang is None:
            lang = self.user_languages.get(chat_id, 'en')
        
        if lang == 'am':
            help_text = f"""
❓ <b>እርዳታ እና መረጃ</b>

🤖 <b>የሚገኙ ትዕዛዞች:</b>
/start - ቦቱን ጀምር
/help - ይህንን እርዳታ አሳይ

📋 <b>የሜኑ አማራጮች:</b>
🏪 አገልግሎቶች - የማተሚያ አገልግሎቶቻችንን ይመልከቱ
🛒 ትዕዛዝ ይስጡ - ትዕዛዝ ያድርጉ
📅 ቀጠሮ ይያዙ - ውይይት ያስይዙ
💬 ያነጋግሩን - የእኛን የመገናኛ መረጃ ያግኙ
📢 መረጃ ቻናል - የቅርብ ጊዜ ማሳወቂያዎች
❓ እርዳታ - ይህንን እርዳታ አሳይ

💡 <b>ጠቃሚ ምክር:</b> መልዕክትዎን ብቻ ይተይቡ እና በቀጥታ እንቀበላለን!
            """
        else:
            help_text = f"""
❓ <b>Help & Information</b>

🤖 <b>Available Commands:</b>
/start - Start the bot
/help - Show this help

📋 <b>Menu Options:</b>
🏪 View Services - View our printing services
🛒 Place Order - Place an order
📅 Schedule Consultation - Book a consultation
💬 Contact Us - Get our contact information
📢 Updates Channel - Recent announcements
❓ Help & Info - Show this help

💡 <b>Tip:</b> Just type your message and we'll get it directly!
            """
        
        await self.send_message(chat_id, help_text)

    async def run_bot(self):
        """Main bot polling loop with enhanced error recovery"""
        logger.info("🤖 Starting enhanced bot polling...")
        self.running = True
        offset = 0
        
        # Clear webhook first to avoid conflicts
        await self.clear_webhook()
        
        error_count = 0
        max_errors = 10
        
        while self.running:
            try:
                updates = await self.get_updates(offset)
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        await self.handle_message(update['message'])
                
                # Reset error count on successful iteration
                error_count = 0
                # Small delay to prevent overwhelming the API
                await asyncio.sleep(0.5)
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Bot polling error #{error_count}: {e}")
                
                if error_count >= max_errors:
                    logger.error("🚨 Too many consecutive errors, restarting bot...")
                    await asyncio.sleep(30)  # Wait longer before restart
                    error_count = 0
                
                await asyncio.sleep(5)  # Wait before retrying

def start_health_server():
    """Start Flask health check server - FIXED (no waitress)"""
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
    
    # Use Flask's built-in server (no waitress dependency)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

def run_bot_async():
    """Run bot in async event loop"""
    try:
        bot = SimpleBot()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.run_bot())
    except Exception as e:
        logger.error(f"❌ Async bot error: {e}")
        logger.error(traceback.format_exc())

def main():
    """Main function for enhanced bot deployment - FIXED for 24/7 operation"""
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
        
        logger.info("🎯 Mode: ENHANCED BOT SERVICE (24/7 Fixed)")
        
        # Start health server in a separate thread
        logger.info("🌐 Starting health server thread...")
        server_thread = threading.Thread(target=start_health_server, daemon=True)
        server_thread.start()
        
        # Give server time to start
        time.sleep(3)
        
        # Run bot in the main thread (this will keep the process alive)
        logger.info("🤖 Starting bot in main thread...")
        run_bot_async()
    
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