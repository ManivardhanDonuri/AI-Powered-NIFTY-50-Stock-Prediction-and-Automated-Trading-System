'use client';

import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { ThemeProvider as NextThemeProvider, useTheme as useNextTheme } from 'next-themes';
import { ThemeContextValue } from '@/types/theme';
import { themeConfigs, applyThemeToDocument } from '@/utils/theme';

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

interface EnhancedThemeProviderProps {
  children: React.ReactNode;
  attribute?: 'class' | 'data-theme' | string;
  defaultTheme?: string;
  enableSystem?: boolean;
  disableTransitionOnChange?: boolean;
  storageKey?: string;
}

function ThemeContextProvider({ children }: { children: React.ReactNode }) {
  const { theme, setTheme, resolvedTheme, systemTheme } = useNextTheme();
  const [mounted, setMounted] = useState(false);
  const [isHydrating, setIsHydrating] = useState(true);

  // Enhanced theme persistence with fallback detection
  const getStoredTheme = useCallback(() => {
    if (typeof window === 'undefined') return null;
    
    try {
      const stored = localStorage.getItem('theme');
      if (stored && ['light', 'dark', 'system'].includes(stored)) {
        return stored;
      }
    } catch (error) {
      console.warn('Failed to read theme from localStorage:', error);
    }
    
    return null;
  }, []);

  const detectSystemTheme = useCallback(() => {
    if (typeof window === 'undefined') return 'light';
    
    try {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } catch (error) {
      console.warn('Failed to detect system theme:', error);
      return 'light';
    }
  }, []);

  // Handle mounting and hydration
  useEffect(() => {
    const handleMount = () => {
      // Add theme loading class to prevent FOUC
      document.documentElement.classList.add('theme-loading');
      
      setMounted(true);
      
      // Remove loading class after a short delay
      setTimeout(() => {
        document.documentElement.classList.remove('theme-loading');
        document.documentElement.classList.add('theme-loaded');
        setIsHydrating(false);
      }, 50);
    };

    handleMount();
  }, []);

  // Apply theme to document with enhanced error handling
  useEffect(() => {
    if (!mounted) return;

    const currentTheme = resolvedTheme || detectSystemTheme();
    
    try {
      // Force theme application with immediate style updates
      document.documentElement.setAttribute('data-theme', currentTheme);
      
      // Add theme class for additional styling
      document.documentElement.classList.remove('theme-light', 'theme-dark');
      document.documentElement.classList.add(`theme-${currentTheme}`);
      
      // Force immediate background and color application
      if (currentTheme === 'light') {
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
      
      // Apply theme using utility function
      applyThemeToDocument(currentTheme as 'light' | 'dark');
      
      // Store theme preference (only if not system)
      if (theme && theme !== 'system') {
        try {
          localStorage.setItem('theme', theme);
        } catch (error) {
          console.warn('Failed to save theme to localStorage:', error);
        }
      }
      
      // Force a repaint to ensure styles are applied
      document.documentElement.style.setProperty('--force-repaint', Math.random().toString());
      
    } catch (error) {
      console.error('Failed to apply theme:', error);
      // Fallback to light theme
      document.documentElement.setAttribute('data-theme', 'light');
      document.documentElement.classList.remove('theme-light', 'theme-dark');
      document.documentElement.classList.add('theme-light');
      document.documentElement.style.backgroundColor = '#ffffff';
      document.documentElement.style.color = '#0f172a';
      document.body.style.backgroundColor = '#ffffff';
      document.body.style.color = '#0f172a';
      applyThemeToDocument('light');
    }
  }, [mounted, resolvedTheme, theme, detectSystemTheme]);

  // Enhanced theme change handler with validation
  const handleThemeChange = useCallback((newTheme: 'light' | 'dark' | 'system') => {
    if (!['light', 'dark', 'system'].includes(newTheme)) {
      console.warn('Invalid theme provided:', newTheme);
      return;
    }

    try {
      setTheme(newTheme);
      
      // Store preference immediately for better UX
      if (newTheme !== 'system') {
        localStorage.setItem('theme', newTheme);
      } else {
        localStorage.removeItem('theme');
      }
    } catch (error) {
      console.error('Failed to change theme:', error);
    }
  }, [setTheme]);

  // Listen for system theme changes
  useEffect(() => {
    if (!mounted || theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      if (theme === 'system') {
        const newSystemTheme = e.matches ? 'dark' : 'light';
        applyThemeToDocument(newSystemTheme);
        document.documentElement.setAttribute('data-theme', newSystemTheme);
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
  }, [mounted, theme]);

  const contextValue: ThemeContextValue = {
    theme: theme as 'light' | 'dark' | 'system',
    setTheme: handleThemeChange,
    resolvedTheme: (resolvedTheme as 'light' | 'dark') || detectSystemTheme(),
    config: themeConfigs,
    isHydrating,
    systemTheme: systemTheme as 'light' | 'dark' | undefined,
  };

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return (
      <div className="theme-loading">
        {children}
      </div>
    );
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

export function EnhancedThemeProvider({
  children,
  attribute = 'data-theme',
  defaultTheme = 'light',
  enableSystem = true,
  disableTransitionOnChange = false,
  storageKey = 'theme',
}: EnhancedThemeProviderProps) {
  return (
    <NextThemeProvider
      attribute={attribute as any}
      defaultTheme={defaultTheme}
      enableSystem={enableSystem}
      disableTransitionOnChange={disableTransitionOnChange}
      storageKey={storageKey}
    >
      <ThemeContextProvider>
        {children}
      </ThemeContextProvider>
    </NextThemeProvider>
  );
}

export function useEnhancedTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useEnhancedTheme must be used within an EnhancedThemeProvider');
  }
  return context;
}

// Re-export next-themes hook for backward compatibility
export { useTheme } from 'next-themes';