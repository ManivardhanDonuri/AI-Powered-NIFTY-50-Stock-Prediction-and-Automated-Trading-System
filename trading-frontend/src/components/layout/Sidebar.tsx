'use client';


import { motion, AnimatePresence } from 'framer-motion';
import { usePathname, useRouter } from 'next/navigation';
import {
  Brain,
  History,
  PieChart,
  Settings,
  Power,
  Menu,
  X,
  TrendingUp,
  Activity,
} from 'lucide-react';
import { SIDEBAR_MENU_ITEMS } from '@/utils/constants';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  isMobile?: boolean;
}

const iconMap = {
  TrendingUp,
  History,
  PieChart,
  Settings,
  Power,
  Brain,
  Activity,
};

export default function Sidebar({ collapsed, onToggle, isMobile = false }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();

  const handleNavigation = (href: string) => {
    router.push(href);
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isMobile && !collapsed && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-40 lg:hidden"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{
          width: collapsed ? (isMobile ? 0 : 80) : 280,
          x: isMobile && collapsed ? -280 : 0,
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className={`
          fixed left-0 top-0 h-full border-r z-50 transition-colors duration-200
          ${isMobile ? 'lg:relative' : 'relative'}
          ${collapsed && isMobile ? 'pointer-events-none' : ''}
        `}
        style={{
          backgroundColor: 'var(--color-surface)',
          borderColor: 'var(--color-border)',
        }}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div 
            className="flex items-center justify-between p-4 border-b transition-colors duration-200"
            style={{ borderColor: 'var(--color-border)' }}
          >
            <AnimatePresence mode="wait">
              {!collapsed && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                  className="flex items-center space-x-3"
                >
                  <div 
                    className="flex items-center justify-center w-8 h-8 rounded-lg"
                    style={{
                      background: `linear-gradient(135deg, var(--color-primary), var(--color-accent))`,
                    }}
                  >
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h1 
                      className="text-lg font-bold"
                      style={{ color: 'var(--color-text-primary)' }}
                    >
                      Trading System
                    </h1>
                    <p 
                      className="text-xs"
                      style={{ color: 'var(--color-text-muted)' }}
                    >
                      ML Powered
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <button
              onClick={onToggle}
              className="p-2 rounded-lg transition-colors duration-200"
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              {collapsed ? (
                <Menu 
                  className="w-5 h-5" 
                  style={{ color: 'var(--color-text-secondary)' }}
                />
              ) : (
                <X 
                  className="w-5 h-5" 
                  style={{ color: 'var(--color-text-secondary)' }}
                />
              )}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {SIDEBAR_MENU_ITEMS.map((item) => {
              const Icon = iconMap[item.icon as keyof typeof iconMap] || Settings; // Fallback to Settings icon
              const isActive = pathname === item.href;

              return (
                <motion.button
                  key={item.id}
                  onClick={() => handleNavigation(item.href)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center space-x-3 px-3 py-3 rounded-xl transition-all duration-200"
                  style={{
                    backgroundColor: isActive 
                      ? 'var(--color-primary)' 
                      : 'transparent',
                    color: isActive 
                      ? 'var(--color-primary-foreground)' 
                      : 'var(--color-text-secondary)',
                    boxShadow: isActive ? 'var(--shadow-md)' : 'none',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                      e.currentTarget.style.color = 'var(--color-text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = 'var(--color-text-secondary)';
                    }
                  }}
                >
                  <Icon className={`w-5 h-5 ${collapsed ? 'mx-auto' : ''}`} />
                  <AnimatePresence>
                    {!collapsed && (
                      <motion.span
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.2 }}
                        className="font-medium"
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </motion.button>
              );
            })}
          </nav>

          {/* Footer */}
          <div 
            className="p-4 border-t transition-colors duration-200"
            style={{ borderColor: 'var(--color-border)' }}
          >
            <AnimatePresence>
              {!collapsed && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  transition={{ duration: 0.2 }}
                  className="text-center"
                >
                  <div 
                    className="w-12 h-12 rounded-full mx-auto mb-2 flex items-center justify-center"
                    style={{
                      background: `linear-gradient(135deg, var(--color-success), var(--color-accent))`,
                    }}
                  >
                    <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                  </div>
                  <p 
                    className="text-xs"
                    style={{ color: 'var(--color-text-muted)' }}
                  >
                    System Online
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </>
  );
}