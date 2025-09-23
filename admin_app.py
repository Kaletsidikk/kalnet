"""
KalNetworks Admin Dashboard
A user-friendly web interface for managing services, products, and bot settings
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import sys
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.admin_models import service_manager, product_manager, settings_manager
from bot.models.database import order_model, schedule_model, message_model

# Configure Flask with correct template directory
app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Simple authentication (in production, use proper authentication)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'kalnetworks2024')

@app.before_request
def check_auth():
    """Simple authentication check"""
    public_routes = ['login', 'static']
    if request.endpoint not in public_routes and not session.get('authenticated'):
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['authenticated'] = True
            flash('Welcome to KalNetworks Admin Dashboard!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    """Main dashboard"""
    # Get statistics
    services = service_manager.get_all_services()
    active_services = [s for s in services if s['is_active']]
    
    stats = {
        'total_services': len(services),
        'active_services': len(active_services),
        'categories': len(set(s['category'] for s in services)),
    }
    
    # Get recent services (last 5)
    recent_services = sorted(services, key=lambda x: x['updated_at'], reverse=True)[:5]
    
    return render_template('dashboard.html', stats=stats, recent_services=recent_services)

@app.route('/services')
def services():
    """Services management page"""
    services_list = service_manager.get_all_services()
    categories = list(set(s['category'] for s in services_list))
    return render_template('services.html', services=services_list, categories=categories)

@app.route('/services/create', methods=['GET', 'POST'])
def create_service():
    """Create new service"""
    if request.method == 'POST':
        service_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'base_price': float(request.form.get('base_price', 0)),
            'price_range': request.form.get('price_range'),
            'processing_time': request.form.get('processing_time'),
            'is_active': bool(request.form.get('is_active'))
        }
        
        service_id = service_manager.create_service(service_data)
        flash(f'Service "{service_data["name"]}" created successfully!', 'success')
        return redirect(url_for('services'))
    
    categories = ['marketing', 'apparel', 'promotional', 'packaging', 'general']
    return render_template('service_form.html', service=None, categories=categories)

@app.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
def edit_service(service_id):
    """Edit existing service"""
    service = service_manager.get_service_by_id(service_id)
    if not service:
        flash('Service not found!', 'error')
        return redirect(url_for('services'))
    
    if request.method == 'POST':
        service_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'base_price': float(request.form.get('base_price', 0)),
            'price_range': request.form.get('price_range'),
            'processing_time': request.form.get('processing_time'),
            'is_active': bool(request.form.get('is_active'))
        }
        
        if service_manager.update_service(service_id, service_data):
            flash(f'Service "{service_data["name"]}" updated successfully!', 'success')
        else:
            flash('Failed to update service!', 'error')
        
        return redirect(url_for('services'))
    
    categories = ['marketing', 'apparel', 'promotional', 'packaging', 'general']
    return render_template('service_form.html', service=service, categories=categories)

@app.route('/services/<int:service_id>/delete', methods=['POST'])
def delete_service(service_id):
    """Delete service"""
    service = service_manager.get_service_by_id(service_id)
    if not service:
        flash('Service not found!', 'error')
    else:
        if service_manager.delete_service(service_id):
            flash(f'Service "{service["name"]}" deleted successfully!', 'success')
        else:
            flash('Failed to delete service!', 'error')
    
    return redirect(url_for('services'))

@app.route('/services/<int:service_id>/products')
def service_products(service_id):
    """View products for a specific service"""
    service = service_manager.get_service_by_id(service_id)
    if not service:
        flash('Service not found!', 'error')
        return redirect(url_for('services'))
    
    products = product_manager.get_products_by_service(service_id)
    return render_template('products.html', service=service, products=products)

@app.route('/services/<int:service_id>/products/create', methods=['GET', 'POST'])
def create_product(service_id):
    """Create new product for a service"""
    service = service_manager.get_service_by_id(service_id)
    if not service:
        flash('Service not found!', 'error')
        return redirect(url_for('services'))
    
    if request.method == 'POST':
        product_data = {
            'service_id': service_id,
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'unit': request.form.get('unit'),
            'min_quantity': int(request.form.get('min_quantity', 1)),
            'is_active': bool(request.form.get('is_active'))
        }
        
        # Handle specifications
        specs = {}
        for key in request.form.keys():
            if key.startswith('spec_'):
                spec_name = key[5:]  # Remove 'spec_' prefix
                specs[spec_name] = request.form.get(key)
        product_data['specifications'] = specs
        
        product_id = product_manager.create_product(product_data)
        flash(f'Product "{product_data["name"]}" created successfully!', 'success')
        return redirect(url_for('service_products', service_id=service_id))
    
    return render_template('product_form.html', service=service, product=None)

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit existing product"""
    # Get product details (you'll need to implement get_product_by_id)
    products = product_manager.get_products_by_service(0)  # This is a workaround
    product = None
    for p in products:
        if p['id'] == product_id:
            product = p
            break
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('services'))
    
    service = service_manager.get_service_by_id(product['service_id'])
    
    if request.method == 'POST':
        product_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'unit': request.form.get('unit'),
            'min_quantity': int(request.form.get('min_quantity', 1)),
            'is_active': bool(request.form.get('is_active'))
        }
        
        # Handle specifications
        specs = {}
        for key in request.form.keys():
            if key.startswith('spec_'):
                spec_name = key[5:]  # Remove 'spec_' prefix
                specs[spec_name] = request.form.get(key)
        product_data['specifications'] = specs
        
        if product_manager.update_product(product_id, product_data):
            flash(f'Product "{product_data["name"]}" updated successfully!', 'success')
        else:
            flash('Failed to update product!', 'error')
        
        return redirect(url_for('service_products', service_id=product['service_id']))
    
    return render_template('product_form.html', service=service, product=product)

