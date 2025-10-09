// Configuration types
export interface TradingConfig {
  trading: {
    stocks: string[];
    rsiPeriod: number;
    smaShort: number;
    smaLong: number;
    rsiOversold: number;
    rsiOverbought: number;
    lookbackDays: number;
  };
  ml: {
    enabled: boolean;
    models: string[];
    sequenceLength: number;
    predictionHorizon: number;
    trainTestSplit: number;
    validationSplit: number;
    epochs: number;
    batchSize: number;
    learningRate: number;
    dropoutRate: number;
    lstmUnits: number;
    gruUnits: number;
    features: string[];
    modelSavePath: string;
    scalerSavePath: string;
  };
  signals: {
    mode: string;
    ruleWeight: number;
    mlWeight: number;
    mlThreshold: number;
    confidenceThreshold: number;
  };
  dashboard: {
    enabled: boolean;
    port: number;
    title: string;
  };
}

export interface TelegramConfig {
  botToken: string;
  chatId: string;
  notifications: {
    signals: boolean;
    trades: boolean;
    errors: boolean;
    training: boolean;
  };
}

// Real-time update types
export interface RealtimeUpdate {
  type:
    | 'PRICE_UPDATE'
    | 'SIGNAL_GENERATED'
    | 'TRADE_EXECUTED'
    | 'TRAINING_PROGRESS';
  symbol?: string;
  data: unknown;
  timestamp: Date;
}

// API Error types
export interface APIError {
  code: string;
  message: string;
  details?: unknown;
  timestamp: Date;
}

export interface ValidationError {
  field: string;
  message: string;
  value: unknown;
}
