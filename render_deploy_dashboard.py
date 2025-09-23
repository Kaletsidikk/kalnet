#!/usr/bin/env python3
"""
Render Dashboard-Only Deployment Script
Dedicated script for deploying only the admin dashboard
"""

import os
import sys
import logging
import time
from datetime import datetime
import signal
import traceback
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
    logger.info("🛑 Dashboard shutdown signal received")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_environment():
    """Check required environment variables for dashboard"""
    logger.info("🔍 Checking dashboard environment variables...")
    
    required_vars = {
        'FLASK_SECRET_KEY': 'Flask secret key for sessions',
        'ADMIN_PASSWORD': 'Admin dashboard password',
        'PORT': 'Server port'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ Dashboard environment variables OK")
    return True

def start_dashboard():
    """Start Flask dashboard application"""
    try:
        logger.info("📊 Starting admin dashboard service...")
        
        # Load environment variables
        load_dotenv()
        
        # Import the admin dashboard app
        from admin_app import app
        
        # Get port from environment
        port = int(os.environ.get('PORT', 5001))
        host = '0.0.0.0'
        
        logger.info(f"📊 Dashboard starting on {host}:{port}")
        
        # Add health check route for Render
        @app.route('/health')
        def health_check():
            return {
                'status': 'healthy',
                'service': 'dashboard',
                'timestamp': datetime.now().isoformat()
            }
        
        # Start Flask with production settings
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"❌ Dashboard startup error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    """Main function for dashboard-only deployment"""
    start_time = time.time()
    logger.info("📊 RENDER DASHBOARD-ONLY DEPLOYMENT")
    logger.info("=" * 50)
    
    try:
        # Environment check
        if not check_environment():
            logger.error("❌ Environment check failed")
            sys.exit(1)
        
        logger.info("🎯 Mode: DASHBOARD-ONLY SERVICE")
        
        # Start dashboard (this will run indefinitely)
        start_dashboard()
    
    except KeyboardInterrupt:
        logger.info("🛑 Dashboard shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        elapsed = time.time() - start_time
        logger.info(f"⏱️ Total runtime: {elapsed:.2f} seconds")

if __name__ == '__main__':
    main()
