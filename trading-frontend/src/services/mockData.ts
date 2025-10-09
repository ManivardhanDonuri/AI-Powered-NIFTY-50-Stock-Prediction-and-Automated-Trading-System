import { Stock, TradingSignal, CandlestickData, MLModel, TrainingProgress } from '@/types/trading';

// Mock stock data
export const MOCK_STOCKS: Stock[] = [
  { symbol: 'RELIANCE.NS', name: 'Reliance Industries Ltd', exchange: 'NSE', currentPrice: 2456.78, change: 45.67, changePercent: 1.89 },
  { symbol: 'TCS.NS', name: 'Tata Consultancy Services Ltd', exchange: 'NSE', currentPrice: 3234.56, change: -23.45, changePercent: -0.72 },
  { symbol: 'HDFCBANK.NS', name: 'HDFC Bank Ltd', exchange: 'NSE', currentPrice: 1678.90, change: 12.34, changePercent: 0.74 },
  { symbol: 'INFY.NS', name: 'Infosys Ltd', exchange: 'NSE', currentPrice: 1456.78, change: 34.56, changePercent: 2.43 },
  { symbol: 'HINDUNILVR.NS', name: 'Hindustan Unilever Ltd', exchange: 'NSE', currentPrice: 2789.12, change: -15.67, changePercent: -0.56 },
  { symbol: 'ICICIBANK.NS', name: 'ICICI Bank Ltd', exchange: 'NSE', currentPrice: 987.65, change: 8.90, changePercent: 0.91 },
  { symbol: 'KOTAKBANK.NS', name: 'Kotak Mahindra Bank Ltd', exchange: 'NSE', currentPrice: 1876.54, change: 23.45, changePercent: 1.27 },
  { symbol: 'BHARTIARTL.NS', name: 'Bharti Airtel Ltd', exchange: 'NSE', currentPrice: 876.54, change: -5.43, changePercent: -0.62 },
  { symbol: 'ITC.NS', name: 'ITC Ltd', exchange: 'NSE', currentPrice: 456.78, change: 2.34, changePercent: 0.51 },
  { symbol: 'SBIN.NS', name: 'State Bank of India', exchange: 'NSE', currentPrice: 654.32, change: 12.45, changePercent: 1.94 },
];

// Mock trading signals
export const MOCK_SIGNALS: TradingSignal[] = [
  {
    id: '1',
    symbol: 'RELIANCE.NS',
    type: 'BUY',
    price: 2456.78,
    confidence: 0.85,
    timestamp: new Date(Date.now() - 2 * 60 * 1000),
    reasoning: 'Strong bullish momentum with RSI oversold condition',
    indicators: { RSI: 32.5, SMA_20: 2420.45, SMA_50: 2380.12 }
  },
  {
    id: '2',
    symbol: 'TCS.NS',
    type: 'SELL',
    price: 3234.56,
    confidence: 0.92,
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    reasoning: 'Bearish divergence with high RSI levels',
    indicators: { RSI: 78.2, SMA_20: 3250.30, SMA_50: 3200.15 }
  },
  {
    id: '3',
    symbol: 'HDFCBANK.NS',
    type: 'BUY',
    price: 1678.90,
    confidence: 0.78,
    timestamp: new Date(Date.now() - 8 * 60 * 1000),
    reasoning: 'Golden cross formation with volume confirmation',
    indicators: { RSI: 45.8, SMA_20: 1665.20, SMA_50: 1650.45 }
  },
];

// Generate mock candlestick data
export const generateMockCandlestickData = (symbol: string, days: number = 100): CandlestickData[] => {
  const data: CandlestickData[] = [];
  const basePrice = MOCK_STOCKS.find(s => s.symbol === symbol)?.currentPrice || 1000;
  let currentPrice = basePrice;
  
  for (let i = days; i >= 0; i--) {
    const time = Date.now() - i * 24 * 60 * 60 * 1000;
    const volatility = 0.02; // 2% daily volatility
    const change = (Math.random() - 0.5) * volatility * currentPrice;
    
    const open = currentPrice;
    const close = currentPrice + change;
    const high = Math.max(open, close) + Math.random() * 0.01 * currentPrice;
    const low = Math.min(open, close) - Math.random() * 0.01 * currentPrice;
    const volume = Math.floor(Math.random() * 1000000) + 100000;
    
    data.push({
      time: Math.floor(time / 1000),
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume
    });
    
    currentPrice = close;
  }
  
  return data;
};

// Mock ML models
export const MOCK_ML_MODELS: MLModel[] = [
  {
    id: '1',
    name: 'RELIANCE_LSTM_v1',
    type: 'LSTM',
    symbol: 'RELIANCE.NS',
    accuracy: 0.847,
    trainedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    parameters: {
      sequenceLength: 60,
      epochs: 50,
      batchSize: 32,
      learningRate: 0.001,
      dropoutRate: 0.2,
      units: 50
    },
    performance: {
      accuracy: 0.847,
      precision: 0.823,
      recall: 0.856,
      f1Score: 0.839,
      trainingLoss: 0.0234,
      validationLoss: 0.0287,
      backtestResults: {
        totalReturns: 0.156,
        sharpeRatio: 1.34,
        maxDrawdown: 0.087,
        winRate: 0.623,
        totalTrades: 45
      }
    }
  },
  {
    id: '2',
    name: 'TCS_GRU_v2',
    type: 'GRU',
    symbol: 'TCS.NS',
    accuracy: 0.792,
    trainedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    parameters: {
      sequenceLength: 60,
      epochs: 75,
      batchSize: 32,
      learningRate: 0.0015,
      dropoutRate: 0.3,
      units: 64
    },
    performance: {
      accuracy: 0.792,
      precision: 0.778,
      recall: 0.801,
      f1Score: 0.789,
      trainingLoss: 0.0312,
      validationLoss: 0.0356,
      backtestResults: {
        totalReturns: 0.123,
        sharpeRatio: 1.12,
        maxDrawdown: 0.094,
        winRate: 0.587,
        totalTrades: 38
      }
    }
  }
];

// Mock training progress
export const createMockTrainingProgress = (): TrainingProgress => ({
  epoch: Math.floor(Math.random() * 50) + 1,
  totalEpochs: 50,
  loss: Math.random() * 0.1,
  accuracy: 0.6 + Math.random() * 0.3,
  estimatedTimeRemaining: Math.floor(Math.random() * 1800) + 300, // 5-35 minutes
  status: 'TRAINING'
});

// Search stocks function
export const searchStocks = async (query: string): Promise<Stock[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 200));
  
  if (!query.trim()) return MOCK_STOCKS;
  
  return MOCK_STOCKS.filter(stock =>
    stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
    stock.name.toLowerCase().includes(query.toLowerCase())
  );
};

// Get stock by symbol
export const getStockBySymbol = (symbol: string): Stock | undefined => {
  return MOCK_STOCKS.find(stock => stock.symbol === symbol);
};

// Update stock price (simulate real-time updates)
export const updateStockPrice = (symbol: string): Stock | undefined => {
  const stock = MOCK_STOCKS.find(s => s.symbol === symbol);
  if (!stock) return undefined;
  
  // Simulate small price changes
  const changePercent = (Math.random() - 0.5) * 0.02; // ±1% change
  const newPrice = stock.currentPrice * (1 + changePercent);
  const priceChange = newPrice - stock.currentPrice;
  
  return {
    ...stock,
    currentPrice: Number(newPrice.toFixed(2)),
    change: Number(priceChange.toFixed(2)),
    changePercent: Number((changePercent * 100).toFixed(2))
  };
};