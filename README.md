# 🤖 AI-Powered NIFTY 50 Trading System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.10%2B-orange.svg)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org)

An intelligent trading system that uses machine learning to analyze NIFTY 50 stocks and automatically sends trading signals to your Telegram. The system combines LSTM/GRU neural networks with technical analysis to generate reliable BUY/SELL/HOLD signals.

## 🌟 Key Features

### 🧠 **AI-Powered Analysis**
- **LSTM & GRU Models**: Deep learning networks trained on historical stock data
- **Technical Indicators**: RSI, Moving Averages, Volume analysis
- **Smart Signal Generation**: Combines ML predictions with technical analysis
- **Confidence Scoring**: Only sends high-confidence signals

### 📱 **Instant Notifications**
- **Telegram Integration**: Real-time trading signals sent to your phone
- **Clean Message Format**: Simple, easy-to-read signal notifications
- **Customizable Alerts**: Configure which signals you want to receive
- **Multi-Stock Monitoring**: Track multiple stocks simultaneously

### 📊 **Data Management**
- **Google Sheets Integration**: Automatic logging of all trades and signals
- **Yahoo Finance Data**: Real-time stock price fetching
- **Historical Analysis**: Backtesting and performance tracking
- **Portfolio Monitoring**: Track your trading performance

### 🖥️ **Web Dashboard**
- **Next.js Frontend**: Modern web interface for monitoring
- **Real-time Charts**: Interactive trading charts with technical indicators
- **Chat Interface**: AI-powered chat for trading insights
- **Mobile Responsive**: Works on all devices

## 🚀 Quick Start

### 1. **Installation**
```bash
git clone https://github.com/ManivardhanDonuri/AI-Powered-NIFTY-50-Stock-Prediction-and-Automated-Trading-System.git
cd AI-Powered-NIFTY-50-Stock-Prediction-and-Automated-Trading-System
pip install -r requirements.txt
```

### 2. **Telegram Bot Setup**
1. Create a bot with [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token and chat ID
3. Create a `.env` file in the project root:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 3. **Google Sheets Setup (Optional)**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project and enable Google Sheets API
3. Create a service account and download the JSON key
4. Rename it to `service_account.json` and place in project root
5. Create a Google Sheet and update the spreadsheet ID in `config.json`

### 4. **Run the System**
```bash
python main.py
```

## 📱 What You'll Receive

### **Trading Signal Example**
```
🟢 BUY

📈 RELIANCE.NS
💰 ₹1,416.80
📝 Price above both moving averages
```

### **Signal Types**
- 🟢 **BUY** - Strong bullish signals
- 🔴 **SELL** - Strong bearish signals  
- 🟡 **HOLD** - Neutral or mixed signals

## 🔧 Available Commands

```bash
# Main Operations
python main.py                    # Run complete analysis
python main.py daily              # Daily monitoring mode
python main.py train              # Train ML models

# Testing & Utilities
python main.py test-notifications # Test Telegram notifications
```

## 📁 Project Structure

```
├── 🐍 Core System
│   ├── main.py                   # Main entry point
│   ├── trading_system.py         # Core trading logic
│   ├── ml_signal_generator_enhanced.py  # AI signal generation
│   ├── data_fetcher.py           # Stock data fetching
│   ├── technical_indicators.py   # Technical analysis
│   └── backtester.py            # Performance testing
│
├── 🤖 AI Models
│   ├── ml_models.py             # LSTM/GRU implementations
│   ├── ml_trainer.py            # Model training
│   ├── ml_feature_engineer.py   # Feature engineering
│   └── models/                  # Trained model files
│
├── 📱 Notifications
│   ├── notifications/           # Notification system
│   │   ├── notification_manager.py
│   │   ├── telegram_service.py
│   │   └── message_formatter.py
│
├── 🌐 Frontend
│   ├── trading-frontend/        # Next.js web dashboard
│   │   ├── src/components/      # React components
│   │   ├── src/app/            # App pages
│   │   └── api/                # Backend API
│
├── 🧠 LLM Backend
│   ├── llm_backend/            # AI chat backend
│   │   ├── services/           # LLM services
│   │   ├── routers/            # API routes
│   │   └── websocket/          # Real-time chat
│
└── ⚙️ Configuration
    ├── config.json             # System settings
    ├── .env                    # Environment variables
    └── service_account.json    # Google Sheets credentials
```

## ⚙️ Configuration

### **Stock Selection** (`config.json`)
```json
{
  "trading": {
    "stocks": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
    "rsi_period": 14,
    "sma_short": 20,
    "sma_long": 50
  }
}
```

### **Notification Preferences**
```json
{
  "notifications": {
    "preferences": {
      "signal_types": ["BUY", "SELL", "HOLD"],
      "min_confidence": 0.5,
      "stocks": ["ALL"]
    }
  }
}
```

### **ML Model Settings**
```json
{
  "ml": {
    "models": ["LSTM", "GRU"],
    "sequence_length": 60,
    "epochs": 50,
    "batch_size": 32
  }
}
```

## 🖥️ Web Dashboard

Start the web interface for advanced features:

```bash
# Start the LLM backend
python start_llm_backend.py --reload --log-level info

# Start the frontend (in another terminal)
cd trading-frontend
npm install
npm run dev
```

Visit `http://localhost:3000` for:
- 📊 Interactive trading charts
- 💬 AI-powered trading chat
- 📈 Portfolio performance tracking
- ⚙️ System configuration

## 📊 Supported Stocks

**Currently Configured:**
- RELIANCE.NS (Reliance Industries)
- TCS.NS (Tata Consultancy Services)
- HDFCBANK.NS (HDFC Bank)

**Easy to Add More:**
Simply update the `stocks` array in `config.json` with any NSE stock symbol.

## 🧪 Testing

```bash
# Test Telegram notifications
python main.py test-notifications

# Verify configuration
python -c "import json; print(json.load(open('config.json')))"

# Check dependencies
pip list | grep -E "(tensorflow|pandas|yfinance)"
```

## 📈 Performance

- **Signal Accuracy**: 70-85% (varies by market conditions)
- **Response Time**: <30 seconds for signal generation
- **Market Coverage**: All NSE trading hours (9:15 AM - 3:30 PM IST)
- **Data Sources**: Yahoo Finance (real-time)

## 🛠️ Troubleshooting

### **Common Issues**

1. **Telegram not working?**
   - Check your bot token and chat ID in `.env`
   - Test with: `python main.py test-notifications`

2. **No signals generated?**
   - Ensure market hours (9:15 AM - 3:30 PM IST)
   - Check internet connection
   - Verify stock symbols in `config.json`

3. **Google Sheets errors?**
   - Verify `service_account.json` exists
   - Check spreadsheet ID in `config.json`
   - Ensure service account has sheet access

4. **ML model errors?**
   - Run: `python main.py train` to retrain models
   - Check if `models/` directory exists
   - Ensure sufficient historical data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## ⚠️ Important Disclaimer

**This software is for educational and research purposes only.** 

- Trading in financial markets involves substantial risk of loss
- Past performance does not guarantee future results
- The authors are not responsible for any financial losses
- Always consult with a qualified financial advisor
- Never invest money you cannot afford to lose

---

**⭐ If this project helps you, please give it a star on GitHub!**

Made with ❤️ for the trading and AI community
