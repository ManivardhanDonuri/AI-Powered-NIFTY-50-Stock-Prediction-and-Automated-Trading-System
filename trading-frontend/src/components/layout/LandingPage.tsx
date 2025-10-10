'use client';

import { motion } from 'framer-motion';
import { TrendingUp, Brain, BarChart3, Shield, Zap, Target } from 'lucide-react';
import { APP_NAME, APP_DESCRIPTION } from '@/utils/constants';

interface LandingPageProps {
  onEnterDashboard: () => void;
}

export default function LandingPage({ onEnterDashboard }: LandingPageProps) {
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
      className="min-h-screen"
      style={{
        background: 'var(--color-background)',
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

        {/* Background Pattern */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 opacity-40" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
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