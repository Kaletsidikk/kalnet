#!/usr/bin/env python3
"""
Enhanced Telegram Bot for Printing Business Platform
With multi-language support and admin features - Complete working version
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TelegramError, NetworkError, BadRequest

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
BUSINESS_NAME = os.getenv('BUSINESS_NAME', 'KalNetworks – Printing & Business Solutions')
BUSINESS_EMAIL = os.getenv('BUSINESS_EMAIL', 'gebeyatechnologies@gmail.com')
BUSINESS_PHONE = os.getenv('BUSINESS_PHONE', '0965552595')
BUSINESS_ADDRESS = os.getenv('BUSINESS_ADDRESS', 'KalNetworks Business Center')
BUSINESS_USERNAME = os.getenv('BUSINESS_USERNAME', '@ABISSINIANJA')

# Enhanced logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class EnhancedPrintingBot:
    """Enhanced bot class with multi-language support"""
    
    def __init__(self):
        self.admin_chat_id = self.setup_admin_chat_id()
        self.user_languages = {}  # Store user language preferences
        
    def setup_admin_chat_id(self):
        """Setup admin chat ID with validation"""
        try:
            admin_id = os.getenv('ADMIN_CHAT_ID')
            if admin_id and admin_id != "your_telegram_user_id_here":
                admin_id = int(admin_id)
                logger.info(f"Admin chat ID set to: {admin_id}")
                return admin_id
            else:
                logger.warning("Admin chat ID not properly configured")
                return None
        except (ValueError, TypeError):
            logger.error("Invalid ADMIN_CHAT_ID format")
            return None

    async def start_command(self, update: Update, context) -> None:
        """Enhanced /start command with language selection and user ID detection"""
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"User {user.first_name} ({user_id}) started the bot")
        
        # If this is the first time and no admin is set, ask if they're the admin
        if self.admin_chat_id is None or self.admin_chat_id == 123456789:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("👤 Yes, I'm the Owner", callback_data=f"set_admin_{user_id}")],
                [InlineKeyboardButton("👋 I'm a Customer", callback_data="customer_start")]
            ])
            
            await update.message.reply_text(
                f"🤖 <b>Welcome to {BUSINESS_NAME}!</b>\n"
                f"🇪🇹 <b>ወደ {BUSINESS_NAME} እንኳን በደህና መጡ!</b>\n\n"
                f"👤 <b>Your Telegram User ID / የእርስዎ ቴሌግራም መለያ:</b> <code>{user_id}</code>\n\n"
                "❓ Are you the business owner setting up this bot?\n"
                "❓ እርስዎ የዚህ ቦት ባለቤት ነዎት?",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            return
        if user_id not in self.user_languages:
            await self.show_language_selection(update, context)
        else:
            # Regular customer start with selected language
            await self.customer_welcome(update, context)
    
    async def show_language_selection(self, update: Update, context) -> None:
        """Show language selection to new users"""
        user = update.effective_user
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇪🇹 አማርኛ (Amharic)", callback_data="lang_am")]
        ])
        
        welcome_text = f"""
🌍 <b>Welcome to {BUSINESS_NAME}!</b>
🇪🇹 <b>ወደ {BUSINESS_NAME} እንኳን በደህና መጡ!</b>

👋 Hi <b>{user.first_name}</b>! Please choose your preferred language:
👋 ሰላም <b>{user.first_name}</b>! እባክዎን ቋንቋ ይምረጡ:

