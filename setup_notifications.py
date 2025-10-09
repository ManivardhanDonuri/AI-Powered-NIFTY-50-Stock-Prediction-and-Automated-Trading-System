"""
Notification Setup Utility

Interactive script to help users configure Telegram and WhatsApp notifications.
"""

import os
import json
import requests
from typing import Dict, Any, Optional

def print_header():
    """Print setup header."""
    print("🔔 TRADING SYSTEM NOTIFICATION SETUP")
    print("="*50)
    print("This script will help you configure Telegram and WhatsApp notifications")
    print("for your trading system.\n")

def setup_telegram() -> Dict[str, Any]:
    """Setup Telegram bot configuration."""
    print("📱 TELEGRAM SETUP")
    print("-" * 20)
    print("To set up Telegram notifications, you need to:")
    print("1. Create a Telegram bot using @BotFather")
    print("2. Get your bot token")
    print("3. Get your chat ID\n")
    
    # Get bot token
    while True:
        bot_token = input("Enter your Telegram bot token (or 'skip' to skip): ").strip()
        
        if bot_token.lower() == 'skip':
            return {'enabled': False}
        
        if not bot_token:
            print("❌ Bot token cannot be empty")
            continue
        
        # Validate bot token
        if validate_telegram_bot(bot_token):
            print("✅ Bot token is valid!")
            break
        else:
            print("❌ Invalid bot token. Please check and try again.")
    
    # Get chat ID
    print("\nTo get your chat ID:")
    print("1. Send a message to your bot")
    print("2. Visit: https://api.telegram.org/bot{}/getUpdates".format(bot_token))
    print("3. Look for 'chat':{'id': YOUR_CHAT_ID}")
    
    while True:
        chat_id = input("\nEnter your chat ID: ").strip()
        
        if not chat_id:
            print("❌ Chat ID cannot be empty")
            continue
        
        # Try to convert to int to validate
        try:
            int(chat_id)
            break
        except ValueError:
            print("❌ Chat ID must be a number")
    
    # Test the configuration
    print("\n🧪 Testing Telegram configuration...")
    if test_telegram_config(bot_token, chat_id):
        print("✅ Telegram configuration successful!")
        
        return {
            'enabled': True,
            'bot_token': bot_token,
            'chat_id': chat_id,
            'rate_limit': 30
        }
    else:
        print("❌ Telegram test failed. Please check your configuration.")
        return {'enabled': False}

def setup_whatsapp() -> Dict[str, Any]:
    """Setup WhatsApp configuration."""
    print("\n📱 WHATSAPP SETUP")
    print("-" * 20)
    print("WhatsApp notifications can be configured in two ways:")
    print("1. WhatsApp Business API (recommended)")
    print("2. Web automation (fallback)")
    
    while True:
        method = input("\nChoose method (1 for Business API, 2 for Web, 'skip' to skip): ").strip()
        
        if method.lower() == 'skip':
            return {'enabled': False}
        
        if method == '1':
            return setup_whatsapp_business_api()
        elif method == '2':
            return setup_whatsapp_web()
        else:
            print("❌ Please enter 1, 2, or 'skip'")

def setup_whatsapp_business_api() -> Dict[str, Any]:
    """Setup WhatsApp Business API."""
    print("\n🏢 WhatsApp Business API Setup")
    print("You need:")
    print("1. WhatsApp Business Account")
    print("2. Access token from Meta for Developers")
    print("3. Phone number ID")
    print("4. Recipient phone number")
    
    # Get access token
    access_token = input("\nEnter your WhatsApp access token (or 'back' to go back): ").strip()
    if access_token.lower() == 'back':
        return setup_whatsapp()
    
    if not access_token:
        print("❌ Access token cannot be empty")
        return {'enabled': False}
    
    # Get phone number ID
    phone_number_id = input("Enter your phone number ID: ").strip()
    if not phone_number_id:
        print("❌ Phone number ID cannot be empty")
        return {'enabled': False}
    
    # Get recipient
    recipient = input("Enter recipient phone number (with country code, e.g., +1234567890): ").strip()
    if not recipient:
        print("❌ Recipient cannot be empty")
        return {'enabled': False}
    
    return {
        'enabled': True,
        'method': 'business_api',
        'access_token': access_token,
        'phone_number_id': phone_number_id,
        'recipient': recipient
    }

def setup_whatsapp_web() -> Dict[str, Any]:
    """Setup WhatsApp Web automation."""
    print("\n🌐 WhatsApp Web Automation Setup")
    print("This method uses browser automation and requires:")
    print("1. Chrome browser installed")
    print("2. Selenium WebDriver")
    print("3. Manual QR code scanning on first run")
    
    recipient = input("\nEnter recipient name or phone number: ").strip()
    if not recipient:
        print("❌ Recipient cannot be empty")
        return {'enabled': False}
    
    return {
        'enabled': True,
        'method': 'web_automation',
        'recipient': recipient,
        'session_path': './whatsapp_session',
        'headless': False  # Set to False for first-time QR scanning
    }

