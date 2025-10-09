# 🖥️ Trading Frontend Guide

## Overview

The trading frontend is a modern Next.js application that provides a comprehensive web interface for the AI-powered trading system. It features real-time charts, live data updates, PWA capabilities, and a responsive design.

## 🌟 Features

### 📊 **Interactive Charts**
- **TradingView-style Charts**: Professional trading charts with technical indicators
- **Real-time Updates**: Live price data via WebSocket connections
- **Multiple Timeframes**: 1m, 5m, 15m, 1h, 4h, 1d chart intervals
- **Technical Indicators**: RSI, SMA, EMA, MACD, Bollinger Bands
- **Drawing Tools**: Trend lines, support/resistance levels, annotations

### 📱 **Progressive Web App (PWA)**
- **Installable**: Add to home screen on mobile/desktop
- **Offline Support**: Basic functionality works without internet
- **Push Notifications**: Receive trading alerts directly in browser
- **Background Sync**: Updates when connection is restored

### 🎨 **Modern UI/UX**
- **Dark/Light Themes**: Toggle between themes
- **Responsive Design**: Works on all screen sizes
- **Tailwind CSS**: Modern, utility-first styling
- **Framer Motion**: Smooth animations and transitions
- **Radix UI**: Accessible, unstyled components

### 📡 **Real-time Features**
- **Live Price Updates**: WebSocket connection for real-time data
- **Signal Notifications**: Instant alerts for buy/sell signals
- **Portfolio Tracking**: Real-time P&L and performance metrics
- **Market Status**: Live market hours and status indicators

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
cd trading-frontend
npm install
```

### 2. **Environment Setup**
```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local with your settings
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_WS_URL=ws://localhost:3001
```

### 3. **Start Development Server**
```bash
# Start backend API first
cd api
npm install
npm start

# Start frontend (in another terminal)
cd ..
npm run dev
```

### 4. **Build for Production**
```bash
npm run build
npm start
```

## 📁 Frontend Structure

```
trading-frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   ├── dashboard/          # Dashboard pages
│   │   ├── live-charts/        # Live charts page
│   │   └── settings/           # Settings page
│   │
│   ├── components/             # React Components
│   │   ├── charts/             # Chart components
│   │   │   ├── LiveChartsTerminal.tsx
│   │   │   ├── TradingChart.tsx
│   │   │   └── ChartControls.tsx
│   │   ├── ui/                 # UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── PWAInstall.tsx
│   │   │   └── NotificationCenter.tsx
│   │   └── layout/             # Layout components
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   │
│   ├── hooks/                  # Custom React Hooks
│   │   ├── useApiIntegration.ts
│   │   ├── useWebSocket.ts
│   │   └── useNotifications.ts
│   │
│   ├── services/               # API Services
│   │   ├── api.ts              # API client
│   │   ├── websocket.ts        # WebSocket service
│   │   └── notifications.ts    # Notification service
│   │
│   ├── stores/                 # State Management
│   │   ├── useStore.ts         # Main store
│   │   ├── chartStore.ts       # Chart state
│   │   └── settingsStore.ts    # Settings state
│   │
│   ├── types/                  # TypeScript Types
│   │   ├── api.ts              # API types
│   │   ├── chart.ts            # Chart types
│   │   └── trading.ts          # Trading types
│   │
│   └── utils/                  # Utility Functions
│       ├── formatters.ts       # Data formatters
│       ├── calculations.ts     # Trading calculations
│       └── constants.ts        # App constants
│
├── api/                        # Backend API Server
│   ├── server.js               # Express server
│   ├── package.json            # API dependencies
│   └── routes/                 # API routes
│
├── public/                     # Static Assets
│   ├── icons/                  # App icons
│   ├── manifest.json           # PWA manifest
│   └── sw.js                   # Service worker
│
├── package.json                # Dependencies
├── next.config.ts              # Next.js config
├── tailwind.config.js          # Tailwind config
└── tsconfig.json               # TypeScript config
```

## 🔧 Configuration

### **Environment Variables**
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_WS_URL=ws://localhost:3001
NEXT_PUBLIC_APP_NAME=Trading System
NEXT_PUBLIC_ENABLE_PWA=true
```

