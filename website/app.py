"""
Flask web application for the printing business platform
"""
import sys
import os
import threading
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_cors import CORS
from flask_babel import Babel
from datetime import datetime

try:
    from config.web_config import get_config, WEBSITE_CONTENT, VALIDATION_RULES
    from bot.models.database import service_model
    from bot.utils.notifications import NotificationManager
    from bot.utils.validators import ValidationUtils
except ImportError as e:
    print(f"[WARNING] Some imports failed during initialization: {e}")

# Create Flask app
app = Flask(__name__)

# Try to get config, use defaults if config fails
try:
    config = get_config()
    app.config.from_object(config)
except Exception as e:
    print(f"[WARNING] Config loading failed, using defaults: {e}")
    # Default configuration
    class DefaultConfig:
        DEBUG = True
        SECRET_KEY = 'dev-key-change-in-production'
        BUSINESS_NAME = "KalNetworks Printing"
        BUSINESS_EMAIL = "info@kalnetworks.com"
        BUSINESS_PHONE = "+251-965552595"
        BUSINESS_ADDRESS = "Addis Ababa, Ethiopia"
        CHANNEL_USERNAME = "@kalnetworks"
    
    config = DefaultConfig()
    app.config.from_object(DefaultConfig)

# Configure supported languages
app.config['LANGUAGES'] = {
    'en': 'English',
    'am': 'አማርኛ'  # Amharic
}

# Enable CORS
CORS(app)

# Configure Babel settings
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

# App initialization status
app_initialized = False
initialization_error = None
initialization_start_time = time.time()

