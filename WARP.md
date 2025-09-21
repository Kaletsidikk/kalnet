# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a **Printing Business Platform** that provides printing services through both a Telegram bot and a website, with centralized management and notifications. The platform consists of two main components that share a common SQLite database and notification system.

### Architecture Components

- **Telegram Bot** (`bot/`): Handles customer interactions, order processing, scheduling, and direct messaging via Telegram
- **Website** (`website/`): Flask web application providing the same functionality via web forms and API endpoints
- **Shared Database** (`database/`): SQLite database with models for orders, schedules, messages, users, and services
- **Configuration** (`config/`): Separate config files for bot and web components
- **Deployment** (`deployment/`): Docker and cloud deployment configurations

## Common Development Commands

### Setup and Installation
```powershell
# Initial setup (Windows)
python setup.py

# Manual setup
pip install -r requirements.txt
python database/init_db.py
```

### Running the Applications
```powershell
# Run Telegram bot
python bot/bot.py

# Run website (separate terminal)
python website/app.py

# Run both with Docker
docker-compose up -d
```

### Database Operations
```powershell
# Initialize database
python database/init_db.py

# Reset database (WARNING: destroys all data)
python database/init_db.py --reset
```

### Development and Testing
```powershell
# Code formatting
black bot/ website/ config/

# Linting
flake8 bot/ website/ config/

# Run tests (if they exist)
pytest

# Check for syntax errors
python -m py_compile bot/bot.py
python -m py_compile website/app.py
```

### Deployment Commands
```powershell
# Build Docker image
docker build -t printing-business-platform .

# Deploy to production (via Docker)
docker-compose -f docker-compose.yml up -d

# Check deployment logs
docker-compose logs -f
```

## Key Architecture Patterns

### Dual Interface Design
The platform uses a **dual interface pattern** where both the Telegram bot and website provide identical functionality:
- Both use the same database models (`bot/models/database.py`)
- Both use the same validation utilities (`bot/utils/validators.py`)
- Both send notifications via the same notification manager (`bot/utils/notifications.py`)
- Website API endpoints mirror bot conversation flows

### Database Architecture
- **Single SQLite Database**: Shared between bot and website
- **Model Classes**: `UserModel`, `OrderModel`, `ScheduleModel`, `MessageModel`, `ServiceModel`
- **Database Manager**: Central `DatabaseManager` class handles all DB operations
- **Auto-initialization**: Database creates itself on first run

### Notification System
All customer interactions (orders, schedules, messages) trigger Telegram notifications to the business owner via the `NotificationManager` class.

### Configuration Pattern
- **Environment-based Config**: Uses `.env` files with sensible defaults
- **Separate Configs**: `bot_config.py` and `web_config.py` for component-specific settings
- **Business Info Injection**: Business details are configurable and injected globally

### Conversation Handlers (Bot)
The Telegram bot uses **ConversationHandler** pattern with state management:
- `OrderHandler`: Manages multi-step order placement flow
- `ScheduleHandler`: Manages consultation booking flow  
- `MessageHandler`: Manages direct messaging flow

## Important Implementation Details

### Data Flow
1. **Customer Input** → **Validation** (`ValidationUtils`) → **Database Storage** → **Admin Notification**
2. Both bot and website follow identical validation and storage patterns
3. All interactions are logged in the database with timestamps

### Error Handling
- Database operations use context managers for automatic connection cleanup
- Bot includes error handlers that gracefully handle failures and notify users
- Website returns JSON error responses with appropriate HTTP status codes

### Security Considerations
- Telegram bot token and admin chat ID must be kept secure
- Flask secret key is required for session security
- SQLite database file should not be web-accessible in production

### Key File Dependencies
- `bot/bot.py` → Main bot orchestrator, imports all handlers
- `website/app.py` → Flask app, imports database models and utils
- `config/*.py` → Configuration loaded by both components
- `bot/models/database.py` → Core data models used by everything

### Testing Strategy
- Bot functionality should be tested via Telegram interactions
- Website API endpoints can be tested with HTTP requests
- Database operations can be tested directly via model classes
- Use `init_db.py --reset` to create clean test databases

## Development Workflows

### Adding New Features
1. Update database schema in `database/init_db.py` if needed
2. Add/modify models in `bot/models/database.py`
3. Implement bot conversation handler in `bot/handlers/`
4. Add corresponding website API endpoint in `website/app.py`
5. Update validation rules in `bot/utils/validators.py`
6. Test both interfaces thoroughly

### Modifying Business Logic
- Business information is configured in environment variables
- Service definitions are stored in database and can be modified via SQL
- Bot messages and menu structure are in `config/bot_config.py`
- Website content is in `config/web_config.py`

### Deployment Process
1. Test locally with both bot and website running
2. Verify all environment variables are set
3. Run database initialization
4. Deploy to hosting platform (Railway, Render, or Docker)
5. Test deployed bot via Telegram
6. Test deployed website via browser

## Environment Setup Requirements

### Required Environment Variables
- `BOT_TOKEN`: Telegram bot token from @BotFather
- `ADMIN_CHAT_ID`: Telegram user ID for admin notifications  
- `FLASK_SECRET_KEY`: Secret key for Flask sessions

### Optional Configuration
- `BUSINESS_NAME`, `BUSINESS_EMAIL`, `BUSINESS_PHONE`, `BUSINESS_ADDRESS`: Business details
- `CHANNEL_USERNAME`: Telegram channel for updates
- `DATABASE_URL`: Database connection string (defaults to SQLite)

### Development vs Production
- Development: Uses SQLite, Flask debug mode, detailed logging
- Production: Can use PostgreSQL, optimized for performance, secure headers

## Common Troubleshooting

### Bot Not Responding
- Verify `BOT_TOKEN` is correct and bot is active
- Check `ADMIN_CHAT_ID` matches your Telegram user ID
- Review bot logs for error messages

### Website Errors  
- Ensure Flask app is running on correct port
- Verify database file exists and is writable
- Check that all required environment variables are set

### Database Issues
- Run `python database/init_db.py` to ensure database is initialized
- Check file permissions on database directory
- Verify SQLite is available in Python environment

### Notification Failures
- Confirm bot token has permission to send messages
- Verify admin chat ID is a valid Telegram user
- Check network connectivity to Telegram API