### **API Configuration**
```javascript
// api/server.js
const config = {
  port: 3001,
  cors: {
    origin: ['http://localhost:3000'],
    credentials: true
  },
  websocket: {
    enabled: true,
    updateInterval: 1000
  }
}
```

## 📊 Chart Features

### **Supported Chart Types**
- **Candlestick Charts**: OHLC data visualization
- **Line Charts**: Simple price movements
- **Area Charts**: Filled price areas
- **Volume Charts**: Trading volume bars

### **Technical Indicators**
- **Moving Averages**: SMA, EMA (customizable periods)
- **Oscillators**: RSI, MACD, Stochastic
- **Bands**: Bollinger Bands, Keltner Channels
- **Volume**: Volume Profile, OBV

### **Drawing Tools**
- **Trend Lines**: Draw support/resistance lines
- **Horizontal Lines**: Mark key price levels
- **Rectangles**: Highlight price ranges
- **Text Annotations**: Add custom notes

## 📱 PWA Features

### **Installation**
- **Desktop**: Chrome/Edge will show install prompt
- **Mobile**: "Add to Home Screen" option in browser menu
- **Automatic**: PWAInstall component shows install button

### **Offline Capabilities**
- **Chart Data**: Last loaded data available offline
- **Settings**: User preferences cached locally
- **Basic Navigation**: Core app functionality works offline

### **Push Notifications**
- **Trading Signals**: Receive buy/sell alerts
- **Price Alerts**: Custom price level notifications
- **System Updates**: Important system messages

## 🎨 Theming

### **Theme Toggle**
```typescript
// Using next-themes
import { useTheme } from 'next-themes'

const { theme, setTheme } = useTheme()
setTheme(theme === 'dark' ? 'light' : 'dark')
```

### **Custom Colors**
```css
/* globals.css */
:root {
  --primary: 222.2 84% 4.9%;
  --primary-foreground: 210 40% 98%;
  --success: 142.1 76.2% 36.3%;
  --destructive: 0 84.2% 60.2%;
}
```

## 🔌 API Integration

### **REST API Endpoints**
```typescript
// Available endpoints
GET /api/stocks          # Get stock list
GET /api/signals         # Get trading signals
GET /api/portfolio       # Get portfolio data
POST /api/settings       # Update settings
```

### **WebSocket Events**
```typescript
// WebSocket message types
'price_update'           # Real-time price data
'signal_generated'       # New trading signal
'portfolio_update'       # Portfolio changes
'system_status'          # System health
```

## 🧪 Testing

### **Run Tests**
```bash
npm run test
npm run test:watch
npm run test:coverage
```

### **E2E Testing**
```bash
npm run test:e2e
```

## 🚀 Deployment

### **Vercel (Recommended)**
```bash
npm install -g vercel
vercel
```

### **Docker**
```bash
docker build -t trading-frontend .
docker run -p 3000:3000 trading-frontend
```

### **Static Export**
```bash
npm run build
npm run export
```

## 🔧 Development

### **Code Style**
- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting
- **TypeScript**: Type safety
- **Husky**: Git hooks for quality checks

### **Performance**
- **Next.js Optimization**: Automatic code splitting
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: `npm run analyze`
- **Lighthouse**: Performance monitoring

## 📞 Troubleshooting

### **Common Issues**

**1. WebSocket Connection Failed**
```bash
# Check if API server is running
cd api && npm start

# Verify WebSocket URL in .env.local
NEXT_PUBLIC_WS_URL=ws://localhost:3001
```

**2. Charts Not Loading**
```bash
# Clear browser cache
# Check console for errors
# Verify API endpoints are accessible
```

**3. PWA Not Installing**
```bash
# Ensure HTTPS in production
# Check manifest.json is accessible
# Verify service worker registration
```

### **Debug Mode**
```bash
# Enable debug logging
NEXT_PUBLIC_DEBUG=true npm run dev
```

## 🎯 Future Enhancements

- **Mobile App**: React Native version
- **Advanced Charts**: More technical indicators
- **Social Features**: Share signals and strategies
- **Backtesting UI**: Visual strategy testing
- **Multi-language**: Internationalization support

---

The frontend provides a professional, modern interface for your AI-powered trading system with real-time capabilities and PWA features! 🚀📊