# Simple translation dictionary as fallback
SIMPLE_TRANSLATIONS = {
    'en': {
        'Home': 'Home',
        'Services': 'Services',
        'Order': 'Order',
        'Schedule': 'Schedule',
        'Contact': 'Contact',
        'Channel': 'Channel',
        'Professional Printing Services': 'Professional Printing Services',
        'Quality printing solutions for your business needs': 'Quality printing solutions for your business needs',
        'From business cards to large format printing, we deliver exceptional quality and fast turnaround times.': 'From business cards to large format printing, we deliver exceptional quality and fast turnaround times.',
        'Why Choose Us?': 'Why Choose Us?',
        'We deliver excellence in every print job': 'We deliver excellence in every print job',
        'Quality Printing': 'Quality Printing',
        'State-of-the-art equipment for professional results': 'State-of-the-art equipment for professional results',
        'Fast Turnaround': 'Fast Turnaround',
        'Quick delivery without compromising on quality': 'Quick delivery without compromising on quality',
        'Competitive Pricing': 'Competitive Pricing',
        'Affordable rates for all printing services': 'Affordable rates for all printing services',
        'Custom Design': 'Custom Design',
        'Professional design services available': 'Professional design services available',
        'Our Services': 'Our Services',
        'We offer a wide range of printing services to meet all your business needs.': 'We offer a wide range of printing services to meet all your business needs.',
        'View All Services': 'View All Services',
        'Ready to Get Started?': 'Ready to Get Started?',
        'Get your printing project started today with our professional services.': 'Get your printing project started today with our professional services.',
        'Order Now': 'Order Now',
        'Contact Us': 'Contact Us',
        'Order via Telegram Bot': 'Order via Telegram Bot',
        'You can also place orders, schedule consultations, and message us directly through our Telegram bot for a convenient mobile experience.': 'You can also place orders, schedule consultations, and message us directly through our Telegram bot for a convenient mobile experience.',
        'Quick order placement': 'Quick order placement',
        'Easy consultation scheduling': 'Easy consultation scheduling',
        'Direct messaging support': 'Direct messaging support',
        'Real-time notifications': 'Real-time notifications',
        'Search for our bot on Telegram:': 'Search for our bot on Telegram:',
        'Start Bot': 'Start Bot',
        'Stay Updated!': 'Stay Updated!',
        'Join our Telegram channel for the latest updates, promotions, and printing tips.': 'Join our Telegram channel for the latest updates, promotions, and printing tips.',
        'Place Order': 'Place Order',
        'Schedule Consultation': 'Schedule Consultation'
    },
    'am': {
        'Home': 'Home',
        'Services': 'አገልግሎቶች',
        'Order': 'ትዕዛዝ',
        'Schedule': 'ፕሮግራም',
        'Contact': 'ግንኙነት',
        'Channel': 'ቻናል',
        'Professional Printing Services': 'ፕሮፌሽናል የህትመት አገልግሎቶች',
        'Quality printing solutions for your business needs': 'ለንግድ ፍላጎትዎ የጥራት ህትመት መፍትሄዎች',
        'From business cards to large format printing, we deliver exceptional quality and fast turnaround times.': 'ከንግድ ካርዶች እስከ ትላቅ ፎርማት ህትመት፣ እጅግ የላቀ ጥራትና ፈጣን አገልግሎት እንሰጣለን።',
        'Why Choose Us?': 'ለምን እኛን መርጠው?',
        'We deliver excellence in every print job': 'በእያንዳንዱ የህትመት ሥራ ላይ ምርጥነትን እናቀርባለን',
        'Quality Printing': 'የጥራት ህትመት',
        'State-of-the-art equipment for professional results': 'ለፕሮፌሽናል ውጤት ዘመናዊ መሳሪያዎች',
        'Fast Turnaround': 'ፈጣን አገልግሎት',
        'Quick delivery without compromising on quality': 'ጥራትን ሳይጎዳ ፈጣን አቅርቦት',
        'Competitive Pricing': 'ተወዳዳሪ ዋጋ',
        'Affordable rates for all printing services': 'ለሁሉም የህትመት አገልግሎቶች ተመጣጣኝ ዋጋ',
        'Custom Design': 'ብጁ ዲዛይን',
        'Professional design services available': 'ፕሮፌሽናል የዲዛይን አገልግሎቶች አሉ',
        'Our Services': 'የእኛ አገልግሎቶች',
        'We offer a wide range of printing services to meet all your business needs.': 'ሁሉንም የንግድ ፍላጎቶችዎን ለማሟላት ሰፊ የህትመት አገልግሎቶችን እናቀርባለን።',
        'View All Services': 'ሁሉንም አገልግሎቶች ይመልከቱ',
        'Ready to Get Started?': 'ለመጀመር ተዘጋጅተዋል?',
        'Get your printing project started today with our professional services.': 'የህትመት ፕሮጀክትዎን ዛሬ በእኛ ፕሮፌሽናል አገልግሎት ይጀምሩ።',
        'Order Now': 'አሁን ይዘዙ',
        'Contact Us': 'ያግኙን',
        'Order via Telegram Bot': 'በቴሌግራም ቦት ይዘዙ',
        'You can also place orders, schedule consultations, and message us directly through our Telegram bot for a convenient mobile experience.': 'እንዲሁም በቴሌግራም ቦታችን በኩል ትዕዛዞችን መስጠት፣ ምክክር መፈጸም እና በቀጥታ መልዕክት መላክ ይችላሉ።',
        'Quick order placement': 'ፈጣን የትዕዛዝ አቀራረብ',
        'Easy consultation scheduling': 'ቀላል የምክክር መርሐ ግብር',
        'Direct messaging support': 'የቀጥታ መልዕክት ድጋፍ',
        'Real-time notifications': 'በእውነተኛ ጊዜ ማሳወቂያዎች',
        'Search for our bot on Telegram:': 'በቴሌግራም ውስጥ የእኛን ቦት ይፈልጉ፡',
        'Start Bot': 'ቦት ይጀምሩ',
        'Stay Updated!': 'ወቅታዊ ይሁኑ!',
        'Join our Telegram channel for the latest updates, promotions, and printing tips.': 'ለዘመናዊ መረጃዎች፣ ወቅታዊ ስጦታዎች እና የህትመት ምክሮች የቴሌግራም ቻናላችንን ይቀላቀሉ።',
        'Place Order': 'ትዕዛዝ ይስጡ',
        'Schedule Consultation': 'ምክክር ያዘጋጁ'
    }
}

