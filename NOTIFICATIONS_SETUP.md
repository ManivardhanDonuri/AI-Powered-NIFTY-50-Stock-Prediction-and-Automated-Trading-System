# Trading System Notifications Setup Guide

This guide will help you set up Telegram and WhatsApp notifications for your ML-enhanced trading system.

## 🚀 Quick Start

### Option 1: Automated System (Recommended)
1. **Setup automated trading:**
   ```bash
   python setup_automated_trading.py
   ```

2. **Start automated system:**
   ```bash
   # Windows
   start_automated_trading.bat
   
   # Linux/Mac
   ./start_automated_trading.sh
   ```

### Option 2: Manual Setup
1. **Run the setup script:**
   ```bash
   python setup_notifications.py
   ```

2. **Test your configuration:**
   ```bash
   python main.py test-notifications
   ```

3. **Start receiving notifications:**
   ```bash
   python main.py analysis
   ```

## 📱 Telegram Setup

### Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "My Trading Bot")
4. Choose a username (e.g., "my_trading_bot")
5. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID

1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id": YOUR_CHAT_ID}`
4. Copy the chat ID (a number like: `123456789`)

### Step 3: Test Your Bot

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
     -H "Content-Type: application/json" \
     -d '{"chat_id": "<YOUR_CHAT_ID>", "text": "Test message"}'
```

## 📱 WhatsApp Setup

### Option 1: WhatsApp Business API (Recommended)

1. **Create a Meta for Developers account:**
   - Go to [developers.facebook.com](https://developers.facebook.com)
   - Create an app and add WhatsApp product

2. **Get your credentials:**
   - Access Token
   - Phone Number ID
   - Recipient phone number (with country code)

3. **Test your setup:**
   ```bash
   curl -X POST "https://graph.facebook.com/v17.0/<PHONE_NUMBER_ID>/messages" \
        -H "Authorization: Bearer <ACCESS_TOKEN>" \
        -H "Content-Type: application/json" \
        -d '{
          "messaging_product": "whatsapp",
          "to": "<RECIPIENT_PHONE>",
          "type": "text",
          "text": {"body": "Test message"}
        }'
   ```

### Option 2: Web Automation (Fallback)

1. **Install Chrome browser**
2. **Install Selenium:**
   ```bash
   pip install selenium
   ```
3. **First run requires QR code scanning**

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your credentials:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_ID=your_phone_number_id_here
WHATSAPP_RECIPIENT=+1234567890
```

### Configuration File

The `config.json` file contains notification settings:

```json
{
  "notifications": {
    "enabled": true,
    "telegram": {
      "enabled": true,
      "bot_token": "${TELEGRAM_BOT_TOKEN}",
      "chat_id": "${TELEGRAM_CHAT_ID}",
      "rate_limit": 30
    },
    "whatsapp": {
      "enabled": true,
      "method": "business_api",
      "access_token": "${WHATSAPP_ACCESS_TOKEN}",
      "phone_number_id": "${WHATSAPP_PHONE_ID}",
      "recipient": "${WHATSAPP_RECIPIENT}"
    },
    "preferences": {
      "signal_types": ["BUY", "SELL"],
      "min_confidence": 0.7,
      "stocks": ["ALL"],
      "quiet_hours": {
        "enabled": true,
        "start": "22:00",
        "end": "08:00"
      }
    },
    "delivery": {
      "max_retries": 3,
      "retry_delay": 5,
      "queue_size": 100,
      "batch_size": 5
    }
  }
}
```

## 📊 Notification Types

### Trading Signals

You'll receive notifications for:
- **BUY signals** 🟢 with price, confidence, and reasoning
- **SELL signals** 🔴 with suggested targets and stop-loss
- **ML predictions** with model confidence levels

