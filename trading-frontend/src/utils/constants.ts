export const APP_NAME = 'AI-Powered Trading System';
export const APP_DESCRIPTION = 'Advanced NIFTY 50 Stock Prediction and Automated Trading System with Machine Learning';
export const APP_VERSION = '1.0.0';
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003/api';

// Trading constants
export const DEFAULT_STOCKS = [
  { symbol: 'RELIANCE.NS', name: 'Reliance Industries Ltd' },
  { symbol: 'TCS.NS', name: 'Tata Consultancy Services Ltd' },
  { symbol: 'HDFCBANK.NS', name: 'HDFC Bank Ltd' },
  { symbol: 'INFY.NS', name: 'Infosys Ltd' },
  { symbol: 'HINDUNILVR.NS', name: 'Hindustan Unilever Ltd' },
];

export const MODEL_TYPES = [
  { id: 'lstm', name: 'LSTM Neural Network', description: 'Long Short-Term Memory network for time series prediction' },
  { id: 'random_forest', name: 'Random Forest', description: 'Ensemble learning method for classification and regression' },
  { id: 'svm', name: 'Support Vector Machine', description: 'Supervised learning model for classification and regression' },
  { id: 'xgboost', name: 'XGBoost', description: 'Gradient boosting framework for machine learning' },
];

export const SIGNAL_TYPES = [
  { value: 'all', label: 'All Signals' },
  { value: 'BUY', label: 'Buy Signals' },
  { value: 'SELL', label: 'Sell Signals' },
  { value: 'HOLD', label: 'Hold Signals' },
];

export const EXPORT_FORMATS = [
  { value: 'csv', label: 'CSV', icon: '📊' },
  { value: 'json', label: 'JSON', icon: '📄' },
  { value: 'pdf', label: 'PDF', icon: '📋' },
];

export const TIMEFRAMES = [
  { value: '1m', label: '1 Minute' },
  { value: '5m', label: '5 Minutes' },
  { value: '15m', label: '15 Minutes' },
  { value: '1h', label: '1 Hour' },
  { value: '4h', label: '4 Hours' },
  { value: '1d', label: '1 Day' },
  { value: '1w', label: '1 Week' },
  { value: '1M', label: '1 Month' },
];

export const SIDEBAR_MENU_ITEMS = [
  {
    id: 'live-charts',
    label: 'Live Charts',
    href: '/live-charts',
    icon: 'TrendingUp',
    description: 'Real-time trading charts and analysis'
  },
  {
    id: 'portfolio',
    label: 'Portfolio',
    href: '/portfolio',
    icon: 'PieChart',
    description: 'Portfolio management and tracking'
  },
  {
    id: 'history',
    label: 'Trade History',
    href: '/history',
    icon: 'History',
    description: 'Historical trades and performance'
  },
  {
    id: 'system',
    label: 'System Status',
    href: '/system',
    icon: 'Activity',
    description: 'System health and monitoring'
  },
  {
    id: 'settings',
    label: 'Settings',
    href: '/settings',
    icon: 'Settings',
    description: 'Application settings and configuration'
  },
];