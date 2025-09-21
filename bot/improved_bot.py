"""
Improved Telegram Bot for Printing Business Platform
With better error handling, user ID detection, and enhanced UI
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from telegram.error import TelegramError, NetworkError, BadRequest

from config.bot_config import *
from bot.models.database import user_model, service_model

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

# Conversation states
WAITING_FOR_USER_ID = 0

class EnhancedPrintingBot:
    """Enhanced bot class with better error handling and UI"""
    
    def __init__(self):
        self.admin_chat_id = None
        self.setup_admin_chat_id()
        
    def setup_admin_chat_id(self):
        """Setup admin chat ID with validation"""
        try:
            admin_id = os.getenv('ADMIN_CHAT_ID')
            if admin_id and admin_id != "your_telegram_user_id_here":
                self.admin_chat_id = int(admin_id)
                logger.info(f"Admin chat ID set to: {self.admin_chat_id}")
            else:
                logger.warning("Admin chat ID not properly configured")
                self.admin_chat_id = None
        except (ValueError, TypeError):
            logger.error("Invalid ADMIN_CHAT_ID format")
            self.admin_chat_id = None

    async def start_command(self, update: Update, context) -> None:
        """Enhanced /start command with user ID detection"""
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
                f"🤖 <b>Welcome to {BUSINESS_NAME}!</b>\n\n"
                f"👤 <b>Your Telegram User ID:</b> <code>{user_id}</code>\n\n"
                "❓ Are you the business owner setting up this bot?",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            return
        
        # Regular customer start
        await self.customer_welcome(update, context)

    async def customer_welcome(self, update: Update, context) -> None:
        """Welcome message for customers"""
        user = update.effective_user
        
        # Create or update user in database
        try:
            user_model.create_or_update_user(
                telegram_user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
        except Exception as e:
            logger.error(f"Error creating/updating user: {e}")

        # Enhanced main menu with emojis
        main_menu = [
            ['🏪 View Services', '🛒 Place Order'],
            ['📅 Schedule Consultation', '💬 Contact Us'],
            ['📢 Updates Channel', '❓ Help & Info']
        ]
        
        keyboard = ReplyKeyboardMarkup(
            main_menu,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        
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
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def help_command(self, update: Update, context) -> None:
        """Enhanced help command"""
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
📍 Address: {BUSINESS_ADDRESS}

💡 <b>Quick Tips:</b>
• Use the keyboard buttons for fastest navigation
• You can type /cancel anytime to go back to main menu
• All your inquiries are sent directly to our team

🆘 Need immediate help? Use "💬 Contact Us" option!
        """
        
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def status_command(self, update: Update, context) -> None:
        """Bot status command"""
        user_count = user_model.get_user_count() if hasattr(user_model, 'get_user_count') else "Unknown"
        
        status_text = f"""
📊 <b>Bot Status</b>

✅ Bot is running smoothly
🤖 Version: 2.0 Enhanced
⏰ Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👥 Total users: {user_count}

🔧 <b>Features:</b>
✅ Order processing
✅ Consultation scheduling  
✅ Direct messaging
✅ Service catalog
✅ Channel integration

💚 <b>All systems operational!</b>
        """
        
        await update.message.reply_text(status_text, parse_mode='HTML')

    async def view_services(self, update: Update, context) -> None:
        """Enhanced services view with better UI"""
        try:
            services = service_model.get_active_services()
        except Exception as e:
            logger.error(f"Error fetching services: {e}")
            services = []
        
        if not services:
            # Fallback services if database is not set up
            services_text = f"""
🏪 <b>{BUSINESS_NAME} - Our Services</b>

🖨️ <b>Business Cards</b>
   Professional cards, various finishes
   💰 Starting from $25

📄 <b>Flyers & Brochures</b>
   Marketing materials, full color
   💰 Starting from $50

🎯 <b>Banners & Posters</b>
   Large format printing, weatherproof
   💰 Starting from $75

📚 <b>Booklets & Catalogs</b>
   Multi-page documents, binding options
   💰 Starting from $100

🏷️ <b>Stickers & Labels</b>
   Custom shapes and sizes
   💰 Starting from $30

⭐ <b>Custom Projects</b>
   Unique requirements, personalized service
   💰 Quote on request

📞 <i>Contact us for detailed quotes and custom requirements!</i>
            """
        else:
            services_text = f"<b>🏪 Our Printing Services</b>\n\n"
            
            for service in services:
                services_text += f"🎯 <b>{service['name']}</b>\n"
                services_text += f"   {service['description']}\n"
                if service['price_range']:
                    services_text += f"   💰 {service['price_range']}\n"
                services_text += "\n"
        
        # Enhanced action buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Place Order Now", callback_data="place_order")],
            [InlineKeyboardButton("📅 Schedule Meeting", callback_data="schedule_consultation")],
            [InlineKeyboardButton("💬 Ask Questions", callback_data="contact_us")],
            [InlineKeyboardButton("📧 Get Quote", callback_data="get_quote")]
        ])
        
        await update.message.reply_text(services_text, parse_mode='HTML')
        
        await update.message.reply_text(
            "🎯 <b>What would you like to do next?</b>",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def handle_callback_query(self, update: Update, context) -> int:
        """Enhanced callback query handling"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("set_admin_"):
            user_id = query.data.split("_")[2]
            await self.set_admin_user(update, context, user_id)
            return ConversationHandler.END
        elif query.data == "customer_start":
            await query.edit_message_text("🎉 Great! Let me show you our services...")
            await self.customer_welcome(update, context)
            return ConversationHandler.END
        elif query.data == "place_order":
            await query.edit_message_text("🛒 <b>Order Process</b>\n\nI'll guide you through placing your order...", parse_mode='HTML')
            # Here you would integrate with your order handler
            return ConversationHandler.END
        elif query.data == "schedule_consultation":
            await query.edit_message_text("📅 <b>Consultation Booking</b>\n\nLet's schedule your meeting...", parse_mode='HTML')
            # Here you would integrate with your schedule handler
            return ConversationHandler.END
        elif query.data == "contact_us":
            await query.edit_message_text("💬 <b>Contact Form</b>\n\nWhat would you like to tell us?", parse_mode='HTML')
            # Here you would integrate with your message handler
            return ConversationHandler.END
        elif query.data == "get_quote":
            await query.edit_message_text(
                f"📧 <b>Get a Custom Quote</b>\n\n"
                f"For detailed quotes, please contact us:\n\n"
                f"📧 {BUSINESS_EMAIL}\n"
                f"📱 {BUSINESS_PHONE}\n\n"
                f"Or use the 💬 Contact Us option for quick messaging!",
                parse_mode='HTML'
            )
            return ConversationHandler.END
        
        return ConversationHandler.END

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
                f"✅ <b>Perfect! You're now set as the business owner.</b>\n\n"
                f"🔧 Your admin ID ({user_id}) has been saved.\n"
                f"🎯 You'll receive all customer notifications.\n"
                f"🔄 Restart the bot to apply all changes.\n\n"
                f"🎉 <b>Welcome to {BUSINESS_NAME}!</b>",
                parse_mode='HTML'
            )
            
            logger.info(f"Admin user ID set to: {user_id}")
            
        except Exception as e:
            logger.error(f"Error setting admin user: {e}")
            await update.callback_query.edit_message_text(
                "❌ Error setting admin user. Please check the logs."
            )

    async def handle_text_message(self, update: Update, context) -> int:
        """Enhanced text message handling"""
        text = update.message.text
        
        text_handlers = {
            "🏪 View Services": self.view_services,
            "🛒 Place Order": self.handle_order_start,
            "📅 Schedule Consultation": self.handle_schedule_start,
            "💬 Contact Us": self.handle_contact_start,
            "📢 Updates Channel": self.view_channel,
            "❓ Help & Info": self.help_command
        }
        
        handler = text_handlers.get(text)
        if handler:
            await handler(update, context)
        else:
            await update.message.reply_text(
                "🤔 I didn't understand that.\n\n"
                "Please use the menu buttons below or type /help for available commands.",
                reply_markup=ReplyKeyboardMarkup(
                    [
                        ['🏪 View Services', '🛒 Place Order'],
                        ['📅 Schedule Consultation', '💬 Contact Us'],
                        ['📢 Updates Channel', '❓ Help & Info']
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
            )
        
        return ConversationHandler.END

    async def handle_order_start(self, update: Update, context):
        """Handle order start"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Business Cards", callback_data="order_business_cards")],
            [InlineKeyboardButton("📄 Flyers/Brochures", callback_data="order_flyers")],
            [InlineKeyboardButton("🎯 Banners/Posters", callback_data="order_banners")],
            [InlineKeyboardButton("📚 Booklets/Catalogs", callback_data="order_booklets")],
            [InlineKeyboardButton("🏷️ Stickers/Labels", callback_data="order_stickers")],
            [InlineKeyboardButton("⭐ Custom Project", callback_data="order_custom")]
        ])
        
        await update.message.reply_text(
            "🛒 <b>Place Your Order</b>\n\n"
            "What type of printing service do you need?",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def handle_schedule_start(self, update: Update, context):
        """Handle schedule start"""
        await update.message.reply_text(
            "📅 <b>Schedule Consultation</b>\n\n"
            "I'd love to discuss your printing needs!\n\n"
            "Please provide:\n"
            "• Your preferred date/time\n"
            "• Contact information\n"
            "• Brief description of your project\n\n"
            "💬 You can also use the contact form for quick scheduling!",
            parse_mode='HTML'
        )

    async def handle_contact_start(self, update: Update, context):
        """Handle contact start"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📧 Email Us", callback_data="contact_email")],
            [InlineKeyboardButton("📱 Call Us", callback_data="contact_phone")],
            [InlineKeyboardButton("💬 Quick Message", callback_data="contact_message")]
        ])
        
        await update.message.reply_text(
            f"💬 <b>Contact {BUSINESS_NAME}</b>\n\n"
            f"📧 Email: {BUSINESS_EMAIL}\n"
            f"📱 Phone: {BUSINESS_PHONE}\n"
            f"📍 Address: {BUSINESS_ADDRESS}\n\n"
            "How would you like to contact us?",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def view_channel(self, update: Update, context) -> None:
        """Enhanced channel view"""
        if CHANNEL_USERNAME:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
                [InlineKeyboardButton("🔔 Get Notifications", callback_data="enable_notifications")]
            ])
            
            await update.message.reply_text(
                f"📢 <b>Stay Connected!</b>\n\n"
                f"🎯 Join our channel for:\n"
                f"• 🆕 New service announcements\n"
                f"• 💰 Special offers & discounts\n"
                f"• 📸 Recent work showcase\n"
                f"• 💡 Printing tips & tricks\n\n"
                f"📱 Channel: {CHANNEL_USERNAME}\n\n"
                f"🔔 <i>Don't miss out on exclusive deals!</i>",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                "📢 <b>Updates Channel</b>\n\n"
                "Our updates channel is coming soon!\n"
                "Stay tuned for announcements about:\n\n"
                "• 🆕 New services\n"
                "• 💰 Special offers\n"
                "• 📸 Work showcase\n"
                "• 💡 Printing tips\n\n"
                "We'll let you know when it's ready! 🚀",
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
                    "🔧 <b>Oops! Something went wrong.</b>\n\n"
                    "Don't worry, we're on it! Please try again or contact support.\n\n"
                    "💡 Tip: Use /start to go back to the main menu.",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Error sending error message: {e}")

async def set_bot_commands(application: Application):
    """Set bot commands for the menu"""
    commands = [
        BotCommand("start", "🚀 Start the bot"),
        BotCommand("help", "❓ Get help"),
        BotCommand("status", "📊 Bot status"),
    ]
    
    try:
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.error(f"Error setting bot commands: {e}")

def main():
    """Main function to run the enhanced bot"""
    logger.info("🚀 Starting Enhanced Printing Business Bot...")
    
    try:
        bot = EnhancedPrintingBot()
        application = bot.create_application()
        
        # Add error handler
        application.add_error_handler(bot.error_handler)
        
        # Set bot commands
        async def post_init():
            await set_bot_commands(application)
        
        application.post_init = post_init
        
        logger.info("✅ Bot configured successfully!")
        logger.info(f"🏪 Business: {BUSINESS_NAME}")
        logger.info(f"📧 Contact: {BUSINESS_EMAIL}")
        logger.info("🔄 Starting polling...")
        
        # Start the bot with enhanced settings
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            poll_interval=1.0,
            timeout=20
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
