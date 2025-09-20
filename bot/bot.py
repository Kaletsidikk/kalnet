"""
Main Telegram Bot for Printing Business Platform
"""
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters

from config.bot_config import *
from bot.models.database import user_model, service_model
from bot.handlers.order_handler import OrderHandler
from bot.handlers.schedule_handler import ScheduleHandler
from bot.handlers.message_handler import DirectMessageHandler
from bot.utils.notifications import NotificationManager
from bot.utils.validators import ValidationUtils

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PrintingBot:
    """Main bot class that handles all bot operations"""
    
    def __init__(self):
        self.notification_manager = NotificationManager()
        self.validator = ValidationUtils()
        
        # Initialize handlers
        self.order_handler = OrderHandler(self.notification_manager)
        self.schedule_handler = ScheduleHandler(self.notification_manager)
        self.message_handler = DirectMessageHandler(self.notification_manager)
    
    async def start_command(self, update: Update, context) -> None:
        """Handle the /start command"""
        user = update.effective_user
        
        # Create or update user in database
        user_model.create_or_update_user(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Send welcome message with main menu
        keyboard = ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        logger.info(f"User {user.first_name} ({user.id}) started the bot")
    
    async def help_command(self, update: Update, context) -> None:
        """Handle the /help command"""
        help_text = f\"\"\"
<b>🖨️ {BUSINESS_NAME} - Help</b>

<b>Available Commands:</b>
/start - Start the bot and show main menu
/help - Show this help message
/cancel - Cancel current operation

<b>Main Menu Options:</b>
📋 <b>View Services</b> - See our available printing services
🛒 <b>Place Order</b> - Start the ordering process
📅 <b>Schedule a Talk</b> - Book a consultation
💬 <b>Message Me Directly</b> - Send a direct message
📢 <b>View Channel</b> - Access our updates channel

<b>Contact Information:</b>
📧 Email: {BUSINESS_EMAIL}
📞 Phone: {BUSINESS_PHONE}
📍 Address: {BUSINESS_ADDRESS}

For immediate assistance, use the "Message Me Directly" option!
        \"\"\"
        
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def cancel_command(self, update: Update, context) -> int:
        """Handle the /cancel command"""
        await update.message.reply_text(
            "❌ Operation cancelled. You're back to the main menu.",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_MENU_KEYBOARD,
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
        return ConversationHandler.END
    
    async def view_services(self, update: Update, context) -> None:
        """Handle the View Services button"""
        services = service_model.get_active_services()
        
        if not services:
            await update.message.reply_text(
                "⚠️ No services available at the moment. Please contact us directly for more information."
            )
            return
        
        services_text = f"<b>🖨️ Our Printing Services</b>\\n\\n"
        
        for service in services:
            services_text += f"<b>📋 {service['name']}</b>\\n"
            services_text += f"   {service['description']}\\n"
            if service['price_range']:
                services_text += f"   💰 {service['price_range']}\\n"
            services_text += "\\n"
        
        services_text += f"<i>For custom requirements or detailed quotes, please contact us!</i>\\n\\n"
        services_text += f"📧 {BUSINESS_EMAIL}\\n📞 {BUSINESS_PHONE}"
        
        await update.message.reply_text(services_text, parse_mode='HTML')
        
        # Show action buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Place Order", callback_data="place_order")],
            [InlineKeyboardButton("📅 Schedule Consultation", callback_data="schedule_talk")],
            [InlineKeyboardButton("💬 Ask Questions", callback_data="direct_message")]
        ])
        
        await update.message.reply_text(
            "What would you like to do next?",
            reply_markup=keyboard
        )
    
    async def view_channel(self, update: Update, context) -> None:
        """Handle the View Channel button"""
        if CHANNEL_USERNAME:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Visit Our Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
            ])
            
            await update.message.reply_text(
                f"📢 <b>Stay Updated!</b>\\n\\n"
                f"Join our Telegram channel for the latest updates, promotions, and printing tips!\\n\\n"
                f"Channel: {CHANNEL_USERNAME}",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                "📢 Our updates channel is coming soon! Stay tuned for announcements."
            )
    
    async def handle_callback_query(self, update: Update, context) -> int:
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "place_order":
            return await self.order_handler.start_order_conversation(update, context)
        elif query.data == "schedule_talk":
            return await self.schedule_handler.start_schedule_conversation(update, context)
        elif query.data == "direct_message":
            return await self.message_handler.start_message_conversation(update, context)
        
        return ConversationHandler.END
    
    async def handle_text_message(self, update: Update, context) -> int:
        """Handle text messages based on main menu"""
        text = update.message.text
        
        if text == "📋 View Services":
            await self.view_services(update, context)
        elif text == "🛒 Place Order":
            return await self.order_handler.start_order_conversation(update, context)
        elif text == "📅 Schedule a Talk":
            return await self.schedule_handler.start_schedule_conversation(update, context)
        elif text == "💬 Message Me Directly":
            return await self.message_handler.start_message_conversation(update, context)
        elif text == "📢 View Channel":
            await self.view_channel(update, context)
        else:
            await update.message.reply_text(
                "Please use the menu buttons below or type /help for available commands.",
                reply_markup=ReplyKeyboardMarkup(
                    MAIN_MENU_KEYBOARD,
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
            )
        
        return ConversationHandler.END
    
    def create_application(self) -> Application:
        """Create and configure the bot application"""
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("cancel", self.cancel_command))
        
        # Add conversation handlers
        application.add_handler(self.order_handler.get_conversation_handler())
        application.add_handler(self.schedule_handler.get_conversation_handler())
        application.add_handler(self.message_handler.get_conversation_handler())
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Add text message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        return application
    
    async def error_handler(self, update: Update, context) -> None:
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                ERROR_MESSAGES['general_error']
            )

def main():
    """Main function to run the bot"""
    bot = PrintingBot()
    application = bot.create_application()
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    logger.info("Starting Printing Business Bot...")
    
    try:
        # Start the bot
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()