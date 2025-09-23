#!/usr/bin/env python3
"""
Production-Ready Telegram Bot for Printing Business
Optimized for Render deployment with minimal dependencies
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Core telegram imports
try:
    from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
    from telegram.error import TelegramError
except ImportError as e:
    print(f"❌ Failed to import telegram: {e}")
    sys.exit(1)

# Environment variables
from dotenv import load_dotenv
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
BUSINESS_NAME = os.getenv('BUSINESS_NAME', 'KalNetworks – Printing & Business Solutions')
BUSINESS_EMAIL = os.getenv('BUSINESS_EMAIL', 'gebeyatechnologies@gmail.com')
BUSINESS_PHONE = os.getenv('BUSINESS_PHONE', '0965552595')
BUSINESS_USERNAME = os.getenv('BUSINESS_USERNAME', '@ABISSINIANJA')

# Production logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class ProductionBot:
    """Production-ready bot with essential features only"""
    
    def __init__(self):
        self.admin_chat_id = self.parse_admin_id()
        self.user_languages = {}
        
    def parse_admin_id(self):
        """Parse admin chat ID safely"""
        try:
            if ADMIN_CHAT_ID and ADMIN_CHAT_ID.isdigit():
                return int(ADMIN_CHAT_ID)
        except:
            pass
        return None

    async def start_command(self, update: Update, context) -> None:
        """Start command with language selection"""
        user = update.effective_user
        
        # Language selection
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am")]
        ])
        
        await update.message.reply_text(
            f"🤖 Welcome to {BUSINESS_NAME}!\n"
            f"🇪🇹 ወደ {BUSINESS_NAME} እንኳን በደህና መጡ!\n\n"
            "🌐 Choose your language / ቋንቋ ይምረጡ:",
            reply_markup=keyboard
        )

    async def handle_callback(self, update: Update, context) -> None:
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "lang_en":
            self.user_languages[query.from_user.id] = 'en'
            await self.show_menu(query, 'en')
        elif query.data == "lang_am":
            self.user_languages[query.from_user.id] = 'am'
            await self.show_menu(query, 'am')

    async def show_menu(self, query, lang):
        """Show main menu based on language"""
        if lang == 'en':
            menu = [
                ['🏪 Services', '🛒 Order'],
                ['💬 Contact', '❓ Help']
            ]
            text = f"🎉 Welcome to {BUSINESS_NAME}!\n\n🎯 How can I help you today?"
        else:
            menu = [
                ['🏪 አገልግሎቶች', '🛒 ትዕዛዝ'],
                ['💬 ያነጋግሩን', '❓ እርዳታ']
            ]
            text = f"🎉 ወደ {BUSINESS_NAME} እንኳን በደህና መጡ!\n\n🎯 ዛሬ እንዴት ልረዳዎት ችላለሁ?"
        
        keyboard = ReplyKeyboardMarkup(menu, resize_keyboard=True)
        await query.edit_message_text(text)
        await query.message.reply_text("👇 Use the menu below:", reply_markup=keyboard)

    async def handle_text(self, update: Update, context) -> None:
        """Handle text messages"""
        text = update.message.text
        user = update.effective_user
        
        # Menu handlers
        if text in ['🏪 Services', '🏪 አገልግሎቶች']:
            await self.show_services(update)
        elif text in ['🛒 Order', '🛒 ትዕዛዝ']:
            await self.show_order_info(update)
        elif text in ['💬 Contact', '💬 ያነጋግሩን']:
            await self.show_contact(update)
        elif text in ['❓ Help', '❓ እርዳታ']:
            await self.show_help(update)
        else:
            # Forward message to admin
            await self.forward_to_admin(update, context)

    async def show_services(self, update: Update):
        """Show services"""
        services_text = f"""🏪 {BUSINESS_NAME} - Services

