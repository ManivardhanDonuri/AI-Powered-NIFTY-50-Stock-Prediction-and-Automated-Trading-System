'use client';

import { motion } from 'framer-motion';
import { Menu, User } from 'lucide-react';
import NotificationCenter from '@/components/ui/NotificationCenter';
import ThemeToggle from '@/components/ui/ThemeToggle';

interface HeaderProps {
  title: string;
  onSidebarToggle: () => void;
}

export default function Header({ title, onSidebarToggle }: HeaderProps) {

  return (
    <header 
      className="px-6 py-4 border-b transition-colors duration-200"
      style={{
        backgroundColor: 'var(--color-background)',
        borderColor: 'var(--color-border)',
      }}
    >
      <div className="flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center space-x-4">
          {/* Mobile Menu Button */}
          <button
            onClick={onSidebarToggle}
            className="lg:hidden p-2 rounded-lg transition-colors duration-200"
            style={{
              '--hover-bg': 'var(--color-surface-hover)',
            } as React.CSSProperties}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <Menu 
              className="w-5 h-5" 
              style={{ color: 'var(--color-text-secondary)' }}
            />
          </button>

          {/* Page Title */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h1 
              className="text-2xl font-bold"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {title}
            </h1>
            <p 
              className="text-sm"
              style={{ color: 'var(--color-text-muted)' }}
            >
              {new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </motion.div>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-4">
          {/* Market Status */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="hidden sm:flex items-center space-x-2 px-3 py-2 rounded-lg border"
            style={{
              backgroundColor: 'rgba(16, 185, 129, 0.1)', // success color with 10% opacity
              borderColor: 'rgba(16, 185, 129, 0.2)', // success color with 20% opacity
            }}
          >
            <div 
              className="w-2 h-2 rounded-full animate-pulse"
              style={{ backgroundColor: 'var(--color-success)' }}
            ></div>
            <span 
              className="text-sm font-medium"
              style={{ color: 'var(--color-success)' }}
            >
              Market Open
            </span>
          </motion.div>

          {/* Enhanced Theme Toggle */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <ThemeToggle 
              variant="button" 
              size="md" 
              aria-label="Toggle theme"
            />
          </motion.div>

          {/* Notifications */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            <NotificationCenter />
          </motion.div>

          {/* User Profile */}
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.4 }}
            className="flex items-center space-x-2 p-2 rounded-lg transition-colors duration-200"
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center"
              style={{
                background: `linear-gradient(135deg, var(--color-primary), var(--color-accent))`,
              }}
            >
              <User className="w-4 h-4 text-white" />
            </div>
            <span 
              className="hidden sm:block text-sm font-medium"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Trader
            </span>
          </motion.button>
        </div>
      </div>
    </header>
  );
}