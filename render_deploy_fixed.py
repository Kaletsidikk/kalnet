#!/usr/bin/env python3
"""
FIXED Render Deployment Script - Production Ready
Resolves common deployment errors and ensures stable bot operation
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime
import signal
import traceback

# Enhanced logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    """Handle shutdown gracefully"""
    logger.info("🛑 Shutdown signal received")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_environment():
    """Comprehensive environment check"""
    logger.info("🔍 Checking environment variables...")
    
    required_vars = {
        'BOT_TOKEN': 'Telegram bot token',
        'ADMIN_CHAT_ID': 'Admin chat ID',
        'PORT': 'Server port'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ Environment variables OK")
    return True

def start_bot():
    """Start bot with enhanced error handling"""
    try:
        logger.info("🤖 Starting Telegram bot...")
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import and start the bot
        try:
            # Try the production bot first
            from bot_production import ProductionBot
            logger.info("📡 Using production bot")
            
            bot = ProductionBot()
            application = bot.create_application()
            
            # Add error handler
            application.add_error_handler(bot.error_handler)
            
            logger.info("🚀 Starting bot polling...")
            
            # Start polling in production mode
            application.run_polling(
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True,
                poll_interval=2.0,
                timeout=30,
                read_timeout=20,
                write_timeout=20,
                connect_timeout=20,
                pool_timeout=20
            )
            
        except ImportError as e:
            logger.warning(f"Production bot import failed: {e}")
            logger.info("📡 Falling back to simple bot")
            
            # Fallback to simple bot
            try:
                from bot_simple import EnhancedPrintingBot
                bot = EnhancedPrintingBot()
                application = bot.create_application()
                application.add_error_handler(bot.error_handler if hasattr(bot, 'error_handler') else None)
                
                application.run_polling(
                    allowed_updates=['message', 'callback_query'],
                    drop_pending_updates=True,
                    poll_interval=2.0,
                    timeout=30
                )
            except ImportError:
                logger.error("❌ No bot implementation found!")
                return
            
    except Exception as e:
        logger.error(f"❌ Bot startup error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't exit - let the web app continue

def start_webapp():
    """Start Flask web application"""
    try:
        logger.info("🌐 Starting Flask web application...")
        
        # Import the fast web app
        from app_fast import app
        
        # Get port from environment
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        logger.info(f"🌐 Web app starting on {host}:{port}")
        
        # Start Flask with production settings
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"❌ Web app error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    """Main function with comprehensive error handling"""
    start_time = time.time()
    logger.info("🚀 RENDER DEPLOYMENT - FIXED VERSION")
    logger.info("=" * 50)
    
    try:
        # Environment check
        if not check_environment():
            logger.error("❌ Environment check failed")
            sys.exit(1)
        
        # Determine run mode
        run_mode = os.environ.get('RUN_MODE', 'both').lower()
        
        logger.info(f"🎯 Run mode: {run_mode.upper()}")
        
        if run_mode == 'web':
            # Web only mode
            logger.info("🌐 Running in WEB-ONLY mode")
            start_webapp()
            
        elif run_mode == 'bot':
            # Bot only mode  
            logger.info("🤖 Running in BOT-ONLY mode")
            start_bot()
            
        else:
            # Both bot and web (default for Render)
            logger.info("🚀 Running BOTH bot and web application")
            
            # Start bot in background thread with daemon=True
            logger.info("🤖 Starting bot thread...")
            bot_thread = threading.Thread(target=start_bot, daemon=True, name="BotThread")
            bot_thread.start()
            
            # Give bot time to initialize
            logger.info("⏳ Waiting for bot initialization...")
            time.sleep(3)
            
            # Start web app in main thread (this is what Render monitors)
            logger.info("🌐 Starting web application...")
            start_webapp()
    
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        elapsed = time.time() - start_time
        logger.info(f"⏱️ Total runtime: {elapsed:.2f} seconds")

if __name__ == '__main__':
    main()
