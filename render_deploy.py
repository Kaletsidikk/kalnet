#!/usr/bin/env python3
"""
Ultra-Fast Render Deployment Script
Combines bot and web app with optimized startup for minimal cold start time
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime

# Set up optimized logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def check_environment():
    """Quick environment check"""
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("❌ BOT_TOKEN missing!")
        return False
    logger.info("✅ Environment OK")
    return True

def start_bot():
    """Start bot in separate thread"""
    try:
        logger.info("🤖 Starting bot thread...")
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import optimized bot
        try:
            from test_bot_fixed import main as run_bot
            logger.info("🚀 Bot starting...")
            run_bot()
        except ImportError:
            logger.warning("Fallback to bot_simple...")
            from bot_simple import main as run_bot
            run_bot()
            
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")

def start_webapp():
    """Start web app - MAIN THREAD"""
    try:
        logger.info("🌐 Starting web app...")
        
        # Import fast web app
        from app_fast import app
        
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"🚀 Web app ready on port {port}")
        
        # Start Flask app (this blocks)
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True,  # Enable threading
            use_reloader=False  # Disable reloader for production
        )
        
    except Exception as e:
        logger.error(f"❌ Web app error: {e}")
        sys.exit(1)

def main():
    """Main unified startup"""
    start_time = time.time()
    logger.info("🚀 ULTRA-FAST RENDER STARTUP INITIATED")
    
    # Quick environment check
    if not check_environment():
        sys.exit(1)
    
    try:
        # Determine what to run based on environment or args
        run_mode = os.environ.get('RUN_MODE', 'both')  # both, bot, web
        
        if len(sys.argv) > 1:
            run_mode = sys.argv[1]
        
        if run_mode == 'web':
            # Web only
            logger.info("🌐 Running WEB ONLY mode")
            start_webapp()
            
        elif run_mode == 'bot':
            # Bot only  
            logger.info("🤖 Running BOT ONLY mode")
            start_bot()
            
        else:
            # Both (default)
            logger.info("🚀 Running BOTH bot and web")
            
            # Start bot in background thread
            bot_thread = threading.Thread(target=start_bot, daemon=True)
            bot_thread.start()
            
            # Give bot a moment to start
            time.sleep(2)
            
            # Start web app in main thread
            start_webapp()
    
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        sys.exit(1)
    finally:
        elapsed = time.time() - start_time
        logger.info(f"⏱️ Startup completed in {elapsed:.2f}s")

if __name__ == '__main__':
    main()
