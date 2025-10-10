'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, X, CheckCircle, AlertTriangle, Info, XCircle, TrendingUp, DollarSign, AlertCircle, Brain, Settings } from 'lucide-react';
import { notificationService, NotificationData } from '@/services/notifications';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { cn } from '@/utils/cn';

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState<NotificationData[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const unsubscribe = notificationService.subscribe((newNotifications) => {
      setNotifications(newNotifications);
      setUnreadCount(newNotifications.length);
    });

    // Get initial notifications
    setNotifications(notificationService.getNotifications());

    return unsubscribe;
  }, []);

  const getIcon = (type: string, severity: string) => {
    // First check by type for specific icons
    switch (type) {
      case 'signal':
        return <TrendingUp className="w-5 h-5 text-[var(--color-primary)]" />;
      case 'trade':
        return <DollarSign className="w-5 h-5 text-[var(--color-success)]" />;
      case 'training':
        return <Brain className="w-5 h-5 text-[var(--color-info)]" />;
      case 'system':
        return <Settings className="w-5 h-5 text-[var(--color-secondary)]" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-[var(--color-error)]" />;
      default:
        // Fallback to severity-based icons
        switch (severity) {
          case 'success':
            return <CheckCircle className="w-5 h-5 text-[var(--color-success)]" />;
          case 'warning':
            return <AlertTriangle className="w-5 h-5 text-[var(--color-warning)]" />;
          case 'error':
            return <XCircle className="w-5 h-5 text-[var(--color-error)]" />;
          default:
            return <Info className="w-5 h-5 text-[var(--color-info)]" />;
        }
    }
  };

  const getNotificationStyles = (type: string, severity: string) => {
    // Enhanced theme-aware styling with proper contrast ratios
    const baseStyles = 'border-l-4 transition-all duration-200 ease-in-out hover:shadow-[var(--shadow-md)]';
    
    switch (severity) {
      case 'success':
        return cn(
          baseStyles,
          'border-l-[var(--color-success)] bg-[var(--color-success)]/5',
          'hover:bg-[var(--color-success)]/10'
        );
      case 'warning':
        return cn(
          baseStyles,
          'border-l-[var(--color-warning)] bg-[var(--color-warning)]/5',
          'hover:bg-[var(--color-warning)]/10'
        );
      case 'error':
        return cn(
          baseStyles,
          'border-l-[var(--color-error)] bg-[var(--color-error)]/5',
          'hover:bg-[var(--color-error)]/10'
        );
      case 'info':
      default:
        return cn(
          baseStyles,
          'border-l-[var(--color-info)] bg-[var(--color-info)]/5',
          'hover:bg-[var(--color-info)]/10'
        );
    }
  };

  const getSeverityBadgeStyles = (severity: string) => {
    const baseStyles = 'text-xs font-medium px-2 py-1 rounded-[var(--radius-sm)] border';
    
    switch (severity) {
      case 'success':
        return cn(
          baseStyles,
          'bg-[var(--color-success)]/10 text-[var(--color-success)] border-[var(--color-success)]/20'
        );
      case 'warning':
        return cn(
          baseStyles,
          'bg-[var(--color-warning)]/10 text-[var(--color-warning)] border-[var(--color-warning)]/20'
        );
      case 'error':
        return cn(
          baseStyles,
          'bg-[var(--color-error)]/10 text-[var(--color-error)] border-[var(--color-error)]/20'
        );
      case 'info':
      default:
        return cn(
          baseStyles,
          'bg-[var(--color-info)]/10 text-[var(--color-info)] border-[var(--color-info)]/20'
        );
    }
  };

  const clearNotifications = () => {
    notificationService.clearNotifications();
    setUnreadCount(0);
  };

  const formatTime = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
    return timestamp.toLocaleDateString();
  };

  return (
    <div className="relative">
      {/* Notification Bell */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 bg-[var(--color-error)] text-white text-xs rounded-full min-w-[20px] h-5 flex items-center justify-center font-medium shadow-sm border-2 border-[var(--color-background)]"
            style={{
              backgroundColor: 'var(--color-error)',
              color: 'white',
              fontSize: '11px',
              lineHeight: '1',
            }}
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </motion.div>
        )}
      </Button>

      {/* Notification Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />

            {/* Panel */}
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              className="absolute right-0 top-12 w-96 z-50 max-h-96 overflow-hidden"
            >
              <Card variant="elevated" padding="none" className="shadow-[var(--shadow-xl)]">
                {/* Header */}
                <div className="flex items-center justify-between p-[var(--spacing-md)] border-b border-[var(--color-border)]">
                  <h3 className="font-semibold text-[var(--color-text-primary)]">
                    Notifications ({notifications.length})
                  </h3>
                  <div className="flex items-center space-x-2">
                    {notifications.length > 0 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={clearNotifications}
                        className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
                      >
                        Clear all
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsOpen(false)}
                      className="text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Notifications List */}
                <div className="max-h-80 overflow-y-auto" role="list" aria-label="Notifications">
                  {notifications.length === 0 ? (
                    <div className="p-8 text-center text-[var(--color-text-muted)]">
                      <Bell className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p className="text-sm">No notifications yet</p>
                      <p className="text-xs mt-1 opacity-75">You'll see trading signals and system updates here</p>
                    </div>
                  ) : (
                    <div className="space-y-0">
                      {notifications.map((notification, index) => (
                        <motion.div
                          key={`${notification.timestamp.getTime()}-${index}`}
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className={cn(
                            'p-[var(--spacing-md)] border-b border-[var(--color-border)] last:border-b-0 cursor-pointer',
                            getNotificationStyles(notification.type, notification.severity)
                          )}
                          role="listitem"
                          tabIndex={0}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              // Handle notification click/selection
                              e.preventDefault();
                            }
                          }}
                        >
                          <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0 mt-0.5">
                              {getIcon(notification.type, notification.severity)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between gap-2">
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                    <h4 className="text-sm font-semibold text-[var(--color-text-primary)] truncate">
                                      {notification.title}
                                    </h4>
                                    <span className={getSeverityBadgeStyles(notification.severity)}>
                                      {notification.severity.toUpperCase()}
                                    </span>
                                  </div>
                                  <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                                    {notification.message}
                                  </p>
                                </div>
                                <span className="text-xs text-[var(--color-text-muted)] flex-shrink-0 mt-0.5">
                                  {formatTime(notification.timestamp)}
                                </span>
                              </div>
                              {(notification.symbol || notification.price) && (
                                <div className="flex items-center gap-2 mt-3 pt-2 border-t border-[var(--color-border)]/50">
                                  {notification.symbol && (
                                    <span className="text-xs bg-[var(--color-surface)] text-[var(--color-text-secondary)] px-2 py-1 rounded-[var(--radius-sm)] border border-[var(--color-border)]">
                                      📊 {notification.symbol}
                                    </span>
                                  )}
                                  {notification.price && (
                                    <span className="text-xs bg-[var(--color-primary)]/10 text-[var(--color-primary)] px-2 py-1 rounded-[var(--radius-sm)] border border-[var(--color-primary)]/20 font-medium">
                                      💰 ₹{notification.price.toFixed(2)}
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}