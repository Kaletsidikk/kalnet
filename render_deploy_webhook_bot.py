#!/usr/bin/env python3
"""
Webhook-based Bot Deployment for Render
Uses Flask webhook approach - most stable for cloud deployment
"""

import os
import sys
import logging
import time
from datetime import datetime
import signal
import traceback
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Enhanced logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WebhookBot:
    """Simple webhook-based bot implementation"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.admin_chat_id = os.getenv('ADMIN_CHAT_ID')
        self.business_name = os.getenv('BUSINESS_NAME', 'KalNetworks')
        
    def send_message(self, chat_id, text, parse_mode='HTML'):
        """Send message via Telegram API"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Message sent to {chat_id}")
                return True
            else:
                logger.error(f"❌ Failed to send message: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False

    def handle_message(self, message):
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
                
                return self.send_message(chat_id, welcome_text)
                
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
                
                return self.send_message(chat_id, help_text)
                
            else:
                # Forward message to admin
                if str(chat_id) != str(self.admin_chat_id):
                    forward_text = f"""<b>📨 New Message</b>

<b>From:</b> {first_name} (@{user.get('username', 'N/A')})
<b>Chat ID:</b> {chat_id}
<b>Message:</b> {text}

Reply to customer: /reply {chat_id} your_message"""
                    
                    self.send_message(self.admin_chat_id, forward_text)
                
                # Reply to user
                reply_text = f"""Thank you for contacting {self.business_name}! 

Your message has been received and forwarded to our team. We'll get back to you as soon as possible.

For urgent matters, please call: 0965552595"""
                
                return self.send_message(chat_id, reply_text)
                
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            return False

# Initialize bot
bot = WebhookBot()

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return {
        'status': 'healthy',
        'service': 'webhook-telegram-bot',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/')
def home():
    """Home endpoint"""
    return {
        'service': 'KalNetworks Telegram Bot',
        'status': 'running',
        'mode': 'webhook',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    try:
        update = request.get_json()
        logger.info(f"📨 Webhook received: {update}")
        
        if 'message' in update:
            bot.handle_message(update['message'])
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def setup_webhook():
    """Set up webhook with Telegram"""
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        logger.warning("⚠️ WEBHOOK_URL not set, skipping webhook setup")
        return False
        
    url = f"https://api.telegram.org/bot{bot.bot_token}/setWebhook"
    data = {'url': f"{webhook_url}/webhook"}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Webhook set up successfully: {webhook_url}/webhook")
            return True
        else:
            logger.error(f"❌ Failed to set webhook: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error setting webhook: {e}")
        return False

def main():
    """Main function for webhook bot deployment"""
    start_time = time.time()
    logger.info("🤖 RENDER WEBHOOK BOT DEPLOYMENT")
    logger.info("=" * 50)
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Check required environment variables
        if not os.getenv('BOT_TOKEN'):
            logger.error("❌ BOT_TOKEN not set")
            sys.exit(1)
            
        if not os.getenv('ADMIN_CHAT_ID'):
            logger.error("❌ ADMIN_CHAT_ID not set")
            sys.exit(1)
        
        logger.info("✅ Environment variables OK")
        logger.info("🎯 Mode: WEBHOOK BOT SERVICE")
        
        # Set up webhook (optional)
        setup_webhook()
        
        # Start Flask app
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"🌐 Starting webhook server on port {port}")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    
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
