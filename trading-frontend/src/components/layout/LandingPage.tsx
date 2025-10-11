'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { TrendingUp, Brain, BarChart3, Shield, Zap, Target } from 'lucide-react';
import { APP_NAME, APP_DESCRIPTION } from '@/utils/constants';

interface LandingPageProps {
  onEnterDashboard: () => void;
}

export default function LandingPage({ onEnterDashboard }: LandingPageProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Generate deterministic chart data to avoid hydration mismatch
  const generateChartData = () => {
    const data = [];
    for (let i = 0; i < 20; i++) {
      const x = 70 + i * 60;
      const baseY = 400 + Math.sin(i * 0.5) * 50;
      // Use deterministic values based on index instead of Math.random()
      const height = 20 + (i * 7 % 40);
      const isGreen = i % 3 !== 0; // Deterministic pattern
      data.push({ x, baseY, height, isGreen, i });
    }
    return data;
  };

  const chartData = generateChartData();

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Trading',
      description: 'Advanced LSTM and GRU models for intelligent market predictions',
    },
    {
      icon: BarChart3,
      title: 'Real-time Analytics',
      description: 'Live market data with professional trading charts and indicators',
    },
    {
      icon: Shield,
      title: 'Risk Management',
      description: 'Built-in risk controls and portfolio management tools',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Real-time signal generation and trade execution capabilities',
    },
    {
      icon: Target,
      title: 'Precision Trading',
      description: 'Technical analysis combined with machine learning insights',
    },
    {
      icon: TrendingUp,
      title: 'Performance Tracking',
      description: 'Comprehensive analytics and performance metrics',
    },
  ];

  return (
    <div 
      className="min-h-screen relative bg-trading-floor"
      style={{
        background: `
          linear-gradient(135deg, rgba(248, 250, 252, 0.95) 0%, rgba(226, 232, 240, 0.9) 50%, rgba(203, 213, 225, 0.85) 100%),
          url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23e2e8f0' fill-opacity='0.1'%3E%3Cpath d='M0 0h100v100H0z'/%3E%3Cpath d='M20 20h60v60H20z' fill='%23cbd5e1' fill-opacity='0.05'/%3E%3C/g%3E%3C/svg%3E")
        `,
        color: 'var(--color-text-primary)',
      }}
    >
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            {/* Logo/Brand */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mb-8"
            >
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl mb-6">
                <TrendingUp className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                {APP_NAME}
              </h1>
            </motion.div>

            {/* Description */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto leading-relaxed"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              {APP_DESCRIPTION}
            </motion.p>

            {/* CTA Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="mb-16"
            >
              <button
                onClick={onEnterDashboard}
                className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                <span className="mr-2">Get Started</span>
                <motion.div
                  animate={{ x: [0, 4, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <TrendingUp className="w-5 h-5" />
                </motion.div>
              </button>
            </motion.div>
          </motion.div>
        </div>

        {/* Dynamic Stock Market Background */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          {/* Trading Floor Atmosphere */}
          <div className="absolute inset-0">
            {/* Base gradient with trading floor colors */}
            <div className="absolute inset-0 bg-gradient-to-br from-slate-100 via-blue-50 to-indigo-100 opacity-90"></div>
            
            {/* Simulated depth with multiple layers */}
            <div className="absolute inset-0 bg-gradient-radial from-transparent via-blue-50/20 to-slate-200/40"></div>
            
            {/* Trading screen glow effect */}
            <div className="absolute top-0 left-0 w-full h-1/3 bg-gradient-to-b from-blue-400/10 to-transparent"></div>
            <div className="absolute bottom-0 left-0 w-full h-1/3 bg-gradient-to-t from-green-400/10 to-transparent"></div>
          </div>
          
          {/* Dynamic Stock Chart Animation */}
          <div className="absolute inset-0 opacity-15">
            <svg className="w-full h-full" viewBox="0 0 1400 900" fill="none" xmlns="http://www.w3.org/2000/svg">
              {/* Animated Candlestick Chart */}
              <g className="animate-pulse">
                {chartData.map((item) => (
                  <g key={item.i} className={item.isGreen ? "text-green-500" : "text-red-500"}>
                    <line 
                      x1={item.x} y1={item.baseY - item.height/2 - 10} 
                      x2={item.x} y2={item.baseY + item.height/2 + 10} 
                      stroke="currentColor" 
                      strokeWidth="1"
                    />
                    <rect 
                      x={item.x - 5} y={item.baseY - item.height/2} 
                      width="10" height={item.height} 
                      fill="currentColor" 
                      opacity="0.7"
                    />
                  </g>
                ))}
              </g>
              
              {/* Animated Trend Lines */}
              <g className="text-blue-500 opacity-30">
                <motion.path 
                  d="M50 500 Q400 300 800 200 Q1000 150 1350 100" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeDasharray="10,5"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                />
                <motion.path 
                  d="M50 600 Q400 450 800 350 Q1000 300 1350 250" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="1" 
                  strokeDasharray="5,3"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                />
              </g>
              
              {/* Market Data Grid */}
              <g stroke="currentColor" strokeWidth="0.5" className="text-slate-300 opacity-20">
                {Array.from({ length: 12 }, (_, i) => (
                  <line key={`h-${i}`} x1="0" y1={i * 75} x2="1400" y2={i * 75} />
                ))}
                {Array.from({ length: 18 }, (_, i) => (
                  <line key={`v-${i}`} x1={i * 80} y1="0" x2={i * 80} y2="900" />
                ))}
              </g>
            </svg>
          </div>
          
          {/* Floating Stock Data */}
          <div className="absolute inset-0 overflow-hidden">
            {[
              { symbol: 'RELIANCE', price: '₹2,847', change: '+1.2%', color: 'text-green-500' },
              { symbol: 'TCS', price: '₹4,125', change: '-0.3%', color: 'text-red-500' },
              { symbol: 'HDFC', price: '₹1,678', change: '+2.1%', color: 'text-green-500' },
              { symbol: 'INFY', price: '₹1,892', change: '+0.8%', color: 'text-green-500' },
              { symbol: 'NIFTY', price: '25,046', change: '-0.2%', color: 'text-red-500' },
            ].map((stock, i) => (
              <motion.div
                key={stock.symbol}
                className="absolute font-mono text-xs opacity-20 bg-white/30 backdrop-blur-sm rounded-lg p-2 border border-slate-200/50"
                style={{
                  left: `${15 + i * 18}%`,
                  top: `${25 + (i % 2) * 40}%`,
                }}
                animate={{
                  y: [-10, 10, -10],
                  opacity: [0.15, 0.25, 0.15],
                  scale: [0.95, 1.05, 0.95],
                }}
                transition={{
                  duration: 5 + i * 0.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: i * 0.8,
                }}
              >
                <div className="text-slate-700 font-semibold">{stock.symbol}</div>
                <div className="text-slate-600">{stock.price}</div>
                <div className={`${stock.color} text-xs`}>{stock.change}</div>
              </motion.div>
            ))}
          </div>
          
          {/* Animated Financial Icons */}
          <div className="absolute inset-0">
            <motion.div
              className="absolute top-20 left-10 w-16 h-16 border-2 border-blue-300/30 rounded-full"
              animate={{ 
                scale: [1, 1.2, 1],
                rotate: [0, 180, 360],
              }}
              transition={{ 
                duration: 8, 
                repeat: Infinity, 
                ease: "easeInOut" 
              }}
            />
            <motion.div
              className="absolute top-40 right-20 w-12 h-12 border-2 border-green-300/30 rounded-lg"
              animate={{ 
                rotate: [0, 45, 0],
                scale: [1, 1.1, 1],
              }}
              transition={{ 
                duration: 6, 
                repeat: Infinity, 
                ease: "easeInOut",
                delay: 1,
              }}
            />
            <motion.div
              className="absolute bottom-40 left-20 w-20 h-20 border-2 border-indigo-300/30 rounded-full"
              animate={{ 
                scale: [1, 1.3, 1],
                opacity: [0.2, 0.4, 0.2],
              }}
              transition={{ 
                duration: 5, 
                repeat: Infinity, 
                ease: "easeInOut",
                delay: 2,
              }}
            />
          </div>
          
          {/* Live Market Ticker */}
          <div className="absolute bottom-0 left-0 right-0 h-8 bg-slate-900/90 backdrop-blur-sm overflow-hidden">
            <motion.div
              className="flex items-center h-full whitespace-nowrap text-white text-sm"
              animate={{ x: ['-100%', '100%'] }}
              transition={{ 
                duration: 25, 
                repeat: Infinity, 
                ease: "linear" 
              }}
            >
              <span className="mx-8 text-green-400">RELIANCE ₹2,847.50 ↗ +1.2%</span>
              <span className="mx-8 text-red-400">TCS ₹4,125.80 ↘ -0.3%</span>
              <span className="mx-8 text-green-400">HDFCBANK ₹1,678.25 ↗ +2.1%</span>
              <span className="mx-8 text-green-400">INFY ₹1,892.45 ↗ +0.8%</span>
              <span className="mx-8 text-red-400">NIFTY 50 25,046.15 ↘ -0.2%</span>
              <span className="mx-8 text-blue-400">SENSEX 81,773.68 ↘ -0.19%</span>
              <span className="mx-8 text-green-400">WIPRO ₹432.15 ↗ +1.5%</span>
              <span className="mx-8 text-red-400">ICICIBANK ₹1,245.30 ↘ -0.7%</span>
            </motion.div>
          </div>
          
          {/* Particle Effect */}
          {mounted && (
            <div className="absolute inset-0">
              {Array.from({ length: 15 }, (_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-1 bg-blue-400 rounded-full opacity-20"
                  style={{
                    left: `${(i * 7) % 100}%`,
                    top: `${(i * 11) % 100}%`,
                  }}
                  animate={{
                    y: [-10, 10, -10],
                    x: [-5, 5, -5],
                    opacity: [0.1, 0.3, 0.1],
                  }}
                  transition={{
                    duration: 3 + (i % 3),
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: i * 0.2,
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="text-center mb-16"
        >
          <h2 
            className="text-3xl md:text-4xl font-bold mb-4"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Powerful Trading Features
          </h2>
          <p 
            className="text-lg max-w-2xl mx-auto"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Everything you need for successful algorithmic trading in one comprehensive platform
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1 + index * 0.1 }}
              className="group relative rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border"
              style={{
                backgroundColor: 'var(--color-card-background)',
                borderColor: 'var(--color-card-border)',
                boxShadow: 'var(--shadow-lg)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-card-border)';
              }}
            >
              <div className="flex items-center mb-4">
                <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl group-hover:scale-110 transition-transform duration-200">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
              </div>
              <h3 
                className="text-xl font-semibold mb-3"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {feature.title}
              </h3>
              <p 
                className="leading-relaxed"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div 
        className="border-t backdrop-blur-sm"
        style={{
          borderColor: 'var(--color-border)',
          backgroundColor: 'var(--color-surface)',
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div 
            className="text-center"
            style={{ color: 'var(--color-text-muted)' }}
          >
            <p>&copy; 2024 {APP_NAME}. Built with Next.js and TypeScript.</p>
          </div>
        </div>
      </div>
    </div>
  );
}