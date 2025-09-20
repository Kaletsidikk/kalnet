"""
Direct message conversation handler for the printing business bot
"""
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, filters

from config.bot_config import *
from bot.models.database import message_model
from bot.utils.validators import ValidationUtils

class DirectMessageHandler:
    """Handles direct messaging conversations"""
    
    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
        self.validator = ValidationUtils()
    
    async def start_message_conversation(self, update: Update, context) -> int:
        """Start the direct message conversation"""
        # Clear any existing conversation data
        context.user_data.clear()
        
        await update.effective_message.reply_text(
            "💬 <b>Send Direct Message</b>\\n\\n"
            "I'll help you send a direct message to our team. "
            "We'll get back to you as soon as possible!\\n\\n"
            "First, please tell me your <b>full name</b>:",
            parse_mode='HTML',
            reply_markup=ReplyKeyboardRemove()
        )
        
        return WAITING_MESSAGE_NAME
    
    async def handle_message_name(self, update: Update, context) -> int:
        """Handle customer name input for messaging"""
        user_input = update.message.text
        
        is_valid, processed_name = self.validator.validate_name(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                f"❌ {processed_name}\\n\\nPlease enter a valid name:"
            )
            return WAITING_MESSAGE_NAME
        
        context.user_data['customer_name'] = processed_name
        
        await update.message.reply_text(
            f"👋 Hello {processed_name}!\\n\\n"
            "Please provide your <b>contact information</b> (phone number or email address) "
            "so we can respond to your message:",
            parse_mode='HTML'
        )
        
        return WAITING_MESSAGE_CONTACT
    
    async def handle_message_contact(self, update: Update, context) -> int:
        """Handle contact information for messaging"""
        user_input = update.message.text
        
        is_valid, contact_info = self.validator.validate_contact_info(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Please provide a valid phone number or email address:"
            )
            return WAITING_MESSAGE_CONTACT
        
        context.user_data['contact_info'] = contact_info
        
        message_info = """
📝 <b>What would you like to tell us?</b>

You can ask about:
• Pricing for specific printing services
• Custom printing requirements
• Delivery options and timelines  
• Design services and support
• Bulk order discounts
• Technical specifications
• Any other questions or concerns

Please type your message (maximum 1000 characters):
        """
        
        await update.message.reply_text(message_info.strip(), parse_mode='HTML')
        
        return WAITING_MESSAGE_TEXT
    
    async def handle_message_text(self, update: Update, context) -> int:
        """Handle message text and complete the direct message"""
        user_input = update.message.text
        
        is_valid, processed_message = self.validator.validate_message_text(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                f"❌ {processed_message}\\n\\n"
                "Please enter a valid message (5-1000 characters):"
            )
            return WAITING_MESSAGE_TEXT
        
        context.user_data['message_text'] = processed_message
        
        # Create the message entry
        try:
            message_id = message_model.create_message(
                customer_name=context.user_data['customer_name'],
                contact_info=context.user_data['contact_info'],
                message_text=processed_message,
                telegram_user_id=update.effective_user.id
            )
            
            # Prepare message summary
            message_preview = processed_message[:100] + "..." if len(processed_message) > 100 else processed_message
            
            message_summary = f"""
✅ <b>Message Sent Successfully!</b>

📋 <b>Message ID:</b> #{message_id}
👤 <b>Name:</b> {context.user_data['customer_name']}
📞 <b>Contact:</b> {self.validator.format_contact_display(context.user_data['contact_info'])}

📝 <b>Your Message:</b>
"{message_preview}"

<b>What happens next?</b>
• Your message has been forwarded to our team
• We will review it and respond within 24 hours
• You'll receive a response via the contact method you provided
• For urgent matters, you can also call us directly

<b>Response Time:</b>
• General inquiries: Within 24 hours
• Urgent requests: Within 4-6 hours during business hours
• Technical questions: Within 48 hours

Thank you for contacting us! 💬

<i>Business Hours: Monday-Friday, 8 AM - 6 PM</i>
<i>Phone: {BUSINESS_PHONE}</i>
<i>Email: {BUSINESS_EMAIL}</i>
            """
            
            await update.message.reply_text(
                message_summary.strip(),
                parse_mode='HTML',
                reply_markup=ReplyKeyboardMarkup(
                    MAIN_MENU_KEYBOARD,
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
            )
            
            # Send notification to admin
            await self.notification_manager.notify_new_message(
                message_id=message_id,
                customer_name=context.user_data['customer_name'],
                contact_info=context.user_data['contact_info'],
                message_text=processed_message
            )
            
        except Exception as e:
            await update.message.reply_text(
                "❌ Sorry, there was an error sending your message. "
                "Please try again or contact us directly at:\\n"
                f"📧 {BUSINESS_EMAIL}\\n"
                f"📞 {BUSINESS_PHONE}",
                reply_markup=ReplyKeyboardMarkup(
                    MAIN_MENU_KEYBOARD,
                    resize_keyboard=True,
                    one_time_keyboard=False
                ),
                parse_mode='HTML'
            )
        
        # Clear user data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def cancel_message(self, update: Update, context) -> int:
        """Cancel the messaging conversation"""
        await update.message.reply_text(
            "❌ Message cancelled. You're back to the main menu.",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_MENU_KEYBOARD,
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
        
        context.user_data.clear()
        return ConversationHandler.END
    
    def get_conversation_handler(self) -> ConversationHandler:
        """Get the conversation handler for messaging"""
        return ConversationHandler(
            entry_points=[],  # Entry points are handled by the main bot
            states={
                WAITING_MESSAGE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message_name)],
                WAITING_MESSAGE_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message_contact)],
                WAITING_MESSAGE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message_text)],
            },
            fallbacks=[
                MessageHandler(filters.Regex("^/cancel$"), self.cancel_message)
            ],
            name="message_conversation",
            persistent=False
        )