'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  LineChart,
  Minus,
  Square,
  Type,
  MousePointer,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Settings,
  Wifi,
  WifiOff,
  ChevronDown
} from 'lucide-react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import LiveChartsTerminal from '@/components/charts/LiveChartsTerminal';
import { useStockPrice, useConnectionStatus } from '@/hooks/useApiIntegration';

// Available stocks for the dropdown
interface StockOption {
  symbol: string;
  name: string;
  displayName: string;
  currentPrice: number;
  price?: number;
  change: number;
  changePercent: number;
  high: number;
  low: number;
  volume: string;
}

const availableStocks: StockOption[] = [
  {
    symbol: 'RELIANCE.NS',
    name: 'Reliance Industries Ltd',
    displayName: 'RELIANCE',
    currentPrice: 2847.50,
    price: 2847.50,
    change: 12.75,
    changePercent: 0.45,
    high: 2865.20,
    low: 2832.10,
    volume: '2.1M'
  },
  {
    symbol: 'TCS.NS',
    name: 'Tata Consultancy Services Ltd',
    displayName: 'TCS',
    currentPrice: 4125.80,
    price: 4125.80,
    change: -4.95,
    changePercent: -0.12,
    high: 4142.30,
    low: 4118.45,
    volume: '1.8M'
  },
  {
    symbol: 'HDFCBANK.NS',
    name: 'HDFC Bank Ltd',
    displayName: 'HDFC BANK',
    currentPrice: 1678.25,
    price: 1678.25,
    change: 8.40,
    changePercent: 0.50,
    high: 1685.90,
    low: 1665.75,
    volume: '3.2M'
  }
];

// Mock data for market indices
const marketIndices = [
  { name: 'NIFTY', value: 25046.15, change: -49.85, changePercent: -0.20 },
  { name: 'SENSEX', value: 81773.68, change: -153.08, changePercent: -0.19 },
  { name: 'BANKNIFTY', value: 54012.35, change: -211.16, changePercent: -0.39 }
];

// Drawing tools configuration
const drawingTools = [
  { id: 'cursor', name: 'Cursor', icon: MousePointer, active: true },
  { id: 'line', name: 'Trend Line', icon: Minus },
  { id: 'horizontal', name: 'Horizontal Line', icon: Minus },
  { id: 'rectangle', name: 'Rectangle', icon: Square },
  { id: 'text', name: 'Text', icon: Type }
];

// Chart types
const chartTypes = [
  { id: 'candlestick', name: 'Candlestick', icon: BarChart3, active: true },
  { id: 'line', name: 'Line', icon: LineChart }
];

// Timeframes
const timeframes = ['5y', '1y', '1m', '3d', '1d'];

