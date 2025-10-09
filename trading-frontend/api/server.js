const express = require('express');
const cors = require('cors');
const http = require('http');
const socketIo = require('socket.io');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const axios = require('axios');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Store for active Python processes
let tradingProcess = null;
let trainingProcess = null;

// Yahoo Finance API integration
const yahooFinance = require('yahoo-finance2').default;

// Cache for stock data to avoid excessive API calls
const stockDataCache = new Map();
const CACHE_DURATION = 30000; // 30 seconds

// Helper function to fetch real-time stock data from Yahoo Finance
async function fetchStockData(symbol) {
  try {
    // Check cache first
    const cached = stockDataCache.get(symbol);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.data;
    }

    console.log(`Fetching real-time data for ${symbol} from Yahoo Finance...`);
    
    // Fetch current quote
    const quote = await yahooFinance.quote(symbol);
    
    if (!quote) {
      throw new Error(`No data found for symbol ${symbol}`);
    }

    const stockData = {
      symbol: symbol,
      currentPrice: quote.regularMarketPrice || quote.price || 0,
      price: quote.regularMarketPrice || quote.price || 0,
      change: quote.regularMarketChange || 0,
      changePercent: quote.regularMarketChangePercent || 0,
      high: quote.regularMarketDayHigh || quote.dayHigh || 0,
      low: quote.regularMarketDayLow || quote.dayLow || 0,
      volume: formatVolume(quote.regularMarketVolume || quote.volume || 0),
      previousClose: quote.regularMarketPreviousClose || quote.previousClose || 0,
      marketCap: quote.marketCap || 0,
      timestamp: new Date().toISOString()
    };

    // Cache the data
    stockDataCache.set(symbol, {
      data: stockData,
      timestamp: Date.now()
    });

    return stockData;
  } catch (error) {
    console.error(`Error fetching data for ${symbol}:`, error.message);
    
    // Return fallback mock data if Yahoo Finance fails
    return getFallbackData(symbol);
  }
}

// Helper function to format volume numbers
function formatVolume(volume) {
  if (volume >= 1000000) {
    return (volume / 1000000).toFixed(1) + 'M';
  } else if (volume >= 1000) {
    return (volume / 1000).toFixed(1) + 'K';
  }
  return volume.toString();
}

// Fallback mock data when Yahoo Finance is unavailable
function getFallbackData(symbol) {
  const mockData = {
    'RELIANCE.NS': {
      symbol: 'RELIANCE.NS',
      currentPrice: 2847.50,
      price: 2847.50,
      change: 12.75,
      changePercent: 0.45,
      high: 2865.20,
      low: 2832.10,
      volume: '2.1M',
      previousClose: 2834.75,
      marketCap: 19250000000000,
      timestamp: new Date().toISOString()
    },
    'TCS.NS': {
      symbol: 'TCS.NS',
      currentPrice: 4125.80,
      price: 4125.80,
      change: -4.95,
      changePercent: -0.12,
      high: 4142.30,
      low: 4118.45,
      volume: '1.8M',
      previousClose: 4130.75,
      marketCap: 15100000000000,
      timestamp: new Date().toISOString()
    },
    'HDFCBANK.NS': {
      symbol: 'HDFCBANK.NS',
      currentPrice: 1678.25,
      price: 1678.25,
      change: 8.40,
      changePercent: 0.50,
      high: 1685.90,
      low: 1665.75,
      volume: '3.2M',
      previousClose: 1669.85,
      marketCap: 12800000000000,
      timestamp: new Date().toISOString()
    }
  };

  return mockData[symbol] || {
    symbol: symbol,
    currentPrice: 1000 + Math.random() * 1000,
    price: 1000 + Math.random() * 1000,
    change: (Math.random() - 0.5) * 50,
    changePercent: (Math.random() - 0.5) * 5,
    high: 1050 + Math.random() * 1000,
    low: 950 + Math.random() * 1000,
    volume: formatVolume(Math.random() * 5000000),
    previousClose: 1000 + Math.random() * 1000,
    marketCap: Math.random() * 10000000000000,
    timestamp: new Date().toISOString()
  };
}