🌐 Choose your language / ቋንቋ ይምረጡ:
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def customer_welcome(self, update: Update, context) -> None:
        """Welcome message for customers with language support"""
        user = update.effective_user
        user_id = user.id
        
        # Get user's language preference (default to Amharic if not set)
        user_lang = self.user_languages.get(user_id, 'am')
        
        if user_lang == 'en':
            # English main menu
            main_menu = [
                ['🏪 View Services', '🛒 Place Order'],
                ['📅 Schedule Consultation', '💬 Contact Us'],
                ['📢 Updates Channel', '❓ Help & Info']
            ]
            
            welcome_text = f"""
🎉 <b>Welcome to {BUSINESS_NAME}!</b>

👋 Hi <b>{user.first_name}</b>! I'm your printing assistant.

🎯 <b>What I can help you with:</b>
🏪 <b>View Services</b> - See our printing offerings
🛒 <b>Place Order</b> - Quick & easy ordering
📅 <b>Schedule Consultation</b> - Book a meeting
💬 <b>Contact Us</b> - Direct messaging
📢 <b>Updates Channel</b> - Latest news & offers

🚀 <i>Choose an option below to get started!</i>
            """
        else:
            # Amharic main menu
            main_menu = [
                ['🏪 አገልግሎቶች', '🛒 ትዕዛዝ ይስጡ'],
                ['📅 ቀጠሮ ይያዙ', '💬 ያነጋግሩን'],
                ['📢 መረጃ ቻናል', '❓ እርዳታ']
            ]
            
            welcome_text = f"""
🎉 <b>ወደ {BUSINESS_NAME} እንኳን በደህና መጡ!</b>

👋 ሰላም <b>{user.first_name}</b>! እኔ የእርስዎ የህትመት አጋር ነኝ።

🎯 <b>ልረዳዎት የምችላቸው ነገሮች:</b>
🏪 <b>አገልግሎቶች</b> - የእኛን የህትመት አገልግሎቶች ይመልከቱ
🛒 <b>ትዕዛዝ ይስጡ</b> - ቀላል እና ፈጣን ትዕዛዝ
📅 <b>ቀጠሮ ይያዙ</b> - ቀጠሮ  ያስይዙ
💬 <b>ያነጋግሩን</b> - ቀጥተኛ መልእክት ይላኩ
📢 <b>መረጃ ቻናል</b> - የመጨረሻ ዜናዎች እና ቅናሾች

🚀 <i>ከታች ካሉት አማራጮች ይምረጡ!</i>
            """
        
        keyboard = ReplyKeyboardMarkup(
            main_menu,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def help_command(self, update: Update, context) -> None:
        """Enhanced help command with language support"""
        user = update.effective_user
        user_lang = self.user_languages.get(user.id, 'am')
        
        if user_lang == 'en':
            help_text = f"""
🤖 <b>{BUSINESS_NAME} - Help Guide</b>

📋 <b>Available Commands:</b>
/start - Start the bot and show main menu
/help - Show this help message
/status - Check bot status
/cancel - Cancel current operation

🎯 <b>Main Menu Options:</b>
🏪 <b>View Services</b> - Browse our printing services
🛒 <b>Place Order</b> - Start ordering process
📅 <b>Schedule Consultation</b> - Book a meeting
💬 <b>Contact Us</b> - Send us a message
📢 <b>Updates Channel</b> - Join our channel
❓ <b>Help & Info</b> - Business information

📞 <b>Contact Information:</b>
📧 Email: {BUSINESS_EMAIL}
📱 Phone: {BUSINESS_PHONE}
💬 Telegram: {BUSINESS_USERNAME}
📍 Address: {BUSINESS_ADDRESS}

💡 <b>Quick Tips:</b>
• Use the keyboard buttons for fastest navigation
• You can type /cancel anytime to go back to main menu
• All your inquiries are sent directly to our team

🆘 Need immediate help? Use "💬 Contact Us" option!
            """
        else:
            help_text = f"""
🤖 <b>{BUSINESS_NAME} - የእርዳታ መመሪያ</b>

📋 <b>የሚገኙ ትዕዛዞች:</b>
/start - ቦቱን ጀምሩ እና ዋና ሜኑ ይመልከቱ
/help - ይህንን የእርዳታ መልእክት ይመልከቱ
/status - የቦት ሁኔታ ይመልከቱ
/cancel - አሁኑኑን ተግባር ይሰርዙ

🎯 <b>የዋና ሜኑ አማራጮች:</b>
🏪 <b>አገልግሎቶች</b> - የእኛን የህትመት አገልግሎቶች ይመልከቱ
🛒 <b>ትዕዛዝ ይስጡ</b> - የትዕዛዝ ሂደት ይጀምሩ
📅 <b>ቀጠሮ ይያዙ</b> - ቀጠሮ ያስይዙ
💬 <b>ያነጋግሩን</b> - መልእክት ይላኩልን
📢 <b>መረጃ ቻናል</b> - ቻናላችንን ይቀላቀሉ
❓ <b>እርዳታ</b> - የቢዝነስ መረጃ

📞 <b>የመገኛ መረጃ:</b>
📧 ኢሜይል: {BUSINESS_EMAIL}
📱 ስልክ: {BUSINESS_PHONE}
💬 ቴሌግራም: {BUSINESS_USERNAME}
📍 አድራሻ: {BUSINESS_ADDRESS}

💡 <b>ጠቃሚ ምክሮች:</b>
• ለፈጣን መንቀሳቀስ የሚያስችሉ ቁልፎችን ይጠቀሙ
• በማንኛውም ጊዜ /cancel ብለው ወደ ዋና ሜኑ ይመለሱ
• ሁሉም ጥያቄዎችዎ በቀጥታ ወደ ቡድናችን ይላካሉ

🆘 ፈጣን እርዳታ ይፈልጋሉ? "💬 ያነጋግሩን" አማራጩን ይጠቀሙ!
        """
        
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def status_command(self, update: Update, context) -> None:
        """Bot status command"""
        status_text = f"""
📊 <b>የቦት ሁኔታ</b>

✅ ቦቱ በጥሩ ሁኔታ እየሰራ ነው
🤖 ስሪት: 2.0 የተሻሻለ አማርኛ
⏰ አሁኑን ጊዜ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🏪 ቢዝነስ: {BUSINESS_NAME}

🔧 <b>የሚገኙ ባህሪያት:</b>
✅ የአገልግሎት ካታሎግ
✅ የትዕዛዝ ጥያቄዎች
✅ የውይይት እይታ
✅ ቀጥተኛ መልእክት
✅ የቻናል ግንኙነት
✅ የተሻሻለ የተጠቃሚ በላይ

💚 <b>ሁሉም ስርዓቶች እየሰሩ ናቸው!</b>
        """
        
        await update.message.reply_text(status_text, parse_mode='HTML')

    async def view_services(self, update: Update, context) -> None:
        """Enhanced services view with better UI"""
        services_text = f"""
🏪 <b>{BUSINESS_NAME} - የእኛ አገልግሎቶች</b>

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
        
        # Enhanced action buttons in Amharic
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 አሁኑኑ ይመዝግቡ", callback_data="place_order")],
            [InlineKeyboardButton("📅 ቀጠሮ ያስይዙ", callback_data="schedule_consultation")],
            [InlineKeyboardButton("💬 ጥያቄ ይጠይቁ", callback_data="contact_us")],
            [InlineKeyboardButton("📧 ዋጋ ይጠይቁ", callback_data="get_quote")]
        ])
        
        await update.message.reply_text(services_text, parse_mode='HTML')
        
        await update.message.reply_text(
            "🎯 <b>ቀጥሎ ምን ማድረግ ይፈልጋሉ?</b>",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def handle_callback_query(self, update: Update, context) -> None:
        """Enhanced callback query handling"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("set_admin_"):
            user_id = query.data.split("_")[2]
            await self.set_admin_user(update, context, user_id)
        elif query.data == "customer_start":
            user_id = query.from_user.id
            if user_id not in self.user_languages:
                await query.edit_message_text("🎉 Great! Let me show you language options...")
                await self.show_language_selection(query, context)
            else:
                await query.edit_message_text("🎉 በጣም ጥሩ! አገልግሎቶቻችንን እናሳይዎታለን...")
                # Create a fake update object for customer_welcome
                fake_update = type('obj', (object,), {'effective_user': query.from_user, 'message': query.message})
                await self.customer_welcome(fake_update, context)
        elif query.data == "lang_en":
            user_id = query.from_user.id
            self.user_languages[user_id] = 'en'
            await query.edit_message_text("🇺🇸 <b>English selected!</b>\n\n🎉 Welcome! Let me show you our services...")
            # Create a fake update object for customer_welcome
            fake_update = type('obj', (object,), {'effective_user': query.from_user, 'message': query.message})
            await self.customer_welcome(fake_update, context)
        elif query.data == "lang_am":
            user_id = query.from_user.id
            self.user_languages[user_id] = 'am'
            await query.edit_message_text("🇪🇹 <b>አማርኛ መርጠዋል!</b>\n\n🎉 እንኳን በደህና መጡ! አገልግሎቶቻችንን እናሳይዎታለን...")
            # Create a fake update object for customer_welcome
            fake_update = type('obj', (object,), {'effective_user': query.from_user, 'message': query.message})
            await self.customer_welcome(fake_update, context)
        elif query.data == "place_order":
            await self.handle_order_callback(update, context)
        elif query.data == "schedule_consultation":
            await self.handle_schedule_callback(update, context)
        elif query.data == "contact_us":
            await self.handle_contact_callback(update, context)
        elif query.data == "get_quote":
            await query.edit_message_text(
                f"📧 <b>ዋጋ ይጠይቁ</b>\n\n"
                f"ለዝርዝር ዋጋዎች እባክዎን ያነጋግሩን:\n\n"
                f"📧 {BUSINESS_EMAIL}\n"
                f"📱 {BUSINESS_PHONE}\n\n"
                f"ወይም 💬 ያነጋግሩን አማራጩን ለፈጣን መልእክት ይጠቀሙ!",
                parse_mode='HTML'
            )
        # Add more callback handlers from test_bot.py...

    async def set_admin_user(self, update: Update, context, user_id: str):
        """Set the admin user ID"""
        try:
            # Update the .env file
            env_path = '.env'
            with open(env_path, 'r') as f:
                content = f.read()
            
            content = content.replace('ADMIN_CHAT_ID=123456789', f'ADMIN_CHAT_ID={user_id}')
            
            with open(env_path, 'w') as f:
                f.write(content)
            
            self.admin_chat_id = int(user_id)
            
            await update.callback_query.edit_message_text(
                f"✅ <b>እንኳን ደስ አለዎ! አሁን እርስዎ እንደ ቢዝነስ ባለቤት ተዋቅረዋል።</b>\n\n"
                f"🔧 የእርስዎ አድሚን መለያ ({user_id}) ተቀምጧል።\n"
                f"🎯 ሁሉንም የደንበኞች ማሳወቂያዎች ይደርስዎታል።\n"
                f"🔄 ልውጦችን እንዲተገበሩ ቦቱን እንደገና ያስጀምሩ።\n\n"
                f"🎉 <b>ወደ {BUSINESS_NAME} እንኳን በደህና መጡ!</b>",
                parse_mode='HTML'
            )
            
            logger.info(f"Admin user ID set to: {user_id}")
            
        except Exception as e:
            logger.error(f"Error setting admin user: {e}")
            await update.callback_query.edit_message_text(
                "❌ Error setting admin user. Please check the logs."
            )

    async def handle_order_callback(self, update: Update, context):
        """Handle order callback"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 የንግድ ካርዶች", callback_data="order_business_cards")],
            [InlineKeyboardButton("📄 ፍላየሮች/ብሮሽሮች", callback_data="order_flyers")],
            [InlineKeyboardButton("🎯 ባነሮች/ፖስተሮች", callback_data="order_banners")],
            [InlineKeyboardButton("📚 መጽሀፍት/ካታሎጎች", callback_data="order_booklets")],
            [InlineKeyboardButton("🏷️ ስቲከሮች/መለያዎች", callback_data="order_stickers")],
            [InlineKeyboardButton("⭐ ልዩ ፕሮጀክት", callback_data="order_custom")]
        ])
        
        await update.callback_query.edit_message_text(
            "🛒 <b>ትዕዛዝዎን ይስጡ</b>\n\n"
            "ምን ዓይነት የህትመት አገልግሎት ይፈልጋሉ?",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def handle_schedule_callback(self, update: Update, context):
        """Handle schedule callback"""
        await update.callback_query.edit_message_text(
            "📅 <b>ቀጠሮ ያስይዙ</b>\n\n"
            "የእርስዎን የህትመት ፍላጎቶች ለመወያየት ዝግጁ ነኝ!\n\n"
            "እባክዎን ያቅርቡ:\n"
            "• የሚመርጡትን ቀን/ሰአት\n"
            "• የመገኛ መረጃ\n"
            "• የእርስዎ ፕሮጀክት አጭር መግለጫ\n\n"
            "💬 ይህንን መረጃ በመልእክት መላክ ይቻላሉ፣ ወደ ቡድናችን እልካለሁ!",
            parse_mode='HTML'
        )

    async def handle_contact_callback(self, update: Update, context):
        """Handle contact callback"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📧 ኢሜይል ያድርጉን", callback_data="contact_email")],
            [InlineKeyboardButton("📱 ይደውሉልን", callback_data="contact_phone")],
            [InlineKeyboardButton("💬 ፈጣን መልእክት", callback_data="contact_message")]
        ])
        
        await update.callback_query.edit_message_text(
            f"💬 <b>{BUSINESS_NAME} ያነጋግሩ</b>\n\n"
            f"📧 ኢሜይል: {BUSINESS_EMAIL}\n"
            f"📱 ስልክ: {BUSINESS_PHONE}\n"
            f"💬 ቴሌግራም: {BUSINESS_USERNAME}\n"
            f"📍 አድራሻ: {BUSINESS_ADDRESS}\n\n"
            "እንዴት ማነጋገር ይፈልጋሉ?",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def handle_text_message(self, update: Update, context) -> None:
        """Enhanced text message handling"""
        text = update.message.text
        user = update.effective_user
        
        # Support both English and Amharic text handlers
        text_handlers = {
            # English handlers
            "🏪 View Services": self.view_services,
            "🛒 Place Order": self.handle_order_start,
            "📅 Schedule Consultation": self.handle_schedule_start,
            "💬 Contact Us": self.handle_contact_start,
            "📢 Updates Channel": self.view_channel,
            "❓ Help & Info": self.help_command,
            # Amharic handlers
            "🏪 አገልግሎቶች": self.view_services,
            "🛒 ትዕዛዝ ይስጡ": self.handle_order_start,
            "📅 ቀጠሮ ይያዙ": self.handle_schedule_start,
            "💬 ያነጋግሩን": self.handle_contact_start,
            "📢 መረጃ ቻናል": self.view_channel,
            "❓ እርዳታ": self.help_command
        }
        
        handler = text_handlers.get(text)
        if handler:
            await handler(update, context)
        else:
            # Handle user messages to admin
            if self.admin_chat_id:
                admin_message = f"""
📩 <b>New Customer Message for {BUSINESS_USERNAME}</b>
📩 <b>ከደንበኛ አዲስ መልእክት - {BUSINESS_USERNAME}</b>

👤 <b>Customer / ደንበኛ:</b> {user.first_name or 'Unknown'} {user.last_name or ''}
🆔 <b>User ID / የተጠቃሚ መለያ:</b> {user.id}
👥 <b>Username / የተጠቃሚ ስም:</b> @{user.username or 'No username'}

💬 <b>Message / መልእክት:</b>
{text}

⏰ <b>Time / ጊዜ:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📞 <b>Reply to customer via:</b>
📞 <b>መልስ ይስጡ በ:</b>
📧 Email: {BUSINESS_EMAIL}
📱 Phone: {BUSINESS_PHONE}
💬 Telegram: {BUSINESS_USERNAME}
                """
                
                try:
                    await context.bot.send_message(
                        chat_id=self.admin_chat_id,
                        text=admin_message,
                        parse_mode='HTML'
                    )
                    
                    user_lang = self.user_languages.get(user.id, 'am')
                    if user_lang == 'en':
                        success_msg = (
                            "✅ <b>Message sent successfully!</b>\n\n"
                            "Your message has been forwarded to our team. We'll get back to you soon!\n\n"
                            "💡 You can use the menu buttons below for quick actions."
                        )
                        menu_keyboard = [
                            ['🏪 View Services', '🛒 Place Order'],
                            ['📅 Schedule Consultation', '💬 Contact Us'],
                            ['📢 Updates Channel', '❓ Help & Info']
                        ]
                    else:
                        success_msg = (
                            "✅ <b>መልእክት በተሳካ ሁኔታ ተልኳል!</b>\n\n"
                            "መልእክትዎ ወደ ቡድናችን ተልኳል። ብዙም ሳንዘገይ መልስ እንሰጣለን!\n\n"
                            "💡 ለፈጣን እርጃዎች ከታች ያሉትን የሜኑ ቁልፎች መጠቀም ይችላሉ።"
                        )
                        menu_keyboard = [
                            ['🏪 አገልግሎቶች', '🛒 ትዕዛዝ ይስጡ'],
                            ['📅 ቀጠሮ ይያዙ', '💬 ያነጋግሩን'],
                            ['📢 መረጃ ቻናል', '❓ እርዳታ']
                        ]
                    
                    await update.message.reply_text(
                        success_msg,
                        reply_markup=ReplyKeyboardMarkup(
                            menu_keyboard,
                            resize_keyboard=True,
                            one_time_keyboard=False
                        ),
                        parse_mode='HTML'
                    )
                except Exception as e:
                    logger.error(f"Error forwarding message to admin: {e}")
                    await update.message.reply_text(
                        "❌ ይቅርታ፣ መልእክትዎን ማድረስ አልተቻለም። እባክዎን በቀጥታ ያነጋግሩን:\n\n"
                        f"📧 {BUSINESS_EMAIL}\n"
                        f"📱 {BUSINESS_PHONE}"
                    )

    async def handle_order_start(self, update: Update, context):
        """Handle order start"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 የንግድ ካርዶች", callback_data="order_business_cards")],
            [InlineKeyboardButton("📄 ፍላየሮች/ብሮሽሮች", callback_data="order_flyers")],
            [InlineKeyboardButton("🎯 ባነሮች/ፖስተሮች", callback_data="order_banners")],
            [InlineKeyboardButton("📚 መጽሀፍት/ካታሎጎች", callback_data="order_booklets")],
            [InlineKeyboardButton("🏷️ ስቲከሮች/መለያዎች", callback_data="order_stickers")],
            [InlineKeyboardButton("⭐ ልዩ ፕሮጀክት", callback_data="order_custom")]
        ])
        
        await update.message.reply_text(
            "🛒 <b>ትዕዛዝዎን ይስጡ</b>\n\n"
            "ምን ዓይነት የህትመት አገልግሎት ይፈልጋሉ?",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def handle_schedule_start(self, update: Update, context):
        """Handle schedule start"""
        await update.message.reply_text(
            "📅 <b>ቀጠሮ ያስይዙ</b>\n\n"
            "የእርስዎን የህትመት ፍላጎቶች ለመወያየት ዝግጁ ነኝ!\n\n"
            "እባክዎን ያቅርቡ:\n"
            "• የሚመርጡትን ቀን/ሰአት\n"
            "• የመገኛ መረጃ\n"
            "• የእርስዎ ፕሮጀክት አጭር መግለጫ\n\n"
            "💬 ይህንን መረጃ በመልእክት መላክ ይቻላሉ፣ ወደ ቡድናችን እልካለሁ!",
            parse_mode='HTML'
        )

    async def handle_contact_start(self, update: Update, context):
        """Handle contact start"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📧 ኢሜይል ያድርጉን", callback_data="contact_email")],
            [InlineKeyboardButton("📱 ይደውሉልን", callback_data="contact_phone")],
            [InlineKeyboardButton("💬 ፈጣን መልእክት", callback_data="contact_message")]
        ])
        
        await update.message.reply_text(
            f"💬 <b>{BUSINESS_NAME} ያነጋግሩ</b>\n\n"
            f"📧 ኢሜይል: {BUSINESS_EMAIL}\n"
            f"📱 ስልክ: {BUSINESS_PHONE}\n"
            f"💬 ቴሌግራም: {BUSINESS_USERNAME}\n"
            f"📍 አድራሻ: {BUSINESS_ADDRESS}\n\n"
            "እንዴት ማነጋገር ይፈልጋሉ?",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def view_channel(self, update: Update, context) -> None:
        """Enhanced channel view"""
        if CHANNEL_USERNAME:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 ቻናላችንን ይቀላቀሉ", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
                [InlineKeyboardButton("🔔 ማሳወቂያዎችን ያግኙ", callback_data="enable_notifications")]
            ])
            
            await update.message.reply_text(
                f"📢 <b>ተዘጋጅተው ይቆዩ!</b>\n\n"
                f"🎯 ቻናላችንን ይቀላቀሉ ለ:\n"
                f"• 🆕 አዲስ የአገልግሎቶች ማሳወቂያዎች\n"
                f"• 💰 ልዩ ቅናሾች እና ቅናሾች\n"
                f"• 📸 የቅርብ ጊዜ ስራዎች ማሻያ\n"
                f"• 💡 የህትመት ምክሮች እና ዘዴዎች\n\n"
                f"📱 ቻናል: {CHANNEL_USERNAME}\n\n"
                f"🔔 <i>ልዩ ቅናሾችን አያምለጡ!</i>",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                "📢 <b>የመረጃ ቻናል</b>\n\n"
                "የእኛ የመረጃ ቻናል በቅርቡ ይመጣል!\n"
                "ለማሳወቂያዎች ጠብቁ:\n\n"
                "• 🆕 አዲስ አገልግሎቶች\n"
                "• 💰 ልዩ ቅናሾች\n"
                "• 📸 ስራ ማሻያ\n"
                "• 💡 የህትመት ምክሮች\n\n"
                "ዝግጁ ሲሆን እንገልጽዎታለን! 🚀",
                parse_mode='HTML'
            )

    def create_application(self) -> Application:
        """Create and configure the enhanced bot application"""
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Add text message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        return application

    async def error_handler(self, update: Update, context) -> None:
        """Enhanced error handling"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "🔧 <b>ችግር ደርሷል!</b>\n\n"
                    "በሂደት ላይ ነን! እባክዎን እንደገና ይሞክሩ ወይም ድጋፍን ያነጋግሩ።\n\n"
                    "💡 ምክር: ወደ ዋና ሜኑ ለመመለስ /start ይጠቀሙ።",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Error sending error message: {e}")

async def set_bot_commands(application: Application):
    """Set bot commands for the menu"""
    commands = [
        BotCommand("start", "🚀 ቦቱን ጀምሩ"),
        BotCommand("help", "❓ እርዳታ ያግኙ"),
        BotCommand("status", "📊 የቦት ሁኔታ"),
    ]
    
    try:
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.error(f"Error setting bot commands: {e}")

def main():
    """Main function to run the enhanced bot"""
    logger.info("🚀 የአማርኛ የህትመት ቢዝነስ ቦት በመጀምር ላይ...")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        sys.exit(1)
    
    try:
        bot = EnhancedPrintingBot()
        application = bot.create_application()
        
        # Add error handler
        application.add_error_handler(bot.error_handler)
        
        # Set bot commands
        async def post_init(app):
            await set_bot_commands(app)
        
        application.post_init = post_init
        
        logger.info("✅ Bot configured successfully!")
        logger.info(f"🏪 Business: {BUSINESS_NAME}")
        logger.info(f"📧 Contact: {BUSINESS_EMAIL}")
        logger.info(f"📱 Admin Chat ID: {bot.admin_chat_id}")
        logger.info("🔄 Starting polling...")
        
        # Start the bot with compatible settings
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
