#!/usr/bin/env python3
"""Test script to debug Flask app translation issues"""

import os
import sys
sys.path.append('.')

from flask import Flask, render_template_string, session
from flask_babel import Babel, _, get_locale

# Create Flask app similar to the actual app
app = Flask(__name__, template_folder='website/templates')
app.config['SECRET_KEY'] = 'test'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

# Use absolute path for translations directory (like in the real app)
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(os.path.dirname(os.path.abspath('website/app.py')), 'translations')

print(f"Translation directory: {app.config['BABEL_TRANSLATION_DIRECTORIES']}")

# Configure supported languages
app.config['LANGUAGES'] = {
    'en': 'English',
    'am': 'አማርኛ'  # Amharic
}

# Initialize Babel
babel = Babel(app)

def get_locale():
    return 'am'  # Force Amharic for testing

babel.locale_selector_func = get_locale

# Test route
@app.route('/test')
def test_route():
    return render_template_string("""
    <h1>{{ _('Home') }}</h1>
    <p>{{ _('Services') }}</p>
    <p>{{ _('Professional Printing Services') }}</p>
    """)

if __name__ == '__main__':
    with app.app_context():
        print(f"Current locale: {get_locale()}")
        print(f"Translation of 'Home': {_('Home')}")
        print(f"Translation of 'Services': {_('Services')}")
        print(f"Translation of 'Professional Printing Services': {_('Professional Printing Services')}")
    
    # Run the test server
    print("Starting test server on http://127.0.0.1:5001")
    print("Visit http://127.0.0.1:5001/test to see translations")
    app.run(host='127.0.0.1', port=5001, debug=True)
