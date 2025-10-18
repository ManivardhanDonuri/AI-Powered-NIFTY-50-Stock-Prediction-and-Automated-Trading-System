/**
 * Chat-related type definitions
 */

export interface ChatMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant' | 'system';
  timestamp: Date;
  status?: 'sending' | 'sent' | 'received' | 'error';
  metadata?: {
    confidence?: number;
    cached?: boolean;
    responseTime?: number;
    tokenUsage?: {
      promptTokens: number;
      completionTokens: number;
      totalTokens: number;
    };
  };
}

export interface Conversation {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
  lastMessage?: {
    content: string;
    timestamp: Date;
    type: 'user' | 'assistant' | 'system';
  };
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: string;
  messageId?: string;
}

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface ChatWebSocketHookProps {
  userId: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnectionChange?: (status: ConnectionStatus) => void;
  onError?: (error: string) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export interface QuickActionSuggestion {
  id: string;
  text: string;
  category: string;
  description: string;
}

export interface AIInsight {
  type: 'portfolio' | 'market' | 'signal' | 'risk';
  title: string;
  summary: string;
  confidence: number;
  timestamp: Date;
  data?: any;
}

export interface ChatContextUpdate {
  contextType: string;
  contextData: any;
}

// API Response Types
export interface ChatMessageResponse {
  messageId: string;
  conversationId: string;
  content: string;
  timestamp: string;
  responseTime: number;
  cached: boolean;
  confidence: number;
}

export interface ConversationHistoryResponse {
  conversationId: string;
  messages: Array<{
    id: string;
    content: string;
    messageType: 'user' | 'assistant' | 'system';
    timestamp: string;
    metadata?: any;
  }>;
  totalMessages: number;
  createdAt: string;
  updatedAt: string;
}

export interface QuickActionsResponse {
  suggestions: QuickActionSuggestion[];
  contextType: string;
}