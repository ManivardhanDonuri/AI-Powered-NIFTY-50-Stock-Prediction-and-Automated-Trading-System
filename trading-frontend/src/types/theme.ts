import React from 'react';

/**
 * Comprehensive color palette for theme system
 * All colors should be valid CSS color values (hex, rgb, hsl, etc.)
 */
export interface ThemeColors {
  /** Primary brand color used for main actions and highlights */
  primary: string;
  /** Hover state for primary color */
  primaryHover: string;
  /** Text color that contrasts well with primary background */
  primaryForeground: string;
  
  /** Secondary color for less prominent actions */
  secondary: string;
  /** Hover state for secondary color */
  secondaryHover: string;
  /** Text color that contrasts well with secondary background */
  secondaryForeground: string;
  
  /** Main background color for the application */
  background: string;
  /** Surface color for cards, modals, and elevated elements */
  surface: string;
  /** Hover state for surface elements */
  surfaceHover: string;
  
  /** Primary text color for main content */
  textPrimary: string;
  /** Secondary text color for less important content */
  textSecondary: string;
  /** Muted text color for placeholders and disabled states */
  textMuted: string;
  
  /** Default border color */
  border: string;
  /** Hover state for borders */
  borderHover: string;
  /** Accent color for highlights and focus states */
  accent: string;
  /** Hover state for accent color */
  accentHover: string;
  
  /** Success state color (green) */
  success: string;
  /** Hover state for success color */
  successHover: string;
  /** Text color that contrasts well with success background */
  successForeground: string;
  
  /** Warning state color (yellow/orange) */
  warning: string;
  /** Hover state for warning color */
  warningHover: string;
  /** Text color that contrasts well with warning background */
  warningForeground: string;
  
  /** Error state color (red) */
  error: string;
  /** Hover state for error color */
  errorHover: string;
  /** Text color that contrasts well with error background */
  errorForeground: string;
  
  /** Information state color (blue) */
  info: string;
  /** Hover state for info color */
  infoHover: string;
  /** Text color that contrasts well with info background */
  infoForeground: string;
  
  /** Background color for input fields */
  inputBackground: string;
  /** Border color for input fields */
  inputBorder: string;
  /** Border color for focused input fields */
  inputBorderFocus: string;
  /** Placeholder text color in input fields */
  inputPlaceholder: string;
  
  /** Background color for card components */
  cardBackground: string;
  /** Border color for card components */
  cardBorder: string;
  /** Shadow color for card components (rgba recommended) */
  cardShadow: string;
}

/**
 * Spacing scale for consistent layout and component spacing
 * Values should be in rem, px, or other valid CSS units
 */
export interface ThemeSpacing {
  /** Extra small spacing (0.25rem / 4px) */
  xs: string;
  /** Small spacing (0.5rem / 8px) */
  sm: string;
  /** Medium spacing (1rem / 16px) */
  md: string;
  /** Large spacing (1.5rem / 24px) */
  lg: string;
  /** Extra large spacing (2rem / 32px) */
  xl: string;
  /** 2x extra large spacing (3rem / 48px) */
  '2xl': string;
}

/**
 * Border radius scale for consistent rounded corners
 * Values should be in rem, px, or other valid CSS units
 */
export interface ThemeBorderRadius {
  /** Small border radius (0.375rem / 6px) */
  sm: string;
  /** Medium border radius (0.5rem / 8px) */
  md: string;
  /** Large border radius (0.75rem / 12px) */
  lg: string;
  /** Extra large border radius (1rem / 16px) */
  xl: string;
}

/**
 * Shadow scale for consistent elevation and depth
 * Values should be valid CSS box-shadow values
 */
export interface ThemeShadows {
  /** Small shadow for subtle elevation */
  sm: string;
  /** Medium shadow for moderate elevation */
  md: string;
  /** Large shadow for high elevation */
  lg: string;
  /** Extra large shadow for maximum elevation */
  xl: string;
}

/**
 * Animation and transition configuration
 */
export interface ThemeAnimations {
  /** Fast transition duration (0.15s) */
  fast: string;
  /** Normal transition duration (0.2s) */
  normal: string;
  /** Slow transition duration (0.3s) */
  slow: string;
  /** Ease-out timing function */
  easeOut: string;
  /** Ease-in-out timing function */
  easeInOut: string;
}

/**
 * Complete theme configuration containing all design tokens
 */
export interface ThemeConfig {
  /** Color palette for the theme */
  colors: ThemeColors;
  /** Spacing scale for layout and components */
  spacing: ThemeSpacing;
  /** Border radius scale for rounded corners */
  borderRadius: ThemeBorderRadius;
  /** Shadow scale for elevation effects */
  shadows: ThemeShadows;
  /** Animation and transition settings */
  animations: ThemeAnimations;
}

/**
 * Theme context value provided by ThemeProvider
 * Contains all theme-related state and configuration
 */
