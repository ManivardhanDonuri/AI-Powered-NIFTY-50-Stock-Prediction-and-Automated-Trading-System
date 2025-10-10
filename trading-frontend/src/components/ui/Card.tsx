'use client';

import { forwardRef } from 'react';
import { cn } from '@/utils/cn';
import { CardProps } from '@/types/theme';

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ children, variant = 'default', padding = 'md', className = '', ...props }, ref) => {
    const baseClasses = [
      'bg-[var(--color-card-background)]',
      'transition-all duration-200 ease-in-out',
      'overflow-hidden'
    ].join(' ');
    
    const variants = {
      default: [
        'border border-[var(--color-card-border)]',
        'rounded-[var(--radius-xl)]',
        'shadow-[var(--shadow-sm)]'
      ].join(' '),
      
      elevated: [
        'border border-[var(--color-card-border)]',
        'rounded-[var(--radius-xl)]',
        'shadow-[var(--shadow-lg)]',
        'hover:shadow-[var(--shadow-xl)]'
      ].join(' '),
      
      outlined: [
        'border-2 border-[var(--color-border)]',
        'rounded-[var(--radius-xl)]',
        'shadow-none',
        'hover:border-[var(--color-border-hover)]'
      ].join(' ')
    };

    const paddings = {
      none: '',
      sm: 'p-[var(--spacing-md)]',
      md: 'p-[var(--spacing-lg)]',
      lg: 'p-[var(--spacing-xl)]',
    };

    const classes = cn(baseClasses, variants[variant], paddings[padding], className);

    return (
      <div ref={ref} className={classes} {...props}>
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

export default Card;