#!/usr/bin/env python3
"""Test script to debug translation issues"""

import os
import sys
sys.path.append('.')

from flask import Flask
from flask_babel import Babel, _, get_locale
import babel.support

# Create a minimal Flask app
app = Flask(__name__, template_folder='website/templates')
app.config['SECRET_KEY'] = 'test'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'website/translations'

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

# Test with app context
with app.app_context():
    print(f"Current locale: {get_locale()}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Translation directories config: {app.config.get('BABEL_TRANSLATION_DIRECTORIES')}")
    
    # Check if translation files exist
    trans_dir = os.path.join('website', 'translations', 'am', 'LC_MESSAGES')
    po_file = os.path.join(trans_dir, 'messages.po')
    mo_file = os.path.join(trans_dir, 'messages.mo')
    
    print(f"Translation dir exists: {os.path.exists(trans_dir)}")
    print(f"PO file exists: {os.path.exists(po_file)}")
    print(f"MO file exists: {os.path.exists(mo_file)}")
    
    # Test translation
    try:
        home_translation = _('Home')
        print(f"Translation of 'Home': {home_translation}")
        
        services_translation = _('Services')
        print(f"Translation of 'Services': {services_translation}")
    except Exception as e:
        print(f"Translation error: {e}")
        
    # Try to load translations manually
    try:
        import babel.support
        catalog = babel.support.Translations.load('website/translations', ['am'])
        if catalog:
            print("Catalog loaded successfully")
            print(f"Manual translation of 'Home': {catalog.gettext('Home')}")
        else:
            print("Failed to load catalog")
    except Exception as e:
        print(f"Manual catalog loading error: {e}")
