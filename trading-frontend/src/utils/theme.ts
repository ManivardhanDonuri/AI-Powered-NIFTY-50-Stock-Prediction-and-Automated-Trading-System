import { 
  ThemeConfig, 
  ThemeMode, 
  ResolvedTheme, 
  ThemeConfigs,
  CSSCustomProperty 
} from '@/types/theme';

/**
 * @fileoverview Theme utility functions and configurations
 * 
 * This module provides comprehensive theme management utilities including:
 * - Theme configurations for light and dark modes
 * - Theme persistence and detection utilities
 * - CSS custom property helpers
 * - SSR-safe theme handling
 * 
 * @author Trading Frontend Team
 * @version 1.0.0
 */

/**
 * Light theme configuration with comprehensive design tokens
 */
export const lightThemeConfig: ThemeConfig = {
  colors: {
    primary: '#2563eb',
    primaryHover: '#1d4ed8',
    primaryForeground: '#ffffff',
    secondary: '#64748b',
    secondaryHover: '#475569',
    secondaryForeground: '#ffffff',
    background: '#ffffff',
    surface: '#f8fafc',
    surfaceHover: '#f1f5f9',
    textPrimary: '#0f172a',
    textSecondary: '#475569',
    textMuted: '#94a3b8',
    border: '#e2e8f0',
    borderHover: '#cbd5e1',
    accent: '#3b82f6',
    accentHover: '#2563eb',
    success: '#10b981',
    successHover: '#059669',
    successForeground: '#ffffff',
    warning: '#f59e0b',
    warningHover: '#d97706',
    warningForeground: '#ffffff',
    error: '#ef4444',
    errorHover: '#dc2626',
    errorForeground: '#ffffff',
    info: '#3b82f6',
    infoHover: '#2563eb',
    infoForeground: '#ffffff',
    inputBackground: '#ffffff',
    inputBorder: '#d1d5db',
    inputBorderFocus: '#3b82f6',
    inputPlaceholder: '#9ca3af',
    cardBackground: '#ffffff',
    cardBorder: '#e5e7eb',
    cardShadow: 'rgba(0, 0, 0, 0.1)',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
  },
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  animations: {
    fast: '0.15s',
    normal: '0.2s',
    slow: '0.3s',
    easeOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.6, 1)',
  },
};

/**
 * Dark theme configuration with comprehensive design tokens
 */
export const darkThemeConfig: ThemeConfig = {
  colors: {
    primary: '#3b82f6',
    primaryHover: '#60a5fa',
    primaryForeground: '#ffffff',
    secondary: '#64748b',
    secondaryHover: '#94a3b8',
    secondaryForeground: '#ffffff',
    background: '#0f172a',
    surface: '#1e293b',
    surfaceHover: '#334155',
    textPrimary: '#f8fafc',
    textSecondary: '#cbd5e1',
    textMuted: '#64748b',
    border: '#334155',
    borderHover: '#475569',
    accent: '#60a5fa',
    accentHover: '#93c5fd',
    success: '#34d399',
    successHover: '#6ee7b7',
    successForeground: '#065f46',
    warning: '#fbbf24',
    warningHover: '#fcd34d',
    warningForeground: '#92400e',
    error: '#f87171',
    errorHover: '#fca5a5',
    errorForeground: '#991b1b',
    info: '#60a5fa',
    infoHover: '#93c5fd',
    infoForeground: '#1e3a8a',
    inputBackground: '#1e293b',
    inputBorder: '#475569',
    inputBorderFocus: '#60a5fa',
    inputPlaceholder: '#64748b',
    cardBackground: '#1e293b',
    cardBorder: '#334155',
    cardShadow: 'rgba(0, 0, 0, 0.3)',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
  },
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
  },
  animations: {
    fast: '0.15s',
    normal: '0.2s',
    slow: '0.3s',
    easeOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.6, 1)',
  },
};

/**
 * Complete theme configurations for both light and dark modes
 */
