"""
Quick script to verify your Telegram User ID
"""
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def show_user_info(update: Update, context):
    user = update.effective_user
    
    message = f"""
🆔 **YOUR TELEGRAM INFO**

👤 **Name:** {user.first_name} {user.last_name or ''}
🆔 **User ID:** {user.id}
👥 **Username:** @{user.username or 'No username'}
📱 **Is Bot:** {user.is_bot}

✅ **This is the ID saved in your .env file:** 1349142732

{'✅ **MATCH!** Messages will be sent to you.' if user.id == 1349142732 else '❌ **MISMATCH!** Update your .env file with the correct ID.'}
    """
    
    await update.message.reply_text(message, parse_mode='Markdown')
    print(f"\n🆔 User ID detected: {user.id}")
    print(f"📁 Saved in .env: 1349142732")
    print(f"✅ Match: {user.id == 1349142732}")

def main():
    print("🔍 Send any message to this bot to verify your User ID...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, show_user_info))
    app.run_polling()

if __name__ == '__main__':
    main()
