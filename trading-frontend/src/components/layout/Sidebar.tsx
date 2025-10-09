'use client';

import { useState } from 'react';
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
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
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
          fixed left-0 top-0 h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 z-50
          ${isMobile ? 'lg:relative' : 'relative'}
          ${collapsed && isMobile ? 'pointer-events-none' : ''}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <AnimatePresence mode="wait">
              {!collapsed && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                  className="flex items-center space-x-3"
                >
                  <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                      Trading System
                    </h1>
                    <p className="text-xs text-gray-500 dark:text-gray-400">ML Powered</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <button
              onClick={onToggle}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {collapsed ? (
                <Menu className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              ) : (
                <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              )}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {SIDEBAR_MENU_ITEMS.map((item) => {
              const Icon = iconMap[item.icon as keyof typeof iconMap];
              const isActive = pathname === item.href;

              return (
                <motion.button
                  key={item.id}
                  onClick={() => handleNavigation(item.href)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`
                    w-full flex items-center space-x-3 px-3 py-3 rounded-xl transition-all duration-200
                    ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }
                  `}
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
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <AnimatePresence>
              {!collapsed && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  transition={{ duration: 0.2 }}
                  className="text-center"
                >
                  <div className="w-12 h-12 bg-gradient-to-r from-green-400 to-blue-500 rounded-full mx-auto mb-2 flex items-center justify-center">
                    <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">System Online</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </>
  );
}