def setup_preferences() -> Dict[str, Any]:
    """Setup notification preferences."""
    print("\n⚙️ NOTIFICATION PREFERENCES")
    print("-" * 30)
    
    preferences = {}
    
    # Signal types
    print("Which signal types do you want to receive?")
    print("1. BUY signals only")
    print("2. SELL signals only") 
    print("3. Both BUY and SELL signals")
    
    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice == '1':
            preferences['signal_types'] = ['BUY']
            break
        elif choice == '2':
            preferences['signal_types'] = ['SELL']
            break
        elif choice == '3':
            preferences['signal_types'] = ['BUY', 'SELL']
            break
        else:
            print("❌ Please enter 1, 2, or 3")
    
    # Confidence threshold
    while True:
        try:
            confidence = float(input("Minimum confidence level (0.0-1.0, recommended 0.7): ").strip() or "0.7")
            if 0.0 <= confidence <= 1.0:
                preferences['min_confidence'] = confidence
                break
            else:
                print("❌ Confidence must be between 0.0 and 1.0")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Stock filter
    print("\nStock filtering:")
    print("1. All stocks")
    print("2. Specific stocks only")
    
    while True:
        choice = input("Enter choice (1-2): ").strip()
        if choice == '1':
            preferences['stocks'] = ['ALL']
            break
        elif choice == '2':
            stocks = input("Enter stock symbols separated by commas (e.g., RELIANCE.NS,TCS.NS): ").strip()
            if stocks:
                preferences['stocks'] = [s.strip().upper() for s in stocks.split(',')]
                break
            else:
                print("❌ Please enter at least one stock symbol")
        else:
            print("❌ Please enter 1 or 2")
    
    # Quiet hours
    quiet_hours_enabled = input("\nEnable quiet hours? (y/n): ").strip().lower() == 'y'
    
    if quiet_hours_enabled:
        start_time = input("Quiet hours start time (HH:MM, e.g., 22:00): ").strip() or "22:00"
        end_time = input("Quiet hours end time (HH:MM, e.g., 08:00): ").strip() or "08:00"
        
        preferences['quiet_hours'] = {
            'enabled': True,
            'start': start_time,
            'end': end_time
        }
    else:
        preferences['quiet_hours'] = {'enabled': False}
    
    return preferences

def validate_telegram_bot(bot_token: str) -> bool:
    """Validate Telegram bot token."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        return response.status_code == 200 and response.json().get('ok', False)
    except:
        return False

def test_telegram_config(bot_token: str, chat_id: str) -> bool:
    """Test Telegram configuration by sending a test message."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': '🤖 Trading System Setup Test\n\nTelegram notifications are configured correctly!',
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200 and response.json().get('ok', False)
    except:
        return False

def save_configuration(config: Dict[str, Any]):
    """Save configuration to config.json."""
    config_file = 'config.json'
    
    # Load existing configuration
    try:
        with open(config_file, 'r') as f:
            existing_config = json.load(f)
    except FileNotFoundError:
        existing_config = {}
    
    # Update with notification configuration
    existing_config['notifications'] = config
    
    # Save updated configuration
    with open(config_file, 'w') as f:
        json.dump(existing_config, f, indent=4)
    
    print(f"\n✅ Configuration saved to {config_file}")

def create_env_template(telegram_config: Dict[str, Any], whatsapp_config: Dict[str, Any]):
    """Create .env template file."""
    env_content = "# Trading System Notification Environment Variables\n"
    env_content += "# Copy this file to .env and fill in your actual values\n\n"
    
    if telegram_config.get('enabled'):
        env_content += "# Telegram Configuration\n"
        env_content += f"TELEGRAM_BOT_TOKEN={telegram_config.get('bot_token', 'your_bot_token_here')}\n"
        env_content += f"TELEGRAM_CHAT_ID={telegram_config.get('chat_id', 'your_chat_id_here')}\n\n"
    
    if whatsapp_config.get('enabled') and whatsapp_config.get('method') == 'business_api':
        env_content += "# WhatsApp Business API Configuration\n"
        env_content += f"WHATSAPP_ACCESS_TOKEN={whatsapp_config.get('access_token', 'your_access_token_here')}\n"
        env_content += f"WHATSAPP_PHONE_ID={whatsapp_config.get('phone_number_id', 'your_phone_id_here')}\n"
        env_content += f"WHATSAPP_RECIPIENT={whatsapp_config.get('recipient', 'recipient_phone_here')}\n\n"
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment template created: .env.template")
    print("📝 Remember to create .env file with your actual credentials!")

def main():
    """Main setup function."""
    print_header()
    
    # Setup Telegram
    telegram_config = setup_telegram()
    
    # Setup WhatsApp
    whatsapp_config = setup_whatsapp()
    
    # Setup preferences
    preferences = setup_preferences()
    
    # Create final configuration
    notification_config = {
        'enabled': telegram_config.get('enabled', False) or whatsapp_config.get('enabled', False),
        'telegram': telegram_config,
        'whatsapp': whatsapp_config,
        'preferences': preferences,
        'delivery': {
            'max_retries': 3,
            'retry_delay': 5,
            'queue_size': 100,
            'batch_size': 5
        }
    }
    
    # Show summary
    print("\n📋 CONFIGURATION SUMMARY")
    print("=" * 30)
    print(f"Notifications Enabled: {notification_config['enabled']}")
    print(f"Telegram Enabled: {telegram_config.get('enabled', False)}")
    print(f"WhatsApp Enabled: {whatsapp_config.get('enabled', False)}")
    print(f"Signal Types: {', '.join(preferences['signal_types'])}")
    print(f"Min Confidence: {preferences['min_confidence']}")
    print(f"Quiet Hours: {preferences['quiet_hours']['enabled']}")
    
    # Confirm and save
    if input("\nSave this configuration? (y/n): ").strip().lower() == 'y':
        save_configuration(notification_config)
        create_env_template(telegram_config, whatsapp_config)
        
        print("\n🎉 Setup complete!")
        print("\nNext steps:")
        print("1. Test your configuration: python main.py test-notifications")
        print("2. Run the trading system: python main.py analysis")
        print("3. Check notification logs in trading_system.log")
    else:
        print("\n❌ Configuration not saved.")

if __name__ == "__main__":
    main()