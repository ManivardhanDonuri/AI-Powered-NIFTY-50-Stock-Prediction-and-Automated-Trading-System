'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, XCircle, Info, X, AlertTriangle } from 'lucide-react';
import Button from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import { forwardRef } from 'react';
import { AlertProps as BaseAlertProps } from '@/types/theme';

interface AlertProps {
  variant: 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  title?: string;
  message: string;
  children?: React.ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
  icon?: React.ReactNode;
  className?: string;
  'data-testid'?: string;
}

const Alert = forwardRef<HTMLDivElement, AlertProps>(({
  variant = 'info',
  size = 'md',
  title,
  message,
  dismissible = false,
  onDismiss,
  className = '',
  children
}, ref) => {
  const icons = {
    success: CheckCircle,
    warning: AlertTriangle,
    error: XCircle,
    info: Info,
  };

  const getVariantStyles = (variant: string) => {
    const baseStyles = 'border transition-all duration-200 ease-in-out';
    
    switch (variant) {
      case 'success':
        return cn(
          baseStyles,
          'bg-[var(--color-success)]/8 border-[var(--color-success)]/25',
          'text-[var(--color-success)] [&_h4]:text-[var(--color-success)]',
          '[&_p]:text-[var(--color-success)]/80'
        );
      case 'warning':
        return cn(
          baseStyles,
          'bg-[var(--color-warning)]/8 border-[var(--color-warning)]/25',
          'text-[var(--color-warning)] [&_h4]:text-[var(--color-warning)]',
          '[&_p]:text-[var(--color-warning)]/80'
        );
      case 'error':
        return cn(
          baseStyles,
          'bg-[var(--color-error)]/8 border-[var(--color-error)]/25',
          'text-[var(--color-error)] [&_h4]:text-[var(--color-error)]',
          '[&_p]:text-[var(--color-error)]/80'
        );
      case 'info':
      default:
        return cn(
          baseStyles,
          'bg-[var(--color-info)]/8 border-[var(--color-info)]/25',
          'text-[var(--color-info)] [&_h4]:text-[var(--color-info)]',
          '[&_p]:text-[var(--color-info)]/80'
        );
    }
  };

  const getSizeStyles = (size: string) => {
    switch (size) {
      case 'sm':
        return 'p-[var(--spacing-sm)] rounded-[var(--radius-md)] text-xs';
      case 'lg':
        return 'p-[var(--spacing-lg)] rounded-[var(--radius-xl)] text-base';
      case 'md':
      default:
        return 'p-[var(--spacing-md)] rounded-[var(--radius-lg)] text-sm';
    }
  };

  const getIconSize = (size: string) => {
    switch (size) {
      case 'sm':
        return 'w-4 h-4';
      case 'lg':
        return 'w-6 h-6';
      case 'md':
      default:
        return 'w-5 h-5';
    }
  };

  const Icon = icons[variant];

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (dismissible && onDismiss && (e.key === 'Escape')) {
      onDismiss();
    }
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: -10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
      tabIndex={dismissible ? 0 : -1}
      onKeyDown={handleKeyDown}
      className={cn(
        'flex items-start relative focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/50 focus:ring-offset-2 focus:ring-offset-[var(--color-background)]',
        getVariantStyles(variant),
        getSizeStyles(size),
        className
      )}
    >
      <div className="flex-shrink-0 mt-0.5">
        <Icon 
          className={cn(
            'flex-shrink-0',
            getIconSize(size)
          )} 
          aria-hidden="true"
        />
      </div>
      
      <div className="flex-1 ml-3 min-w-0">
        {title && (
          <h4 className={cn(
            'font-semibold mb-1 leading-tight',
            size === 'sm' ? 'text-xs' : size === 'lg' ? 'text-base' : 'text-sm'
          )}>
            {title}
          </h4>
        )}
        <div className={cn(
          'leading-relaxed',
          size === 'sm' ? 'text-xs' : size === 'lg' ? 'text-sm' : 'text-sm'
        )}>
          {children ? children : <p>{message}</p>}
        </div>
      </div>
      
      {dismissible && onDismiss && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onDismiss}
          className={cn(
            'ml-3 flex-shrink-0 text-current hover:bg-current/10 focus:bg-current/10',
            'transition-colors duration-150 ease-in-out',
            size === 'sm' ? 'p-1' : 'p-1.5'
          )}
          aria-label="Dismiss alert"
        >
          <X className={cn(
            size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'
          )} />
        </Button>
      )}
    </motion.div>
  );
});

Alert.displayName = 'Alert';

export default Alert;