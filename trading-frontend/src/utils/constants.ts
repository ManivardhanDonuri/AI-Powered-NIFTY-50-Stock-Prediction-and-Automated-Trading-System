// Application constants
export const APP_NAME = 'NIFTY 50 ML Trading System';
export const APP_DESCRIPTION =
  'Advanced algorithmic trading system with machine learning capabilities for NIFTY 50 stocks';

export const TIMEFRAMES = [
  { label: '1D', value: '1D' },
  { label: '1W', value: '1W' },
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
  { label: '6M', value: '6M' },
  { label: '1Y', value: '1Y' },
];

export const MODEL_TYPES = [
  { label: 'LSTM', value: 'LSTM' },
  { label: 'GRU', value: 'GRU' },
];

export const SIGNAL_TYPES = [
  { label: 'All', value: 'ALL' },
  { label: 'Buy', value: 'BUY' },
  { label: 'Sell', value: 'SELL' },
  { label: 'Hold', value: 'HOLD' },
];

export const EXPORT_FORMATS = [
  { label: 'CSV', value: 'csv' },
  { label: 'Excel', value: 'xlsx' },
  { label: 'JSON', value: 'json' },
];

export const SIDEBAR_MENU_ITEMS = [
  {
    id: 'live-charts',
    label: 'Live Charts',
    icon: 'TrendingUp',
    href: '/live-charts',
  },
  {
    id: 'history',
    label: 'Trading History',
    icon: 'History',
    href: '/history',
  },
  { id: 'portfolio', label: 'Portfolio', icon: 'PieChart', href: '/portfolio' },
  { id: 'settings', label: 'Settings', icon: 'Settings', href: '/settings' },
  { id: 'system', label: 'System Control', icon: 'Power', href: '/system' },
];

export const DEFAULT_STOCKS = [
  'RELIANCE.NS',
  'TCS.NS',
  'HDFCBANK.NS',
  'INFY.NS',
  'HINDUNILVR.NS',
  'ICICIBANK.NS',
  'KOTAKBANK.NS',
  'BHARTIARTL.NS',
  'ITC.NS',
  'SBIN.NS',
];
