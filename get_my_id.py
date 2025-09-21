import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def get_user_id(update: Update, context):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "User"
    
    await update.message.reply_text(f"""
🆔 YOUR TELEGRAM USER ID: {user_id}

✅ Copy this number and add it to your .env file:
ADMIN_CHAT_ID={user_id}

Then restart the bot!
    """)
    
    print(f"📱 FOUND USER ID: {user_id}")
    print(f"💡 Add this to .env file: ADMIN_CHAT_ID={user_id}")

def main():
    print("🤖 Temporary bot to get your User ID")
    print("📱 Go to @kalnetworks_bot and send any message")
    print("⏳ Waiting for your message...\n")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, get_user_id))
    app.run_polling()

if __name__ == '__main__':
    main()
