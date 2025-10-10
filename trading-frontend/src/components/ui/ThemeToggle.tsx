'use client';

import { useState, useEffect, useCallback } from 'react';
import { Sun, Moon, Monitor, Palette } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useEnhancedTheme } from '@/components/providers/ThemeProvider';
import { cn } from '@/utils/cn';

export interface ThemeToggleProps {
  variant?: 'button' | 'switch' | 'dropdown';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
  'aria-label'?: string;
}

const themes = [
  { 
    name: 'light' as const, 
    icon: Sun, 
    label: 'Light Mode',
    description: 'Clean and bright interface'
  },
  { 
    name: 'dark' as const, 
    icon: Moon, 
    label: 'Dark Mode',
    description: 'Easy on the eyes'
  },
  { 
    name: 'system' as const, 
    icon: Monitor, 
    label: 'System',
    description: 'Follow system preference'
  },
];

export default function ThemeToggle({
  variant = 'button',
  size = 'md',
  showLabel = false,
  className,
  'aria-label': ariaLabel,
}: ThemeToggleProps) {
  const { theme, setTheme, resolvedTheme } = useEnhancedTheme();
  const [mounted, setMounted] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleThemeChange = useCallback((newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    setIsDropdownOpen(false);
    
    // Add smooth transition class to document
    if (typeof document !== 'undefined') {
      document.documentElement.classList.add('theme-transitioning');
      
      // Force immediate theme application
      const resolvedNewTheme = newTheme === 'system' 
        ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
        : newTheme;
      
      document.documentElement.setAttribute('data-theme', resolvedNewTheme);
      document.documentElement.classList.remove('theme-light', 'theme-dark');
      document.documentElement.classList.add(`theme-${resolvedNewTheme}`);
      
      // Force immediate background and color application
      if (resolvedNewTheme === 'light') {
        document.documentElement.style.backgroundColor = '#ffffff';
        document.documentElement.style.color = '#0f172a';
        document.body.style.backgroundColor = '#ffffff';
        document.body.style.color = '#0f172a';
      } else {
        document.documentElement.style.backgroundColor = '#0f172a';
        document.documentElement.style.color = '#f8fafc';
        document.body.style.backgroundColor = '#0f172a';
        document.body.style.color = '#f8fafc';
      }
      
      // Force a repaint
      document.documentElement.style.setProperty('--force-repaint', Math.random().toString());
      
      setTimeout(() => {
        document.documentElement.classList.remove('theme-transitioning');
      }, 300);
    }
  }, [setTheme]);

  const cycleTheme = useCallback(() => {
    const currentIndex = themes.findIndex(t => t.name === theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    handleThemeChange(themes[nextIndex].name);
  }, [theme, handleThemeChange]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (variant === 'dropdown') {
        setIsDropdownOpen(!isDropdownOpen);
      } else {
        cycleTheme();
      }
    } else if (event.key === 'Escape' && isDropdownOpen) {
      setIsDropdownOpen(false);
    }
  }, [variant, isDropdownOpen, cycleTheme]);

  if (!mounted) {
    return (
      <div 
        className={cn(
          'animate-pulse rounded-lg',
          size === 'sm' && 'w-8 h-8',
          size === 'md' && 'w-10 h-10',
          size === 'lg' && 'w-12 h-12'
        )}
        style={{ backgroundColor: 'var(--color-surface)' }}
      />
    );
  }

  const currentTheme = themes.find(t => t.name === theme) || themes[0];
  const nextTheme = themes[(themes.findIndex(t => t.name === theme) + 1) % themes.length];

  const buttonSizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-10 h-10 text-base',
    lg: 'w-12 h-12 text-lg',
  };

  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  if (variant === 'switch') {
    return (
      <div className={cn('flex items-center space-x-3', className)}>
        {showLabel && (
          <span 
            className="text-sm font-medium"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            {currentTheme.label}
          </span>
        )}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={cycleTheme}
          onKeyDown={handleKeyDown}
          className={cn(
            'relative inline-flex items-center rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2',
            size === 'sm' && 'h-5 w-9',
            size === 'md' && 'h-6 w-11',
            size === 'lg' && 'h-7 w-13'
          )}
          style={{
            backgroundColor: resolvedTheme === 'dark' ? 'var(--color-primary)' : 'var(--color-border)',
            '--focus-ring-color': 'var(--color-primary)',
          } as React.CSSProperties}
          aria-label={ariaLabel || `Switch to ${nextTheme.label}`}
          role="switch"
          aria-checked={resolvedTheme === 'dark'}
        >
          <motion.span
            layout
            className={cn(
              'inline-block rounded-full bg-white shadow-lg transform transition-transform duration-300',
              size === 'sm' && 'h-4 w-4',
              size === 'md' && 'h-5 w-5',
              size === 'lg' && 'h-6 w-6'
            )}
            style={{
              transform: resolvedTheme === 'dark' 
                ? `translateX(${size === 'sm' ? '16px' : size === 'md' ? '20px' : '24px'})` 
                : 'translateX(2px)',
            }}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={resolvedTheme}
                initial={{ rotate: -180, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 180, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="flex items-center justify-center w-full h-full"
              >
                {resolvedTheme === 'dark' ? (
                  <Moon className={cn(iconSizeClasses[size], 'text-gray-600')} />
                ) : (
                  <Sun className={cn(iconSizeClasses[size], 'text-yellow-500')} />
                )}
              </motion.div>
            </AnimatePresence>
          </motion.span>
        </motion.button>
      </div>
    );
  }

  if (variant === 'dropdown') {
    return (
      <div className={cn('relative', className)}>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          onKeyDown={handleKeyDown}
          className={cn(
            'flex items-center justify-center rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2',
            buttonSizeClasses[size]
          )}
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            '--focus-ring-color': 'var(--color-primary)',
          } as React.CSSProperties}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
            e.currentTarget.style.borderColor = 'var(--color-border-hover)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-surface)';
            e.currentTarget.style.borderColor = 'var(--color-border)';
          }}
          aria-label={ariaLabel || 'Theme options'}
          aria-expanded={isDropdownOpen}
          aria-haspopup="menu"
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={theme}
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <currentTheme.icon 
                className={iconSizeClasses[size]} 
                style={{ color: 'var(--color-text-secondary)' }}
              />
            </motion.div>
          </AnimatePresence>
        </motion.button>

        <AnimatePresence>
          {isDropdownOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              transition={{ duration: 0.2 }}
              className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg z-50"
              style={{
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                boxShadow: 'var(--shadow-lg)',
              }}
              role="menu"
            >
              {themes.map((themeOption) => (
                <motion.button
                  key={themeOption.name}
                  whileHover={{ backgroundColor: 'var(--color-surface-hover)' }}
                  onClick={() => handleThemeChange(themeOption.name)}
                  className={cn(
                    'w-full flex items-center space-x-3 px-4 py-3 text-left transition-colors duration-200 first:rounded-t-lg last:rounded-b-lg',
                    theme === themeOption.name && 'font-medium'
                  )}
                  style={{
                    color: theme === themeOption.name ? 'var(--color-primary)' : 'var(--color-text-primary)',
                  }}
                  role="menuitem"
                >
                  <themeOption.icon 
                    className="w-4 h-4" 
                    style={{ 
                      color: theme === themeOption.name ? 'var(--color-primary)' : 'var(--color-text-secondary)' 
                    }}
                  />
                  <div>
                    <div className="text-sm font-medium">{themeOption.label}</div>
                    <div 
                      className="text-xs"
                      style={{ color: 'var(--color-text-muted)' }}
                    >
                      {themeOption.description}
                    </div>
                  </div>
                  {theme === themeOption.name && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="ml-auto w-2 h-2 rounded-full"
                      style={{ backgroundColor: 'var(--color-primary)' }}
                    />
                  )}
                </motion.button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Backdrop for dropdown */}
        {isDropdownOpen && (
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsDropdownOpen(false)}
            aria-hidden="true"
          />
        )}
      </div>
    );
  }

  // Default button variant
  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={cycleTheme}
        onKeyDown={handleKeyDown}
        className={cn(
          'flex items-center justify-center rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2',
          buttonSizeClasses[size]
        )}
        style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          '--focus-ring-color': 'var(--color-primary)',
        } as React.CSSProperties}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
          e.currentTarget.style.borderColor = 'var(--color-border-hover)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--color-surface)';
          e.currentTarget.style.borderColor = 'var(--color-border)';
        }}
        aria-label={ariaLabel || `Switch to ${nextTheme.label}`}
        title={`Switch to ${nextTheme.label}`}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={theme}
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: 90, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <currentTheme.icon 
              className={iconSizeClasses[size]} 
              style={{ 
                color: theme === 'dark' && currentTheme.name === 'light' 
                  ? 'var(--color-warning)' 
                  : 'var(--color-text-secondary)' 
              }}
            />
          </motion.div>
        </AnimatePresence>
      </motion.button>
      
      {showLabel && (
        <span 
          className="text-sm font-medium"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {currentTheme.label}
        </span>
      )}
    </div>
  );
}