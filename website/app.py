"""
Flask web application for the printing business platform
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_cors import CORS
from flask_babel import Babel, gettext, ngettext, get_locale, lazy_gettext
import requests
from datetime import datetime
import babel.support

from config.web_config import get_config, WEBSITE_CONTENT, VALIDATION_RULES
from bot.models.database import service_model
from bot.utils.notifications import NotificationManager
from bot.utils.validators import ValidationUtils

# Create Flask app
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

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

# Manual translation loading
translations = {}

def load_translations():
    """Load translation catalogs manually"""
    global translations
    translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
    
    for lang in ['en', 'am']:
        try:
            catalog = babel.support.Translations.load(translations_dir, [lang])
            translations[lang] = catalog
            print(f"[INFO] Loaded {lang} translations successfully")
        except Exception as e:
            print(f"[WARNING] Failed to load {lang} translations: {e}")
            translations[lang] = babel.support.NullTranslations()

# Load translations on startup
load_translations()

# Manual translation function
def _(text):
    """Manual translation function"""
    current_lang = session.get('lang', 'en')
    if current_lang in translations:
        return translations[current_lang].gettext(text)
    return text

# Initialize Babel (still needed for locale detection)
babel = Babel(app)

# Locale selector function
def get_locale():
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

# Initialize utilities
notification_manager = NotificationManager()
validator = ValidationUtils()

@app.route('/')
def home():
    """Home page"""
    services = service_model.get_active_services()
    return render_template('home.html', 
                         content=WEBSITE_CONTENT,
                         services=services,
                         config=config)

@app.route('/services')
def services():
    """Services page"""
    services = service_model.get_active_services()
    return render_template('services.html',
                         content=WEBSITE_CONTENT,
                         services=services,
                         config=config)

@app.route('/order')
def order_form():
    """Order form page"""
    services = service_model.get_active_services()
    return render_template('order.html',
                         content=WEBSITE_CONTENT,
                         services=services,
                         config=config)

@app.route('/schedule')
def schedule_form():
    """Schedule form page"""
    return render_template('schedule.html',
                         content=WEBSITE_CONTENT,
                         config=config)

@app.route('/contact')
def contact_form():
    """Contact form page"""
    return render_template('contact.html',
                         content=WEBSITE_CONTENT,
                         config=config)

@app.route('/debug')
def debug_translations():
    """Debug translations"""
    current_locale = get_locale()
    current_lang = session.get('lang', 'en')
    
    # Test manual translation
    home_translation = _('Home')
    services_translation = _('Services')
    
    return jsonify({
        'current_locale': str(current_locale),
        'session_lang': current_lang,
        'translations_loaded': list(translations.keys()),
        'home_translation': home_translation,
        'services_translation': services_translation,
        'manual_am_home': translations.get('am', {}).gettext('Home') if 'am' in translations else 'N/A',
        'translations_dir': os.path.join(os.path.dirname(__file__), 'translations')
    })

@app.route('/api/order', methods=['POST'])
def submit_order():
    """Submit order via API"""
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
    try:
        services = service_model.get_active_services()
        services_list = []
        for service in services:
            services_list.append({
                'id': service['id'],
                'name': service['name'],
                'description': service['description'],
                'price_range': service['price_range']
            })
        return jsonify({'success': True, 'services': services_list})
    except Exception as e:
        print(f"Error getting services: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html', config=config), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
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
    if language in app.config['LANGUAGES']:
        session['lang'] = language
    return redirect(request.referrer or url_for('home'))

@app.context_processor
def inject_common_vars():
    """Inject common variables into all templates"""
    return {
        'now': datetime.now(),
        'business_name': config.BUSINESS_NAME,
        'business_email': config.BUSINESS_EMAIL,
        'business_phone': config.BUSINESS_PHONE,
        'business_address': config.BUSINESS_ADDRESS,
        'channel_username': config.CHANNEL_USERNAME,
        'languages': app.config['LANGUAGES'],
        'current_language': get_locale(),
        '_': _  # Make translation function available in templates
    }

if __name__ == '__main__':
    # Initialize database
    try:
        from database.init_db import create_database
        create_database()
        print("[SUCCESS] Database initialized")
    except Exception as e:
        print(f"[WARNING] Database initialization warning: {e}")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = config.DEBUG
    
    print(f"[INFO] Starting web application on port {port}")
    print(f"[INFO] Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)