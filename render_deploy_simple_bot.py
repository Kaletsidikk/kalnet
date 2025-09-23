#!/usr/bin/env python3
"""
Simple Render Bot Deployment - No Updater Issues
Uses a basic HTTP server approach that's compatible with Render
"""

import os
import sys
import logging
import time
from datetime import datetime
import signal
import traceback
import asyncio
import threading
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
        'ADMIN_CHAT_ID': 'Admin chat ID'
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

class SimpleBot:
    """Simple bot implementation without Updater issues"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.admin_chat_id = os.getenv('ADMIN_CHAT_ID')
        self.business_name = os.getenv('BUSINESS_NAME', 'KalNetworks')
        self.running = False
        
    async def send_message(self, chat_id, text, parse_mode='HTML'):
        """Send message via Telegram API"""
        import aiohttp
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info(f"✅ Message sent to {chat_id}")
                        return True
                    else:
                        logger.error(f"❌ Failed to send message: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False

    async def get_updates(self, offset=0):
        """Get updates from Telegram"""
        import aiohttp
        
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {
            'offset': offset,
            'timeout': 30,
            'allowed_updates': ['message', 'callback_query']
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result', [])
                    else:
                        logger.error(f"❌ Failed to get updates: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"❌ Error getting updates: {e}")
            return []

    async def handle_message(self, message):
        """Handle incoming message"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user = message.get('from', {})
            first_name = user.get('first_name', 'User')
            
            logger.info(f"📨 Message from {first_name} ({chat_id}): {text}")
            
            if text.startswith('/start'):
                welcome_text = f"""<b>🖨️ Welcome to {self.business_name}!</b>

<b>Our Services:</b>
📋 Business Cards & Flyers
🎽 T-shirt & Apparel Printing  
📦 Promotional Materials
🏷️ Labels & Stickers
📄 Document Services

<b>How to Order:</b>
1. Tell us what you need
2. Share your design or let us create one
3. Get a quote
4. We'll handle the rest!

<b>Contact:</b>
📧 gebeyatechnologies@gmail.com
📞 0965552595
📍 KalNetworks Business Center

Type your request or send us your design files!"""
                
                await self.send_message(chat_id, welcome_text)
                
            elif text.startswith('/help'):
                help_text = f"""<b>🖨️ {self.business_name} - Help</b>

<b>Available Commands:</b>
/start - Start the bot and see services
/help - Show this help message

<b>How to Use:</b>
• Simply type what you need
• Send us your design files
• Ask for quotes and information

<b>We Print:</b>
📋 Business materials
🎽 Custom apparel
📦 Promotional items
🏷️ Labels & stickers

For immediate assistance, just send us a message!"""
                
                await self.send_message(chat_id, help_text)
                
            else:
                # Forward message to admin
                if str(chat_id) != str(self.admin_chat_id):
                    forward_text = f"""<b>📨 New Message</b>

<b>From:</b> {first_name} (@{user.get('username', 'N/A')})
<b>Chat ID:</b> {chat_id}
<b>Message:</b> {text}

Reply with: /reply {chat_id} your_message"""
                    
                    await self.send_message(self.admin_chat_id, forward_text)
                
                # Reply to user
                reply_text = f"""Thank you for contacting {self.business_name}! 

Your message has been received and forwarded to our team. We'll get back to you as soon as possible.

For urgent matters, please call: 0965552595"""
                
                await self.send_message(chat_id, reply_text)
                
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")

    async def run_bot(self):
        """Main bot polling loop"""
        logger.info("🤖 Starting simple bot polling...")
        self.running = True
        offset = 0
        
        while self.running:
            try:
                updates = await self.get_updates(offset)
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        await self.handle_message(update['message'])
                
                # Small delay to prevent overwhelming the API
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Bot polling error: {e}")
                await asyncio.sleep(5)  # Wait before retrying

def start_health_server():
    """Start Flask health check server"""
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'simple-telegram-bot',
            'timestamp': datetime.now().isoformat()
        }
    
    @app.route('/')
    def home():
        return {
            'service': 'KalNetworks Telegram Bot',
            'status': 'running',
            'timestamp': datetime.now().isoformat()
        }
    
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"✅ Health server starting on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def run_bot_async():
    """Run bot in async event loop"""
    try:
        bot = SimpleBot()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.run_bot())
    except Exception as e:
        logger.error(f"❌ Async bot error: {e}")

def main():
    """Main function for simple bot deployment"""
    start_time = time.time()
    logger.info("🤖 RENDER SIMPLE BOT DEPLOYMENT")
    logger.info("=" * 50)
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Environment check
        if not check_environment():
            logger.error("❌ Environment check failed")
            sys.exit(1)
        
        logger.info("🎯 Mode: SIMPLE BOT SERVICE")
        
        # Start bot in background thread
        logger.info("🤖 Starting bot thread...")
        bot_thread = threading.Thread(target=run_bot_async, daemon=True)
        bot_thread.start()
        
        # Start health server in main thread (required by Render)
        start_health_server()
    
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
