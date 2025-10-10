'use client';

import { forwardRef } from 'react';
import { cn } from '@/utils/cn';
import { InputProps as BaseInputProps } from '@/types/theme';

interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  variant?: 'default' | 'filled' | 'outlined';
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    variant = 'default', 
    size = 'md',
    label, 
    error, 
    helperText, 
    icon, 
    iconPosition = 'left',
    className = '', 
    ...props 
  }, ref) => {
    const baseClasses = [
      'w-full transition-all duration-200 ease-in-out',
      'focus:outline-none focus:ring-2 focus:ring-offset-1',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'placeholder:text-[var(--color-input-placeholder)]'
    ].join(' ');
    
    const variants = {
      default: error ? [
        'bg-[var(--color-input-background)]',
        'border border-[var(--color-error)]',
        'text-[var(--color-text-primary)]',
        'focus:border-[var(--color-error)]',
        'focus:ring-[var(--color-error)]',
        'rounded-[var(--radius-md)]'
      ].join(' ') : [
        'bg-[var(--color-input-background)]',
        'border border-[var(--color-input-border)]',
        'text-[var(--color-text-primary)]',
        'focus:border-[var(--color-input-border-focus)]',
        'focus:ring-[var(--color-input-border-focus)]',
        'hover:border-[var(--color-border-hover)]',
        'rounded-[var(--radius-md)]'
      ].join(' '),
      
      filled: error ? [
        'bg-[var(--color-surface)]',
        'border border-transparent',
        'text-[var(--color-text-primary)]',
        'focus:border-[var(--color-error)]',
        'focus:ring-[var(--color-error)]',
        'rounded-[var(--radius-md)]'
      ].join(' ') : [
        'bg-[var(--color-surface)]',
        'border border-transparent',
        'text-[var(--color-text-primary)]',
        'focus:border-[var(--color-input-border-focus)]',
        'focus:ring-[var(--color-input-border-focus)]',
        'hover:bg-[var(--color-surface-hover)]',
        'rounded-[var(--radius-md)]'
      ].join(' '),
      
      outlined: error ? [
        'bg-transparent',
        'border-2 border-[var(--color-error)]',
        'text-[var(--color-text-primary)]',
        'focus:border-[var(--color-error)]',
        'focus:ring-[var(--color-error)]',
        'rounded-[var(--radius-md)]'
      ].join(' ') : [
        'bg-transparent',
        'border-2 border-[var(--color-border)]',
        'text-[var(--color-text-primary)]',
        'focus:border-[var(--color-input-border-focus)]',
        'focus:ring-[var(--color-input-border-focus)]',
        'hover:border-[var(--color-border-hover)]',
        'rounded-[var(--radius-md)]'
      ].join(' ')
    };

    const inputPadding = icon 
      ? iconPosition === 'left' 
        ? 'pl-10 pr-3 py-2.5' 
        : 'pl-3 pr-10 py-2.5'
      : 'px-3 py-2.5';

    const inputClasses = cn(baseClasses, variants[variant], inputPadding, className);

    const labelClasses = error 
      ? 'block text-sm font-medium text-[var(--color-error)] mb-1'
      : 'block text-sm font-medium text-[var(--color-text-secondary)] mb-1';

    const helperTextClasses = error
      ? 'text-sm text-[var(--color-error)] mt-1'
      : 'text-sm text-[var(--color-text-muted)] mt-1';

    return (
      <div className="space-y-0">
        {label && (
          <label className={labelClasses}>
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className={cn(
              'absolute inset-y-0 flex items-center pointer-events-none',
              'text-[var(--color-text-muted)]',
              iconPosition === 'left' ? 'left-3' : 'right-3'
            )}>
              <span className="w-4 h-4">{icon}</span>
            </div>
          )}
          <input
            ref={ref}
            className={inputClasses}
            {...props}
          />
        </div>
        {error && (
          <p className={helperTextClasses}>{error}</p>
        )}
        {helperText && !error && (
          <p className={helperTextClasses}>{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;