"""
Order conversation handler for the printing business bot
"""
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, filters

from config.bot_config import *
from bot.models.database import order_model, service_model
from bot.utils.validators import ValidationUtils

class OrderHandler:
    """Handles order placement conversations"""
    
    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
        self.validator = ValidationUtils()
    
    async def start_order_conversation(self, update: Update, context) -> int:
        """Start the order placement conversation"""
        # Clear any existing conversation data
        context.user_data.clear()
        
        await update.effective_message.reply_text(
            "🛒 <b>Place Your Order</b>\\n\\n"
            "I'll help you place an order for our printing services. "
            "Let me collect some information from you.\\n\\n"
            "First, please tell me your <b>full name</b>:",
            parse_mode='HTML',
            reply_markup=ReplyKeyboardRemove()
        )
        
        return WAITING_NAME
    
    async def handle_name(self, update: Update, context) -> int:
        """Handle customer name input"""
        user_input = update.message.text
        
        is_valid, processed_name = self.validator.validate_name(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                f"❌ {processed_name}\\n\\nPlease enter a valid name:"
            )
            return WAITING_NAME
        
        context.user_data['customer_name'] = processed_name
        
        await update.message.reply_text(
            f"👋 Nice to meet you, {processed_name}!\\n\\n"
            "Now, please tell me your <b>company name</b> (or type 'skip' if this is a personal order):",
            parse_mode='HTML'
        )
        
        return WAITING_COMPANY
    
    async def handle_company(self, update: Update, context) -> int:
        """Handle company name input"""
        user_input = update.message.text
        
        if user_input.lower().strip() in ['skip', 'none', 'personal', '-']:
            context.user_data['company_name'] = None
        else:
            is_valid, processed_company = self.validator.validate_company_name(user_input)
            
            if not is_valid:
                await update.message.reply_text(
                    f"❌ {processed_company}\\n\\nPlease enter a valid company name or type 'skip':"
                )
                return WAITING_COMPANY
            
            context.user_data['company_name'] = processed_company
        
        # Get available services
        services = service_model.get_active_services()
        services_text = "📋 <b>Available Services:</b>\\n\\n"
        
        for i, service in enumerate(services, 1):
            services_text += f"{i}. <b>{service['name']}</b>\\n"
            services_text += f"   {service['description']}\\n"
            if service['price_range']:
                services_text += f"   💰 {service['price_range']}\\n"
            services_text += "\\n"
        
        services_text += "Please tell me which service you need (you can type the name or number):"
        
        await update.message.reply_text(services_text, parse_mode='HTML')
        
        return WAITING_PRODUCT
    
    async def handle_product(self, update: Update, context) -> int:
        """Handle product/service selection"""
        user_input = update.message.text.strip()
        services = service_model.get_active_services()
        service_names = [service['name'] for service in services]
        
        selected_service = None
        
        # Check if input is a number
        try:
            service_index = int(user_input) - 1
            if 0 <= service_index < len(services):
                selected_service = services[service_index]['name']
        except ValueError:
            # Not a number, try name matching
            is_valid, matched_service = self.validator.validate_service_selection(user_input, service_names)
            if is_valid:
                selected_service = matched_service
        
        if not selected_service:
            await update.message.reply_text(
                "❌ I couldn't find that service. Please choose from the list above "
                "(type the service name or number):"
            )
            return WAITING_PRODUCT
        
        context.user_data['product_type'] = selected_service
        
        await update.message.reply_text(
            f"✅ Great! You selected: <b>{selected_service}</b>\\n\\n"
            "How many do you need? Please enter the <b>quantity</b>:",
            parse_mode='HTML'
        )
        
        return WAITING_QUANTITY
    
    async def handle_quantity(self, update: Update, context) -> int:
        """Handle quantity input"""
        user_input = update.message.text
        
        is_valid, quantity = self.validator.validate_quantity(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Please enter a valid quantity (positive number):"
            )
            return WAITING_QUANTITY
        
        context.user_data['quantity'] = quantity
        
        await update.message.reply_text(
            f"📊 Quantity: <b>{quantity}</b>\\n\\n"
            "When do you need this delivered?\\n"
            "Please enter the <b>delivery date</b> (format: DD/MM/YYYY, e.g., 25/12/2024):",
            parse_mode='HTML'
        )
        
        return WAITING_DELIVERY
    
    async def handle_delivery_date(self, update: Update, context) -> int:
        """Handle delivery date input"""
        user_input = update.message.text
        
        is_valid, formatted_date = self.validator.validate_delivery_date(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Please enter a valid future date in DD/MM/YYYY format (e.g., 25/12/2024):"
            )
            return WAITING_DELIVERY
        
        context.user_data['delivery_date'] = formatted_date
        
        await update.message.reply_text(
            f"📅 Delivery date: <b>{formatted_date}</b>\\n\\n"
            "Finally, please provide your <b>contact information</b>\\n"
            "(phone number or email address):",
            parse_mode='HTML'
        )
        
        return WAITING_CONTACT
    
    async def handle_contact(self, update: Update, context) -> int:
        """Handle contact information and complete the order"""
        user_input = update.message.text
        
        is_valid, contact_info = self.validator.validate_contact_info(user_input)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Please provide a valid phone number or email address:"
            )
            return WAITING_CONTACT
        
        context.user_data['contact_info'] = contact_info
        
        # Create the order
        try:
            order_id = order_model.create_order(
                customer_name=context.user_data['customer_name'],
                company_name=context.user_data.get('company_name'),
                product_type=context.user_data['product_type'],
                quantity=context.user_data['quantity'],
                delivery_date=context.user_data['delivery_date'],
                contact_info=contact_info,
                telegram_user_id=update.effective_user.id
            )
            
            # Prepare order summary
            company_info = f"\\n🏢 Company: {context.user_data['company_name']}" if context.user_data.get('company_name') else ""
            
            order_summary = f"""
✅ <b>Order Placed Successfully!</b>

📋 <b>Order ID:</b> #{order_id}
👤 <b>Name:</b> {context.user_data['customer_name']}{company_info}
🖨️ <b>Service:</b> {context.user_data['product_type']}
📊 <b>Quantity:</b> {context.user_data['quantity']}
📅 <b>Delivery Date:</b> {context.user_data['delivery_date']}
📞 <b>Contact:</b> {self.validator.format_contact_display(contact_info)}

We will review your order and contact you within 24 hours to confirm details and provide a quote.

Thank you for choosing our printing services! 🖨️
            """
            
            await update.message.reply_text(
                order_summary.strip(),
                parse_mode='HTML',
                reply_markup=ReplyKeyboardMarkup(
                    MAIN_MENU_KEYBOARD,
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
            )
            
            # Send notification to admin
            await self.notification_manager.notify_new_order(
                order_id=order_id,
                customer_name=context.user_data['customer_name'],
                company_name=context.user_data.get('company_name'),
                product_type=context.user_data['product_type'],
                quantity=context.user_data['quantity'],
                delivery_date=context.user_data['delivery_date'],
                contact_info=contact_info
            )
            
        except Exception as e:
            await update.message.reply_text(
                "❌ Sorry, there was an error processing your order. "
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
    
    async def cancel_order(self, update: Update, context) -> int:
        """Cancel the order conversation"""
        await update.message.reply_text(
            "❌ Order cancelled. You're back to the main menu.",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_MENU_KEYBOARD,
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
        
        context.user_data.clear()
        return ConversationHandler.END
    
    def get_conversation_handler(self) -> ConversationHandler:
        """Get the conversation handler for orders"""
        return ConversationHandler(
            entry_points=[],  # Entry points are handled by the main bot
            states={
                WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_name)],
                WAITING_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_company)],
                WAITING_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_product)],
                WAITING_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_quantity)],
                WAITING_DELIVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_delivery_date)],
                WAITING_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_contact)],
            },
            fallbacks=[
                MessageHandler(filters.Regex("^/cancel$"), self.cancel_order)
            ],
            name="order_conversation",
            persistent=False
        )