'use client';

import { useEffect, useState } from 'react';
import { useEnhancedTheme } from '@/components/providers/ThemeProvider';

export default function ThemeDebug() {
  let theme = 'unknown';
  let resolvedTheme = 'unknown';
  let systemTheme = 'unknown';
  
  try {
    const themeContext = useEnhancedTheme();
    theme = themeContext.theme;
    resolvedTheme = themeContext.resolvedTheme;
    systemTheme = themeContext.systemTheme || 'unknown';
  } catch (error) {
    // Theme provider not available
  }
  const [domTheme, setDomTheme] = useState<string>('');
  const [domClass, setDomClass] = useState<string>('');
  const [computedBg, setComputedBg] = useState<string>('');
  const [computedColor, setComputedColor] = useState<string>('');

  useEffect(() => {
    const updateDomInfo = () => {
      if (typeof document !== 'undefined') {
        setDomTheme(document.documentElement.getAttribute('data-theme') || 'none');
        setDomClass(document.documentElement.className);
        
        const styles = getComputedStyle(document.documentElement);
        setComputedBg(styles.backgroundColor);
        setComputedColor(styles.color);
      }
    };

    updateDomInfo();
    const interval = setInterval(updateDomInfo, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div 
      className="fixed bottom-4 right-4 p-4 rounded-lg border text-xs font-mono z-50 max-w-xs"
      style={{
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
        color: 'var(--color-text-primary)',
        boxShadow: 'var(--shadow-lg)',
      }}
    >
      <div className="font-bold mb-2">Theme Debug</div>
      <div>Theme: {theme}</div>
      <div>Resolved: {resolvedTheme}</div>
      <div>System: {systemTheme}</div>
      <div>DOM Theme: {domTheme}</div>
      <div>DOM Classes: {domClass}</div>
      <div>Computed BG: {computedBg}</div>
      <div>Computed Color: {computedColor}</div>
      <div className="mt-2 text-xs">
        CSS Vars:
        <div>--color-background: {typeof document !== 'undefined' ? getComputedStyle(document.documentElement).getPropertyValue('--color-background') : 'N/A'}</div>
        <div>--color-text-primary: {typeof document !== 'undefined' ? getComputedStyle(document.documentElement).getPropertyValue('--color-text-primary') : 'N/A'}</div>
      </div>
    </div>
  );
}