// Helper function to fetch historical data
async function fetchHistoricalData(symbol, timeframe = '1d') {
  try {
    console.log(`Fetching historical data for ${symbol} with timeframe ${timeframe}...`);
    
    // Map timeframe to Yahoo Finance periods
    const periodMap = {
      '1d': '1d',
      '3d': '5d',
      '1m': '1mo',
      '1y': '1y',
      '5y': '5y'
    };
    
    const period = periodMap[timeframe] || '1mo';
    
    const result = await yahooFinance.historical(symbol, {
      period1: getStartDate(period),
      period2: new Date(),
      interval: getInterval(timeframe)
    });

    return result.map(item => ({
      time: item.date.toISOString().split('T')[0],
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
      volume: item.volume
    }));
  } catch (error) {
    console.error(`Error fetching historical data for ${symbol}:`, error.message);
    return generateMockHistoricalData(symbol, timeframe);
  }
}

// Helper functions for date calculations
function getStartDate(period) {
  const now = new Date();
  switch (period) {
    case '1d': return new Date(now.getTime() - 24 * 60 * 60 * 1000);
    case '5d': return new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000);
    case '1mo': return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    case '1y': return new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
    case '5y': return new Date(now.getTime() - 5 * 365 * 24 * 60 * 60 * 1000);
    default: return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  }
}

function getInterval(timeframe) {
  switch (timeframe) {
    case '1d': return '5m';
    case '3d': return '15m';
    case '1m': return '1d';
    case '1y': return '1d';
    case '5y': return '1wk';
    default: return '1d';
  }
}

// Generate mock historical data as fallback
function generateMockHistoricalData(symbol, timeframe) {
  const data = [];
  const days = timeframe === '1d' ? 1 : timeframe === '3d' ? 3 : timeframe === '1m' ? 30 : timeframe === '1y' ? 365 : 1825;
  const basePrice = symbol.includes('RELIANCE') ? 2800 : symbol.includes('TCS') ? 4100 : 1650;
  
  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    
    const open = basePrice + (Math.random() - 0.5) * 100;
    const close = open + (Math.random() - 0.5) * 50;
    const high = Math.max(open, close) + Math.random() * 20;
    const low = Math.min(open, close) - Math.random() * 20;
    
    data.push({
      time: date.toISOString().split('T')[0],
      open,
      high,
      low,
      close,
      volume: Math.floor(Math.random() * 5000000)
    });
  }
  
  return data;
}

// Routes

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    services: {
      trading: tradingProcess ? 'running' : 'stopped',
      training: trainingProcess ? 'running' : 'stopped'
    }
  });
});

// Get real-time stock data
app.get('/api/stocks/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    console.log(`API request for stock data: ${symbol}`);
    
    const stockData = await fetchStockData(symbol);
    res.json(stockData);
  } catch (error) {
    console.error('Error in /api/stocks/:symbol:', error);
    res.status(500).json({ 
      error: 'Failed to fetch stock data',
      message: error.message 
    });
  }
});

// Get historical stock data
app.get('/api/stocks/:symbol/historical', async (req, res) => {
  try {
    const { symbol } = req.params;
    const { timeframe = '1m' } = req.query;
    
    console.log(`API request for historical data: ${symbol}, timeframe: ${timeframe}`);
    
    const historicalData = await fetchHistoricalData(symbol, timeframe);
    res.json({
      symbol,
      timeframe,
      data: historicalData
    });
  } catch (error) {
    console.error('Error in /api/stocks/:symbol/historical:', error);
    res.status(500).json({ 
      error: 'Failed to fetch historical data',
      message: error.message 
    });
  }
});