@app.route('/products/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    """Delete product"""
    # Get service_id before deleting
    products = product_manager.get_products_by_service(0)  # Workaround
    service_id = None
    for p in products:
        if p['id'] == product_id:
            service_id = p['service_id']
            break
    
    if product_manager.delete_product(product_id):
        flash('Product deleted successfully!', 'success')
    else:
        flash('Failed to delete product!', 'error')
    
    return redirect(url_for('service_products', service_id=service_id) if service_id else url_for('services'))

@app.route('/settings')
def settings():
    """Settings management page"""
    all_settings = settings_manager.get_all_settings()
    return render_template('settings.html', settings=all_settings)

@app.route('/settings/update', methods=['POST'])
def update_settings():
    """Update settings"""
    for key in request.form.keys():
        if not key.startswith('setting_'):
            continue
        
        setting_key = key[8:]  # Remove 'setting_' prefix
        setting_value = request.form.get(key)
        description = request.form.get(f'desc_{setting_key}', '')
        
        settings_manager.set_setting(setting_key, setting_value, description)
    
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('settings'))

@app.route('/orders')
def orders():
    """Orders management page"""
    recent_orders = order_model.get_recent_orders(50)  # Get last 50 orders
    return render_template('orders.html', orders=recent_orders)

@app.route('/orders/<int:order_id>')
def view_order(order_id):
    """View specific order details"""
    order = order_model.get_order(order_id)
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('orders'))
    return render_template('order_detail.html', order=order)

@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    """Update order status"""
    new_status = request.form.get('status')
    if order_model.update_order_status(order_id, new_status):
        flash(f'Order #{order_id} status updated to {new_status}!', 'success')
    else:
        flash('Failed to update order status!', 'error')
    return redirect(url_for('view_order', order_id=order_id))

@app.route('/messages')
def messages():
    """Messages management page"""
    recent_messages = message_model.get_pending_messages()  # Get pending messages
    return render_template('messages.html', messages=recent_messages)

@app.route('/messages/<int:message_id>')
def view_message(message_id):
    """View specific message details"""
    message = message_model.get_message(message_id)
    if not message:
        flash('Message not found!', 'error')
        return redirect(url_for('messages'))
    return render_template('message_detail.html', message=message)

@app.route('/schedules')
def schedules():
    """Schedules management page"""
    pending_schedules = schedule_model.get_pending_schedules()  # Get pending schedules
    return render_template('schedules.html', schedules=pending_schedules)

@app.route('/api/services')
def api_services():
    """API endpoint for services (for bot consumption)"""
    services = service_manager.get_all_services(active_only=True)
    return jsonify(services)

@app.route('/api/products/<int:service_id>')
def api_products(service_id):
    """API endpoint for products by service"""
    products = product_manager.get_products_by_service(service_id, active_only=True)
    return jsonify(products)

@app.route('/api/settings/<setting_key>')
def api_setting(setting_key):
    """API endpoint for specific setting"""
    value = settings_manager.get_setting(setting_key)
    return jsonify({'key': setting_key, 'value': value})

# Production configuration
if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Production configuration
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)