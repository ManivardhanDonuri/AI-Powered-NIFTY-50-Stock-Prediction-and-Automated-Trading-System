import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import { EnhancedThemeProvider } from '@/components/providers/ThemeProvider';
import './globals.css';
import { APP_NAME, APP_DESCRIPTION } from '@/utils/constants';
import PWAInstall from '@/components/ui/PWAInstall';

import { Suspense } from 'react';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: APP_NAME,
  description: APP_DESCRIPTION,
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Trading System',
  },
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: '32x32', type: 'image/x-icon' },
      { url: '/icons/icon-192x192.png', sizes: '192x192', type: 'image/png' },
    ],
    apple: '/icons/icon-192x192.png',
    shortcut: '/favicon.ico',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#3b82f6',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('theme');
                  var systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                  var resolvedTheme = theme === 'system' || !theme ? systemTheme : theme;
                  
                  if (['light', 'dark'].includes(resolvedTheme)) {
                    document.documentElement.setAttribute('data-theme', resolvedTheme);
                    document.documentElement.classList.add('theme-' + resolvedTheme);
                    
                    // Force immediate style application
                    if (resolvedTheme === 'light') {
                      document.documentElement.style.backgroundColor = '#ffffff';
                      document.documentElement.style.color = '#0f172a';
                      document.body.style.backgroundColor = '#ffffff';
                      document.body.style.color = '#0f172a';
                    } else {
                      document.documentElement.style.backgroundColor = '#0f172a';
                      document.documentElement.style.color = '#f8fafc';
                      document.body.style.backgroundColor = '#0f172a';
                      document.body.style.color = '#f8fafc';
                    }
                  } else {
                    document.documentElement.setAttribute('data-theme', 'light');
                    document.documentElement.classList.add('theme-light');
                    document.documentElement.style.backgroundColor = '#ffffff';
                    document.documentElement.style.color = '#0f172a';
                    document.body.style.backgroundColor = '#ffffff';
                    document.body.style.color = '#0f172a';
                  }
                } catch (e) {
                  document.documentElement.setAttribute('data-theme', 'light');
                  document.documentElement.classList.add('theme-light');
                  document.documentElement.style.backgroundColor = '#ffffff';
                  document.documentElement.style.color = '#0f172a';
                  document.body.style.backgroundColor = '#ffffff';
                  document.body.style.color = '#0f172a';
                }
              })();
            `,
          }}
        />
      </head>
      <body className={`${inter.variable} font-sans antialiased`}>
        <EnhancedThemeProvider
          attribute="data-theme"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange={false}
          storageKey="theme"
        >
          {children}
          <Suspense fallback={null}>
            <PWAInstall />
          </Suspense>

        </EnhancedThemeProvider>
        
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                      console.log('SW registered: ', registration);
                    })
                    .catch(function(registrationError) {
                      console.log('SW registration failed: ', registrationError);
                    });
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
}
