'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from './Sidebar';
import Header from './Header';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();

  // Handle mounting to prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  // Check if mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarCollapsed(true);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);



  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  // Get current page title from pathname
  const getPageTitle = () => {
    const pathMap: Record<string, string> = {
      '/live-charts': 'Live Charts Terminal',
      '/history': 'Trading History',
      '/portfolio': 'Portfolio',
      '/settings': 'Settings',
      '/system': 'System Control',
    };
    return pathMap[pathname] || 'Live Charts Terminal';
  };

  // Don't render until mounted to prevent hydration mismatch
  if (!mounted) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div 
      className="flex h-screen transition-colors duration-200"
      style={{
        backgroundColor: 'var(--color-background)',
        color: 'var(--color-text-primary)',
      }}
    >
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={handleSidebarToggle}
        isMobile={isMobile}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header
          title={getPageTitle()}
          onSidebarToggle={handleSidebarToggle}
        />

        {/* Page Content */}
        <main 
          className="flex-1 overflow-auto transition-colors duration-200"
          style={{
            backgroundColor: 'var(--color-surface)',
          }}
        >
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="h-full min-h-full"
            style={{
              backgroundColor: 'var(--color-surface)',
            }}
          >
            <div 
              className="h-full p-6"
              style={{
                backgroundColor: 'var(--color-surface)',
              }}
            >
              {children}
            </div>
          </motion.div>
        </main>
      </div>
    </div>
  );
}