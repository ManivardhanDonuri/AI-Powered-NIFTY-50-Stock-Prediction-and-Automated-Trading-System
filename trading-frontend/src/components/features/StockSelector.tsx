'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronDown, Clock, TrendingUp } from 'lucide-react';
import { Stock } from '@/types/trading';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { cn } from '@/utils/cn';

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
    if (change > 0) return 'text-[var(--color-success)]';
    if (change < 0) return 'text-[var(--color-error)]';
    return 'text-[var(--color-text-muted)]';
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Selected Stock Display */}
      <Button
        variant="outline"
        size="lg"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full justify-between p-[var(--spacing-md)] h-auto bg-[var(--color-card-background)] border-[var(--color-border)] hover:border-[var(--color-border-hover)]"
      >
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-accent)] rounded-[var(--radius-lg)] flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div className="text-left">
            <div className="font-medium text-[var(--color-text-primary)]">
              {selectedStockData?.symbol || selectedStock}
            </div>
            {selectedStockData && (
              <div className="text-sm text-[var(--color-text-muted)] truncate max-w-48">
                {selectedStockData.name}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {selectedStockData && (
            <div className="text-right">
              <div className="font-medium text-[var(--color-text-primary)]">
                {formatPrice(selectedStockData.currentPrice)}
              </div>
              <div className={cn('text-sm', getChangeColor(selectedStockData.change))}>
                {formatChange(selectedStockData.change, selectedStockData.changePercent)}
              </div>
            </div>
          )}
          <ChevronDown className={cn('w-5 h-5 text-[var(--color-text-muted)] transition-transform', isOpen && 'rotate-180')} />
        </div>
      </Button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 right-0 mt-2 z-50 max-h-96 overflow-hidden"
          >
            <Card variant="elevated" padding="none" className="shadow-[var(--shadow-xl)]">
              {/* Search Input */}
              <div className="p-[var(--spacing-md)] border-b border-[var(--color-border)]">
                <Input
                  variant="filled"
                  placeholder="Search stocks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  icon={<Search />}
                  iconPosition="left"
                  className="text-sm"
                />
              </div>

              <div className="max-h-80 overflow-y-auto">
                {/* Recent Stocks */}
                {!searchQuery && recentStocksData.length > 0 && (
                  <div className="p-[var(--spacing-md)] border-b border-[var(--color-border)]">
                    <div className="flex items-center space-x-2 mb-[var(--spacing-sm)]">
                      <Clock className="w-4 h-4 text-[var(--color-text-muted)]" />
                      <span className="text-sm font-medium text-[var(--color-text-secondary)]">Recent</span>
                    </div>
                    <div className="space-y-1">
                      {recentStocksData.map((stock) => (
                        <Button
                          key={stock.symbol}
                          variant="ghost"
                          size="sm"
                          onClick={() => handleStockSelect(stock.symbol)}
                          className="w-full justify-between p-[var(--spacing-sm)] h-auto hover:bg-[var(--color-surface)]"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="text-left">
                              <div className="font-medium text-[var(--color-text-primary)] text-sm">
                                {stock.symbol}
                              </div>
                              <div className="text-xs text-[var(--color-text-muted)] truncate max-w-40">
                                {stock.name}
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-medium text-[var(--color-text-primary)]">
                              {formatPrice(stock.currentPrice)}
                            </div>
                            <div className={cn('text-xs', getChangeColor(stock.change))}>
                              {stock.changePercent.toFixed(2)}%
                            </div>
                          </div>
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {/* All Stocks */}
                <div className="p-[var(--spacing-md)]">
                  {!searchQuery && (
                    <div className="text-sm font-medium text-[var(--color-text-secondary)] mb-[var(--spacing-sm)]">
                      All Stocks
                    </div>
                  )}
                  <div className="space-y-1">
                    {filteredStocks.length > 0 ? (
                      filteredStocks.map((stock) => (
                        <Button
                          key={stock.symbol}
                          variant={stock.symbol === selectedStock ? "secondary" : "ghost"}
                          size="md"
                          onClick={() => handleStockSelect(stock.symbol)}
                          className={cn(
                            'w-full justify-between p-[var(--spacing-md)] h-auto hover:bg-[var(--color-surface)]',
                            stock.symbol === selectedStock && 'bg-[var(--color-primary)]/10 border border-[var(--color-primary)]/20'
                          )}
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-accent)] rounded-[var(--radius-lg)] flex items-center justify-center">
                              <span className="text-xs font-bold text-white">
                                {stock.symbol.substring(0, 2)}
                              </span>
                            </div>
                            <div className="text-left">
                              <div className="font-medium text-[var(--color-text-primary)]">
                                {stock.symbol}
                              </div>
                              <div className="text-sm text-[var(--color-text-muted)] truncate max-w-48">
                                {stock.name}
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium text-[var(--color-text-primary)]">
                              {formatPrice(stock.currentPrice)}
                            </div>
                            <div className={cn('text-sm', getChangeColor(stock.change))}>
                              {formatChange(stock.change, stock.changePercent)}
                            </div>
                          </div>
                        </Button>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <div className="text-[var(--color-text-muted)] mb-2">
                          No stocks found
                        </div>
                        <div className="text-sm text-[var(--color-text-muted)]">
                          Try searching with a different term
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}