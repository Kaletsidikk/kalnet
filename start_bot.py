#!/usr/bin/env python3
"""
Cloud-ready start script for the Telegram bot deployment
Includes health endpoint for Fly.io monitoring
"""

import os
import sys
import logging
import asyncio
from threading import Thread
from flask import Flask

# Ensure we're in the right directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create Flask app for health checks (required by Fly.io)
app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for Fly.io"""
    return {'status': 'healthy', 'service': 'telegram-bot'}, 200

@app.route('/')
def root():
    """Root endpoint"""
    return {'message': 'Printing Business Bot is running', 'status': 'active'}, 200

def run_flask():
    """Run Flask app in a separate thread"""
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

async def run_telegram_bot():
    """Run the Telegram bot"""
    try:
        logger.info("🚀 Starting Telegram Bot...")
        
        # Import and run the main bot
        from bot.bot import PrintingBot
        from telegram.ext import Application
        from telegram import Update
        
        # Initialize bot
        bot = PrintingBot()
        
        # Create application with handlers
        application = bot.create_application()
        
        # Add error handler
        application.add_error_handler(bot.error_handler)
        
        # Start the bot
        logger.info("🤖 Bot is starting...")
        await application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        raise

def main():
    """Main entry point for cloud deployment"""
    try:
        # Start Flask health server in background thread
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("✅ Health server started")
        
        # Run the Telegram bot
        asyncio.run(run_telegram_bot())
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