export const themeConfigs: ThemeConfigs = {
  light: lightThemeConfig,
  dark: darkThemeConfig,
};

// ============================================================================
// Theme Application Utilities
// ============================================================================

/**
 * Applies the specified theme to the document element
 * 
 * @param theme - The theme to apply ('light' or 'dark')
 * @throws {Error} When theme application fails
 * 
 * @example
 * ```typescript
 * applyThemeToDocument('dark');
 * ```
 */
export const applyThemeToDocument = (theme: ResolvedTheme): void => {
  if (typeof document !== 'undefined') {
    try {
      // Set data-theme attribute
      document.documentElement.setAttribute('data-theme', theme);
      
      // Add theme class for additional styling
      document.documentElement.classList.remove('theme-light', 'theme-dark');
      document.documentElement.classList.add(`theme-${theme}`);
      
      // Force style recalculation
      document.documentElement.style.setProperty('--force-recalc', Math.random().toString());
      
      // Dispatch custom event for other components to listen
      const themeChangeEvent = new CustomEvent('themeChange', {
        detail: { theme }
      });
      document.dispatchEvent(themeChangeEvent);
      
    } catch (error) {
      console.error('Failed to apply theme to document:', error);
    }
  }
};

/**
 * Gets the theme configuration for the specified theme
 * 
 * @param theme - The theme to get configuration for
 * @returns The theme configuration object
 * 
 * @example
 * ```typescript
 * const config = getThemeConfig('dark');
 * console.log(config.colors.primary); // '#3b82f6'
 * ```
 */
export const getThemeConfig = (theme: ResolvedTheme): ThemeConfig => {
  return themeConfigs[theme] || themeConfigs.light;
};

// ============================================================================
// Theme Persistence Utilities
// ============================================================================

/**
 * Retrieves the stored theme preference from localStorage
 * 
 * @returns The stored theme preference or null if not found/invalid
 * 
 * @example
 * ```typescript
 * const storedTheme = getStoredTheme();
 * if (storedTheme) {
 *   console.log('User prefers:', storedTheme);
 * }
 * ```
 */
export const getStoredTheme = (): ThemeMode | null => {
  if (typeof window === 'undefined') return null;
  
  try {
    const stored = localStorage.getItem('theme');
    if (stored && ['light', 'dark', 'system'].includes(stored)) {
      return stored as ThemeMode;
    }
  } catch (error) {
    console.warn('Failed to read theme from localStorage:', error);
  }
  
  return null;
};

/**
 * Stores the theme preference in localStorage
 * 
 * @param theme - The theme preference to store
 * 
 * @example
 * ```typescript
 * setStoredTheme('dark');
 * setStoredTheme('system'); // Removes from localStorage
 * ```
 */
export const setStoredTheme = (theme: ThemeMode): void => {
  if (typeof window === 'undefined') return;
  
  try {
    if (theme === 'system') {
      localStorage.removeItem('theme');
    } else {
      localStorage.setItem('theme', theme);
    }
  } catch (error) {
    console.warn('Failed to save theme to localStorage:', error);
  }
};

/**
 * Detects the system theme preference using media queries
 * 
 * @returns The system theme preference ('light' or 'dark')
 * 
 * @example
 * ```typescript
 * const systemTheme = detectSystemTheme();
 * console.log('System prefers:', systemTheme);
 * ```
 */
export const detectSystemTheme = (): ResolvedTheme => {
  if (typeof window === 'undefined') return 'light';
  
  try {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  } catch (error) {
    console.warn('Failed to detect system theme:', error);
    return 'light';
  }
};

/**
 * Gets the initial theme based on stored preference and system detection
 * 
 * @returns The resolved initial theme ('light' or 'dark')
 * 
 * @example
 * ```typescript
 * const initialTheme = getInitialTheme();
 * applyThemeToDocument(initialTheme);
 * ```
 */
export const getInitialTheme = (): ResolvedTheme => {
  const stored = getStoredTheme();
  
  if (stored === 'system' || !stored) {
    return detectSystemTheme();
  }
  
  return stored as ResolvedTheme;
};

