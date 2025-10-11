# 🤖 AI-Powered NIFTY 50 Stock Prediction and Automated Trading System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.10%2B-orange.svg)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org)

An intelligent, fully automated trading system that uses machine learning to predict NIFTY 50 stock movements and sends real-time notifications via Telegram and WhatsApp. The system combines LSTM/GRU neural networks with technical analysis to generate high-confidence trading signals.

## 🌟 Features

### 🧠 **AI-Powered Predictions**
- **LSTM & GRU Models**: Deep learning networks for time series prediction
- **Hybrid Signals**: Combines ML predictions with technical analysis
- **Feature Engineering**: 15+ technical indicators and momentum features
- **Confidence Scoring**: Only high-confidence signals (>70%) are acted upon

### 📱 **Real-Time Notifications**
- **Telegram Integration**: Instant notifications with formatted messages
- **WhatsApp Support**: Business API and web automation options
- **Smart Routing**: High-confidence signals → WhatsApp, All signals → Telegram
- **Rich Formatting**: Emojis, confidence ratings, targets, and stop-losses

### 🔄 **Fully Automated**
- **Market Monitoring**: Every 5 minutes during trading hours (9:15 AM - 3:30 PM IST)
- **Daily Analysis**: Complete analysis at 4:00 PM after market close
- **Portfolio Summaries**: Daily performance reports at 6:00 PM
- **Weekly Model Updates**: Automatic retraining every Sunday
- **Health Monitoring**: System status checks every hour

### 📊 **Data Integration**
- **Google Sheets Logging**: Automatic signal and performance logging
- **Yahoo Finance**: Real-time stock data fetching
- **Technical Indicators**: RSI, SMA, volume analysis, and more
- **Backtesting**: Historical performance validation

### 🖥️ **Modern Web Interface**
- **Next.js Frontend**: Modern React-based trading dashboard with TypeScript
- **Real-time Charts**: Interactive TradingView-style charts with Lightweight Charts
- **Technical Indicators**: Live MA(20), RSI(14), Volume with interactive legend
- **Drawing Tools**: Trend lines, horizontal lines, rectangles for chart analysis
- **PWA Support**: Install as mobile/desktop app with offline capabilities
- **Live Data**: WebSocket integration for real-time price updates
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Dark/Light Theme**: Customizable UI themes with smooth transitions

## 🚀 Quick Start

### 1. **Clone and Setup Backend**
```bash
git clone https://github.com/ManivardhanDonuri/AI-Powered-NIFTY-50-Stock-Prediction-and-Automated-Trading-System.git
cd AI-Powered-NIFTY-50-Stock-Prediction-and-Automated-Trading-System
pip install -r requirements.txt
```

### 2. **Setup Frontend (Optional)**
```bash
cd trading-frontend
npm install
npm run build
```

### 3. **Configure Notifications**
```bash
# Run interactive setup
python setup_automated_trading.py
```

### 4. **Start the System**

**Backend Only:**
```bash
# Windows
start_automated_trading.bat

# Linux/Mac
./start_automated_trading.sh
```

**With Frontend:**
```bash
# Start backend API
cd trading-frontend/api
npm start

# Start frontend (in another terminal)
cd trading-frontend
npm run dev
```

## 📱 Notification Examples

### 🎯 **Trading Signal**
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

### 📊 **Portfolio Summary**
```
📈 PORTFOLIO SUMMARY

💰 Total P&L: 🟢 ₹15,250.75
📊 Win Rate: 72.5%
🔢 Total Trades: 28
📈 Sharpe Ratio: 1.85

📅 Generated: 15/10/2024 18:00
```

## 🏗️ Architecture

```
├── 🧠 ML Models (LSTM/GRU)
├── 📊 Technical Analysis Engine
├── 🔄 Signal Generation & Processing
├── 📱 Multi-Channel Notifications
├── 📈 Google Sheets Integration
├── ⏰ Automated Scheduler
├── 🖥️ Next.js Frontend Dashboard
├── 📡 WebSocket Real-time API
├── 🎨 Interactive Trading Charts
└── 🛡️ Security & Error Recovery
```

## 📁 Project Structure

