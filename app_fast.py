#!/usr/bin/env python3
"""
Lightning-Fast Flask Web Application for Printing Business Platform
Optimized for Render deployment with minimal startup time
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime

# Minimal imports for fastest startup
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fast-dev-key-2024')

# Business configuration (no external files)
BUSINESS_CONFIG = {
    'BUSINESS_NAME': os.environ.get('BUSINESS_NAME', 'KalNetworks – Printing & Business Solutions'),
    'BUSINESS_EMAIL': os.environ.get('BUSINESS_EMAIL', 'gebeyatechnologies@gmail.com'),
    'BUSINESS_PHONE': os.environ.get('BUSINESS_PHONE', '0965552595'),
    'BUSINESS_ADDRESS': os.environ.get('BUSINESS_ADDRESS', 'KalNetworks Business Center'),
    'BUSINESS_USERNAME': os.environ.get('BUSINESS_USERNAME', '@ABISSINIANJA')
}

# Fast services data (no database calls)
SERVICES = [
    {'id': 1, 'name': 'Business Cards', 'name_am': 'የንግድ ካርዶች', 'price': 'from 25 ETB'},
    {'id': 2, 'name': 'Flyers & Brochures', 'name_am': 'ፍላየሮች እና ብሮሽሮች', 'price': 'from 50 ETB'},
    {'id': 3, 'name': 'Banners & Posters', 'name_am': 'ባነሮች እና ፖስተሮች', 'price': 'from 75 ETB'},
    {'id': 4, 'name': 'Booklets & Catalogs', 'name_am': 'መጽሔቶች እና ካታሎጎች', 'price': 'from 100 ETB'},
    {'id': 5, 'name': 'Stickers & Labels', 'name_am': 'ስቲከሮች እና መለያዎች', 'price': 'from 30 ETB'},
    {'id': 6, 'name': 'Custom Projects', 'name_am': 'ልዩ ፕሮጀክቶች', 'price': 'Quote on request'}
]

# Fast translations (no external files)
TRANSLATIONS = {
    'en': {
        'home': 'Home',
        'services': 'Services',
        'order': 'Place Order',
        'contact': 'Contact',
        'welcome': 'Welcome to KalNetworks',
        'tagline': 'Your Professional Printing Partner',
        'get_started': 'Get Started',
        'learn_more': 'Learn More'
    },
    'am': {
        'home': 'ቤት',
        'services': 'አገልግሎቶች',
        'order': 'ትዕዛዝ ይስጡ',
        'contact': 'ያነጋግሩን',
        'welcome': 'ወደ ካል ኔትወርክስ እንኳን በደህና መጡ',
        'tagline': 'የእርስዎ ሙያዊ የህትመት አጋር',
        'get_started': 'ይጀምሩ',
        'learn_more': 'ተጨማሪ ይወቁ'
    }
}

def get_lang():
    """Get current language"""
    return session.get('lang', 'en')

def _(key, lang=None):
    """Fast translation function"""
    if lang is None:
        lang = get_lang()
    return TRANSLATIONS.get(lang, {}).get(key, key)

@app.route('/health')
def health_check():
    """Health check for Render"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}, 200

