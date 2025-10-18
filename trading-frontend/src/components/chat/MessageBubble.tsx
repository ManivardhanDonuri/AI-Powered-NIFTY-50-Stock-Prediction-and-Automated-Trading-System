'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Check, CheckCheck, AlertCircle, Clock, Bot, User, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
// Inline type definition to avoid module resolution issues
interface ChatMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant' | 'system';
  timestamp: Date;
  status?: 'sending' | 'sent' | 'received' | 'error';
  metadata?: {
    confidence?: number;
    cached?: boolean;
    responseTime?: number;
  };
}

interface MessageBubbleProps {
  message: ChatMessage;
  isUser: boolean;
  onCopy?: (content: string) => void;
  onFeedback?: (messageId: string, feedback: 'positive' | 'negative') => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isUser,
  onCopy,
  onFeedback
}) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    onCopy?.(message.content);
  };
  
  const handleFeedback = (feedback: 'positive' | 'negative') => {
    onFeedback?.(message.id, feedback);
  };
  
  // Format timestamp
  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
  // Get status icon
  const getStatusIcon = () => {
    switch (message.status) {
      case 'sending':
        return <Clock className="w-3 h-3 text-gray-400" />;
      case 'sent':
        return <Check className="w-3 h-3 text-gray-400" />;
      case 'received':
        return <CheckCheck className="w-3 h-3 text-blue-500" />;
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-500" />;
      default:
        return null;
    }
  };
  
  // Parse message content for better formatting
  const formatContent = (content: string) => {
    // Split by double newlines for paragraphs
    const paragraphs = content.split('\n\n');
    
    return paragraphs.map((paragraph, index) => {
      // Check if paragraph contains bullet points or numbered lists
      const lines = paragraph.split('\n');
      
      if (lines.length > 1 && lines.some(line => 
        line.trim().match(/^[\d]+\./) || 
        line.trim().match(/^[•\-\*]/) ||
        line.trim().match(/^[\d]+\)/)
      )) {
        // This is a list
        return (
          <ul key={index} className="space-y-1 ml-4">
            {lines.map((line, lineIndex) => {
              const trimmed = line.trim();
              if (!trimmed) return null;
              
              // Remove list markers
              const cleanLine = trimmed.replace(/^[\d]+[\.\)]?\s*/, '').replace(/^[•\-\*]\s*/, '');
              
              return (
                <li key={lineIndex} className="text-sm leading-relaxed">
                  {cleanLine}
                </li>
              );
            })}
          </ul>
        );
      } else {
        // Regular paragraph
        return (
          <p key={index} className="text-sm leading-relaxed">
            {paragraph}
          </p>
        );
      }
    });
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-blue-500 text-white' 
          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
      }`}>
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>
      
      {/* Message Content */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : 'text-left'}`}>
        <div className={`inline-block p-3 rounded-lg ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-sm'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-sm'
        }`}>
          <div className="space-y-2">
            {formatContent(message.content)}
          </div>
          
          {/* AI Metadata */}
          {!isUser && message.metadata && (
            <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600 text-xs text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-2 flex-wrap">
                {message.metadata.confidence !== undefined && (
                  <span>Confidence: {(message.metadata.confidence * 100).toFixed(0)}%</span>
                )}
                {message.metadata.cached && (
                  <span className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-1 rounded">
                    Cached
                  </span>
                )}
                {message.metadata.responseTime && (
                  <span>{message.metadata.responseTime.toFixed(2)}s</span>
                )}
              </div>
            </div>
          )}
        </div>
        
        {/* Message Footer */}
        <div className={`flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400 ${
          isUser ? 'justify-end' : 'justify-start'
        }`}>
          <span>{formatTime(message.timestamp)}</span>
          
          {isUser && (
            <div className="flex items-center gap-1">
              {getStatusIcon()}
            </div>
          )}
          
          {/* Action Buttons for AI Messages */}
          {!isUser && (
            <div className="flex items-center gap-1 ml-2">
              <button
                onClick={handleCopy}
                className="h-6 w-6 p-0 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                title="Copy message"
              >
                <Copy className="w-3 h-3" />
              </button>
              
              <button
                onClick={() => handleFeedback('positive')}
                className="h-6 w-6 p-0 hover:bg-green-100 dark:hover:bg-green-900/30 hover:text-green-600 rounded text-gray-500 transition-colors"
                title="Good response"
              >
                <ThumbsUp className="w-3 h-3" />
              </button>
              
              <button
                onClick={() => handleFeedback('negative')}
                className="h-6 w-6 p-0 hover:bg-red-100 dark:hover:bg-red-900/30 hover:text-red-600 rounded text-gray-500 transition-colors"
                title="Poor response"
              >
                <ThumbsDown className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;