function LiveChartsContent() {
  const [selectedTool, setSelectedTool] = useState('cursor');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1d');
  const [selectedChartType, setSelectedChartType] = useState('candlestick');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [selectedStock, setSelectedStock] = useState<StockOption>(availableStocks[0]); // Default to RELIANCE
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // API integration
  const { stockData } = useStockPrice(selectedStock.symbol);
  const { isConnected } = useConnectionStatus();

  // Use real stock data or fallback to mock, ensuring we have all required properties
  const currentStock: StockOption = stockData ? {
    ...selectedStock,
    currentPrice: stockData.currentPrice,
    price: stockData.price || stockData.currentPrice,
    change: stockData.change,
    changePercent: stockData.changePercent,
    high: stockData.high || selectedStock.high,
    low: stockData.low || selectedStock.low,
    volume: stockData.volume || selectedStock.volume
  } : selectedStock;

  // Check mobile
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => {
      window.removeEventListener('resize', checkMobile);
    };
  }, []);

  // Handle stock selection
  const handleStockSelect = (stock: StockOption) => {
    setSelectedStock(stock);
    setIsDropdownOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.stock-dropdown')) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div 
      className="h-full flex flex-col overflow-hidden"
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      {/* Top Bar */}
      <motion.div
        className="px-4 py-3 flex items-center justify-between border-b"
        style={{
          backgroundColor: 'var(--color-surface)',
          borderColor: 'var(--color-border)',
        }}
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Stock Selector and Info */}
        <div className="flex items-center space-x-6">
          {/* Stock Selector Dropdown */}
          <div className="relative stock-dropdown">
            <motion.button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 border"
              style={{
                backgroundColor: 'var(--color-card-background)',
                borderColor: 'var(--color-border)',
                color: 'var(--color-text-primary)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-border)';
              }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center space-x-2">
                <div className="text-left">
                  <div 
                    className="text-sm font-semibold"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    {currentStock.displayName || currentStock.symbol}
                  </div>
                  <div 
                    className="text-xs truncate max-w-32"
                    style={{ color: 'var(--color-text-secondary)' }}
                  >
                    {currentStock.name}
                  </div>
                </div>
              </div>
              <ChevronDown
                size={16}
                className={`transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`}
                style={{ color: 'var(--color-text-muted)' }}
              />
            </motion.button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="absolute top-full left-0 mt-2 w-80 rounded-lg shadow-lg z-50 overflow-hidden border"
                style={{
                  backgroundColor: 'var(--color-card-background)',
                  borderColor: 'var(--color-border)',
                  boxShadow: 'var(--shadow-xl)'
                }}
              >
                <div 
                  className="p-3 border-b"
                  style={{ borderColor: 'var(--color-border)' }}
                >
                  <div 
                    className="text-sm font-medium mb-2"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Select Stock
                  </div>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {availableStocks.map((stock, index) => (
                    <motion.button
                      key={stock.symbol}
                      onClick={() => handleStockSelect(stock)}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={`w-full px-4 py-3 text-left transition-colors border-b last:border-b-0`}
                      style={{
                        backgroundColor: selectedStock.symbol === stock.symbol 
                          ? 'rgba(59, 130, 246, 0.1)' 
                          : 'transparent',
                        borderColor: 'var(--color-border)',
                      }}
                      onMouseEnter={(e) => {
                        if (selectedStock.symbol !== stock.symbol) {
                          e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (selectedStock.symbol !== stock.symbol) {
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div 
                            className="font-medium"
                            style={{ color: 'var(--color-text-primary)' }}
                          >
                            {stock.displayName}
                          </div>
                          <div 
                            className="text-sm truncate"
                            style={{ color: 'var(--color-text-secondary)' }}
                          >
                            {stock.name}
                          </div>
                        </div>
                        <div className="text-right">
                          <div 
                            className="font-medium"
                            style={{ color: 'var(--color-text-primary)' }}
                          >
                            ₹{(stock.price || stock.currentPrice).toLocaleString()}
                          </div>
                          <div className={`text-sm flex items-center ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {stock.change >= 0 ? <TrendingUp size={12} className="mr-1" /> : <TrendingDown size={12} className="mr-1" />}
                            {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
                          </div>
                        </div>
                      </div>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
          </div>

          {/* Current Stock Info */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Current:</span>
          </div>

          <motion.div
            key={currentStock.symbol}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="flex items-center space-x-4"
          >
            <div 
              className="text-2xl font-bold"
              style={{ color: 'var(--color-text-primary)' }}
            >
              ₹{(currentStock.price || currentStock.currentPrice).toLocaleString()}
            </div>
            <div className={`flex items-center space-x-1 ${currentStock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {currentStock.change >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
              <span className="font-medium">
                {currentStock.change >= 0 ? '+' : ''}{currentStock.change.toFixed(2)} ({currentStock.changePercent.toFixed(2)}%)
              </span>
            </div>
          </motion.div>

          <motion.div
            key={`${currentStock.symbol}-details`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="flex items-center space-x-4 text-sm"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            <span>H: ₹{(currentStock.high || 25118.30).toLocaleString()}</span>
            <span>L: ₹{(currentStock.low || 24987.45).toLocaleString()}</span>
            <span>Vol: {currentStock.volume || '8.2M'}</span>
          </motion.div>
        </div>

        {/* Market Indices */}
        <div className="flex items-center space-x-6">
          {marketIndices.map((index) => (
            <div key={index.name} className="text-sm">
              <div 
                className="font-medium"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {index.name}
              </div>
              <div className={`flex items-center space-x-1 ${index.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                <span>{index.value.toLocaleString()}</span>
                <span>({index.changePercent.toFixed(2)}%)</span>
              </div>
            </div>
          ))}

          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <Wifi size={16} className="text-green-600" />
            ) : (
              <WifiOff size={16} className="text-red-600" />
            )}
            <span className={`text-xs ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
              {isConnected ? 'Live' : 'Disconnected'}
            </span>
          </div>
        </div>
      </motion.div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <motion.div
          className={`flex flex-col transition-all duration-300 border-r ${isMobile ? 'hidden' : sidebarCollapsed ? 'w-16' : 'w-64'
            }`}
          style={{
            backgroundColor: 'var(--color-surface)',
            borderColor: 'var(--color-border)',
          }}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          {/* Drawing Tools */}
          <div className="p-4">
            <h3 
              className={`font-medium mb-3 ${sidebarCollapsed ? 'hidden' : 'block'}`}
              style={{ color: 'var(--color-text-primary)' }}
            >
              Drawing Tools
            </h3>
            <div className="space-y-2">
              {drawingTools.map((tool) => (
                <motion.button
                  key={tool.id}
                  onClick={() => {
                    console.log(`Switching to drawing tool: ${tool.id}`);
                    setSelectedTool(tool.id);
                  }}
                  className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 border"
                  style={{
                    backgroundColor: selectedTool === tool.id 
                      ? 'rgba(59, 130, 246, 0.1)' 
                      : 'transparent',
                    borderColor: selectedTool === tool.id 
                      ? 'rgba(59, 130, 246, 0.2)' 
                      : 'transparent',
                    color: selectedTool === tool.id 
                      ? 'var(--color-primary)' 
                      : 'var(--color-text-secondary)',
                    boxShadow: selectedTool === tool.id ? 'var(--shadow-sm)' : 'none',
                  }}
                  onMouseEnter={(e) => {
                    if (selectedTool !== tool.id) {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                      e.currentTarget.style.color = 'var(--color-text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedTool !== tool.id) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = 'var(--color-text-secondary)';
                    }
                  }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  animate={selectedTool === tool.id ? { scale: [1, 1.05, 1] } : {}}
                  transition={{ duration: 0.3 }}
                >
                  <tool.icon size={18} />
                  {!sidebarCollapsed && <span className="text-sm">{tool.name}</span>}
                  {selectedTool === tool.id && !sidebarCollapsed && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="ml-auto w-2 h-2 bg-blue-500 rounded-full"
                    />
                  )}
                </motion.button>
              ))}
            </div>
          </div>

          {/* Chart Types */}
          <div 
            className="p-4 border-t"
            style={{ borderColor: 'var(--color-border)' }}
          >
            <h3 
              className={`font-medium mb-3 ${sidebarCollapsed ? 'hidden' : 'block'}`}
              style={{ color: 'var(--color-text-primary)' }}
            >
              Chart Types
            </h3>
            <div className="space-y-2">
              {chartTypes.map((type) => (
                <motion.button
                  key={type.id}
                  onClick={() => setSelectedChartType(type.id)}
                  className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors border"
                  style={{
                    backgroundColor: selectedChartType === type.id 
                      ? 'rgba(59, 130, 246, 0.1)' 
                      : 'transparent',
                    borderColor: selectedChartType === type.id 
                      ? 'rgba(59, 130, 246, 0.2)' 
                      : 'transparent',
                    color: selectedChartType === type.id 
                      ? 'var(--color-primary)' 
                      : 'var(--color-text-secondary)',
                  }}
                  onMouseEnter={(e) => {
                    if (selectedChartType !== type.id) {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                      e.currentTarget.style.color = 'var(--color-text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedChartType !== type.id) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = 'var(--color-text-secondary)';
                    }
                  }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <type.icon size={18} />
                  {!sidebarCollapsed && <span className="text-sm">{type.name}</span>}
                </motion.button>
              ))}
            </div>
          </div>

          {/* Chart Controls */}
          <div 
            className="p-4 border-t"
            style={{ borderColor: 'var(--color-border)' }}
          >
            <h3 
              className={`font-medium mb-3 ${sidebarCollapsed ? 'hidden' : 'block'}`}
              style={{ color: 'var(--color-text-primary)' }}
            >
              Controls
            </h3>
            <div className="space-y-2">
              <motion.button
                onClick={() => {
                  // This will be handled by the chart component
                  console.log('Zoom In clicked');
                }}
                className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors"
                style={{ color: 'var(--color-text-secondary)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                  e.currentTarget.style.color = 'var(--color-text-primary)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = 'var(--color-text-secondary)';
                }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <ZoomIn size={18} />
                {!sidebarCollapsed && <span className="text-sm">Zoom In</span>}
              </motion.button>
              <motion.button
                onClick={() => {
                  // This will be handled by the chart component
                  console.log('Zoom Out clicked');
                }}
                className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors"
                style={{ color: 'var(--color-text-secondary)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                  e.currentTarget.style.color = 'var(--color-text-primary)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = 'var(--color-text-secondary)';
                }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <ZoomOut size={18} />
                {!sidebarCollapsed && <span className="text-sm">Zoom Out</span>}
              </motion.button>
              <motion.button
                onClick={() => {
                  // This will be handled by the chart component
                  console.log('Reset Zoom clicked');
                }}
                className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors"
                style={{ color: 'var(--color-text-secondary)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                  e.currentTarget.style.color = 'var(--color-text-primary)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = 'var(--color-text-secondary)';
                }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <RotateCcw size={18} />
                {!sidebarCollapsed && <span className="text-sm">Reset</span>}
              </motion.button>
            </div>
          </div>

          {/* Collapse Button */}
          <div 
            className="mt-auto p-4 border-t"
            style={{ borderColor: 'var(--color-border)' }}
          >
            <motion.button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="w-full flex items-center justify-center px-3 py-2 rounded-lg transition-colors"
              style={{ color: 'var(--color-text-secondary)' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                e.currentTarget.style.color = 'var(--color-text-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--color-text-secondary)';
              }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Settings size={18} />
            </motion.button>
          </div>
        </motion.div>

        {/* Main Chart Area */}
        <div className="flex-1 flex flex-col">
          {/* Timeframe Controls */}
          <motion.div
            className="px-4 py-3 flex items-center justify-between border-b"
            style={{
              backgroundColor: 'var(--color-surface)',
              borderColor: 'var(--color-border)',
            }}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <div className="flex items-center space-x-2">
              {timeframes.map((timeframe) => (
                <motion.button
                  key={timeframe}
                  onClick={() => setSelectedTimeframe(timeframe)}
                  className="px-4 py-2 rounded-lg text-sm font-medium transition-colors border"
                  style={{
                    backgroundColor: selectedTimeframe === timeframe 
                      ? 'rgba(59, 130, 246, 0.1)' 
                      : 'transparent',
                    borderColor: selectedTimeframe === timeframe 
                      ? 'rgba(59, 130, 246, 0.2)' 
                      : 'var(--color-border)',
                    color: selectedTimeframe === timeframe 
                      ? 'var(--color-primary)' 
                      : 'var(--color-text-secondary)',
                  }}
                  onMouseEnter={(e) => {
                    if (selectedTimeframe !== timeframe) {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                      e.currentTarget.style.color = 'var(--color-text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedTimeframe !== timeframe) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = 'var(--color-text-secondary)';
                    }
                  }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {timeframe}
                </motion.button>
              ))}
            </div>
          </motion.div>

          {/* Chart Container */}
          <motion.div
            className="flex-1 relative p-4"
            style={{ backgroundColor: 'var(--color-background)' }}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: 0.3 }}
          >
            <LiveChartsTerminal
              data={[]}
              symbol={currentStock.symbol}
              timeframe={selectedTimeframe}
              selectedTool={selectedTool}
              chartType={selectedChartType}
              onTimeframeChange={setSelectedTimeframe}
              height={isMobile ? 400 : 600}
              className="w-full h-full"
              key={`${currentStock.symbol}-${selectedChartType}`} // Force re-render when stock or chart type changes
            />
          </motion.div>
        </div>

        {/* Right Sidebar */}
        <motion.div
          className="w-80 border-l flex flex-col hidden lg:flex"
          style={{
            backgroundColor: 'var(--color-surface)',
            borderColor: 'var(--color-border)'
          }}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          {/* Watchlist Panel */}
          <div className="p-4">
            <h3 
              className="font-medium mb-3"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Watchlist
            </h3>
            <div 
              className="rounded-lg border overflow-hidden"
              style={{
                backgroundColor: 'var(--color-card-background)',
                borderColor: 'var(--color-border)',
              }}
            >
              <div className="space-y-0">
                {[
                  ...availableStocks.map(stock => ({
                    symbol: stock.displayName,
                    price: stock.currentPrice,
                    change: stock.changePercent,
                    volume: stock.volume,
                    fullStock: stock
                  })),
                  { symbol: 'NIFTY 50', price: 25046.15, change: -0.20, volume: '8.2M', fullStock: null },
                  { symbol: 'SENSEX', price: 81773.68, change: -0.19, volume: '12.5M', fullStock: null }
                ].map((stock, index) => (
                  <motion.div
                    key={stock.symbol}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-3 border-b last:border-b-0 cursor-pointer transition-colors`}
                    style={{
                      borderColor: 'var(--color-border)',
                      backgroundColor: selectedStock.displayName === stock.symbol 
                        ? 'rgba(59, 130, 246, 0.1)' 
                        : 'transparent'
                    }}
                    onMouseEnter={(e) => {
                      if (selectedStock.displayName !== stock.symbol) {
                        e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (selectedStock.displayName !== stock.symbol) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }
                    }}
                    onClick={() => {
                      if (stock.fullStock) {
                        handleStockSelect(stock.fullStock);
                      }
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div 
                          className="font-medium text-sm"
                          style={{ color: 'var(--color-text-primary)' }}
                        >
                          {stock.symbol}
                        </div>
                        <div 
                          className="text-xs"
                          style={{ color: 'var(--color-text-secondary)' }}
                        >
                          Vol: {stock.volume}
                        </div>
                      </div>
                      <div className="text-right">
                        <div 
                          className="font-medium text-sm"
                          style={{ color: 'var(--color-text-primary)' }}
                        >
                          ₹{stock.price.toLocaleString()}
                        </div>
                        <div className={`text-xs ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Positions Panel */}
          <div className="p-4">
            <h3 
              className="font-medium mb-3"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Positions
            </h3>
            <div 
              className="rounded-lg border p-3"
              style={{
                backgroundColor: 'var(--color-card-background)',
                borderColor: 'var(--color-border)'
              }}
            >
              <div className="space-y-2">
                {[
                  { symbol: 'NIFTY 50', qty: 50, avgPrice: 24980.25, ltp: 25046.15, pnl: 3294.50 },
                  { symbol: 'RELIANCE', qty: 25, avgPrice: 2820.40, ltp: 2847.50, pnl: 677.50 }
                ].map((position, index) => (
                  <motion.div
                    key={position.symbol}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-2 rounded border"
                    style={{
                      backgroundColor: 'var(--color-surface)',
                      borderColor: 'var(--color-border)'
                    }}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span 
                        className="text-sm font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        {position.symbol}
                      </span>
                      <span className={`text-sm font-medium ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {position.pnl >= 0 ? '+' : ''}₹{position.pnl.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-600">
                      <span>Qty: {position.qty}</span>
                      <span>Avg: ₹{position.avgPrice}</span>
                      <span>LTP: ₹{position.ltp}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Orders Panel */}
          <div className="p-4">
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Orders</h3>
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-3">
              <div className="space-y-2">
                {[
                  { symbol: 'TCS', type: 'BUY', qty: 10, price: 4100.00, status: 'PENDING' },
                  { symbol: 'HDFC', type: 'SELL', qty: 15, price: 1650.50, status: 'EXECUTED' }
                ].map((order, index) => (
                  <motion.div
                    key={`${order.symbol}-${index}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-2 bg-gray-50 rounded border"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{order.symbol}</span>
                      <span className={`text-xs px-2 py-1 rounded ${order.status === 'EXECUTED'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-yellow-100 text-yellow-700'
                        }`}>
                        {order.status}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-600">
                      <span className={order.type === 'BUY' ? 'text-green-600' : 'text-red-600'}>
                        {order.type} {order.qty}
                      </span>
                      <span>₹{order.price}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Market Depth Panel */}
          <div className="p-4 flex-1">
            <h3 className="font-medium text-gray-900 dark:text-white mb-3">Market Depth</h3>
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-3 h-full">
              <div className="space-y-3">
                {/* Bid/Ask Header */}
                <div className="grid grid-cols-3 gap-2 text-xs font-medium text-gray-600 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700 pb-2">
                  <span>Bid Qty</span>
                  <span className="text-center">Price</span>
                  <span className="text-right">Ask Qty</span>
                </div>

                {/* Market Depth Data */}
                <div className="space-y-1">
                  {[
                    { bidQty: 1250, price: 25045.50, askQty: 890 },
                    { bidQty: 2100, price: 25045.25, askQty: 1450 },
                    { bidQty: 1800, price: 25045.00, askQty: 2200 },
                    { bidQty: 3200, price: 25044.75, askQty: 1650 },
                    { bidQty: 2800, price: 25044.50, askQty: 2900 }
                  ].map((depth, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                      className="grid grid-cols-3 gap-2 text-xs py-1"
                    >
                      <span className="text-green-600 font-medium">{depth.bidQty.toLocaleString()}</span>
                      <span className="text-center font-medium text-gray-900 dark:text-white">₹{depth.price}</span>
                      <span className="text-right text-red-600 font-medium">{depth.askQty.toLocaleString()}</span>
                    </motion.div>
                  ))}
                </div>

                {/* Depth Chart Visualization */}
                <div className="mt-4 pt-3 border-t">
                  <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">Depth Visualization</div>
                  <div className="space-y-1">
                    {[65, 45, 80, 35, 55].map((width, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div className="w-8 h-2 bg-green-200 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${width}%` }}
                            transition={{ delay: index * 0.1, duration: 0.5 }}
                            className="h-full bg-green-500"
                          />
                        </div>
                        <div className="w-8 h-2 bg-red-200 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${100 - width}%` }}
                            transition={{ delay: index * 0.1, duration: 0.5 }}
                            className="h-full bg-red-500"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Mobile Bottom Sheet */}
        <div className="lg:hidden">
          <motion.div
            initial={{ y: 100 }}
            animate={{ y: 0 }}
            className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 z-30"
          >
            <div className="flex items-center justify-around p-2">
              <button className="flex flex-col items-center p-2 text-gray-600 hover:text-blue-600">
                <div className="w-6 h-6 mb-1">📊</div>
                <span className="text-xs">Watchlist</span>
              </button>
              <button className="flex flex-col items-center p-2 text-gray-600 hover:text-blue-600">
                <div className="w-6 h-6 mb-1">💼</div>
                <span className="text-xs">Positions</span>
              </button>
              <button className="flex flex-col items-center p-2 text-gray-600 hover:text-blue-600">
                <div className="w-6 h-6 mb-1">📋</div>
                <span className="text-xs">Orders</span>
              </button>
              <button className="flex flex-col items-center p-2 text-gray-600 hover:text-blue-600">
                <div className="w-6 h-6 mb-1">📈</div>
                <span className="text-xs">Depth</span>
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default function LiveChartsPage() {
  return (
    <DashboardLayout>
      <LiveChartsContent />
    </DashboardLayout>
  );
}