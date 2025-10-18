'use client';

import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, Loader2, AlertCircle, Wifi } from 'lucide-react';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';

interface ChatMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant';
  timestamp: Date;
  metadata?: {
    confidence?: number;
    cached?: boolean;
    responseTime?: number;
  };
}

interface ChatInterfaceProps {
  userId?: string;
  conversationId?: string;
  contextType?: string;
  className?: string;
  onConversationChange?: (conversationId: string) => void;
}

// Simple MessageBubble component with explicit theme colors
const MessageBubble: React.FC<{ message: ChatMessage; isUser: boolean }> = ({ message, isUser }) => (
  <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
    <div 
      className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
      style={{
        backgroundColor: isUser ? '#3b82f6' : 'var(--color-surface-secondary)',
        color: isUser ? 'white' : 'var(--color-text-primary)'
      }}
    >
      {isUser ? '👤' : '🤖'}
    </div>
    <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : 'text-left'}`}>
      <div 
        className={`inline-block p-3 rounded-lg ${isUser ? 'rounded-br-sm' : 'rounded-bl-sm'}`}
        style={{
          backgroundColor: isUser ? '#3b82f6' : 'var(--color-surface-secondary)',
          color: isUser ? 'white' : 'var(--color-text-primary)',
          border: isUser ? 'none' : '1px solid var(--color-border)'
        }}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap font-medium">{message.content}</p>
        {!isUser && message.metadata && (
          <div 
            className="mt-2 pt-2 text-xs"
            style={{
              borderTop: '1px solid var(--color-border)',
              color: 'var(--color-text-secondary)'
            }}
          >
            {message.metadata.confidence && (
              <span className="font-semibold">Confidence: {(message.metadata.confidence * 100).toFixed(0)}%</span>
            )}
            {message.metadata.cached && (
              <span className="ml-2 px-2 py-1 rounded font-semibold bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200">
                Cached
              </span>
            )}
            {message.metadata.responseTime && (
              <span className="ml-2 font-semibold">{message.metadata.responseTime.toFixed(2)}s</span>
            )}
          </div>
        )}
      </div>
      <div 
        className={`text-xs mt-1 font-medium ${isUser ? 'text-right' : 'text-left'}`}
        style={{ color: 'var(--color-text-secondary)' }}
      >
        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  </div>
);

// Simple QuickActions component with explicit colors for light/dark mode
const QuickActions: React.FC<{ onActionSelect: (action: string) => void }> = ({ onActionSelect }) => (
  <div className="space-y-2">
    <p className="text-sm font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>Try asking:</p>
    <div className="grid grid-cols-1 gap-2">
      {[
        "How is my portfolio performing?",
        "What's the current market outlook?",
        "Explain my recent trading signals",
        "What are my risk exposures?"
      ].map((suggestion, index) => (
        <button
          key={index}
          onClick={() => onActionSelect(suggestion)}
          className="text-left p-3 text-sm font-medium rounded-lg transition-colors border"
          style={{
            color: 'var(--color-text-primary)',
            backgroundColor: 'var(--color-surface-secondary)',
            borderColor: 'var(--color-border)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--color-surface-secondary)';
          }}
        >
          {suggestion}
        </button>
      ))}
    </div>
  </div>
);

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  userId = 'default-user',
  conversationId,
  contextType = 'general',
  className = '',
  onConversationChange
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Send message to API
  const sendMessageToAPI = async (message: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          conversation_id: conversationId,
          context_type: contextType
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return {
          id: data.messageId,
          content: data.content,
          type: 'assistant' as const,
          timestamp: new Date(data.timestamp),
          metadata: {
            confidence: data.confidence,
            cached: data.cached,
            responseTime: data.responseTime
          }
        };
      } else {
        throw new Error(`API Error: ${response.status}`);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  };

  // Handle sending message
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const content = inputMessage.trim();
    setInputMessage('');
    setError(null);

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      content,
      type: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);

    try {
      // Get AI response
      const aiMessage = await sendMessageToAPI(content);
      setMessages(prev => [...prev, aiMessage]);

      // Update conversation ID if provided
      if (aiMessage.id && onConversationChange) {
        onConversationChange(aiMessage.id);
      }
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        content: 'Sorry, I encountered an error. Please try again.',
        type: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setError('Failed to get response from AI assistant');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle key press
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle quick action selection
  const handleQuickAction = (action: string) => {
    setInputMessage(action);
    inputRef.current?.focus();
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <Card className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 border-b"
        style={{
          borderColor: 'var(--color-border)',
          backgroundColor: 'var(--color-surface-secondary)'
        }}
      >
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-blue-500" />
          <h3 
            className="font-bold"
            style={{ color: 'var(--color-text-primary)' }}
          >
            AI Trading Assistant
          </h3>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <Wifi className="w-4 h-4 text-green-500" />
          <span className="font-semibold text-green-700 dark:text-green-300">Connected</span>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-100 dark:bg-red-900/30 border-b border-red-300 dark:border-red-700 p-3">
          <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm font-semibold">{error}</span>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <MessageCircle 
              className="w-12 h-12 mx-auto mb-4" 
              style={{ color: 'var(--color-text-secondary)' }}
            />
            <p 
              className="text-lg font-semibold mb-2"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Welcome to AI Trading Assistant
            </p>
            <p 
              className="text-sm font-medium"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Ask me anything about your portfolio, market conditions, or trading signals.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                isUser={message.type === 'user'}
              />
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
                  🤖
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
                <span className="text-sm font-semibold">AI is thinking...</span>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {messages.length === 0 && (
        <div className="px-4 pb-4">
          <QuickActions onActionSelect={handleQuickAction} />
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me about your trading..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            size="sm"
            className="px-3"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default ChatInterface;