// Get multiple stocks data
app.get('/api/stocks', async (req, res) => {
  try {
    const symbols = req.query.symbols ? req.query.symbols.split(',') : ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS'];
    
    console.log(`API request for multiple stocks: ${symbols.join(', ')}`);
    
    const stocksData = await Promise.all(
      symbols.map(async (symbol) => {
        try {
          return await fetchStockData(symbol.trim());
        } catch (error) {
          console.error(`Error fetching ${symbol}:`, error);
          return getFallbackData(symbol.trim());
        }
      })
    );
    
    res.json({ stocks: stocksData });
  } catch (error) {
    console.error('Error in /api/stocks:', error);
    res.status(500).json({ 
      error: 'Failed to fetch stocks data',
      message: error.message 
    });
  }
});

// Get trading signals
app.get('/api/signals', (req, res) => {
  const { symbol, limit = 10 } = req.query;
  
  // Mock signals data
  const signals = Array.from({ length: parseInt(limit) }, (_, i) => ({
    id: `signal_${Date.now()}_${i}`,
    symbol: symbol || 'NIFTY 50',
    type: Math.random() > 0.5 ? 'BUY' : 'SELL',
    price: 25000 + Math.random() * 100,
    confidence: 0.7 + Math.random() * 0.3,
    timestamp: new Date(Date.now() - i * 3600000).toISOString(),
    reasoning: 'RSI oversold + MA crossover'
  }));
  
  res.json({ signals });
});

// Start trading system with real-time data updates
app.post('/api/trading/start', (req, res) => {
  if (tradingProcess) {
    return res.status(400).json({ error: 'Trading system already running' });
  }
  
  try {
    tradingProcess = { 
      pid: Date.now(), 
      status: 'running',
      startTime: new Date().toISOString()
    };
    
    // Start real-time data updates for configured stocks
    const symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS'];
    
    const updateInterval = setInterval(async () => {
      if (!tradingProcess) {
        clearInterval(updateInterval);
        return;
      }
      
      try {
        // Fetch real-time data for all symbols
        for (const symbol of symbols) {
          const stockData = await fetchStockData(symbol);
          
          // Emit real-time price update
          io.emit('price_update', {
            symbol: symbol,
            currentPrice: stockData.currentPrice,
            price: stockData.price,
            change: stockData.change,
            changePercent: stockData.changePercent,
            high: stockData.high,
            low: stockData.low,
            volume: stockData.volume,
            timestamp: stockData.timestamp
          });
          
          // Emit to specific symbol rooms
          io.to(symbol).emit('symbol_update', stockData);
        }
        
        console.log(`Real-time data updated for ${symbols.length} symbols`);
      } catch (error) {
        console.error('Error in real-time data update:', error);
      }
    }, 5000); // Update every 5 seconds
    
    // Store interval reference for cleanup
    tradingProcess.updateInterval = updateInterval;
    
    res.json({ 
      message: 'Trading system started successfully with real-time data',
      pid: tradingProcess.pid,
      symbols: symbols,
      updateFrequency: '5 seconds'
    });
  } catch (error) {
    console.error('Error starting trading system:', error);
    res.status(500).json({ error: 'Failed to start trading system' });
  }
});

// Stop trading system
app.post('/api/trading/stop', (req, res) => {
  if (!tradingProcess) {
    return res.status(400).json({ error: 'Trading system not running' });
  }
  
  try {
    // Clear the update interval
    if (tradingProcess.updateInterval) {
      clearInterval(tradingProcess.updateInterval);
    }
    
    tradingProcess = null;
    
    // Notify all clients that the system stopped
    io.emit('system_status', {
      status: 'stopped',
      timestamp: new Date().toISOString()
    });
    
    res.json({ message: 'Trading system stopped successfully' });
  } catch (error) {
    console.error('Error stopping trading system:', error);
    res.status(500).json({ error: 'Failed to stop trading system' });
  }
});

