#!/usr/bin/env python3
"""
Simple Telegram Bot for Printing Business
Compatible with Render deployment and python-telegram-bot v20+
"""

import os
import sys
import logging
import asyncio
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '1349142732')

# Business configuration
BUSINESS_NAME = "kalnetworks"
BUSINESS_EMAIL = "info@kalnetworks.com"
BUSINESS_PHONE = "+251911234567"
BUSINESS_ADDRESS = "Addis Ababa, Ethiopia"
CHANNEL_USERNAME = "@kalnetworks_et"

class SimplePrintingBot:
    """Simple printing business bot"""
    
    def __init__(self):
        self.admin_chat_id = ADMIN_CHAT_ID
        logger.info(f"Admin chat ID set to: {self.admin_chat_id}")

    async def start_command(self, update: Update, context) -> None:
        """Handle /start command"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 አገልግሎቶች", callback_data="services")],
            [InlineKeyboardButton("🛒 ይዘዙ", callback_data="order")],
            [InlineKeyboardButton("📅 ቀጠሮ", callback_data="schedule")],
            [InlineKeyboardButton("💬 ያንኳኩ", callback_data="contact")]
        ])
        
        welcome_message = (
            f"🎉 <b>እንኳን ወደ {BUSINESS_NAME} በደህና መጡ!</b>\n\n"
            "🖨️ <b>የተሟላ የህትመት አገልግሎት</b>\n\n"
            "📋 የምናቀርባቸው አገልግሎቶች:\n"
            "• 📄 ዶክመንት ህትመት\n"
            "• 💳 የንግድ ካርዶች\n"
            "• 🎯 ባነሮች እና ፖስተሮች\n"
            "• 📚 መጽሐፍቶች እና ካታሎጎች\n"
            "• 🏷️ ስቲከሮች እና ላቤሎች\n\n"
            "💡 ምን መምረጥ ይፈልጋሉ?"
        )
        
        await update.message.reply_text(
            welcome_message, 
            reply_markup=keyboard, 
            parse_mode='HTML'
        )

    async def help_command(self, update: Update, context) -> None:
        """Handle /help command"""
        help_text = (
            "❓ <b>እርዳታ</b>\n\n"
            "🤖 <b>የቦት አገልግሎቶች:</b>\n"
            "/start - ዋና ሜኑ\n"
            "/help - ይህ እርዳታ\n"
            "/status - የቦት ሁኔታ\n\n"
            "💡 <b>አገልግሎቶች:</b>\n"
            "📋 አገልግሎቶችን ይመልከቱ\n"
            "🛒 ቀጥታ ኦርደር ያድርጉ\n"
            "📅 ቀጠሮ ያስይዙ\n"
            "💬 እኛን ያንኳኩ\n\n"
            f"📧 ኢሜይል: {BUSINESS_EMAIL}\n"
            f"📱 ስልክ: {BUSINESS_PHONE}"
        )
        
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def status_command(self, update: Update, context) -> None:
        """Handle /status command"""
        status_text = (
            "📊 <b>የቦት ሁኔታ</b>\n\n"
            "✅ ቦት እየሰራ ነው\n"
            f"🕐 ጊዜ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🏪 ንግድ: {BUSINESS_NAME}\n"
            "🔄 ሁሉም ስርዓቶች መደበኛ"
        )
        
        await update.message.reply_text(status_text, parse_mode='HTML')

    async def handle_callback_query(self, update: Update, context) -> None:
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "services":
            await self.show_services(query)
        elif query.data == "order":
            await self.handle_order(query)
        elif query.data == "schedule":
            await self.handle_schedule(query)
        elif query.data == "contact":
            await self.handle_contact(query)

    async def show_services(self, query) -> None:
        """Show services menu"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 ዶክመንት ህትመት", callback_data="service_documents")],
            [InlineKeyboardButton("💳 የንግድ ካርዶች", callback_data="service_cards")],
            [InlineKeyboardButton("🎯 ባነሮች", callback_data="service_banners")],
            [InlineKeyboardButton("📚 መጽሐፍ/ካታሎግ", callback_data="service_books")],
            [InlineKeyboardButton("🔙 ወደ ዋና ሜኑ", callback_data="back_to_main")]
        ])
        
        text = (
            "📋 <b>የአገልግሎቶች ዝርዝር</b>\n\n"
            "📄 <b>ዶክመንት ህትመት</b> - ከ2 ብር\n"
            "💳 <b>የንግድ ካርዶች</b> - ከ50 ብር\n"
            "🎯 <b>ባነሮች</b> - ከ200 ብር\n"
            "📚 <b>መጽሐፍ/ካታሎግ</b> - ከ10 ብር\n"
            "🏷️ <b>ስቲከሮች</b> - ከ5 ብር\n\n"
            "💡 የትኛውን አገልግሎት ይመርጣሉ?"
        )
        
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')

    async def handle_order(self, query) -> None:
        """Handle order process"""
        text = (
            "🛒 <b>ኦርደር ማድረግ</b>\n\n"
            "እባክዎን የሚከተሉትን መረጃዎች ይላኩ:\n\n"
            "1️⃣ የሚፈልጉትን አገልግሎት\n"
            "2️⃣ መጠን/ብዛት\n"
            "3️⃣ የአጠናቃቂያ ቀን\n"
            "4️⃣ ልዩ መመሪያዎች\n"
            "5️⃣ የመገኛ አድራሻ\n\n"
            "📧 ወይም ኢሜይል ያድርጉን: " + BUSINESS_EMAIL + "\n"
            "📱 ወይም ይደውሉ: " + BUSINESS_PHONE
        )
        
        await query.edit_message_text(text, parse_mode='HTML')

    async def handle_schedule(self, query) -> None:
        """Handle schedule appointment"""
        text = (
            "📅 <b>ቀጠሮ ማስይዝ</b>\n\n"
            "የእርስዎን የህትመት ፍላጎቶች ለመወያየት ዝግጁ ነኝ!\n\n"
            "እባክዎን ያካትቱ:\n"
            "• የሚመርጡትን ቀን/ሰአት\n"
            "• የመገኛ መረጃ\n"
            "• የእርስዎ ፕሮጀክት አጭር መግለጫ\n\n"
            "💬 ይህንን መረጃ በመልእክት መላክ ይቻላሉ!\n\n"
            "📧 ወይም: " + BUSINESS_EMAIL + "\n"
            "📱 ወይም: " + BUSINESS_PHONE
        )
        
        await query.edit_message_text(text, parse_mode='HTML')

    async def handle_contact(self, query) -> None:
        """Handle contact information"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📧 ኢሜይል", url=f"mailto:{BUSINESS_EMAIL}")],
            [InlineKeyboardButton("📱 ስልክ", url=f"tel:{BUSINESS_PHONE}")],
            [InlineKeyboardButton("📢 ቻናል", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton("🔙 ወደ ዋና ሜኑ", callback_data="back_to_main")]
        ])
        
        text = (
            f"💬 <b>{BUSINESS_NAME} ያነጋግሩ</b>\n\n"
            f"📧 ኢሜይል: {BUSINESS_EMAIL}\n"
            f"📱 ስልክ: {BUSINESS_PHONE}\n"
            f"📍 አድራሻ: {BUSINESS_ADDRESS}\n"
            f"📢 ቻናል: {CHANNEL_USERNAME}\n\n"
            "እንዴት ማነጋገር ይፈልጋሉ?"
        )
        
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')

    async def handle_text_message(self, update: Update, context) -> None:
        """Handle text messages"""
        # Forward to admin
        if self.admin_chat_id and update.effective_user.id != int(self.admin_chat_id):
            try:
                await context.bot.send_message(
                    chat_id=self.admin_chat_id,
                    text=f"📩 <b>አዲስ መልእክት</b>\n\n"
                         f"👤 ከ: {update.effective_user.first_name}\n"
                         f"📱 ID: {update.effective_user.id}\n"
                         f"💬 መልእክት: {update.message.text}",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Error forwarding message: {e}")
        
        # Respond to user
        await update.message.reply_text(
            "✅ <b>መልእክትዎ ተደርሶናል!</b>\n\n"
            "🔄 በቅርቡ እንመልስዎታለን።\n"
            "⏰ መደበኛ መልስ ጊዜ: 1-2 ሰአት\n\n"
            "💡 ወደ ዋና ሜኑ ለመመለስ /start ይጫኑ",
            parse_mode='HTML'
        )

    async def error_handler(self, update: Update, context) -> None:
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "🔧 <b>ችግር ደርሷል!</b>\n\n"
                    "እባክዎን እንደገና ይሞክሩ ወይም ድጋፍን ያነጋግሩ።\n\n"
                    "💡 /start - ወደ ዋና ሜኑ",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Error sending error message: {e}")

def create_application() -> Application:
    """Create the bot application"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found!")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    bot = SimplePrintingBot()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text_message))
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    return application

async def set_bot_commands(application: Application):
    """Set bot commands"""
    commands = [
        BotCommand("start", "🚀 ቦቱን ጀምሩ"),
        BotCommand("help", "❓ እርዳታ"),
        BotCommand("status", "📊 ሁኔታ"),
    ]
    
    try:
        await application.bot.set_my_commands(commands)
        logger.info("✅ Bot commands set")
    except Exception as e:
        logger.error(f"❌ Error setting commands: {e}")

def main():
    """Run the bot"""
    logger.info("🚀 Starting Simple Printing Bot...")
    
    try:
        # Create application
        application = create_application()
        logger.info("✅ Application created")
        
        # Set commands
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(set_bot_commands(application))
        
        logger.info(f"🏪 Business: {BUSINESS_NAME}")
        logger.info(f"📧 Contact: {BUSINESS_EMAIL}")
        logger.info("🔄 Starting polling...")
        
        # Start polling
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    main()