// ============================================================================
// CSS Custom Property Utilities
// ============================================================================

/**
 * Gets the value of a CSS custom property from the document
 * 
 * @param property - The CSS custom property name (with or without --)
 * @returns The property value or empty string if not found
 * 
 * @example
 * ```typescript
 * const primaryColor = getCSSVariable('--color-primary');
 * const borderRadius = getCSSVariable('--radius-md');
 * ```
 */
export const getCSSVariable = (property: string): string => {
  if (typeof document !== 'undefined') {
    try {
      return getComputedStyle(document.documentElement).getPropertyValue(property).trim();
    } catch (error) {
      console.warn('Failed to get CSS variable:', property, error);
      return '';
    }
  }
  return '';
};

/**
 * Sets the value of a CSS custom property on the document
 * 
 * @param property - The CSS custom property name (with or without --)
 * @param value - The value to set
 * 
 * @example
 * ```typescript
 * setCSSVariable('--color-primary', '#ff0000');
 * setCSSVariable('--radius-md', '8px');
 * ```
 */
export const setCSSVariable = (property: string, value: string): void => {
  if (typeof document !== 'undefined') {
    try {
      document.documentElement.style.setProperty(property, value);
    } catch (error) {
      console.warn('Failed to set CSS variable:', property, error);
    }
  }
};

// ============================================================================
// Theme Validation Utilities
// ============================================================================

/**
 * Type guard to check if a string is a valid theme mode
 * 
 * @param theme - The string to validate
 * @returns True if the theme is valid
 * 
 * @example
 * ```typescript
 * if (isValidTheme(userInput)) {
 *   setTheme(userInput);
 * }
 * ```
 */
export const isValidTheme = (theme: string): theme is ThemeMode => {
  return ['light', 'dark', 'system'].includes(theme);
};

/**
 * Sanitizes a theme string to ensure it's valid, with fallback
 * 
 * @param theme - The theme string to sanitize
 * @returns A valid theme mode, defaulting to 'light' if invalid
 * 
 * @example
 * ```typescript
 * const safeTheme = sanitizeTheme(untrustedInput);
 * setTheme(safeTheme); // Always safe to use
 * ```
 */
export const sanitizeTheme = (theme: string): ThemeMode => {
  return isValidTheme(theme) ? theme : 'light';
};

// ============================================================================
// SSR-Safe Theme Utilities
// ============================================================================

/**
 * Gets a theme that's safe for server-side rendering
 * Always returns 'light' on server to prevent hydration mismatches
 * 
 * @returns A resolved theme safe for SSR
 * 
 * @example
 * ```typescript
 * // In a component that renders on server
 * const ssrTheme = getSSRSafeTheme();
 * ```
 */
export const getSSRSafeTheme = (): ResolvedTheme => {
  // Always return light for SSR to prevent hydration mismatch
  if (typeof window === 'undefined') return 'light';
  
  return getInitialTheme();
};

// ============================================================================
// Advanced Theme Utilities
// ============================================================================

/**
 * Creates a type-safe CSS custom property name
 * 
 * @param category - The property category (color, spacing, etc.)
 * @param name - The property name
 * @returns A properly formatted CSS custom property name
 * 
 * @example
 * ```typescript
 * const primaryColorVar = createCSSProperty('color', 'primary');
 * // Returns: '--color-primary'
 * ```
 */
export const createCSSProperty = (
  category: 'color' | 'spacing' | 'radius' | 'shadow' | 'transition',
  name: string
): string => {
  return `--${category}-${name}`;
};

/**
 * Gets multiple CSS variables at once
 * 
 * @param properties - Array of CSS custom property names
 * @returns Object with property names as keys and values as values
 * 
 * @example
 * ```typescript
 * const colors = getCSSVariables(['--color-primary', '--color-secondary']);
 * // Returns: { '--color-primary': '#2563eb', '--color-secondary': '#64748b' }
 * ```
 */