// Train ML model
app.post('/api/models/train', (req, res) => {
  const { symbol, modelType, epochs, batchSize } = req.body;
  
  if (trainingProcess) {
    return res.status(400).json({ error: 'Training already in progress' });
  }
  
  try {
    // Mock training process
    trainingProcess = { 
      pid: Date.now(), 
      symbol, 
      modelType, 
      epochs: epochs || 50,
      currentEpoch: 0,
      status: 'training' 
    };
    
    // Simulate training progress
    const progressInterval = setInterval(() => {
      if (!trainingProcess) {
        clearInterval(progressInterval);
        return;
      }
      
      trainingProcess.currentEpoch++;
      const progress = (trainingProcess.currentEpoch / trainingProcess.epochs) * 100;
      
      io.emit('training_progress', {
        modelId: trainingProcess.pid,
        epoch: trainingProcess.currentEpoch,
        totalEpochs: trainingProcess.epochs,
        progress: Math.min(progress, 100),
        loss: 0.5 - (progress / 200), // Mock decreasing loss
        accuracy: 0.5 + (progress / 200) // Mock increasing accuracy
      });
      
      if (trainingProcess.currentEpoch >= trainingProcess.epochs) {
        io.emit('training_complete', {
          modelId: trainingProcess.pid,
          symbol: trainingProcess.symbol,
          modelType: trainingProcess.modelType,
          accuracy: 0.85,
          loss: 0.15
        });
        trainingProcess = null;
        clearInterval(progressInterval);
      }
    }, 1000);
    
    res.json({ 
      message: 'Model training started',
      modelId: trainingProcess.pid,
      estimatedTime: `${epochs || 50} seconds`
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to start model training' });
  }
});

// Get model performance
app.get('/api/models', (req, res) => {
  // Mock model data
  const models = [
    {
      id: 'lstm_nifty_v1',
      name: 'LSTM_NIFTY_v1',
      symbol: 'NIFTY 50',
      type: 'LSTM',
      accuracy: 0.847,
      precision: 0.823,
      recall: 0.891,
      f1Score: 0.856,
      trainedAt: '2024-01-15T10:30:00Z',
      status: 'active'
    },
    {
      id: 'gru_reliance_v2',
      name: 'GRU_RELIANCE_v2',
      symbol: 'RELIANCE',
      type: 'GRU',
      accuracy: 0.792,
      precision: 0.778,
      recall: 0.805,
      f1Score: 0.791,
      trainedAt: '2024-01-14T15:45:00Z',
      status: 'active'
    }
  ];
  
  res.json({ models });
});

// Configuration endpoints
app.get('/api/config', (req, res) => {
  // Mock configuration
  const config = {
    trading: {
      stocks: ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS'],
      rsiPeriod: 14,
      smaShort: 20,
      smaLong: 50
    },
    ml: {
      enabled: true,
      epochs: 50,
      batchSize: 32
    }
  };
  
  res.json(config);
});

app.post('/api/config', (req, res) => {
  // Mock configuration save
  console.log('Saving configuration:', req.body);
  res.json({ message: 'Configuration saved successfully' });
});

// Telegram notification endpoint
app.post('/api/telegram/test', (req, res) => {
  const { botToken, chatId } = req.body;
  
  // Mock Telegram test
  if (botToken && chatId) {
    setTimeout(() => {
      io.emit('telegram_test_result', { success: true });
    }, 1000);
    res.json({ message: 'Testing Telegram connection...' });
  } else {
    res.status(400).json({ error: 'Bot token and chat ID required' });
  }
});

// WebSocket connections
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  // Send initial connection confirmation
  socket.emit('connected', { 
    message: 'Connected to trading system',
    timestamp: new Date().toISOString()
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
  
  // Handle subscription to specific symbols
  socket.on('subscribe', (data) => {
    console.log('Client subscribed to:', data);
    socket.join(data.symbol);
  });
  
  socket.on('unsubscribe', (data) => {
    console.log('Client unsubscribed from:', data);
    socket.leave(data.symbol);
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
server.listen(PORT, () => {
  console.log(`Trading API Server running on port ${PORT}`);
  console.log(`WebSocket server ready for connections`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
  });
});

module.exports = app;