@app.route('/')
def home():
    """Lightning fast home page"""
    lang = get_lang()
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{BUSINESS_CONFIG['BUSINESS_NAME']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        header {{ background: #2c5530; color: white; padding: 1rem 0; }}
        .header-content {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }}
        .logo {{ font-size: 1.5rem; font-weight: bold; }}
        .nav {{ display: flex; gap: 20px; }}
        .nav a {{ color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 5px; transition: background 0.3s; }}
        .nav a:hover {{ background: rgba(255,255,255,0.1); }}
        .hero {{ background: linear-gradient(135deg, #4ade80, #22c55e); color: white; padding: 4rem 0; text-align: center; }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.25rem; margin-bottom: 2rem; }}
        .btn {{ display: inline-block; padding: 12px 24px; background: #fff; color: #22c55e; text-decoration: none; border-radius: 25px; font-weight: bold; transition: transform 0.3s; }}
        .btn:hover {{ transform: translateY(-2px); }}
        .services {{ padding: 4rem 0; }}
        .services-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem; }}
        .service-card {{ background: white; border-radius: 10px; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; transition: transform 0.3s; }}
        .service-card:hover {{ transform: translateY(-5px); }}
        .service-icon {{ font-size: 3rem; margin-bottom: 1rem; }}
        footer {{ background: #1f2937; color: white; padding: 2rem 0; text-align: center; }}
        .lang-switcher {{ margin-top: 1rem; }}
        .lang-switcher a {{ color: white; text-decoration: none; margin: 0 10px; }}
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2rem; }}
            .nav {{ flex-direction: column; gap: 10px; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">{BUSINESS_CONFIG['BUSINESS_NAME']}</div>
                <nav class="nav">
                    <a href="/">{_('home', lang)}</a>
                    <a href="/services">{_('services', lang)}</a>
                    <a href="/order">{_('order', lang)}</a>
                    <a href="/contact">{_('contact', lang)}</a>
                </nav>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <h1>{_('welcome', lang)}</h1>
            <p>{_('tagline', lang)}</p>
            <a href="/services" class="btn">{_('get_started', lang)}</a>
        </div>
    </section>

    <section class="services">
        <div class="container">
            <h2 style="text-align: center; margin-bottom: 1rem;">{_('services', lang)}</h2>
            <div class="services-grid">
                {''.join([f'''
                <div class="service-card">
                    <div class="service-icon">🖨️</div>
                    <h3>{service['name_am'] if lang == 'am' else service['name']}</h3>
                    <p>{service['price']}</p>
                </div>
                ''' for service in SERVICES[:3]])}
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2024 {BUSINESS_CONFIG['BUSINESS_NAME']}. All rights reserved.</p>
            <p>📧 {BUSINESS_CONFIG['BUSINESS_EMAIL']} | 📱 {BUSINESS_CONFIG['BUSINESS_PHONE']}</p>
            <div class="lang-switcher">
                <a href="/lang/en">English</a> | <a href="/lang/am">አማርኛ</a>
            </div>
        </div>
    </footer>
</body>
</html>"""

@app.route('/services')
def services():
    """Fast services page"""
    lang = get_lang()
    services_html = ''.join([f"""
        <div class="service-card">
            <div class="service-icon">{'🖨️' if i % 2 == 0 else '📄'}</div>
            <h3>{service['name_am'] if lang == 'am' else service['name']}</h3>
            <p>{service['price']}</p>
            <a href="/order?service={service['id']}" class="btn">Order Now</a>
        </div>
    """ for i, service in enumerate(SERVICES)])
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Services - {BUSINESS_CONFIG['BUSINESS_NAME']}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #22c55e; text-align: center; }}
        .services-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .service-card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        .service-icon {{ font-size: 2rem; margin-bottom: 1rem; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #22c55e; color: white; text-decoration: none; border-radius: 5px; margin-top: 1rem; }}
        .nav {{ text-align: center; margin-bottom: 2rem; }}
        .nav a {{ margin: 0 15px; color: #22c55e; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a> | <a href="/services">Services</a> | <a href="/order">Order</a> | <a href="/contact">Contact</a>
        </div>
        <h1>{_('services', lang)}</h1>
        <div class="services-grid">
            {services_html}
        </div>
    </div>
</body>
</html>"""

@app.route('/order')
def order():
    """Fast order page"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Order - {BUSINESS_CONFIG['BUSINESS_NAME']}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f9fafb; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .form-card {{ background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #22c55e; text-align: center; margin-bottom: 2rem; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        label {{ display: block; margin-bottom: 0.5rem; font-weight: bold; }}
        input, select, textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }}
        .btn {{ width: 100%; padding: 15px; background: #22c55e; color: white; border: none; border-radius: 5px; font-size: 18px; cursor: pointer; }}
        .btn:hover {{ background: #16a34a; }}
        .nav {{ text-align: center; margin-bottom: 2rem; }}
        .nav a {{ margin: 0 15px; color: #22c55e; text-decoration: none; }}
        .success {{ background: #d1fae5; color: #065f46; padding: 15px; border-radius: 5px; margin-bottom: 20px; display: none; }}
        .error {{ background: #fee2e2; color: #991b1b; padding: 15px; border-radius: 5px; margin-bottom: 20px; display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a> | <a href="/services">Services</a> | <a href="/order">Order</a> | <a href="/contact">Contact</a>
        </div>
        <div class="form-card">
            <h1>Quick Order</h1>
            <div id="message"></div>
            <form id="orderForm">
                <div class="form-group">
                    <label>Name *</label>
                    <input type="text" id="name" required>
                </div>
                <div class="form-group">
                    <label>Service *</label>
                    <select id="service" required>
                        <option value="">Select Service</option>
                        {''.join([f'<option value="{s["name"]}">{s["name"]} - {s["price"]}</option>' for s in SERVICES])}
                    </select>
                </div>
                <div class="form-group">
                    <label>Quantity *</label>
                    <input type="number" id="quantity" min="1" required>
                </div>
                <div class="form-group">
                    <label>Contact (Phone/Email) *</label>
                    <input type="text" id="contact" required>
                </div>
                <div class="form-group">
                    <label>Notes</label>
                    <textarea id="notes" rows="3"></textarea>
                </div>
                <button type="submit" class="btn">Submit Order</button>
            </form>
        </div>
    </div>
    <script>
        document.getElementById('orderForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            const messageDiv = document.getElementById('message');
            const formData = {{
                name: document.getElementById('name').value,
                product_type: document.getElementById('service').value,
                quantity: parseInt(document.getElementById('quantity').value),
                contact: document.getElementById('contact').value,
                delivery_date: new Date(Date.now() + 7*24*60*60*1000).toISOString().split('T')[0], // 7 days from now
                notes: document.getElementById('notes').value
            }};
            
            try {{
                const response = await fetch('/api/order', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(formData)
                }});
                const result = await response.json();
                
                if (result.success) {{
                    messageDiv.innerHTML = '<div class="success">✅ Order submitted successfully! We will contact you soon.</div>';
                    document.getElementById('orderForm').reset();
                }} else {{
                    messageDiv.innerHTML = '<div class="error">❌ ' + result.error + '</div>';
                }}
            }} catch (error) {{
                messageDiv.innerHTML = '<div class="error">❌ Network error. Please try again.</div>';
            }}
        }});
    </script>
</body>
</html>"""

@app.route('/contact')
def contact():
    """Fast contact page"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Contact - {BUSINESS_CONFIG['BUSINESS_NAME']}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f9fafb; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .contact-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
        .contact-info {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .contact-form {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #22c55e; text-align: center; margin-bottom: 2rem; }}
        .contact-item {{ margin-bottom: 1.5rem; padding: 15px; background: #f8fafc; border-radius: 8px; }}
        .contact-item strong {{ color: #22c55e; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        label {{ display: block; margin-bottom: 0.5rem; font-weight: bold; }}
        input, textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .btn {{ width: 100%; padding: 15px; background: #22c55e; color: white; border: none; border-radius: 5px; cursor: pointer; }}
        .nav {{ text-align: center; margin-bottom: 2rem; }}
        .nav a {{ margin: 0 15px; color: #22c55e; text-decoration: none; }}
        @media (max-width: 768px) {{ .contact-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a> | <a href="/services">Services</a> | <a href="/order">Order</a> | <a href="/contact">Contact</a>
        </div>
        <h1>Contact Us</h1>
        <div class="contact-grid">
            <div class="contact-info">
                <h2>Get In Touch</h2>
                <div class="contact-item">
                    <strong>📧 Email:</strong><br>
                    {BUSINESS_CONFIG['BUSINESS_EMAIL']}
                </div>
                <div class="contact-item">
                    <strong>📱 Phone:</strong><br>
                    {BUSINESS_CONFIG['BUSINESS_PHONE']}
                </div>
                <div class="contact-item">
                    <strong>📍 Address:</strong><br>
                    {BUSINESS_CONFIG['BUSINESS_ADDRESS']}
                </div>
                <div class="contact-item">
                    <strong>💬 Telegram:</strong><br>
                    {BUSINESS_CONFIG['BUSINESS_USERNAME']}
                </div>
            </div>
            <div class="contact-form">
                <h2>Send Message</h2>
                <div id="message"></div>
                <form id="contactForm">
                    <div class="form-group">
                        <label>Name *</label>
                        <input type="text" id="name" required>
                    </div>
                    <div class="form-group">
                        <label>Contact *</label>
                        <input type="text" id="contact" required>
                    </div>
                    <div class="form-group">
                        <label>Message *</label>
                        <textarea id="messageText" rows="4" required></textarea>
                    </div>
                    <button type="submit" class="btn">Send Message</button>
                </form>
            </div>
        </div>
    </div>
    <script>
        document.getElementById('contactForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            const messageDiv = document.getElementById('message');
            const formData = {{
                name: document.getElementById('name').value,
                contact: document.getElementById('contact').value,
                message: document.getElementById('messageText').value
            }};
            
            try {{
                const response = await fetch('/api/message', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(formData)
                }});
                const result = await response.json();
                
                if (result.success) {{
                    messageDiv.innerHTML = '<div style="background: #d1fae5; color: #065f46; padding: 15px; border-radius: 5px; margin-bottom: 20px;">✅ Message sent successfully!</div>';
                    document.getElementById('contactForm').reset();
                }} else {{
                    messageDiv.innerHTML = '<div style="background: #fee2e2; color: #991b1b; padding: 15px; border-radius: 5px; margin-bottom: 20px;">❌ ' + result.error + '</div>';
                }}
            }} catch (error) {{
                messageDiv.innerHTML = '<div style="background: #fee2e2; color: #991b1b; padding: 15px; border-radius: 5px; margin-bottom: 20px;">❌ Network error. Please try again.</div>';
            }}
        }});
    </script>
</body>
</html>"""

@app.route('/lang/<language>')
def set_language(language):
    """Set language preference"""
    if language in ['en', 'am']:
        session['lang'] = language
    return home()  # Redirect to home with new language

@app.route('/api/order', methods=['POST'])
def api_order():
    """Fast order API"""
    try:
        data = request.get_json()
        # Simple validation
        required = ['name', 'product_type', 'quantity', 'contact']
        for field in required:
            if not data.get(field):
                return jsonify({{'success': False, 'error': f'Missing {field}'}}), 400
        
        # Simulate order processing (replace with real logic)
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        return jsonify({{'success': True, 'message': 'Order received!', 'order_id': order_id}})
    except Exception as e:
        return jsonify({{'success': False, 'error': 'Server error'}}), 500

@app.route('/api/message', methods=['POST'])
def api_message():
    """Fast message API"""
    try:
        data = request.get_json()
        # Simple validation
        required = ['name', 'contact', 'message']
        for field in required:
            if not data.get(field):
                return jsonify({{'success': False, 'error': f'Missing {field}'}}), 400
        
        # Simulate message processing (replace with real logic)
        message_id = f"MSG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        return jsonify({{'success': True, 'message': 'Message sent!', 'message_id': message_id}})
    except Exception as e:
        return jsonify({{'success': False, 'error': 'Server error'}}), 500

if __name__ == '__main__':
    # Fast startup - no database initialization, no complex setup
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Lightning-fast app starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
