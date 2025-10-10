'use client';

import { useState, useMemo } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Download, Filter, Search, Calendar, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { TradingSignal } from '@/types/trading';
import { MOCK_SIGNALS } from '@/services/mockData';
import { formatCurrency, formatPercentage, getChangeColor } from '@/utils/formatters';
import { SIGNAL_TYPES, EXPORT_FORMATS } from '@/utils/constants';

export default function HistoryPage() {
  const [signals] = useState<TradingSignal[]>([
    ...MOCK_SIGNALS,
    // Add more mock signals for demonstration
    {
      id: '4',
      symbol: 'INFY.NS',
      type: 'BUY',
      price: 1456.78,
      confidence: 0.82,
      timestamp: new Date(Date.now() - 15 * 60 * 1000),
      reasoning: 'Bullish breakout with volume confirmation',
      indicators: { RSI: 42.1, SMA_20: 1445.30, SMA_50: 1420.15 }
    },
    {
      id: '5',
      symbol: 'ICICIBANK.NS',
      type: 'SELL',
      price: 987.65,
      confidence: 0.75,
      timestamp: new Date(Date.now() - 25 * 60 * 1000),
      reasoning: 'Resistance level reached with overbought RSI',
      indicators: { RSI: 76.8, SMA_20: 995.20, SMA_50: 980.45 }
    },
    {
      id: '6',
      symbol: 'SBIN.NS',
      type: 'HOLD',
      price: 654.32,
      confidence: 0.65,
      timestamp: new Date(Date.now() - 35 * 60 * 1000),
      reasoning: 'Sideways movement, waiting for clear direction',
      indicators: { RSI: 52.3, SMA_20: 650.15, SMA_50: 648.90 }
    }
  ]);

  const [filters, setFilters] = useState({
    symbol: '',
    signalType: 'ALL',
    dateFrom: '',
    dateTo: '',
    searchQuery: '',
  });

  const [selectedSignals, setSelectedSignals] = useState<string[]>([]);

  // Filter signals based on current filters
  const filteredSignals = useMemo(() => {
    return signals.filter(signal => {
      const matchesSymbol = !filters.symbol || signal.symbol.toLowerCase().includes(filters.symbol.toLowerCase());
      const matchesType = filters.signalType === 'ALL' || signal.type === filters.signalType;
      const matchesSearch = !filters.searchQuery || 
        signal.symbol.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
        signal.reasoning.toLowerCase().includes(filters.searchQuery.toLowerCase());
      
      const signalDate = signal.timestamp.toISOString().split('T')[0];
      const matchesDateFrom = !filters.dateFrom || signalDate >= filters.dateFrom;
      const matchesDateTo = !filters.dateTo || signalDate <= filters.dateTo;

      return matchesSymbol && matchesType && matchesSearch && matchesDateFrom && matchesDateTo;
    });
  }, [signals, filters]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSelectSignal = (signalId: string) => {
    setSelectedSignals(prev => 
      prev.includes(signalId) 
        ? prev.filter(id => id !== signalId)
        : [...prev, signalId]
    );
  };

  const handleSelectAll = () => {
    if (selectedSignals.length === filteredSignals.length) {
      setSelectedSignals([]);
    } else {
      setSelectedSignals(filteredSignals.map(signal => signal.id));
    }
  };

  const handleExport = (format: string) => {
    const dataToExport = filteredSignals.filter(signal => 
      selectedSignals.length === 0 || selectedSignals.includes(signal.id)
    );

    if (format === 'csv') {
      const csvContent = [
        ['Timestamp', 'Symbol', 'Type', 'Price', 'Confidence', 'Reasoning', 'RSI', 'SMA_20', 'SMA_50'],
        ...dataToExport.map(signal => [
          signal.timestamp.toISOString(),
          signal.symbol,
          signal.type,
          signal.price.toString(),
          (signal.confidence * 100).toFixed(1) + '%',
          signal.reasoning,
          signal.indicators.RSI?.toString() || '',
          signal.indicators.SMA_20?.toString() || '',
          signal.indicators.SMA_50?.toString() || ''
        ])
      ].map(row => row.join(',')).join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `trading-signals-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    }
    // Add other export formats as needed
  };

  const getSignalIcon = (type: string) => {
    switch (type) {
      case 'BUY': return <TrendingUp className="w-4 h-4" />;
      case 'SELL': return <TrendingDown className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getSignalColor = (type: string) => {
    switch (type) {
      case 'BUY': return { backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--color-success)' };
      case 'SELL': return { backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)' };
      default: return { backgroundColor: 'var(--color-surface)', color: 'var(--color-text-muted)' };
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 
              className="text-3xl font-bold"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Trading History
            </h1>
            <p 
              className="mt-2"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              View and analyze your trading signals and execution history
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button variant="outline" className="flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </Button>
            <div className="relative">
              <select
                onChange={(e) => handleExport(e.target.value)}
                className="appearance-none rounded-lg px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2"
                style={{
                  backgroundColor: 'var(--color-input-background)',
                  borderColor: 'var(--color-input-border)',
                  color: 'var(--color-text-primary)',
                  '--focus-ring-color': 'var(--color-primary)',
                } as React.CSSProperties}
                defaultValue=""
              >
                <option value="" disabled>Export</option>
                {EXPORT_FORMATS.map(format => (
                  <option key={format.value} value={format.value}>{format.label}</option>
                ))}
              </select>
              <Download className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search signals..."
                value={filters.searchQuery}
                onChange={(e) => handleFilterChange('searchQuery', e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
                style={{
                  backgroundColor: 'var(--color-input-background)',
                  borderColor: 'var(--color-input-border)',
                  color: 'var(--color-text-primary)',
                  '--focus-ring-color': 'var(--color-primary)',
                } as React.CSSProperties}
              />
            </div>

            <Input
              placeholder="Symbol (e.g., RELIANCE.NS)"
              value={filters.symbol}
              onChange={(e) => handleFilterChange('symbol', e.target.value)}
            />

            <select
              value={filters.signalType}
              onChange={(e) => handleFilterChange('signalType', e.target.value)}
              className="px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2"
              style={{
                backgroundColor: 'var(--color-input-background)',
                borderColor: 'var(--color-input-border)',
                color: 'var(--color-text-primary)',
                '--focus-ring-color': 'var(--color-primary)',
              } as React.CSSProperties}
            >
              {SIGNAL_TYPES.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>

            <Input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
              label="From Date"
            />

            <Input
              type="date"
              value={filters.dateTo}
              onChange={(e) => handleFilterChange('dateTo', e.target.value)}
              label="To Date"
            />
          </div>
        </Card>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Total Signals
                </p>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {filteredSignals.length}
                </p>
              </div>
              <Activity className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Buy Signals
                </p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {filteredSignals.filter(s => s.type === 'BUY').length}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Sell Signals
                </p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {filteredSignals.filter(s => s.type === 'SELL').length}
                </p>
              </div>
              <TrendingDown className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>
          </Card>

          <Card padding="md">
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Avg Confidence
                </p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {filteredSignals.length > 0 
                    ? Math.round(filteredSignals.reduce((acc, s) => acc + s.confidence, 0) / filteredSignals.length * 100)
                    : 0}%
                </p>
              </div>
              <Calendar className="w-8 h-8 text-purple-600 dark:text-purple-400" />
            </div>
          </Card>
        </div>

        {/* Signals Table */}
        <Card>
          <div className="flex items-center justify-between mb-6">
            <h3 
              className="text-xl font-semibold"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Trading Signals ({filteredSignals.length})
            </h3>
            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <input
                  type="checkbox"
                  checked={selectedSignals.length === filteredSignals.length && filteredSignals.length > 0}
                  onChange={handleSelectAll}
                  className="rounded border-gray-300 dark:border-gray-600"
                />
                <span>Select All</span>
              </label>
              {selectedSignals.length > 0 && (
                <span className="text-sm text-blue-600 dark:text-blue-400">
                  {selectedSignals.length} selected
                </span>
              )}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr 
                  className="border-b"
                  style={{ borderColor: 'var(--color-border)' }}
                >
                  <th 
                    className="text-left py-3 px-4 font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Select
                  </th>
                  <th 
                    className="text-left py-3 px-4 font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Time
                  </th>
                  <th 
                    className="text-left py-3 px-4 font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Symbol
                  </th>
                  <th 
                    className="text-left py-3 px-4 font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Signal
                  </th>
                  <th 
                    className="text-left py-3 px-4 font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Price
                  </th>
                  <th 
                    className="text-left py-3 px-4 font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Confidence
                  </th>
                  <th 
                    className="text-left py-3 px-4 font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Reasoning
                  </th>
                  <th 
                    className="text-left py-3 px-4 font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Indicators
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredSignals.map((signal, index) => (
                  <tr 
                    key={signal.id} 
                    className="border-b"
                    style={{ 
                      borderColor: 'var(--color-border)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <td className="py-4 px-4">
                      <input
                        type="checkbox"
                        checked={selectedSignals.includes(signal.id)}
                        onChange={() => handleSelectSignal(signal.id)}
                        className="rounded border-gray-300 dark:border-gray-600"
                      />
                    </td>
                    <td className="py-4 px-4">
                      <div 
                        className="text-sm"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        {signal.timestamp.toLocaleDateString()}
                      </div>
                      <div 
                        className="text-xs"
                        style={{ color: 'var(--color-text-muted)' }}
                      >
                        {signal.timestamp.toLocaleTimeString()}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div 
                        className="font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        {signal.symbol}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div 
                        className="inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium"
                        style={getSignalColor(signal.type)}
                      >
                        {getSignalIcon(signal.type)}
                        <span>{signal.type}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div 
                        className="font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        {formatCurrency(signal.price)}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div 
                        className="text-sm font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        {Math.round(signal.confidence * 100)}%
                      </div>
                    </td>
                    <td className="py-4 px-4 max-w-xs">
                      <div 
                        className="text-sm truncate" 
                        title={signal.reasoning}
                        style={{ color: 'var(--color-text-secondary)' }}
                      >
                        {signal.reasoning}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="text-xs space-y-1">
                        <div>RSI: {signal.indicators.RSI?.toFixed(1) || 'N/A'}</div>
                        <div>SMA20: {signal.indicators.SMA_20?.toFixed(2) || 'N/A'}</div>
                        <div>SMA50: {signal.indicators.SMA_50?.toFixed(2) || 'N/A'}</div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredSignals.length === 0 && (
            <div className="text-center py-12">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No signals found</h3>
              <p className="text-gray-500 dark:text-gray-400">
                Try adjusting your filters to see more results.
              </p>
            </div>
          )}
        </Card>
      </div>
    </DashboardLayout>
  );
}