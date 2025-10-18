'use client';

import React from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import SimpleChatInterface from '@/components/chat/SimpleChatInterface';

const SimpleChatPage: React.FC = () => {
  return (
    <DashboardLayout>
      <div className="h-full p-6">
        <div className="max-w-4xl mx-auto h-full">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              AI Trading Assistant
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Get AI-powered insights about your portfolio, market conditions, and trading signals.
            </p>
          </div>
          
          <div className="h-[calc(100vh-200px)]">
            <SimpleChatInterface />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default SimpleChatPage;