def initialize_app():
    """Initialize application components in background"""
    global app_initialized, initialization_error, service_model, notification_manager, validator
    
    try:
        print("[INFO] Starting application initialization...")
        
        # Initialize database
        try:
            from database.init_db import create_database
            create_database()
            print("[SUCCESS] Database initialized")
        except Exception as e:
            print(f"[WARNING] Database initialization warning: {e}")
        
        # Initialize utilities
        try:
            notification_manager = NotificationManager()
            validator = ValidationUtils()
            print("[SUCCESS] Utilities initialized")
        except Exception as e:
            print(f"[WARNING] Utility initialization warning: {e}")
            # Create dummy utilities if real ones fail
            class DummyNotificationManager:
                def send_to_admin_sync(self, message):
                    print(f"[NOTIFICATION] {message}")
                    return True
                
                def _get_current_time(self):
                    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            class DummyValidator:
                def validate_name(self, name):
                    return True, name.strip()
                
                def validate_company_name(self, company):
                    return True, company.strip() if company else ""
                
                def validate_quantity(self, quantity):
                    try:
                        return True, int(quantity)
                    except:
                        return False, 0
                
                def validate_delivery_date(self, date_str):
                    return True, date_str
                
                def validate_contact_info(self, contact):
                    return True, contact.strip()
                
                def validate_datetime_preference(self, datetime_str):
                    return True, datetime_str
                
                def validate_message_text(self, message):
                    return True, message.strip()
            
            notification_manager = DummyNotificationManager()
            validator = DummyValidator()
        
        # Test service model
        try:
            services = service_model.get_active_services()
            print(f"[SUCCESS] Service model initialized with {len(services)} services")
        except Exception as e:
            print(f"[WARNING] Service model test failed: {e}")
            # Create dummy service model if real one fails
            class DummyServiceModel:
                def get_active_services(self):
                    return [
                        {'id': 1, 'name': 'Business Cards', 'description': 'Professional business cards', 'price_range': 'From 20 birr'},
                        {'id': 2, 'name': 'Flyers/Brochures', 'description': 'Marketing materials', 'price_range': 'From 50 birr'},
                        {'id': 3, 'name': 'Banners/Posters', 'description': 'Large format printing', 'price_range': 'From 100 birr'},
                        {'id': 4, 'name': 'Booklets/Catalogs', 'description': 'Professional booklets and catalogs', 'price_range': 'From 75 birr'},
                        {'id': 5, 'name': 'Stickers/Labels', 'description': 'Custom stickers and labels', 'price_range': 'From 30 birr'},
                        {'id': 6, 'name': 'Custom Printing', 'description': 'Custom printing solutions', 'price_range': 'Contact for quote'}
                    ]
            
            service_model = DummyServiceModel()
        
        app_initialized = True
        initialization_time = time.time() - initialization_start_time
        print(f"[SUCCESS] Application initialized in {initialization_time:.2f} seconds")
        
    except Exception as e:
        initialization_error = str(e)
        print(f"[ERROR] Application initialization failed: {e}")
        # Even if initialization fails, mark as initialized to show error page
        app_initialized = True

# Manual translation function using simple dictionary
def _(text):
    """Manual translation function using simple dictionary"""
    current_lang = session.get('lang', 'en')
    
    # Use simple translations dictionary
    if current_lang in SIMPLE_TRANSLATIONS:
        return SIMPLE_TRANSLATIONS[current_lang].get(text, text)
    
    return text

# Initialize Babel (still needed for locale detection)
babel = Babel(app)

# Locale selector function
def get_locale():
    """Get the current locale"""
    # 1) URL arg ?lang=am, 2) session, 3) request accept headers
    lang = request.args.get('lang')
    if lang and lang in app.config['LANGUAGES']:
        session['lang'] = lang
        return lang
    if 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(list(app.config['LANGUAGES'].keys())) or 'en'

# Set locale selector
babel.locale_selector_func = get_locale

# Initialize utilities (will be set in background thread)
service_model = None
notification_manager = None
validator = None

@app.before_request
def check_initialization():
    """Check if app is initialized before processing requests"""
    if not app_initialized and request.endpoint not in ['loading', 'static', 'health']:
        return redirect(url_for('loading'))

@app.route('/loading')
def loading():
    """Loading page shown during application initialization"""
    if app_initialized:
        if initialization_error:
            return render_template('error_loading.html', 
                                 error=initialization_error, 
                                 config=config)
        return redirect(url_for('home'))
    
    # Show initialization progress
    initialization_time = time.time() - initialization_start_time
    return render_template('loading.html', 
                         initialization_time=initialization_time,
                         config=config)

@app.route('/')
def home():
    """Home page"""
    if not app_initialized:
        return redirect(url_for('loading'))
    
    if initialization_error:
        return render_template('error_loading.html', 
                             error=initialization_error, 
                             config=config)
    
    try:
        services = service_model.get_active_services() if service_model else []
        return render_template('home.html', 
                             content=WEBSITE_CONTENT if 'WEBSITE_CONTENT' in globals() else {},
                             services=services,
                             config=config)
    except Exception as e:
        print(f"[ERROR] Home page error: {e}")
        return render_template('error_loading.html', 
                             error=f"Page loading error: {str(e)}", 
                             config=config)

