#!/usr/bin/env python3
"""
Comprehensive fix for Render deployment Updater error
This script fixes the 'Updater' object has no attribute '_Updater__polling_cleanup_cb' error
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['BOT_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def check_python_telegram_bot():
    """Check if python-telegram-bot is properly installed with correct version"""
    try:
        import telegram
        logger.info(f"✅ python-telegram-bot version: {telegram.__version__}")
        
        # Check if we have the correct imports
        from telegram import Update
        from telegram.ext import Application
        logger.info("✅ All telegram imports are working correctly")
        
        return True
    except ImportError as e:
        logger.error(f"❌ Error importing telegram: {e}")
        return False

def main():
    """Main function to run the comprehensive fix"""
    logger.info("🔧 Starting comprehensive deployment fix...")
    
    # Check environment
    if not check_environment():
        logger.error("❌ Environment check failed")
        sys.exit(1)
    
    # Check python-telegram-bot
    if not check_python_telegram_bot():
        logger.error("❌ python-telegram-bot check failed")
        sys.exit(1)
    
    logger.info("✅ All checks passed. Starting bot...")
    
    try:
        # Import and run the fixed bot
        from test_bot_fixed import main as run_bot
        logger.info("🚀 Running fixed bot...")
        run_bot()
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Trying alternative bot file...")
        
        try:
            from bot_simple import main as run_bot
            logger.info("🚀 Running alternative bot...")
            run_bot()
        except ImportError as e2:
            logger.error(f"❌ Alternative import failed: {e2}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    main()