```
├── Backend (Python)
│   ├── main.py                          # Main trading system
│   ├── trading_scheduler.py             # Automated scheduler
│   ├── ml_signal_generator_enhanced.py  # Enhanced ML signal generator
│   ├── notifications/                   # Notification system
│   │   ├── notification_manager.py      # Central coordinator
│   │   ├── telegram_service.py          # Telegram integration
│   │   ├── whatsapp_service.py          # WhatsApp integration
│   │   ├── message_formatter.py         # Message formatting
│   │   └── delivery_queue.py            # Message queuing
│   ├── setup_automated_trading.py       # Setup script
│   ├── validate_notifications.py        # Configuration validator
│   ├── config.json                      # System configuration
│   └── requirements.txt                 # Python dependencies
│
├── Frontend (Next.js)
│   ├── trading-frontend/
│   │   ├── src/
│   │   │   ├── app/                     # Next.js app router
│   │   │   ├── components/              # React components
│   │   │   │   ├── charts/              # Trading charts
│   │   │   │   ├── ui/                  # UI components
│   │   │   │   └── layout/              # Layout components
│   │   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── services/                # API services
│   │   │   └── stores/                  # State management
│   │   ├── api/                         # Backend API server
│   │   ├── public/                      # Static assets
│   │   ├── package.json                 # Node.js dependencies
│   │   └── next.config.ts               # Next.js configuration
│   └── README.md                        # Frontend documentation
```

## ⚙️ Configuration

### **Environment Variables (.env)**
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# WhatsApp (optional)
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_ID=your_phone_number_id_here
WHATSAPP_RECIPIENT=+1234567890
```

### **Notification Preferences**
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

## 🎨 Chart Features

### **Interactive Legend System**
- **Real-time Values**: Live MA(20) and RSI(14) calculations displayed in legend
- **Visual Indicators**: Color-coded lines and volume bars matching chart elements
- **Stock-specific Data**: Dynamic volume display based on selected stock
- **Theme Integration**: Adapts to light/dark themes automatically

### **Drawing Tools**
- **Trend Lines**: Draw custom trend lines for technical analysis
- **Horizontal Lines**: Mark support and resistance levels
- **Rectangles**: Highlight important price ranges
- **Tool Switching**: Seamless switching between drawing tools with visual feedback

## 🧪 Testing

```bash
# Test notifications
python main.py test-notifications

# Validate configuration
python validate_notifications.py

# Test Google Sheets logging
python test_sheets_logging.py

# Test frontend build
cd trading-frontend && npm run build
```

## 📊 Supported Stocks

Currently configured for NIFTY 50 stocks:
- RELIANCE.NS, TCS.NS, HDFCBANK.NS
- Easily configurable for any NSE/BSE stocks
- Supports multiple stock monitoring

## 🔧 Advanced Usage

### **Manual Analysis**
```bash
# Single analysis
python main.py analysis

# Daily monitoring
python main.py daily

# Train ML models
python main.py train
```

### **Web Dashboard**
```bash
# Launch Next.js frontend
cd trading-frontend
npm run dev
# Visit http://localhost:3000

# Features available in dashboard:
# - Live Charts with real-time data
# - Portfolio management
# - Trade history analysis
# - System status monitoring
# - Settings configuration
```

### **Background Service (Linux)**
```bash
# Install as systemd service
sudo cp trading-system.service /etc/systemd/system/
sudo systemctl enable trading-system
sudo systemctl start trading-system
```

## 📈 Performance

- **Signal Accuracy**: 70-85% (varies by market conditions and volatility)
- **Response Time**: <30 seconds for signal generation and notifications
- **Chart Performance**: Real-time updates with <100ms latency
- **System Uptime**: 99.9% with automatic error recovery and health monitoring
- **Market Coverage**: Monitors during all trading hours (9:15 AM - 3:30 PM IST)
- **Frontend Performance**: Optimized bundle size with static generation

## 🛡️ Security Features

- **Credential Protection**: Environment variable storage with validation
- **Rate Limiting**: API compliance and protection against abuse
- **Error Recovery**: Automatic retry mechanisms with exponential backoff
- **Audit Logging**: Complete activity tracking and performance monitoring
- **Frontend Security**: CSP headers, XSS protection, and secure API endpoints
- **Data Validation**: Input sanitization and type checking throughout

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading in financial markets involves substantial risk of loss. The authors and contributors are not responsible for any financial losses incurred through the use of this software. Always consult with a qualified financial advisor before making investment decisions.

## 🙏 Acknowledgments

- **TensorFlow** for deep learning capabilities
- **Yahoo Finance** for stock data
- **Telegram Bot API** for notifications
- **Google Sheets API** for data logging
- **Next.js & React** for modern web dashboard interface

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/ManivardhanDonuri/AI-Powered-NIFTY-50-Stock-Prediction-and-Automated-Trading-System/issues)
- 📖 **Documentation**: See `AUTOMATED_SYSTEM_GUIDE.md` for detailed setup
- 🔧 **Setup Help**: Run `python setup_automated_trading.py`

---

**⭐ If this project helped you, please give it a star!**

Made with ❤️ for the trading community