export const getCSSVariables = (properties: string[]): Record<string, string> => {
  const result: Record<string, string> = {};
  
  properties.forEach(property => {
    result[property] = getCSSVariable(property);
  });
  
  return result;
};

/**
 * Sets multiple CSS variables at once
 * 
 * @param variables - Object with property names as keys and values as values
 * 
 * @example
 * ```typescript
 * setCSSVariables({
 *   '--color-primary': '#ff0000',
 *   '--color-secondary': '#00ff00'
 * });
 * ```
 */
export const setCSSVariables = (variables: Record<string, string>): void => {
  Object.entries(variables).forEach(([property, value]) => {
    setCSSVariable(property, value);
  });
};

/**
 * Resolves a theme mode to its actual theme (handles 'system')
 * 
 * @param themeMode - The theme mode to resolve
 * @returns The resolved theme ('light' or 'dark')
 * 
 * @example
 * ```typescript
 * const resolved = resolveThemeMode('system');
 * // Returns: 'dark' (if system preference is dark)
 * ```
 */
export const resolveThemeMode = (themeMode: ThemeMode): ResolvedTheme => {
  if (themeMode === 'system') {
    return detectSystemTheme();
  }
  return themeMode;
};

/**
 * Creates a theme-aware style object with CSS custom properties
 * 
 * @param styles - Style object with theme-aware values
 * @returns CSS-in-JS compatible style object
 * 
 * @example
 * ```typescript
 * const buttonStyles = createThemeAwareStyles({
 *   backgroundColor: 'var(--color-primary)',
 *   color: 'var(--color-primary-foreground)',
 *   borderRadius: 'var(--radius-md)'
 * });
 * ```
 */
export const createThemeAwareStyles = (
  styles: Record<string, string | number>
): React.CSSProperties => {
  return styles as React.CSSProperties;
};

/**
 * Checks if the current environment supports CSS custom properties
 * 
 * @returns True if CSS custom properties are supported
 * 
 * @example
 * ```typescript
 * if (supportsCSSCustomProperties()) {
 *   // Use modern theme system
 * } else {
 *   // Fallback to static styles
 * }
 * ```
 */
export const supportsCSSCustomProperties = (): boolean => {
  if (typeof window === 'undefined') return false;
  
  try {
    return window.CSS && window.CSS.supports && window.CSS.supports('color', 'var(--test)');
  } catch (error) {
    return false;
  }
};

/**
 * Validates a complete theme configuration
 * 
 * @param config - The theme configuration to validate
 * @returns True if the configuration is valid
 * 
 * @example
 * ```typescript
 * if (validateThemeConfig(userThemeConfig)) {
 *   applyCustomTheme(userThemeConfig);
 * }
 * ```
 */
export const validateThemeConfig = (config: Partial<ThemeConfig>): config is ThemeConfig => {
  const requiredSections = ['colors', 'spacing', 'borderRadius', 'shadows', 'animations'];
  
  return requiredSections.every(section => 
    config[section as keyof ThemeConfig] && 
    typeof config[section as keyof ThemeConfig] === 'object'
  );
};

/**
 * Merges theme configurations with proper type safety
 * 
 * @param baseConfig - The base theme configuration
 * @param overrides - The configuration overrides
 * @returns Merged theme configuration
 * 
 * @example
 * ```typescript
 * const customTheme = mergeThemeConfigs(lightThemeConfig, {
 *   colors: { primary: '#ff0000' }
 * });
 * ```
 */
export const mergeThemeConfigs = (
  baseConfig: ThemeConfig,
  overrides: Partial<ThemeConfig>
): ThemeConfig => {
  return {
    colors: { ...baseConfig.colors, ...overrides.colors },
    spacing: { ...baseConfig.spacing, ...overrides.spacing },
    borderRadius: { ...baseConfig.borderRadius, ...overrides.borderRadius },
    shadows: { ...baseConfig.shadows, ...overrides.shadows },
    animations: { ...baseConfig.animations, ...overrides.animations },
  };
};