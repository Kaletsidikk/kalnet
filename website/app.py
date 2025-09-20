"""
Flask web application for the printing business platform
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
import requests
from datetime import datetime

from config.web_config import get_config, WEBSITE_CONTENT, VALIDATION_RULES
from bot.models.database import service_model
from bot.utils.notifications import NotificationManager
from bot.utils.validators import ValidationUtils

# Create Flask app
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Enable CORS
CORS(app)

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
        success = await notification_manager.notify_new_order(
            order_id=order_id,
            customer_name=processed_name,
            company_name=processed_company,
            product_type=data['product_type'],
            quantity=quantity,
            delivery_date=delivery_date,
            contact_info=contact_info
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Order submitted successfully!',
                'order_id': order_id
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Order submitted successfully! (Admin notification pending)',
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
        success = await notification_manager.notify_new_schedule(
            schedule_id=schedule_id,
            customer_name=processed_name,
            contact_info=contact_info,
            preferred_datetime=preferred_datetime
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Consultation scheduled successfully!',
                'schedule_id': schedule_id
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Consultation scheduled successfully! (Admin notification pending)',
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
        success = await notification_manager.notify_new_message(
            message_id=message_id,
            customer_name=processed_name,
            contact_info=contact_info,
            message_text=message_text
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Message sent successfully!',
                'message_id': message_id
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Message sent successfully! (Admin notification pending)',
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
@app.context_processor
def inject_common_vars():
    """Inject common variables into all templates"""
    return {
        'now': datetime.now(),
        'business_name': config.BUSINESS_NAME,
        'business_email': config.BUSINESS_EMAIL,
        'business_phone': config.BUSINESS_PHONE,
        'business_address': config.BUSINESS_ADDRESS,
        'channel_username': config.CHANNEL_USERNAME
    }

if __name__ == '__main__':
    # Initialize database
    try:
        from database.init_db import create_database
        create_database()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = config.DEBUG
    
    print(f"🌐 Starting web application on port {port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)