@app.route('/services')
def services():
    """Services page"""
    if not app_initialized:
        return redirect(url_for('loading'))
    
    if initialization_error:
        return render_template('error_loading.html', 
                             error=initialization_error, 
                             config=config)
    
    try:
        services = service_model.get_active_services() if service_model else []
        return render_template('services.html',
                             content=WEBSITE_CONTENT if 'WEBSITE_CONTENT' in globals() else {},
                             services=services,
                             config=config)
    except Exception as e:
        print(f"[ERROR] Services page error: {e}")
        return render_template('error_loading.html', 
                             error=f"Page loading error: {str(e)}", 
                             config=config)

@app.route('/order')
def order_form():
    """Order form page"""
    if not app_initialized:
        return redirect(url_for('loading'))
    
    if initialization_error:
        return render_template('error_loading.html', 
                             error=initialization_error, 
                             config=config)
    
    try:
        services = service_model.get_active_services() if service_model else []
        return render_template('order.html',
                             content=WEBSITE_CONTENT if 'WEBSITE_CONTENT' in globals() else {},
                             services=services,
                             config=config)
    except Exception as e:
        print(f"[ERROR] Order page error: {e}")
        return render_template('error_loading.html', 
                             error=f"Page loading error: {str(e)}", 
                             config=config)

@app.route('/schedule')
def schedule_form():
    """Schedule form page"""
    if not app_initialized:
        return redirect(url_for('loading'))
    
    if initialization_error:
        return render_template('error_loading.html', 
                             error=initialization_error, 
                             config=config)
    
    try:
        return render_template('schedule.html',
                             content=WEBSITE_CONTENT if 'WEBSITE_CONTENT' in globals() else {},
                             config=config)
    except Exception as e:
        print(f"[ERROR] Schedule page error: {e}")
        return render_template('error_loading.html', 
                             error=f"Page loading error: {str(e)}", 
                             config=config)

@app.route('/contact')
def contact_form():
    """Contact form page"""
    if not app_initialized:
        return redirect(url_for('loading'))
    
    if initialization_error:
        return render_template('error_loading.html', 
                             error=initialization_error, 
                             config=config)
    
    try:
        return render_template('contact.html',
                             content=WEBSITE_CONTENT if 'WEBSITE_CONTENT' in globals() else {},
                             config=config)
    except Exception as e:
        print(f"[ERROR] Contact page error: {e}")
        return render_template('error_loading.html', 
                             error=f"Page loading error: {str(e)}", 
                             config=config)

@app.route('/debug')
def debug_translations():
    """Debug translations"""
    if not app_initialized:
        return redirect(url_for('loading'))
    
    current_locale = get_locale()
    current_lang = session.get('lang', 'en')
    
    # Test manual translation
    home_translation = _('Home')
    services_translation = _('Services')
    
    return jsonify({
        'current_locale': str(current_locale),
        'session_lang': current_lang,
        'translations_loaded': list(SIMPLE_TRANSLATIONS.keys()),
        'home_translation': home_translation,
        'services_translation': services_translation,
        'app_initialized': app_initialized,
        'initialization_error': initialization_error,
        'initialization_time': time.time() - initialization_start_time
    })

