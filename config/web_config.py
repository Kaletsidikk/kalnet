"""
Web Application Configuration Settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Telegram Bot Integration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
    
    # Business Information
    BUSINESS_NAME = os.getenv('BUSINESS_NAME', 'Printing Business')
    BUSINESS_EMAIL = os.getenv('BUSINESS_EMAIL', 'contact@printingbusiness.com')
    BUSINESS_PHONE = os.getenv('BUSINESS_PHONE', '+1234567890')
    BUSINESS_ADDRESS = os.getenv('BUSINESS_ADDRESS', 'Business Address')
    CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@printingchannel')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database/printing_business.db')
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'website/static/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Production-specific settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Get current configuration
def get_config():
    """Get the current configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# Website Content
WEBSITE_CONTENT = {
    'hero_title': f'Professional Printing Services',
    'hero_subtitle': 'Quality printing solutions for your business needs',
    'hero_description': 'From business cards to large format printing, we deliver exceptional quality and fast turnaround times.',
    
    'services_title': 'Our Services',
    'services_description': 'We offer a wide range of printing services to meet all your business needs.',
    
    'about_title': 'About Us',
    'about_description': 'With years of experience in the printing industry, we pride ourselves on delivering high-quality products and exceptional customer service.',
    
    'contact_title': 'Get in Touch',
    'contact_description': 'Ready to start your printing project? Contact us today for a quote or consultation.',
    
    'features': [
        {
            'icon': '🖨️',
            'title': 'Quality Printing',
            'description': 'State-of-the-art equipment for professional results'
        },
        {
            'icon': '⚡',
            'title': 'Fast Turnaround',
            'description': 'Quick delivery without compromising on quality'
        },
        {
            'icon': '💰',
            'title': 'Competitive Pricing',
            'description': 'Affordable rates for all printing services'
        },
        {
            'icon': '🎨',
            'title': 'Custom Design',
            'description': 'Professional design services available'
        }
    ]
}

# Form validation rules
VALIDATION_RULES = {
    'name': {
        'required': True,
        'min_length': 2,
        'max_length': 50
    },
    'company': {
        'required': False,
        'max_length': 100
    },
    'email': {
        'required': True,
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    },
    'phone': {
        'required': True,
        'min_length': 10,
        'max_length': 15
    },
    'message': {
        'required': True,
        'min_length': 10,
        'max_length': 1000
    }
}