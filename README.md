# 🤖 AI Trading System for NIFTY 50

A simple AI-powered trading system that analyzes NIFTY 50 stocks and sends trading signals to your Telegram.

## What it does

- 📊 Analyzes stock prices using AI (LSTM/GRU models)
- 📱 Sends BUY/SELL/HOLD signals to Telegram
- 📈 Logs trades to Google Sheets
- 🔄 Runs automatically

## Quick Setup

### 1. Install
```bash
git clone <your-repo-url>
cd trading-system
pip install -r requirements.txt
```

### 2. Configure
Create a `.env` file:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 3. Setup Google Sheets (Optional)
- Create a Google Cloud project
- Enable Google Sheets API
- Download `service_account.json`
- Update `config.json` with your spreadsheet ID

### 4. Run
```bash
python main.py
```

## What you'll get

### Telegram Messages
```
🟢 BUY

📈 RELIANCE.NS
💰 ₹1,416.80
📝 Price above moving averages
```

### Commands
```bash
python main.py                    # Run analysis
python main.py test-notifications # Test Telegram
python main.py train              # Train AI models
python main.py daily              # Daily monitoring
```

## Files you need to know

- `main.py` - Main program
- `config.json` - Settings
- `.env` - Your bot tokens
- `service_account.json` - Google Sheets access

## Configuration

Edit `config.json` to change:
- Which stocks to monitor
- Notification preferences
- AI model settings

## Requirements

- Python 3.8+
- Telegram bot token
- Internet connection

## Supported Stocks

Currently monitors:
- RELIANCE.NS
- TCS.NS  
- HDFCBANK.NS

Add more stocks in `config.json`.

## Disclaimer

⚠️ **This is for educational purposes only. Trading involves risk. Don't invest money you can't afford to lose.**

## Need Help?

1. Check your `.env` file has correct tokens
2. Make sure `config.json` is properly formatted
3. Test notifications with `python main.py test-notifications`

---

Made with ❤️ for learning AI and trading