@app.route('/api/order', methods=['POST'])
def submit_order():
    """Submit order via API"""
    if not app_initialized or initialization_error:
        return jsonify({'success': False, 'error': 'Application not fully initialized'}), 503
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'product_type', 'quantity', 'delivery_date', 'contact']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Validate data
        is_valid, processed_name = validator.validate_name(data['name'])
        if not is_valid:
            return jsonify({'success': False, 'error': f'Invalid name: {processed_name}'}), 400
        
        is_valid, processed_company = validator.validate_company_name(data.get('company', ''))
        if not is_valid:
            return jsonify({'success': False, 'error': f'Invalid company name: {processed_company}'}), 400
        
        is_valid, quantity = validator.validate_quantity(str(data['quantity']))
        if not is_valid:
            return jsonify({'success': False, 'error': 'Invalid quantity'}), 400
        
        is_valid, delivery_date = validator.validate_delivery_date(data['delivery_date'])
        if not is_valid:
            return jsonify({'success': False, 'error': 'Invalid delivery date'}), 400
        
        is_valid, contact_info = validator.validate_contact_info(data['contact'])
        if not is_valid:
            return jsonify({'success': False, 'error': 'Invalid contact information'}), 400
        
        # Create order in database
        from bot.models.database import order_model
        order_id = order_model.create_order(
            customer_name=processed_name,
            company_name=processed_company if processed_company else None,
            product_type=data['product_type'],
            quantity=quantity,
            delivery_date=delivery_date,
            contact_info=contact_info,
            notes=data.get('notes', '')
        )
        
        # Send notification to admin
        try:
            company_info = f" ({processed_company})" if processed_company else ""
            message = f"""
🆕 <b>NEW ORDER RECEIVED!</b>

📋 <b>Order ID:</b> #{order_id}
👤 <b>Customer:</b> {processed_name}{company_info}
🖨️ <b>Product:</b> {data['product_type']}
📊 <b>Quantity:</b> {quantity}
📅 <b>Delivery Date:</b> {delivery_date}
📞 <b>Contact:</b> {contact_info}

⏰ <b>Received:</b> {notification_manager._get_current_time()}

Please review and process this order promptly.
            """
            notification_sent = notification_manager.send_to_admin_sync(message.strip())
            print(f"[ORDER] New Order #{order_id}: {processed_name} - {data['product_type']} (Notification {'sent' if notification_sent else 'failed'})")
        except Exception as e:
            print(f"[WARNING] Notification failed: {e}")
            notification_sent = False
        
        return jsonify({
            'success': True,
            'message': 'Order submitted successfully!' + (' (Notification sent)' if notification_sent else ' (Running in test mode)'),
            'order_id': order_id
        })
        
    except Exception as e:
        print(f"Error submitting order: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/schedule', methods=['POST'])
def submit_schedule():
    """Submit schedule request via API"""
    if not app_initialized or initialization_error:
        return jsonify({'success': False, 'error': 'Application not fully initialized'}), 503
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'contact', 'preferred_datetime']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Validate data
        is_valid, processed_name = validator.validate_name(data['name'])
        if not is_valid:
            return jsonify({'success': False, 'error': f'Invalid name: {processed_name}'}), 400
        
        is_valid, contact_info = validator.validate_contact_info(data['contact'])
        if not is_valid:
            return jsonify({'success': False, 'error': 'Invalid contact information'}), 400
        
        is_valid, preferred_datetime = validator.validate_datetime_preference(data['preferred_datetime'])
        if not is_valid:
            return jsonify({'success': False, 'error': 'Invalid preferred date/time'}), 400
        
        # Create schedule in database
        from bot.models.database import schedule_model
        schedule_id = schedule_model.create_schedule(
            customer_name=processed_name,
            contact_info=contact_info,
            preferred_datetime=preferred_datetime,
            notes=data.get('notes', '')
        )
        
        # Send notification to admin
        try:
            message = f"""
📅 <b>NEW CONSULTATION SCHEDULED!</b>

📋 <b>Schedule ID:</b> #{schedule_id}
👤 <b>Customer:</b> {processed_name}
🕒 <b>Preferred Time:</b> {preferred_datetime}
📞 <b>Contact:</b> {contact_info}

⏰ <b>Requested:</b> {notification_manager._get_current_time()}

Please confirm the appointment with the customer.
            """
            notification_sent = notification_manager.send_to_admin_sync(message.strip())
            print(f"[SCHEDULE] New Schedule #{schedule_id}: {processed_name} - {preferred_datetime} (Notification {'sent' if notification_sent else 'failed'})")
        except Exception as e:
            print(f"[WARNING] Notification failed: {e}")
            notification_sent = False
        
        return jsonify({
            'success': True,
            'message': 'Consultation scheduled successfully!' + (' (Notification sent)' if notification_sent else ' (Running in test mode)'),
            'schedule_id': schedule_id
        })
        
    except Exception as e:
        print(f"Error submitting schedule: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/message', methods=['POST'])
def submit_message():
    """Submit direct message via API"""
    if not app_initialized or initialization_error:
        return jsonify({'success': False, 'error': 'Application not fully initialized'}), 503
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'contact', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Validate data
        is_valid, processed_name = validator.validate_name(data['name'])
        if not is_valid:
            return jsonify({'success': False, 'error': f'Invalid name: {processed_name}'}), 400
        
        is_valid, contact_info = validator.validate_contact_info(data['contact'])
        if not is_valid:
            return jsonify({'success': False, 'error': 'Invalid contact information'}), 400
        
        is_valid, message_text = validator.validate_message_text(data['message'])
        if not is_valid:
            return jsonify({'success': False, 'error': f'Invalid message: {message_text}'}), 400
        
        # Create message in database
        from bot.models.database import message_model
        message_id = message_model.create_message(
            customer_name=processed_name,
            contact_info=contact_info,
            message_text=message_text
        )
        
        # Send notification to admin
        try:
            display_message = message_text[:200] + "..." if len(message_text) > 200 else message_text
            message = f"""
💬 <b>NEW DIRECT MESSAGE!</b>

📋 <b>Message ID:</b> #{message_id}
👤 <b>From:</b> {processed_name}
📞 <b>Contact:</b> {contact_info}

💭 <b>Message:</b>
{display_message}

⏰ <b>Received:</b> {notification_manager._get_current_time()}

Please respond to the customer promptly.
            """
            notification_sent = notification_manager.send_to_admin_sync(message.strip())
            print(f"[MESSAGE] New Message #{message_id}: {processed_name} - {message_text[:50]}... (Notification {'sent' if notification_sent else 'failed'})")
        except Exception as e:
            print(f"[WARNING] Notification failed: {e}")
            notification_sent = False
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully!' + (' (Notification sent)' if notification_sent else ' (Running in test mode)'),
            'message_id': message_id
        })
        
    except Exception as e:
        print(f"Error submitting message: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/services')
def get_services():
    """Get available services via API"""
    if not app_initialized or initialization_error:
        return jsonify({'success': False, 'error': 'Application not fully initialized'}), 503
    
    try:
        services = service_model.get_active_services() if service_model else []
        services_list = []
        for service in services:
            services_list.append({
                'id': service.get('id', 0),
                'name': service.get('name', 'Unknown Service'),
                'description': service.get('description', ''),
                'price_range': service.get('price_range', '')
            })
        return jsonify({'success': True, 'services': services_list})
    except Exception as e:
        print(f"Error getting services: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    status = {
        'status': 'initializing',
        'initialized': app_initialized,
        'error': initialization_error,
        'uptime': time.time() - initialization_start_time
    }
    
    if app_initialized:
        if initialization_error:
            status['status'] = 'error'
        else:
            status['status'] = 'healthy'
    
    return jsonify(status)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    if not app_initialized:
        return redirect(url_for('loading'))
    return render_template('404.html', config=config), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if not app_initialized:
        return redirect(url_for('loading'))
    return render_template('500.html', config=config), 500

# Template filters
@app.template_filter('datetime')
def datetime_filter(timestamp):
    """Format datetime for templates"""
    if isinstance(timestamp, str):
        return timestamp
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

# Template context processor
# Language switching route
@app.route('/set_language/<language>')
def set_language(language=None):
    """Set language preference"""
    if not app_initialized:
        return redirect(url_for('loading'))
    
    if language in app.config['LANGUAGES']:
        session['lang'] = language
    return redirect(request.referrer or url_for('home'))

@app.context_processor
def inject_common_vars():
    """Inject common variables into all templates"""
    common_vars = {
        'now': datetime.now(),
        'business_name': getattr(config, 'BUSINESS_NAME', 'Printing Services'),
        'business_email': getattr(config, 'BUSINESS_EMAIL', ''),
        'business_phone': getattr(config, 'BUSINESS_PHONE', ''),
        'business_address': getattr(config, 'BUSINESS_ADDRESS', ''),
        'channel_username': getattr(config, 'CHANNEL_USERNAME', ''),
        'languages': app.config['LANGUAGES'],
        'current_language': get_locale(),
        '_': _  # Make translation function available in templates
    }
    
    return common_vars

if __name__ == '__main__':
    # Start initialization in background thread
    init_thread = threading.Thread(target=initialize_app)
    init_thread.daemon = True
    init_thread.start()
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = getattr(config, 'DEBUG', True)
    
    print(f"[INFO] Starting web application on port {port}")
    print(f"[INFO] Debug mode: {debug}")
    print(f"[INFO] Application initialization started...")
    print(f"[INFO] Loading page available at: http://localhost:{port}/loading")
    print(f"[INFO] Health check at: http://localhost:{port}/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