🖨️ Business Cards - from 25 ETB
📄 Flyers & Brochures - from 50 ETB  
🎯 Banners & Posters - from 75 ETB
📚 Booklets & Catalogs - from 100 ETB
🏷️ Stickers & Labels - from 30 ETB
⭐ Custom Projects - Quote on request

📞 Contact us for detailed quotes!"""
        
        await update.message.reply_text(services_text)

    async def show_order_info(self, update: Update):
        """Show order information"""
        order_text = f"""🛒 Place Your Order

To place an order, please provide:
• Service type you need
• Quantity required  
• Your contact information
• Any special requirements

📞 Contact us:
📧 {BUSINESS_EMAIL}
📱 {BUSINESS_PHONE}
💬 {BUSINESS_USERNAME}

Or just send us a message here!"""
        
        await update.message.reply_text(order_text)

    async def show_contact(self, update: Update):
        """Show contact information"""
        contact_text = f"""💬 Contact {BUSINESS_NAME}

📧 Email: {BUSINESS_EMAIL}
📱 Phone: {BUSINESS_PHONE}  
💬 Telegram: {BUSINESS_USERNAME}

💡 You can also send us a message directly here!"""
        
        await update.message.reply_text(contact_text)

    async def show_help(self, update: Update):
        """Show help information"""
        help_text = f"""❓ Help & Information

🤖 Available Commands:
/start - Start the bot
/help - Show this help

📋 Menu Options:
🏪 Services - View our printing services
🛒 Order - Place an order
💬 Contact - Get our contact information
❓ Help - Show this help

💡 Tip: Just type your message and we'll get it directly!"""
        
        await update.message.reply_text(help_text)

    async def forward_to_admin(self, update: Update, context):
        """Forward user message to admin"""
        if not self.admin_chat_id:
            await update.message.reply_text(
                "✅ Message received! We'll get back to you soon.\n\n"
                f"📧 You can also email us: {BUSINESS_EMAIL}"
            )
            return
            
        user = update.effective_user
        admin_message = f"""📩 New Customer Message

👤 Customer: {user.first_name or 'Unknown'}
🆔 User ID: {user.id}
👥 Username: @{user.username or 'No username'}

💬 Message:
{update.message.text}

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Reply via: {BUSINESS_EMAIL} or {BUSINESS_PHONE}"""

        try:
            await context.bot.send_message(
                chat_id=self.admin_chat_id,
                text=admin_message
            )
            
            await update.message.reply_text(
                "✅ Message sent successfully!\n"
                "We'll get back to you soon! 🚀"
            )
        except Exception as e:
            logger.error(f"Failed to forward message: {e}")
            await update.message.reply_text(
                "✅ Message received! We'll contact you soon.\n\n"
                f"📧 Direct contact: {BUSINESS_EMAIL}"
            )

    async def help_command(self, update: Update, context):
        """Help command"""
        await self.show_help(update)

    async def error_handler(self, update: Update, context) -> None:
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "🔧 Something went wrong! Please try again or contact us directly.\n\n"
                    f"📧 {BUSINESS_EMAIL}"
                )
            except:
                pass

    def create_application(self):
        """Create the application"""
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not found!")
            raise ValueError("BOT_TOKEN is required")
        
        try:
            application = Application.builder().token(BOT_TOKEN).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CallbackQueryHandler(self.handle_callback))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
            
            logger.info("✅ Bot application created successfully")
            return application
            
        except Exception as e:
            logger.error(f"❌ Failed to create application: {e}")
            raise

def main():
    """Main function"""
    logger.info("🚀 Starting Production Bot")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment!")
        sys.exit(1)
    
    try:
        bot = ProductionBot()
        application = bot.create_application()
        application.add_error_handler(bot.error_handler)
        
        logger.info(f"🏪 Business: {BUSINESS_NAME}")
        logger.info(f"📧 Contact: {BUSINESS_EMAIL}")
        logger.info("🔄 Starting polling...")
        
        # Start the bot
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query']
        )
        
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
