# 🚀 Deploy Bot to Fly.io (FREE)

This guide will help you deploy your Telegram bot to Fly.io completely free.

## 📋 Prerequisites

1. **GitHub account** (to store your code)
2. **Telegram Bot Token** (from @BotFather)
3. **Your Telegram User ID** (for admin notifications)

## 🛠️ Setup Steps

### 1. Install Fly CLI

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Or download from:** https://fly.io/docs/hands-on/install-flyctl/

### 2. Create Fly.io Account
```bash
fly auth signup
```
- No credit card required for free tier!

### 3. Prepare Your Bot

Your bot is already configured with these files:
- ✅ `fly.toml` - Fly.io configuration
- ✅ `Dockerfile.bot` - Container configuration  
- ✅ `start_bot.py` - Cloud-ready bot starter
- ✅ `requirements-bot.txt` - Minimal dependencies

### 4. Set Environment Variables

Create your `.env` file with:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_telegram_user_id
BUSINESS_NAME=Your Business Name
BUSINESS_EMAIL=contact@yourbusiness.com
BUSINESS_PHONE=+251912345678
BUSINESS_ADDRESS=Your Address, Addis Ababa
CHANNEL_USERNAME=@yourbusinesschannel
```

### 5. Deploy to Fly.io

```bash
# Login to Fly.io
fly auth login

# Launch your app (this creates the app)
fly launch --no-deploy

# Set your environment variables
fly secrets set BOT_TOKEN=your_bot_token_here
fly secrets set ADMIN_CHAT_ID=your_telegram_user_id
fly secrets set BUSINESS_NAME="Your Business Name"
fly secrets set BUSINESS_EMAIL=contact@yourbusiness.com
fly secrets set BUSINESS_PHONE=+251912345678
fly secrets set BUSINESS_ADDRESS="Your Address, Addis Ababa"
fly secrets set CHANNEL_USERNAME=@yourbusinesschannel

# Deploy your bot
fly deploy
```

### 6. Monitor Your Bot

```bash
# Check if bot is running
fly status

# View logs
fly logs

# Check health
curl https://your-app-name.fly.dev/health
```

## 🔧 Troubleshooting

### Bot Not Starting?
```bash
fly logs --app your-app-name
```

### Need to Update Code?
```bash
# After making changes
fly deploy
```

### Reset Bot?
```bash
fly apps restart your-app-name
```

## 📊 Free Tier Limits

Fly.io free tier includes:
- ✅ **3 shared VMs** (256MB each)
- ✅ **160GB bandwidth/month**  
- ✅ **3GB persistent storage**
- ✅ **Perfect for your bot!**

## 🎉 Success!

Once deployed:
1. Your bot will be running 24/7 on Fly.io
2. Health endpoint: `https://your-app-name.fly.dev/health`
3. Test your bot on Telegram
4. All notifications will reach your admin chat

## 🔄 Next Steps

After bot deployment:
1. **Deploy Website** to Render (free web service)
2. **Deploy Admin Dashboard** to Render (free web service)  
3. **Update database** to use shared PostgreSQL

Your bot is now live and free forever! 🎊
