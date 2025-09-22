#!/usr/bin/env python3
"""
Install script for the Telegram bot dependencies
This will ensure all required packages are installed correctly
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 Installing Telegram Bot Dependencies...")
    
    # Required packages
    packages = [
        "python-telegram-bot==20.7",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "python-dateutil==2.8.2"
    ]
    
    failed_packages = []
    
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("Please install them manually using:")
        for package in failed_packages:
            print(f"   pip install {package}")
        sys.exit(1)
    else:
        print("\n✅ All dependencies installed successfully!")
        print("🎉 You can now run the bot using: python3 test_bot_fixed.py")

if __name__ == "__main__":
    main()
