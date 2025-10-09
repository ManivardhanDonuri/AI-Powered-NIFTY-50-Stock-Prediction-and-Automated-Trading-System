"""
Notification Configuration Validation Script

Validates notification configuration and tests connectivity.
"""

import json
import os
import sys
from notifications.config import NotificationConfigManager
from notifications.telegram_service import TelegramService
from notifications.whatsapp_service import WhatsAppService

def validate_configuration():
    """Validate notification configuration."""
    print("🔍 VALIDATING NOTIFICATION CONFIGURATION")
    print("=" * 50)
    
    try:
        # Load configuration
        config_manager = NotificationConfigManager()
        config = config_manager.load_config()
        
        # Validate configuration
        validation_result = config_manager.validate_config(config)
        
        print(f"Configuration Valid: {'✅ YES' if validation_result['valid'] else '❌ NO'}")
        
        if validation_result['errors']:
            print("\n❌ ERRORS:")
            for error in validation_result['errors']:
                print(f"  • {error}")
        
        if validation_result['warnings']:
            print("\n⚠️ WARNINGS:")
            for warning in validation_result['warnings']:
                print(f"  • {warning}")
        
        if not validation_result['valid']:
            return False
        
        # Test services if configuration is valid
        print("\n🧪 TESTING SERVICES")
        print("-" * 20)
        
        success = True
        
        # Test Telegram
        if config.telegram_enabled:
            print("Testing Telegram service...")
            telegram_service = TelegramService(config.telegram_config)
            
            if telegram_service.validate_connection():
                print("✅ Telegram: Connection valid")
            else:
                print("❌ Telegram: Connection failed")
                success = False
        else:
            print("⏭️ Telegram: Disabled")
        
        # Test WhatsApp
        if config.whatsapp_enabled:
            print("Testing WhatsApp service...")
            whatsapp_service = WhatsAppService(config.whatsapp_config)
            
            if whatsapp_service.validate_connection():
                print("✅ WhatsApp: Connection valid")
            else:
                print("❌ WhatsApp: Connection failed")
                success = False
        else:
            print("⏭️ WhatsApp: Disabled")
        
        return success
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return False

def check_environment_variables():
    """Check if required environment variables are set."""
    print("\n🔐 CHECKING ENVIRONMENT VARIABLES")
    print("-" * 35)
    
    required_vars = [
        ('TELEGRAM_BOT_TOKEN', 'Telegram bot token'),
        ('TELEGRAM_CHAT_ID', 'Telegram chat ID'),
        ('WHATSAPP_ACCESS_TOKEN', 'WhatsApp access token'),
        ('WHATSAPP_PHONE_ID', 'WhatsApp phone number ID'),
        ('WHATSAPP_RECIPIENT', 'WhatsApp recipient')
    ]
    
    missing_vars = []
    
    for var_name, description in required_vars:
        value = os.getenv(var_name)
        if value:
            # Mask sensitive values
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var_name}: {masked_value}")
        else:
            print(f"❌ {var_name}: Not set")
            missing_vars.append((var_name, description))
    
    if missing_vars:
        print(f"\n⚠️ Missing {len(missing_vars)} environment variables:")
        for var_name, description in missing_vars:
            print(f"  • {var_name}: {description}")
        print("\nCreate a .env file or set these variables in your environment.")
        return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 CHECKING DEPENDENCIES")
    print("-" * 25)
    
    required_packages = [
        ('requests', 'HTTP requests'),
        ('selenium', 'WhatsApp web automation (optional)')
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            if package == 'selenium':
                print(f"⚠️ {package}: Not installed (optional for WhatsApp web)")
            else:
                print(f"❌ {package}: Not installed")
                missing_packages.append((package, description))
    
    if missing_packages:
        print(f"\n❌ Missing {len(missing_packages)} required packages:")
        for package, description in missing_packages:
            print(f"  • {package}: {description}")
        print("\nInstall missing packages: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main validation function."""
    print("🔔 NOTIFICATION SYSTEM VALIDATION")
    print("=" * 40)
    
    all_checks_passed = True
    
    # Check dependencies
    if not check_dependencies():
        all_checks_passed = False
    
    # Check environment variables
    if not check_environment_variables():
        all_checks_passed = False
    
    # Validate configuration
    if not validate_configuration():
        all_checks_passed = False
    
    # Final result
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("Your notification system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python main.py test-notifications")
        print("2. Run: python main.py analysis")
    else:
        print("❌ SOME CHECKS FAILED")
        print("Please fix the issues above before using notifications.")
        sys.exit(1)

if __name__ == "__main__":
    main()