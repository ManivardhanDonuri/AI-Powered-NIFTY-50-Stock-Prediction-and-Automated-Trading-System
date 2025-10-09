// Core trading data types
export interface CandlestickData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TradingSignal {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL' | 'HOLD';
  price: number;
  confidence: number;
  timestamp: Date;
  reasoning: string;
  indicators: Record<string, number>;
}

export interface Stock {
  symbol: string;
  name: string;
  exchange?: string;
  price?: number;
  currentPrice: number;
  change: number;
  changePercent: number;
  high?: number;
  low?: number;
  volume?: string;
}

export interface TechnicalIndicator {
  name: string;
  value: number;
  signal: 'BUY' | 'SELL' | 'NEUTRAL';
}

// ML Model types
export interface MLModel {
  id: string;
  name: string;
  type: 'LSTM' | 'GRU';
  symbol: string;
  accuracy: number;
  trainedAt: Date;
  parameters: ModelParameters;
  performance: ModelPerformance;
}

export interface ModelParameters {
  sequenceLength: number;
  epochs: number;
  batchSize: number;
  learningRate: number;
  dropoutRate: number;
  units: number;
}

export interface ModelPerformance {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  trainingLoss: number;
  validationLoss: number;
  backtestResults?: BacktestResults;
}

export interface BacktestResults {
  totalReturns: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
}

export interface TrainingProgress {
  epoch: number;
  totalEpochs: number;
  loss: number;
  accuracy: number;
  estimatedTimeRemaining: number;
  status: 'TRAINING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
}

export interface TrainingConfig {
  symbol: string;
  modelType: 'LSTM' | 'GRU';
  parameters: ModelParameters;
  dataRange: {
    startDate: string;
    endDate: string;
  };
}