Example message:
```
🟢 BUY SIGNAL

📈 Stock: RELIANCE.NS
💰 Price: ₹2,450.50
🎯 Confidence: ⭐⭐⭐⭐ (85.2%)
🤖 ML Probability: 78.5%

📊 Suggested Levels:
• Target: ₹2,523.52
• Stop Loss: ₹2,401.49

💡 Reason: RSI oversold (28.5) and SMA crossover bullish

🕐 14:30:25 | 15/10/2024
```

### Portfolio Summaries

Daily/weekly performance summaries:
```
📈 PORTFOLIO SUMMARY

💰 Total P&L: 🟢 ₹15,250.75
📊 Win Rate: 72.5%
🔢 Total Trades: 28
📈 Sharpe Ratio: 1.85

📅 Generated: 15/10/2024 18:00
```

### System Alerts

- Error notifications 🚨
- System status updates ℹ️
- Performance warnings ⚠️

## 🎛️ Customization

### Signal Filtering

Filter notifications by:
- **Signal types:** BUY, SELL, or both
- **Confidence level:** Minimum threshold (0.0-1.0)
- **Stock symbols:** Specific stocks or all
- **Quiet hours:** No notifications during specified times

### Platform Preferences

- **Telegram:** All signals and summaries
- **WhatsApp:** High-confidence signals only (configurable threshold)

### Delivery Settings

- **Retry logic:** 3 attempts with exponential backoff
- **Rate limiting:** Respects platform limits
- **Queue management:** Priority-based message handling

## 🧪 Testing

### Test All Services
```bash
python main.py test-notifications
```

### Test Individual Components
```python
from notifications.notification_manager import NotificationManager

# Initialize manager
manager = NotificationManager()

# Test services
results = manager.test_notifications()
print(results)

# Get health status
status = manager.get_health_status()
print(status)
```

## 🔧 Troubleshooting

### Common Issues

1. **Telegram bot not responding:**
   - Check bot token is correct
   - Ensure you've sent at least one message to the bot
   - Verify chat ID is correct

2. **WhatsApp messages not sending:**
   - Check access token and phone number ID
   - Verify recipient number format (+1234567890)
   - Ensure WhatsApp Business API is properly configured

3. **No notifications received:**
   - Check if notifications are enabled in config
   - Verify signal confidence meets minimum threshold
   - Check if quiet hours are blocking messages

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger('notifications').setLevel(logging.DEBUG)
```

### Log Files

Check logs for detailed information:
- `trading_system.log` - Main system logs
- Console output during setup and testing

## 📈 Usage Examples

### Automated System (Runs Continuously)
```bash
# Setup and start automated system
python setup_automated_trading.py
start_automated_trading.bat  # Windows
./start_automated_trading.sh # Linux/Mac

# The system will automatically:
# - Monitor markets every 5 minutes during trading hours
# - Send notifications for all buy/sell signals
# - Generate daily analysis at 4:00 PM
# - Send portfolio summaries at 6:00 PM
# - Retrain models weekly on Sundays
# - Perform health checks every hour
```

### Manual Usage
```bash
# Run complete analysis with notifications
python main.py analysis

# Daily monitoring with notifications
python main.py daily

# Test notification setup
python main.py test-notifications
```

### Advanced Configuration

Update preferences programmatically:
```python
from ml_signal_generator_enhanced import EnhancedMLSignalGenerator

generator = EnhancedMLSignalGenerator()

# Update notification preferences
new_preferences = {
    'min_confidence': 0.8,
    'signal_types': ['BUY'],
    'stocks': ['RELIANCE.NS', 'TCS.NS']
}

generator.update_notification_preferences(new_preferences)
```

## 🔒 Security

- Store credentials in environment variables
- Use `.env` file for local development
- Never commit credentials to version control
- Regularly rotate API tokens
- Monitor notification logs for suspicious activity

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review log files for error messages
3. Test individual components
4. Verify API credentials and permissions
5. Check network connectivity

For additional help, refer to:
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- Trading system logs and error messages