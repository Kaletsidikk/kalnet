# Printing Business Platform

A comprehensive platform that provides printing services through both a Telegram bot and a website, with centralized management and notifications.

## 🎯 Objectives

- Provide printing services with easy ordering system
- Schedule talks/consultations with clients
- Enable direct messaging to business owner
- Centralize all interactions in Telegram
- Use Telegram channel for updates and promotions
- Keep both website and bot simple and compatible

## ✨ Features

### Telegram Bot
- **Main Menu**: View Services, Place Order, Schedule Talk, Message Directly, View Channel
- **Order Flow**: Name → Company → Product → Quantity → Delivery Date → Contact → Confirmation
- **Schedule Flow**: Name → Contact → Preferred Date/Time → Confirmation
- **Direct Message Flow**: Name → Contact → Message → Notification
- **Notifications**: All activities sent to owner's Telegram account
- **Channel Integration**: Broadcast updates to subscribers

### Website
- **Landing Page**: Professional intro with action buttons
- **Services Page**: Product showcase with images/PDFs
- **Order Form**: Matches bot functionality, integrates via API
- **Schedule Form**: Direct integration with Telegram notifications
- **Direct Message**: Sends messages to owner's Telegram
- **Channel Subscribe**: Link to Telegram channel

## 🛠 Technical Stack

- **Bot Framework**: python-telegram-bot
- **Database**: SQLite with optional Google Sheets integration
- **Web Backend**: Flask with API endpoints
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Deployment**: Railway/Render (bot), GitHub Pages/shared hosting (website)
- **Notifications**: Telegram API integration

## 📁 Project Structure

```
printing-business-platform/
├── bot/                    # Telegram bot implementation
│   ├── bot.py             # Main bot application
│   ├── handlers/          # Command and conversation handlers
│   ├── models/            # Data models and database operations
│   └── utils/             # Helper functions
├── website/               # Web application
│   ├── app.py            # Flask application
│   ├── static/           # CSS, JS, images
│   ├── templates/        # HTML templates
│   └── api/              # API endpoints
├── database/             # Database files and schemas
├── config/               # Configuration files
├── docs/                 # Documentation
└── deployment/           # Deployment configurations
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- Telegram Bot Token (from @BotFather)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd printing-business-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_CHAT_ID=your_telegram_user_id
   CHANNEL_USERNAME=@your_channel
   FLASK_SECRET_KEY=your_secret_key
   ```

4. **Initialize database**
   ```bash
   python database/init_db.py
   ```

5. **Run the bot**
   ```bash
   python bot/bot.py
   ```

6. **Run the website** (in another terminal)
   ```bash
   python website/app.py
   ```

## 📊 Database Schema

### Orders
- customer_name (TEXT)
- company_name (TEXT)
- product_type (TEXT)
- quantity (INTEGER)
- delivery_date (TEXT)
- contact_info (TEXT)
- order_status (TEXT, default: 'Pending')
- created_at (TIMESTAMP)

### Schedules
- customer_name (TEXT)
- contact_info (TEXT)
- preferred_datetime (TEXT)
- status (TEXT, default: 'Pending')
- created_at (TIMESTAMP)

### Messages
- customer_name (TEXT)
- contact_info (TEXT)
- message_text (TEXT)
- status (TEXT, default: 'Pending')
- created_at (TIMESTAMP)

## 🔧 Configuration

### Bot Configuration
Set up your bot token and admin chat ID in the environment variables or `config/bot_config.py`.

### Website Configuration
Configure Flask settings in `config/web_config.py`.

## 📱 Usage

### For Customers
1. **Via Telegram Bot**: Search for your bot and start conversation
2. **Via Website**: Visit your website and use the forms

### For Business Owner
- All notifications arrive in your Telegram account
- Manage orders and schedules through the centralized system
- Use Telegram channel for broadcasts and updates

## 🚀 Deployment

### Bot Deployment (Railway/Render)
1. Connect your repository to Railway or Render
2. Set environment variables in the platform
3. Deploy the bot service

### Website Deployment
1. **GitHub Pages**: Push to GitHub and enable Pages
2. **Shared Hosting**: Upload files via FTP
3. **Cloud Hosting**: Deploy Flask app to cloud provider

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, contact [Your Contact Information] or create an issue in this repository.

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added website integration
- **v1.2.0**: Enhanced notifications and channel integration

---

Made with ❤️ for efficient printing business management