'use client';

import { useState, useMemo } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  PieChart, 
  BarChart3,
  Calendar,
  Target,
  Activity,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { formatCurrency, formatPercentage, getChangeColor } from '@/utils/formatters';

interface Position {
  symbol: string;
  name: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  marketValue: number;
  pnl: number;
  pnlPercent: number;
  allocation: number;
}

interface Trade {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  value: number;
  date: Date;
  pnl?: number;
}

export default function PortfolioPage() {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1M');
  
  // Mock portfolio data
  const portfolioSummary = {
    totalValue: 245678.50,
    totalInvested: 220000.00,
    totalPnL: 25678.50,
    totalPnLPercent: 11.67,
    dayChange: 3456.78,
    dayChangePercent: 1.43,
    cash: 15000.00,
  };

  const positions: Position[] = [
    {
      symbol: 'RELIANCE.NS',
      name: 'Reliance Industries Ltd',
      quantity: 50,
      avgPrice: 2400.00,
      currentPrice: 2456.78,
      marketValue: 122839.00,
      pnl: 2839.00,
      pnlPercent: 2.37,
      allocation: 50.0,
    },
    {
      symbol: 'TCS.NS',
      name: 'Tata Consultancy Services',
      quantity: 30,
      avgPrice: 3300.00,
      currentPrice: 3234.56,
      marketValue: 97036.80,
      pnl: -1963.20,
      pnlPercent: -1.98,
      allocation: 39.5,
    },
    {
      symbol: 'HDFCBANK.NS',
      name: 'HDFC Bank Ltd',
      quantity: 15,
      avgPrice: 1650.00,
      currentPrice: 1678.90,
      marketValue: 25183.50,
      pnl: 433.50,
      pnlPercent: 1.75,
      allocation: 10.5,
    },
  ];

  const recentTrades: Trade[] = [
    {
      id: '1',
      symbol: 'RELIANCE.NS',
      type: 'BUY',
      quantity: 10,
      price: 2456.78,
      value: 24567.80,
      date: new Date(Date.now() - 2 * 60 * 60 * 1000),
    },
    {
      id: '2',
      symbol: 'TCS.NS',
      type: 'SELL',
      quantity: 5,
      price: 3234.56,
      value: 16172.80,
      date: new Date(Date.now() - 5 * 60 * 60 * 1000),
      pnl: 672.80,
    },
    {
      id: '3',
      symbol: 'HDFCBANK.NS',
      type: 'BUY',
      quantity: 15,
      price: 1650.00,
      value: 24750.00,
      date: new Date(Date.now() - 24 * 60 * 60 * 1000),
    },
  ];

  const performanceData = [
    { date: '2024-01-01', value: 220000 },
    { date: '2024-01-15', value: 225000 },
    { date: '2024-02-01', value: 230000 },
    { date: '2024-02-15', value: 235000 },
    { date: '2024-03-01', value: 245678 },
  ];

  const totalInvested = positions.reduce((sum, pos) => sum + (pos.avgPrice * pos.quantity), 0);
  const totalMarketValue = positions.reduce((sum, pos) => sum + pos.marketValue, 0);

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
              Portfolio
            </h1>
            <p 
              className="mt-2"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Monitor your portfolio performance and holdings
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button variant="outline">
              <Calendar className="w-4 h-4 mr-2" />
              Export Report
            </Button>
            <Button>
              <Target className="w-4 h-4 mr-2" />
              Rebalance
            </Button>
          </div>
        </div>

        {/* Portfolio Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Total Value
                </p>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {formatCurrency(portfolioSummary.totalValue)}
                </p>
                <p className={`text-sm ${getChangeColor(portfolioSummary.totalPnL)}`}>
                  {portfolioSummary.totalPnL >= 0 ? '+' : ''}{formatCurrency(portfolioSummary.totalPnL)} ({formatPercentage(portfolioSummary.totalPnLPercent)})
                </p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-full">
                <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-indigo-500"></div>
          </Card>

          <Card className="relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Day Change
                </p>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {formatCurrency(portfolioSummary.dayChange)}
                </p>
                <p className={`text-sm ${getChangeColor(portfolioSummary.dayChange)}`}>
                  {formatPercentage(portfolioSummary.dayChangePercent)}
                </p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-full">
                {portfolioSummary.dayChange >= 0 ? (
                  <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
                ) : (
                  <TrendingDown className="w-6 h-6 text-red-600 dark:text-red-400" />
                )}
              </div>
            </div>
            <div className={`absolute bottom-0 left-0 right-0 h-1 ${portfolioSummary.dayChange >= 0 ? 'bg-gradient-to-r from-green-500 to-emerald-500' : 'bg-gradient-to-r from-red-500 to-pink-500'}`}></div>
          </Card>

          <Card className="relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Invested
                </p>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {formatCurrency(portfolioSummary.totalInvested)}
                </p>
                <p 
                  className="text-sm"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  {positions.length} positions
                </p>
              </div>
              <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-full">
                <PieChart className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-pink-500"></div>
          </Card>

          <Card className="relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Available Cash
                </p>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {formatCurrency(portfolioSummary.cash)}
                </p>
                <p 
                  className="text-sm"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  Ready to invest
                </p>
              </div>
              <div className="p-3 bg-orange-100 dark:bg-orange-900/20 rounded-full">
                <Activity className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-500 to-red-500"></div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Holdings */}
          <div className="lg:col-span-2">
            <Card>
              <div className="flex items-center justify-between mb-6">
                <h3 
                  className="text-xl font-semibold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  Holdings
                </h3>
                <Button variant="outline" size="sm">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  View All
                </Button>
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
                        Stock
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        Qty
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        Avg Price
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        Current
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        Value
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        P&L
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-medium"
                        style={{ color: 'var(--color-text-primary)' }}
                      >
                        %
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {positions.map((position) => (
                      <tr key={position.symbol} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="py-4 px-4">
                          <div>
                            <div 
                              className="font-medium"
                              style={{ color: 'var(--color-text-primary)' }}
                            >
                              {position.symbol}
                            </div>
                            <div 
                              className="text-sm truncate max-w-32"
                              style={{ color: 'var(--color-text-muted)' }}
                            >
                              {position.name}
                            </div>
                          </div>
                        </td>
                        <td 
                          className="text-right py-4 px-4"
                          style={{ color: 'var(--color-text-primary)' }}
                        >
                          {position.quantity}
                        </td>
                        <td 
                          className="text-right py-4 px-4"
                          style={{ color: 'var(--color-text-primary)' }}
                        >
                          {formatCurrency(position.avgPrice)}
                        </td>
                        <td 
                          className="text-right py-4 px-4"
                          style={{ color: 'var(--color-text-primary)' }}
                        >
                          {formatCurrency(position.currentPrice)}
                        </td>
                        <td className="text-right py-4 px-4 text-gray-900 dark:text-white">{formatCurrency(position.marketValue)}</td>
                        <td className={`text-right py-4 px-4 ${getChangeColor(position.pnl)}`}>
                          {position.pnl >= 0 ? '+' : ''}{formatCurrency(position.pnl)}
                        </td>
                        <td className={`text-right py-4 px-4 ${getChangeColor(position.pnl)}`}>
                          {formatPercentage(position.pnlPercent)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>

          {/* Portfolio Allocation */}
          <div className="space-y-6">
            <Card>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Allocation</h3>
              
              <div className="space-y-4">
                {positions.map((position) => (
                  <div key={position.symbol}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{position.symbol}</span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">{position.allocation.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500"
                        style={{ width: `${position.allocation}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
                
                {/* Cash allocation */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Cash</span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {((portfolioSummary.cash / portfolioSummary.totalValue) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full bg-gradient-to-r from-green-500 to-emerald-500"
                      style={{ width: `${(portfolioSummary.cash / portfolioSummary.totalValue) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Performance Metrics */}
            <Card>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Performance</h3>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Total Return</span>
                  <span className={`text-sm font-medium ${getChangeColor(portfolioSummary.totalPnL)}`}>
                    {formatPercentage(portfolioSummary.totalPnLPercent)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Best Performer</span>
                  <span className="text-sm font-medium text-green-600 dark:text-green-400">
                    {positions.reduce((best, pos) => pos.pnlPercent > best.pnlPercent ? pos : best).symbol}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Worst Performer</span>
                  <span className="text-sm font-medium text-red-600 dark:text-red-400">
                    {positions.reduce((worst, pos) => pos.pnlPercent < worst.pnlPercent ? pos : worst).symbol}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Diversification</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {positions.length} stocks
                  </span>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Recent Trades */}
        <Card>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Recent Trades</h3>
            <Button variant="outline" size="sm">View All</Button>
          </div>

          <div className="space-y-4">
            {recentTrades.map((trade) => (
              <div key={trade.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`p-2 rounded-full ${
                    trade.type === 'BUY' 
                      ? 'bg-green-100 dark:bg-green-900/20' 
                      : 'bg-red-100 dark:bg-red-900/20'
                  }`}>
                    {trade.type === 'BUY' ? (
                      <ArrowUpRight className="w-4 h-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <ArrowDownRight className="w-4 h-4 text-red-600 dark:text-red-400" />
                    )}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {trade.type} {trade.quantity} {trade.symbol}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      @ {formatCurrency(trade.price)} • {trade.date.toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900 dark:text-white">
                    {formatCurrency(trade.value)}
                  </div>
                  {trade.pnl && (
                    <div className={`text-sm ${getChangeColor(trade.pnl)}`}>
                      P&L: {trade.pnl >= 0 ? '+' : ''}{formatCurrency(trade.pnl)}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
}