// Simple class name utility without external dependencies
export function cn(...inputs: (string | undefined | null | false)[]): string {
  return inputs.filter(Boolean).join(' ');
}

// Theme-aware class name utilities
export const themeClasses = {
  // Background classes
  background: 'bg-[var(--color-background)]',
  surface: 'bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)]',
  card: 'bg-[var(--color-card-background)] border-[var(--color-card-border)]',
  
  // Text classes
  textPrimary: 'text-[var(--color-text-primary)]',
  textSecondary: 'text-[var(--color-text-secondary)]',
  textMuted: 'text-[var(--color-text-muted)]',
  
  // Border classes
  border: 'border-[var(--color-border)] hover:border-[var(--color-border-hover)]',
  borderFocus: 'focus:border-[var(--color-input-border-focus)]',
  
  // Button variants
  buttonPrimary: 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-[var(--color-primary-foreground)]',
  buttonSecondary: 'bg-[var(--color-secondary)] hover:bg-[var(--color-secondary-hover)] text-[var(--color-secondary-foreground)]',
  buttonOutline: 'border border-[var(--color-border)] hover:bg-[var(--color-surface)] text-[var(--color-text-primary)]',
  buttonGhost: 'hover:bg-[var(--color-surface)] text-[var(--color-text-primary)]',
  buttonDanger: 'bg-[var(--color-error)] hover:bg-[var(--color-error-hover)] text-[var(--color-error-foreground)]',
  
  // Status colors
  success: 'bg-[var(--color-success)] text-[var(--color-success-foreground)]',
  warning: 'bg-[var(--color-warning)] text-[var(--color-warning-foreground)]',
  error: 'bg-[var(--color-error)] text-[var(--color-error-foreground)]',
  info: 'bg-[var(--color-info)] text-[var(--color-info-foreground)]',
  
  // Input classes
  input: 'bg-[var(--color-input-background)] border-[var(--color-input-border)] focus:border-[var(--color-input-border-focus)] placeholder:text-[var(--color-input-placeholder)]',
  
  // Shadow classes
  shadowSm: 'shadow-[var(--shadow-sm)]',
  shadowMd: 'shadow-[var(--shadow-md)]',
  shadowLg: 'shadow-[var(--shadow-lg)]',
  shadowXl: 'shadow-[var(--shadow-xl)]',
} as const;