export interface ThemeContextValue {
  /** Current theme setting ('light', 'dark', or 'system') */
  theme: ThemeMode;
  /** Function to change the theme */
  setTheme: (theme: ThemeMode) => void;
  /** Resolved theme after system preference is applied */
  resolvedTheme: ResolvedTheme;
  /** Theme configurations for both light and dark modes */
  config: ThemeConfigs;
  /** Whether the theme is currently hydrating (SSR) */
  isHydrating?: boolean;
  /** System preference theme ('light' or 'dark') */
  systemTheme?: ResolvedTheme;
  /** Whether theme transitions are enabled */
  enableTransitions?: boolean;
}

// ============================================================================
// Theme Mode Types
// ============================================================================

/** Available theme modes */
export type ThemeMode = 'light' | 'dark' | 'system';

/** Resolved theme modes (system is resolved to light or dark) */
export type ResolvedTheme = 'light' | 'dark';

/** Theme configurations for both modes */
export interface ThemeConfigs {
  light: ThemeConfig;
  dark: ThemeConfig;
}

// ============================================================================
// Component Variant Types
// ============================================================================

/** Standard component variants used across the design system */
export type ComponentVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';

/** Standard component sizes used across the design system */
export type ComponentSize = 'sm' | 'md' | 'lg';

/** Button-specific variants */
export type ButtonVariant = ComponentVariant;

/** Card-specific variants */
export type CardVariant = 'default' | 'elevated' | 'outlined';

/** Input-specific variants */
export type InputVariant = 'default' | 'filled' | 'outlined';

/** Alert/notification variants */
export type AlertVariant = 'success' | 'warning' | 'error' | 'info';

/** Padding options for components */
export type PaddingSize = 'none' | 'sm' | 'md' | 'lg';

// ============================================================================
// Component Prop Interfaces
// ============================================================================

/**
 * Base props that all themed components should accept
 */
export interface BaseComponentProps {
  /** Additional CSS classes */
  className?: string;
  /** Inline styles */
  style?: React.CSSProperties;
  /** Test ID for testing */
  'data-testid'?: string;
}

/**
 * Props for components that support variants
 */
export interface VariantComponentProps extends BaseComponentProps {
  /** Component variant */
  variant?: ComponentVariant;
}

/**
 * Props for components that support sizing
 */
export interface SizedComponentProps extends BaseComponentProps {
  /** Component size */
  size?: ComponentSize;
}

/**
 * Props for components that support both variants and sizing
 */
export interface StyledComponentProps extends VariantComponentProps, SizedComponentProps {}

// ============================================================================
// Theme Utility Types
// ============================================================================

/**
 * CSS custom property names used in the theme system
 */
export type CSSCustomProperty = 
  | `--color-${keyof ThemeColors}`
  | `--spacing-${keyof ThemeSpacing}`
  | `--radius-${keyof ThemeBorderRadius}`
  | `--shadow-${keyof ThemeShadows}`
  | `--transition-${keyof ThemeAnimations}`;

/**
 * Theme-aware style object that can use CSS custom properties
 */
export interface ThemeAwareStyles {
  [key: string]: string | number | ThemeAwareStyles;
}

/**
 * Function type for creating theme-aware styles
 */
export type StyleFunction<T = ThemeAwareStyles> = (theme: ThemeConfig) => T;

// ============================================================================
// Component-Specific Interfaces
// ============================================================================

/**
 * Button component props with comprehensive typing
 */
export interface ButtonProps extends StyledComponentProps {
  /** Button variant */
  variant?: ButtonVariant;
  /** Button size */
  size?: ComponentSize;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Whether the button is in loading state */
  loading?: boolean;
  /** Icon to display in the button */
  icon?: React.ReactNode;
  /** Button content */
  children: React.ReactNode;
  /** Click handler */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  /** Button type */
  type?: 'button' | 'submit' | 'reset';
  /** Whether the button should take full width */
  fullWidth?: boolean;
}

/**
 * Card component props with comprehensive typing
 */
export interface CardProps extends BaseComponentProps {
  /** Card variant */
  variant?: CardVariant;
  /** Padding size */
  padding?: PaddingSize;
  /** Card content */
  children: React.ReactNode;
  /** Whether the card is clickable */
  clickable?: boolean;
  /** Click handler for clickable cards */
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void;
}

/**
 * Input component props with comprehensive typing
 */
export interface InputProps extends SizedComponentProps {
  /** Input variant */
  variant?: InputVariant;
  /** Input size */
  size?: ComponentSize;
  /** Error message */
  error?: string;
  /** Input label */
  label?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Whether the input is disabled */
  disabled?: boolean;
  /** Icon to display in the input */
  icon?: React.ReactNode;
  /** Input value */
  value?: string;
  /** Change handler */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Input type */
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  /** Whether the input is required */
  required?: boolean;
}

/**
 * Alert component props with comprehensive typing
 */
export interface AlertProps extends BaseComponentProps {
  /** Alert variant */
  variant: AlertVariant;
  /** Alert title */
  title?: string;
  /** Alert content */
  children: React.ReactNode;
  /** Whether the alert is dismissible */
  dismissible?: boolean;
  /** Dismiss handler */
  onDismiss?: () => void;
  /** Icon to display in the alert */
  icon?: React.ReactNode;
}