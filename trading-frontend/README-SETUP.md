# Trading Frontend Setup Guide

## Quick Start

### Windows
1. Run `start-dev.bat` - this will automatically install dependencies and start both servers
2. Wait for both servers to start
3. Open http://localhost:3000 in your browser
4. Navigate to "Live Charts" to see real-time Yahoo Finance data

### Manual Setup

#### 1. Start API Server
```bash
cd api
npm install
npm run dev
```
The API server will start on http://localhost:8000

#### 2. Start Frontend
```bash
# In a new terminal, from the trading-frontend root
npm install
npm run dev
```
The frontend will start on http://localhost:3000

## Features

### Real-Time Yahoo Finance Integration
- The live charts now fetch real data from Yahoo Finance API
- Stock selection dropdown updates the chart with actual stock data
- Supports RELIANCE.NS, TCS.NS, and HDFCBANK.NS
- Automatic fallback to mock data if Yahoo Finance is unavailable

### How Stock Selection Works
1. Select a stock from the dropdown in the Live Charts page
2. The chart automatically fetches historical data for that stock
3. Real-time price updates are simulated based on the actual stock data
4. All technical indicators (MA, RSI) are calculated from real data

### API Endpoints
- `GET /api/stocks/:symbol` - Get current stock price
- `GET /api/stocks/:symbol/historical?timeframe=1m` - Get historical data
- `POST /api/trading/start` - Start real-time data updates
- `POST /api/trading/stop` - Stop real-time data updates

### Troubleshooting

#### API Server Issues
- Make sure port 8000 is available
- Check if yahoo-finance2 package is installed correctly
- Look for error messages in the API server console

#### Frontend Issues
- Make sure port 3000 is available
- Check browser console for any errors
- Verify API server is running on localhost:8000

#### Yahoo Finance API Issues
- If Yahoo Finance is blocked or unavailable, the system will automatically use mock data
- You'll see a yellow indicator showing "Mock" instead of "Live"
- The chart will still work with realistic mock data

## Development Notes

### Adding New Stocks
To add new stocks, update the `availableStocks` array in:
`src/app/live-charts/page.tsx`

### Modifying Update Frequency
Real-time updates happen every 5 seconds. To change this, modify the interval in:
`api/server.js` (line with `setInterval(..., 5000)`)

### Chart Customization
Chart styling and indicators can be modified in:
`src/components/charts/LiveChartsTerminal.tsx`