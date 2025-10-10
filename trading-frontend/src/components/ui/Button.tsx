'use client';

import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ButtonProps } from '@/types/theme';

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    variant = 'primary', 
    size = 'md', 
    loading = false, 
    children, 
    className = '', 
    disabled, 
    onClick, 
    type = 'button',
    icon 
  }, ref) => {
    const baseClasses = [
      'inline-flex items-center justify-center font-medium',
      'transition-all duration-200 ease-in-out',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
      'relative overflow-hidden'
    ].join(' ');
    
    const variants = {
      primary: [
        'bg-[var(--color-primary)] text-[var(--color-primary-foreground)]',
        'hover:bg-[var(--color-primary-hover)]',
        'focus:ring-[var(--color-primary)]',
        'shadow-[var(--shadow-md)] hover:shadow-[var(--shadow-lg)]',
        'border border-transparent'
      ].join(' '),
      
      secondary: [
        'bg-[var(--color-secondary)] text-[var(--color-secondary-foreground)]',
        'hover:bg-[var(--color-secondary-hover)]',
        'focus:ring-[var(--color-secondary)]',
        'shadow-[var(--shadow-sm)] hover:shadow-[var(--shadow-md)]',
        'border border-transparent'
      ].join(' '),
      
      outline: [
        'bg-transparent text-[var(--color-text-primary)]',
        'border border-[var(--color-border)]',
        'hover:bg-[var(--color-surface)] hover:border-[var(--color-border-hover)]',
        'focus:ring-[var(--color-accent)]',
        'shadow-none hover:shadow-[var(--shadow-sm)]'
      ].join(' '),
      
      ghost: [
        'bg-transparent text-[var(--color-text-primary)]',
        'border border-transparent',
        'hover:bg-[var(--color-surface)]',
        'focus:ring-[var(--color-accent)]',
        'shadow-none'
      ].join(' '),
      
      danger: [
        'bg-[var(--color-error)] text-[var(--color-error-foreground)]',
        'hover:bg-[var(--color-error-hover)]',
        'focus:ring-[var(--color-error)]',
        'shadow-[var(--shadow-md)] hover:shadow-[var(--shadow-lg)]',
        'border border-transparent'
      ].join(' ')
    };

    const sizes = {
      sm: [
        'px-3 py-1.5 text-sm',
        'rounded-[var(--radius-md)]',
        'min-h-[2rem]',
        'gap-1.5'
      ].join(' '),
      
      md: [
        'px-4 py-2 text-sm',
        'rounded-[var(--radius-md)]',
        'min-h-[2.5rem]',
        'gap-2'
      ].join(' '),
      
      lg: [
        'px-6 py-3 text-base',
        'rounded-[var(--radius-lg)]',
        'min-h-[3rem]',
        'gap-2'
      ].join(' ')
    };

    const iconSizes = {
      sm: 'w-4 h-4',
      md: 'w-4 h-4',
      lg: 'w-5 h-5'
    };

    const classes = cn(baseClasses, variants[variant], sizes[size], className);

    return (
      <motion.button
        ref={ref}
        whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
        whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
        className={classes}
        disabled={disabled || loading}
        onClick={onClick}
        type={type}
      >
        {loading && (
          <Loader2 className={cn('animate-spin', iconSizes[size])} />
        )}
        {!loading && icon && (
          <span className={iconSizes[size]}>{icon}</span>
        )}
        {children}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';

export default Button;