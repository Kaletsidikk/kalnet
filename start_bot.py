#!/usr/bin/env python3
"""
Simple start script for the Telegram bot deployment
This ensures the bot runs properly in production environments like Render
"""

import os
import sys
import logging

# Ensure we're in the right directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the bot"""
    try:
        logger.info("🚀 Starting Telegram Bot...")
        
        # Import and run the simple, compatible bot
        from bot_simple import main as run_bot
        run_bot()
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure all dependencies are installed properly")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
