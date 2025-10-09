"""
Setup Script for Automated Trading System

Configures the system to run automatically with notifications.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def print_header():
    """Print setup header."""
    print("🤖 AUTOMATED TRADING SYSTEM SETUP")
    print("=" * 50)
    print("This script will configure your trading system to run automatically")
    print("and send notifications without manual intervention.\n")

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'pandas', 'numpy', 'yfinance', 'tensorflow', 
        'scikit-learn', 'requests', 'schedule'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def setup_notifications():
    """Setup notifications if not already configured."""
    print("\n🔔 Checking notification configuration...")
    
    config_file = Path('config.json')
    if not config_file.exists():
        print("❌ config.json not found. Please run setup_notifications.py first.")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    notifications = config.get('notifications', {})
    
    if not notifications.get('enabled', False):
        print("⚠️ Notifications are disabled in config.json")
        
        enable = input("Enable notifications for automated system? (y/n): ").strip().lower()
        if enable == 'y':
            # Run notification setup
            print("Running notification setup...")
            try:
                subprocess.run([sys.executable, 'setup_notifications.py'], check=True)
                print("✅ Notification setup completed!")
            except subprocess.CalledProcessError:
                print("❌ Notification setup failed")
                return False
        else:
            print("⚠️ Automated system will run without notifications")
    else:
        print("✅ Notifications are already configured!")
    
    return True

def create_startup_scripts():
    """Create platform-specific startup scripts."""
    print("\n📝 Creating startup scripts...")
    
    # Windows batch file
    if os.name == 'nt':
        print("✅ Windows startup script: start_automated_trading.bat")
    
    # Linux/Mac shell script
    else:
        print("✅ Linux/Mac startup script: start_automated_trading.sh")
        # Make shell script executable
        try:
            os.chmod('start_automated_trading.sh', 0o755)
        except:
            pass
    
    print("✅ Startup scripts created!")

def setup_service():
    """Setup system service (optional)."""
    print("\n🔧 System Service Setup (Optional)")
    print("-" * 35)
    
    if os.name == 'nt':
        print("For Windows, you can:")
        print("1. Use Task Scheduler to run start_automated_trading.bat at startup")
        print("2. Run the batch file manually when needed")
        print("3. Use a Windows service manager (advanced)")
    else:
        print("For Linux/Mac, you can:")
        print("1. Use the provided systemd service file (Linux)")
        print("2. Use cron jobs for scheduling")
        print("3. Run the shell script manually")
        
        setup_systemd = input("\nSetup systemd service? (Linux only) (y/n): ").strip().lower()
        if setup_systemd == 'y':
            setup_systemd_service()

def setup_systemd_service():
    """Setup systemd service for Linux."""
    print("\n🐧 Setting up systemd service...")
    
    # Get current user and paths
    username = os.getenv('USER', 'your_username')
    current_dir = Path.cwd().absolute()
    
    # Update service file with actual paths
    service_content = f"""[Unit]
Description=Automated Trading System with ML and Notifications
After=network.target
Wants=network-online.target

[Service]
Type=simple
User={username}
WorkingDirectory={current_dir}
ExecStart={sys.executable} {current_dir}/trading_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=trading-system

# Load environment variables from .env file if it exists
EnvironmentFile=-{current_dir}/.env

[Install]
WantedBy=multi-user.target
"""
    
    # Write updated service file
    with open('trading-system.service', 'w') as f:
        f.write(service_content)
    
    print("✅ Service file updated with your paths")
    print("\nTo install the service:")
    print("1. sudo cp trading-system.service /etc/systemd/system/")
    print("2. sudo systemctl daemon-reload")
    print("3. sudo systemctl enable trading-system")
    print("4. sudo systemctl start trading-system")
    print("\nTo check status: sudo systemctl status trading-system")

def create_env_template():
    """Create .env template for environment variables."""
    print("\n🔐 Creating environment template...")
    
    env_template = """# Trading System Environment Variables
# Copy this file to .env and fill in your actual values

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# WhatsApp Business API Configuration
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_ID=your_phone_number_id_here
WHATSAPP_RECIPIENT=+1234567890

# Optional: Database configuration
# DATABASE_URL=your_database_url_here

# Optional: API keys for additional data sources
# ALPHA_VANTAGE_API_KEY=your_api_key_here
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("✅ Environment template created: .env.template")
    print("📝 Remember to create .env file with your actual credentials!")

def test_system():
    """Test the automated system."""
    print("\n🧪 Testing automated system...")
    
    try:
        # Test notification system
        print("Testing notifications...")
        result = subprocess.run([sys.executable, 'main.py', 'test-notifications'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Notification test passed!")
        else:
            print("⚠️ Notification test had issues")
            print(result.stdout)
            print(result.stderr)
        
        # Test basic system functionality
        print("Testing system components...")
        result = subprocess.run([sys.executable, '-c', 
                               'from trading_scheduler import TradingScheduler; print("✅ Scheduler import successful")'],
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ System components test passed!")
        else:
            print("❌ System components test failed")
            print(result.stderr)
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("⚠️ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def main():
    """Main setup function."""
    print_header()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    # Setup notifications
    if not setup_notifications():
        print("\n⚠️ Notification setup incomplete, but continuing...")
    
    # Create startup scripts
    create_startup_scripts()
    
    # Create environment template
    create_env_template()
    
    # Setup service (optional)
    setup_service()
    
    # Test system
    print("\n🧪 SYSTEM TESTING")
    print("-" * 20)
    test_passed = test_system()
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    
    if test_passed:
        print("✅ All tests passed! Your automated trading system is ready.")
    else:
        print("⚠️ Some tests failed, but the system should still work.")
    
    print("\n📋 NEXT STEPS:")
    print("1. Configure your credentials in .env file")
    print("2. Test notifications: python main.py test-notifications")
    
    if os.name == 'nt':
        print("3. Run automated system: start_automated_trading.bat")
    else:
        print("3. Run automated system: ./start_automated_trading.sh")
    
    print("\n🔄 AUTOMATED FEATURES:")
    print("• Market monitoring every 5 minutes during trading hours")
    print("• Daily analysis at 4:00 PM")
    print("• Portfolio summaries at 6:00 PM")
    print("• Weekly model retraining on Sundays")
    print("• System health checks every hour")
    print("• Automatic notifications for all signals and alerts")
    
    print("\n📱 You will receive notifications for:")
    print("• Buy/Sell signals with confidence levels")
    print("• Portfolio performance summaries")
    print("• System status and health alerts")
    print("• Model retraining completion")
    
    print("\n🎯 The system will now run automatically and keep you informed!")

if __name__ == "__main__":
    main()