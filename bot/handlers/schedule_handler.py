"""
Schedule conversation handler for the printing business bot
"""
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, filters

from config.bot_config import *
from bot.models.database import schedule_model
from bot.utils.validators import ValidationUtils

class ScheduleHandler:
    """Handles consultation scheduling conversations"""
    
    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
        self.validator = ValidationUtils()
    
    async def start_schedule_conversation(self, update: Update, context) -> int:
        """Start the scheduling conversation"""
        # Clear any existing conversation data
        context.user_data.clear()
        
        await update.effective_message.reply_text(
            "📅 <b>Schedule a Consultation</b>\\n\\n"
            "I'd be happy to help you schedule a consultation about our printing services. "
            "Let me collect some information from you.\\n\\n"
            "First, please tell me your <b>full name</b>:",
            parse_mode='HTML',
            reply_markup=ReplyKeyboardRemove()
        )
        
        return WAITING_SCHEDULE_NAME
    
    async def handle_schedule_name(self, update: Update, context) -> int:
        """Handle customer name input for scheduling"""
        user_input = update.message.text
        
        is_valid, processed_name = self.validator.validate_name(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                f"❌ {processed_name}\\n\\nPlease enter a valid name:"
            )
            return WAITING_SCHEDULE_NAME
        
        context.user_data['customer_name'] = processed_name
        
        await update.message.reply_text(
            f"👋 Hello {processed_name}!\\n\\n"
            "Please provide your <b>contact information</b> (phone number or email address) "
            "so we can reach you to confirm the appointment:",
            parse_mode='HTML'
        )
        
        return WAITING_SCHEDULE_CONTACT
    
    async def handle_schedule_contact(self, update: Update, context) -> int:
        """Handle contact information for scheduling"""
        user_input = update.message.text
        
        is_valid, contact_info = self.validator.validate_contact_info(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Please provide a valid phone number or email address:"
            )
            return WAITING_SCHEDULE_CONTACT
        
        context.user_data['contact_info'] = contact_info
        
        scheduling_info = """
🕒 <b>When would you like to schedule the consultation?</b>

You can provide your preferred date and time in various formats:
• <b>Specific datetime:</b> "25/12/2024 14:30" or "25/12/2024 2:30 PM"
• <b>Natural language:</b> "Next Monday at 2 PM" or "Tomorrow afternoon"
• <b>Date only:</b> "25/12/2024" (we'll suggest available times)

Our typical business hours are Monday-Friday, 8 AM - 6 PM, but we can accommodate other times if needed.

Please tell me your preferred date and time:
        """
        
        await update.message.reply_text(scheduling_info.strip(), parse_mode='HTML')
        
        return WAITING_SCHEDULE_DATETIME
    
    async def handle_schedule_datetime(self, update: Update, context) -> int:
        """Handle preferred datetime and complete the scheduling"""
        user_input = update.message.text
        
        is_valid, processed_datetime = self.validator.validate_datetime_preference(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Please provide a valid date and time preference. "
                "You can use formats like:\\n"
                "• 25/12/2024 14:30\\n"
                "• Next Monday 2 PM\\n"
                "• Tomorrow afternoon\\n"
                "• 25/12/2024 (date only)"
            )
            return WAITING_SCHEDULE_DATETIME
        
        context.user_data['preferred_datetime'] = processed_datetime
        
        # Create the schedule entry
        try:
            schedule_id = schedule_model.create_schedule(
                customer_name=context.user_data['customer_name'],
                contact_info=context.user_data['contact_info'],
                preferred_datetime=processed_datetime,
                telegram_user_id=update.effective_user.id
            )
            
            # Prepare schedule summary
            schedule_summary = f"""
✅ <b>Consultation Scheduled!</b>

📋 <b>Schedule ID:</b> #{schedule_id}
👤 <b>Name:</b> {context.user_data['customer_name']}
🕒 <b>Preferred Time:</b> {processed_datetime}
📞 <b>Contact:</b> {self.validator.format_contact_display(context.user_data['contact_info'])}

<b>What happens next?</b>
• We will review your request within 24 hours
• You will receive a confirmation with the exact date and time
• We'll provide you with meeting details (location or video call link)

<b>Discussion Topics:</b>
During the consultation, we can discuss:
• Your specific printing requirements
• Design and customization options  
• Pricing and delivery timelines
• Sample viewing and material options
• Any special requirements or questions

Thank you for your interest in our services! 📅
            """
            
            await update.message.reply_text(
                schedule_summary.strip(),
                parse_mode='HTML',
                reply_markup=ReplyKeyboardMarkup(
                    MAIN_MENU_KEYBOARD,
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
            )
            
            # Send notification to admin
            await self.notification_manager.notify_new_schedule(
                schedule_id=schedule_id,
                customer_name=context.user_data['customer_name'],
                contact_info=context.user_data['contact_info'],
                preferred_datetime=processed_datetime
            )
            
        except Exception as e:
            await update.message.reply_text(
                "❌ Sorry, there was an error scheduling your consultation. "
                "Please try again or contact us directly.",
                reply_markup=ReplyKeyboardMarkup(
                    MAIN_MENU_KEYBOARD,
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
            )
        
        # Clear user data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def cancel_schedule(self, update: Update, context) -> int:
        """Cancel the scheduling conversation"""
        await update.message.reply_text(
            "❌ Scheduling cancelled. You're back to the main menu.",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_MENU_KEYBOARD,
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
        
        context.user_data.clear()
        return ConversationHandler.END
    
    def get_conversation_handler(self) -> ConversationHandler:
        """Get the conversation handler for scheduling"""
        return ConversationHandler(
            entry_points=[],  # Entry points are handled by the main bot
            states={
                WAITING_SCHEDULE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_schedule_name)],
                WAITING_SCHEDULE_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_schedule_contact)],
                WAITING_SCHEDULE_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_schedule_datetime)],
            },
            fallbacks=[
                MessageHandler(filters.Regex("^/cancel$"), self.cancel_schedule)
            ],
            name="schedule_conversation",
            persistent=False
        )