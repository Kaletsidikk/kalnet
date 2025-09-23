#!/usr/bin/env python3
"""
Render Bot-Only Deployment Script
Dedicated script for deploying only the Telegram bot
"""

import os
import sys
import logging
import time
from datetime import datetime
import signal
import traceback
from dotenv import load_dotenv

# Enhanced logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    """Handle shutdown gracefully"""
    logger.info("🛑 Bot shutdown signal received")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_environment():
    """Check required environment variables for bot"""
    logger.info("🔍 Checking bot environment variables...")
    
    required_vars = {
        'BOT_TOKEN': 'Telegram bot token',
        'ADMIN_CHAT_ID': 'Admin chat ID',
        'CHANNEL_USERNAME': 'Telegram channel username'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ Bot environment variables OK")
    return True

def start_health_server():
    """Start a simple health check server for Render"""
    from flask import Flask
    import threading
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'telegram-bot',
            'timestamp': datetime.now().isoformat()
        }
    
    # Start health server in background thread
    port = int(os.environ.get('PORT', 5000))
    
    def run_health_server():
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    logger.info(f"✅ Health server started on port {port}")
    
def start_bot():
    """Start Telegram bot with comprehensive error handling"""
    try:
        logger.info("🤖 Starting Telegram bot service...")
        
        # Load environment variables
        load_dotenv()
        
        # Import and start the bot
        try:
            # Try the production bot first
            from bot_production import ProductionBot
            logger.info("📡 Using production bot implementation")
            
            bot = ProductionBot()
            application = bot.create_application()
            
            # Add error handler
            application.add_error_handler(bot.error_handler)
            
            logger.info("🚀 Starting bot polling...")
            
            # Start polling with optimized settings for bot-only mode
            application.run_polling(
                allowed_updates=['message', 'callback_query', 'inline_query'],
                drop_pending_updates=True,
                poll_interval=1.0,  # Faster polling for bot-only
                timeout=30,
                read_timeout=20,
                write_timeout=20,
                connect_timeout=20,
                pool_timeout=20
            )
            
        except ImportError as e:
            logger.warning(f"Production bot import failed: {e}")
            logger.info("📡 Falling back to enhanced bot")
            
            # Fallback to enhanced bot
            try:
                from bot_simple_enhanced import EnhancedPrintingBot
                bot = EnhancedPrintingBot()
                application = bot.create_application()
                
                if hasattr(bot, 'error_handler'):
                    application.add_error_handler(bot.error_handler)
                
                logger.info("🚀 Starting enhanced bot polling...")
                application.run_polling(
                    allowed_updates=['message', 'callback_query'],
                    drop_pending_updates=True,
                    poll_interval=1.0,
                    timeout=30
                )
                
            except ImportError:
                logger.error("❌ No bot implementation found!")
                sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Bot startup error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    """Main function for bot-only deployment"""
    start_time = time.time()
    logger.info("🤖 RENDER BOT-ONLY DEPLOYMENT")
    logger.info("=" * 50)
    
    try:
        # Environment check
        if not check_environment():
            logger.error("❌ Environment check failed")
            sys.exit(1)
        
        logger.info("🎯 Mode: BOT-ONLY SERVICE")
        
        # Start health check server for Render
        start_health_server()
        
        # Start bot (this will run indefinitely)
        start_bot()
    
    except KeyboardInterrupt:
        logger.info("🛑 Bot shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        elapsed = time.time() - start_time
        logger.info(f"⏱️ Total runtime: {elapsed:.2f} seconds")

if __name__ == '__main__':
    main()
