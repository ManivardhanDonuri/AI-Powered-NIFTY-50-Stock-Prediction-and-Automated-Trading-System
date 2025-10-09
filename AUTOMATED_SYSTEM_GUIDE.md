# 🤖 Automated Trading System Guide

## 🎯 Overview

Your trading system now runs **completely automatically** and sends notifications without any manual intervention. Once started, it will:

- **Monitor markets continuously** during trading hours (9:15 AM - 3:30 PM IST)
- **Send instant notifications** for all buy/sell signals via Telegram and WhatsApp
- **Generate daily analysis** automatically after market close
- **Send portfolio summaries** every evening
- **Retrain ML models** weekly to stay current
- **Monitor system health** and alert you to any issues

## 🚀 Getting Started

### 1. One-Time Setup
```bash
# Run the automated setup script
python setup_automated_trading.py
```

This will:
- ✅ Check all dependencies
- ✅ Configure notifications (if not already done)
- ✅ Create startup scripts for your platform
- ✅ Test the system
- ✅ Provide next steps

### 2. Start the Automated System

**Windows:**
```bash
start_automated_trading.bat
```

**Linux/Mac:**
```bash
./start_automated_trading.sh
```

**As a Background Service (Linux):**
```bash
# Install as systemd service
sudo cp trading-system.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trading-system
sudo systemctl start trading-system
```

## 📅 Automated Schedule

### During Market Hours (9:15 AM - 3:30 PM IST)
- **Every 5 minutes**: Check for new trading signals
- **Instant notifications**: Send alerts for any buy/sell signals found
- **Real-time monitoring**: Continuous market surveillance

### After Market Hours
- **4:00 PM**: Complete daily analysis with backtesting
- **6:00 PM**: Send portfolio performance summary
- **Every hour**: System health checks

### Weekly Maintenance
- **Sunday 2:00 AM**: Retrain ML models with latest data
- **Automatic updates**: Keep predictions current and accurate

## 📱 What You'll Receive Automatically

### 🎯 Trading Signals (Real-time)
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

### 📊 Daily Portfolio Summary (6:00 PM)
```
📈 PORTFOLIO SUMMARY

💰 Total P&L: 🟢 ₹15,250.75
📊 Win Rate: 72.5%
🔢 Total Trades: 28
📈 Sharpe Ratio: 1.85

📅 Generated: 15/10/2024 18:00
```

### 🚨 System Alerts
- **Startup/Shutdown notifications**
- **Health check warnings**
- **Model retraining updates**
- **Error alerts with details**

## ⚙️ Smart Features

### 🎯 Intelligent Filtering
- **Confidence-based routing**: High-confidence signals → WhatsApp, All signals → Telegram
- **Stock filtering**: Choose specific stocks or monitor all
- **Signal type filtering**: BUY only, SELL only, or both

### 🌙 Quiet Hours
- **Default**: No notifications 10:00 PM - 8:00 AM
- **Customizable**: Set your preferred quiet hours
- **Smart queuing**: Messages queued during quiet hours are sent when they end

### 🔄 Reliability Features
- **Automatic retries**: 3 attempts with exponential backoff
- **Fallback delivery**: WhatsApp ↔ Telegram if one fails
- **Health monitoring**: Continuous system status checks
- **Graceful recovery**: Automatic restart after errors

## 🔧 Configuration

### Environment Variables (.env file)
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# WhatsApp
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_ID=your_phone_number_id_here
WHATSAPP_RECIPIENT=+1234567890
```

### Notification Preferences (config.json)
```json
{
  "notifications": {
    "preferences": {
      "signal_types": ["BUY", "SELL"],
      "min_confidence": 0.7,
      "stocks": ["ALL"],
      "quiet_hours": {
        "enabled": true,
        "start": "22:00",
        "end": "08:00"
      }
    }
  }
}
```

## 📊 Monitoring & Control

### Check System Status
```bash
# View live logs
tail -f trading_scheduler.log

# Test notifications
python main.py test-notifications

# Check configuration
python validate_notifications.py
```

### Control the System
```bash
# Stop the system
Ctrl+C (in the terminal where it's running)

# Restart the system
# Stop first, then run the startup script again

# Check service status (Linux)
sudo systemctl status trading-system
```

## 🛠️ Troubleshooting

### Common Issues

**1. No notifications received:**
- Check if system is running: Look for "Market monitoring..." in logs
- Verify credentials: Run `python validate_notifications.py`
- Check quiet hours: Notifications may be paused

**2. System stops unexpectedly:**
- Check logs: `trading_scheduler.log` and `trading_system.log`
- Verify internet connection
- Check API rate limits

**3. Missing signals:**
- Confirm market hours: System only monitors 9:15 AM - 3:30 PM IST
- Check confidence threshold: Low-confidence signals may be filtered
- Verify stock list: Ensure desired stocks are in configuration

### Log Files
- `trading_scheduler.log` - Automated system logs
- `trading_system.log` - Trading analysis logs
- `trading_service.log` - Background service logs (if using service)

## 🔒 Security & Best Practices

### Credential Security
- ✅ Store credentials in `.env` file (never commit to git)
- ✅ Use environment variables for production
- ✅ Regularly rotate API tokens
- ✅ Monitor notification logs for suspicious activity

### System Security
- ✅ Run with minimal required permissions
- ✅ Keep dependencies updated
- ✅ Monitor system resources
- ✅ Regular backups of configuration and logs

## 🎉 Success Indicators

Your automated system is working correctly when you see:

- ✅ **Startup notification** received when system starts
- ✅ **Regular health checks** in logs (every hour)
- ✅ **Market monitoring** messages during trading hours
- ✅ **Signal notifications** when opportunities arise
- ✅ **Daily summaries** received at 6:00 PM
- ✅ **No error alerts** or system warnings

## 📞 Support

If you need help:

1. **Check logs** for error messages
2. **Run validation**: `python validate_notifications.py`
3. **Test components**: `python main.py test-notifications`
4. **Review configuration** in `config.json` and `.env`
5. **Restart system** if needed

## 🎯 Next Level Features

Consider adding:
- **Multiple notification channels** (Discord, Slack, Email)
- **Custom alert conditions** (price targets, volume spikes)
- **Portfolio management** (position sizing, risk management)
- **Advanced analytics** (performance tracking, optimization)

---

## 🚀 You're All Set!

Your trading system is now **fully automated** and will:
- **Never miss a signal** during market hours
- **Keep you informed** with instant notifications
- **Continuously improve** with weekly model updates
- **Monitor itself** and alert you to any issues

**Just start the system once, and it handles everything else automatically!** 📱🤖📈