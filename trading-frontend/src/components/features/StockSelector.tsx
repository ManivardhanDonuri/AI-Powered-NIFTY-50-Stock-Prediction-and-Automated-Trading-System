'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronDown, Clock, TrendingUp } from 'lucide-react';
import { Stock } from '@/types/trading';

interface StockSelectorProps {
  selectedStock: string;
  onStockChange: (symbol: string) => void;
  className?: string;
}

// Mock stock data - will be replaced with real API data
const MOCK_STOCKS: Stock[] = [
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

export default function StockSelector({ selectedStock, onStockChange, className = '' }: StockSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [recentStocks, setRecentStocks] = useState<string[]>(['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter stocks based on search query
  const filteredStocks = MOCK_STOCKS.filter(stock =>
    stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
    stock.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Get recent stocks data
  const recentStocksData = MOCK_STOCKS.filter(stock => recentStocks.includes(stock.symbol));

  // Get selected stock data
  const selectedStockData = MOCK_STOCKS.find(stock => stock.symbol === selectedStock);

  const handleStockSelect = (symbol: string) => {
    onStockChange(symbol);
    setIsOpen(false);
    setSearchQuery('');
    
    // Update recent stocks
    setRecentStocks(prev => {
      const updated = [symbol, ...prev.filter(s => s !== symbol)].slice(0, 5);
      return updated;
    });
  };

  const formatPrice = (price: number) => `₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  const formatChange = (change: number, changePercent: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}₹${change.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)`;
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600 dark:text-green-400';
    if (change < 0) return 'text-red-600 dark:text-red-400';
    return 'text-gray-600 dark:text-gray-400';
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Selected Stock Display */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900 dark:text-white">
              {selectedStockData?.symbol || selectedStock}
            </div>
            {selectedStockData && (
              <div className="text-sm text-gray-500 dark:text-gray-400 truncate max-w-48">
                {selectedStockData.name}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {selectedStockData && (
            <div className="text-right">
              <div className="font-medium text-gray-900 dark:text-white">
                {formatPrice(selectedStockData.currentPrice)}
              </div>
              <div className={`text-sm ${getChangeColor(selectedStockData.change)}`}>
                {formatChange(selectedStockData.change, selectedStockData.changePercent)}
              </div>
            </div>
          )}
          <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </div>
      </button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 max-h-96 overflow-hidden"
          >
            {/* Search Input */}
            <div className="p-3 border-b border-gray-200 dark:border-gray-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search stocks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="max-h-80 overflow-y-auto">
              {/* Recent Stocks */}
              {!searchQuery && recentStocksData.length > 0 && (
                <div className="p-3 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center space-x-2 mb-2">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Recent</span>
                  </div>
                  <div className="space-y-1">
                    {recentStocksData.map((stock) => (
                      <button
                        key={stock.symbol}
                        onClick={() => handleStockSelect(stock.symbol)}
                        className="w-full flex items-center justify-between p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="text-left">
                            <div className="font-medium text-gray-900 dark:text-white text-sm">
                              {stock.symbol}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-40">
                              {stock.name}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {formatPrice(stock.currentPrice)}
                          </div>
                          <div className={`text-xs ${getChangeColor(stock.change)}`}>
                            {stock.changePercent.toFixed(2)}%
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* All Stocks */}
              <div className="p-3">
                {!searchQuery && (
                  <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                    All Stocks
                  </div>
                )}
                <div className="space-y-1">
                  {filteredStocks.length > 0 ? (
                    filteredStocks.map((stock) => (
                      <button
                        key={stock.symbol}
                        onClick={() => handleStockSelect(stock.symbol)}
                        className={`w-full flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors ${
                          stock.symbol === selectedStock ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800' : ''
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
                            <span className="text-xs font-bold text-white">
                              {stock.symbol.substring(0, 2)}
                            </span>
                          </div>
                          <div className="text-left">
                            <div className="font-medium text-gray-900 dark:text-white">
                              {stock.symbol}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400 truncate max-w-48">
                              {stock.name}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium text-gray-900 dark:text-white">
                            {formatPrice(stock.currentPrice)}
                          </div>
                          <div className={`text-sm ${getChangeColor(stock.change)}`}>
                            {formatChange(stock.change, stock.changePercent)}
                          </div>
                        </div>
                      </button>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <div className="text-gray-400 dark:text-gray-500 mb-2">
                        No stocks found
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Try searching with a different term
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}