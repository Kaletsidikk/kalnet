# Deployment Guide - Printing Business Platform

This guide covers how to deploy the Printing Business Platform to various hosting providers.

## 🚀 Quick Deploy Options

### 1. Railway (Recommended for Bot)

Railway is perfect for hosting the Telegram bot with automatic deployments and easy environment variable management.

**Steps:**
1. Sign up at [Railway](https://railway.app)
2. Connect your GitHub repository
3. Create a new project from your repository
4. Set environment variables (see [Environment Variables](#environment-variables))
5. Deploy!

**Railway Configuration:**
- Build Command: `pip install -r requirements.txt && python database/init_db.py`
- Start Command: `python bot/bot.py`
- Port: Not required for bot-only deployment

### 2. Render (Great for Both Bot & Website)

Render offers both web services and background workers, perfect for our dual setup.

**Steps:**
1. Sign up at [Render](https://render.com)
2. Connect your GitHub repository
3. Create services using the `render.yaml` configuration
4. Set environment variables
5. Deploy!

**Render Features:**
- Automatic SSL certificates
- Built-in metrics and logging
- Easy scaling
- Health checks included

### 3. Docker Deployment (Self-hosted)

Use Docker for self-hosted deployments on VPS or cloud instances.

**Prerequisites:**
- Docker and Docker Compose installed
- Server with public IP (for website)

**Steps:**
```bash
# Clone repository
git clone <your-repo-url>
cd printing-business-platform

# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env

# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Heroku (Alternative Option)

While not included in this setup, you can easily deploy to Heroku:

1. Create `Procfile`:
```
web: python website/app.py
worker: python bot/bot.py
```

2. Deploy via Heroku CLI or GitHub integration

## 🔧 Environment Variables

Set these environment variables in your hosting platform:

### Required Variables
```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_telegram_user_id
FLASK_SECRET_KEY=your_secret_key_here
```

### Business Information
```env
BUSINESS_NAME=Your Printing Business
BUSINESS_EMAIL=contact@yourprintingbusiness.com
BUSINESS_PHONE=+1234567890
BUSINESS_ADDRESS=Your Business Address
CHANNEL_USERNAME=@your_channel_name
```

### Application Configuration
```env
FLASK_ENV=production
DATABASE_URL=sqlite:///database/printing_business.db
PORT=5000
```

## 📋 Pre-deployment Checklist

### 1. Telegram Bot Setup
- [ ] Create bot with @BotFather
- [ ] Get bot token
- [ ] Get your user ID for admin notifications
- [ ] Create Telegram channel (optional)

### 2. Environment Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Fill in all required environment variables
- [ ] Test locally with `python bot/bot.py`
- [ ] Test website with `python website/app.py`

### 3. Repository Preparation
- [ ] Commit all changes to Git
- [ ] Push to GitHub/GitLab
- [ ] Verify `.gitignore` excludes sensitive files
- [ ] Update README with your business information

## 🔍 Testing Your Deployment

### Bot Testing
1. Search for your bot on Telegram
2. Send `/start` command
3. Test each menu option:
   - View Services
   - Place Order
   - Schedule a Talk
   - Message Me Directly
   - View Channel

### Website Testing
1. Visit your website URL
2. Test all forms:
   - Order form
   - Schedule form
   - Contact form
3. Verify Telegram notifications are received

## 📊 Monitoring and Maintenance

### Health Checks
Both services include health checks:
- **Bot**: Verifies process is running
- **Website**: Checks HTTP response from `/`

### Logs
Monitor application logs for:
- Error messages
- Failed notifications
- Database issues
- User interactions

### Database Maintenance
- Database is automatically initialized on first run
- SQLite file is persistent across deployments
- Consider regular backups for production

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files
- Use secure secret keys
- Regularly rotate bot tokens if needed

### Database Security
- SQLite file should not be web-accessible
- Consider PostgreSQL for high-traffic deployments

### HTTPS
- Always use HTTPS in production
- Railway and Render provide automatic SSL

## 🚨 Troubleshooting

### Common Issues

**Bot not responding:**
- Check bot token is correct
- Verify admin chat ID
- Check deployment logs

**Website not loading:**
- Verify port configuration
- Check Flask environment variables
- Review build logs

**Database errors:**
- Ensure database directory exists
- Check file permissions
- Verify initialization script ran

**Notifications not working:**
- Verify bot token and admin chat ID
- Check network connectivity
- Review Telegram API rate limits

### Getting Help
- Check deployment platform documentation
- Review application logs
- Test locally with same environment variables
- Verify all dependencies are installed

## 📈 Scaling and Optimization

### Performance Tips
- Use environment-specific configurations
- Implement caching for frequently accessed data
- Monitor resource usage
- Consider database optimization for high volume

### Advanced Deployments
- Set up staging environments
- Implement CI/CD pipelines
- Use database migrations
- Add monitoring and alerting

## 🔄 Updates and Maintenance

### Updating the Application
1. Make changes to your local repository
2. Test changes locally
3. Commit and push to your repository
4. Platform will auto-deploy (if configured)
5. Monitor deployment logs
6. Test updated functionality

### Database Updates
- Changes to database schema require migration scripts
- Always backup database before major updates
- Test schema changes in staging first

---

## 📞 Support

For deployment support:
1. Check platform-specific documentation
2. Review application logs
3. Test with minimal configuration
4. Verify all environment variables

Good luck with your deployment! 🚀