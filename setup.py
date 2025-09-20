#!/usr/bin/env python3
"""
Setup script for Printing Business Platform
This script helps initialize the project with all necessary components.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║     Printing Business Platform Setup          ║
    ║          Telegram Bot + Website               ║
    ╚═══════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required system dependencies are available"""
    dependencies = ['git', 'pip']
    
    for dep in dependencies:
        if shutil.which(dep) is None:
            print(f"❌ Error: {dep} is not installed or not in PATH")
            sys.exit(1)
        print(f"✅ {dep} is available")

def install_requirements():
    """Install Python requirements"""
    try:
        print("📦 Installing Python dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        sys.exit(1)

def initialize_database():
    """Initialize the database"""
    try:
        print("🗄️ Initializing database...")
        subprocess.run([sys.executable, 'database/init_db.py'], check=True)
        print("✅ Database initialized successfully")
    except subprocess.CalledProcessError:
        print("❌ Error initializing database")
        sys.exit(1)

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your actual values before running the application")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.example file found")

def setup_git_hooks():
    """Set up git hooks for development"""
    hooks_dir = Path('.git/hooks')
    if hooks_dir.exists():
        # Create pre-commit hook
        pre_commit = hooks_dir / 'pre-commit'
        pre_commit.write_text("""#!/bin/sh
# Pre-commit hook for Printing Business Platform

echo "Running pre-commit checks..."

# Check for .env file in commits
if git diff --cached --name-only | grep -q "^\.env$"; then
    echo "❌ Error: .env file should not be committed"
    echo "Please remove .env from your commit"
    exit 1
fi

# Run basic Python syntax check
python -m py_compile bot/bot.py
if [ $? -ne 0 ]; then
    echo "❌ Error: bot/bot.py has syntax errors"
    exit 1
fi

python -m py_compile website/app.py
if [ $? -ne 0 ]; then
    echo "❌ Error: website/app.py has syntax errors"
    exit 1
fi

echo "✅ Pre-commit checks passed"
""")
        pre_commit.chmod(0o755)
        print("✅ Git pre-commit hook installed")

def print_next_steps():
    """Print next steps for the user"""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║                Setup Complete!                 ║
    ╚═══════════════════════════════════════════════╝
    
    🎉 Your Printing Business Platform is ready!
    
    📋 Next Steps:
    
    1. Configure your environment:
       • Edit .env file with your actual values
       • Get bot token from @BotFather on Telegram
       • Get your Telegram user ID for admin notifications
    
    2. Test locally:
       • Bot: python bot/bot.py
       • Website: python website/app.py
    
    3. Deploy your platform:
       • See deployment/DEPLOYMENT.md for hosting options
       • Railway, Render, or Docker deployment available
    
    📚 Documentation:
       • README.md - Main documentation
       • deployment/DEPLOYMENT.md - Deployment guide
       • .env.example - Environment variables reference
    
    🔧 Configuration files created:
       • .env (from template)
       • Database initialized
       • Git hooks installed
    
    💡 Tips:
       • Test all bot features before deployment
       • Set up your Telegram channel for updates
       • Customize business information in config files
    
    🚀 Happy printing business management!
    """)

def main():
    """Main setup function"""
    print_header()
    
    # Check system requirements
    print("🔍 Checking system requirements...")
    check_python_version()
    check_dependencies()
    
    # Install dependencies
    install_requirements()
    
    # Initialize database
    initialize_database()
    
    # Create environment file
    create_env_file()
    
    # Set up git hooks
    setup_git_hooks()
    
    # Print success message and next steps
    print_next_steps()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)