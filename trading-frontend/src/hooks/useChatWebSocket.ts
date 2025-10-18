'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { ConnectionStatus, WebSocketMessage, ChatWebSocketHookProps } from '@/types/chat';

export const useChatWebSocket = ({
  userId,
  onMessage,
  onConnectionChange,
  onError,
  autoReconnect = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5
}: ChatWebSocketHookProps) => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const reconnectAttemptsRef = useRef<number>(0);
  const messageQueueRef = useRef<WebSocketMessage[]>([]);
  
  // Get WebSocket URL
  const getWebSocketUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NODE_ENV === 'development' 
      ? 'localhost:8000' 
      : window.location.host;
    
    return `${protocol}//${host}/ws/chat/${userId}`;
  }, [userId]);
  
  // Update connection status
  const updateConnectionStatus = useCallback((status: ConnectionStatus) => {
    setConnectionStatus(status);
    setIsConnected(status === 'connected');
    onConnectionChange?.(status);
  }, [onConnectionChange]);
  
  // Handle WebSocket messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      onMessage?.(message);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
      onError?.('Failed to parse message from server');
    }
  }, [onMessage, onError]);
  
  // Handle WebSocket errors
  const handleError = useCallback((event: Event) => {
    console.error('WebSocket error:', event);
    onError?.('WebSocket connection error');
    updateConnectionStatus('error');
  }, [onError, updateConnectionStatus]);
  
  // Handle WebSocket close
  const handleClose = useCallback((event: CloseEvent) => {
    console.log('WebSocket closed:', event.code, event.reason);
    updateConnectionStatus('disconnected');
    
    // Attempt reconnection if enabled and not a normal closure
    if (autoReconnect && event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
      reconnectAttemptsRef.current += 1;
      
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
        connect();
      }, reconnectInterval);
    } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      onError?.('Maximum reconnection attempts reached');
    }
  }, [autoReconnect, maxReconnectAttempts, reconnectInterval, onError, updateConnectionStatus]);
  
  // Handle WebSocket open
  const handleOpen = useCallback(() => {
    console.log('WebSocket connected');
    updateConnectionStatus('connected');
    reconnectAttemptsRef.current = 0;
    
    // Send queued messages
    if (messageQueueRef.current.length > 0) {
      messageQueueRef.current.forEach(message => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify(message));
        }
      });
      messageQueueRef.current = [];
    }
  }, [updateConnectionStatus]);
  
  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }
    
    updateConnectionStatus('connecting');
    
    try {
      const wsUrl = getWebSocketUrl();
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = handleOpen;
      wsRef.current.onmessage = handleMessage;
      wsRef.current.onerror = handleError;
      wsRef.current.onclose = handleClose;
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      onError?.('Failed to establish connection');
      updateConnectionStatus('error');
    }
  }, [getWebSocketUrl, handleOpen, handleMessage, handleError, handleClose, updateConnectionStatus, onError]);
  
  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onerror = null;
      wsRef.current.onclose = null;
      
      if (wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close(1000, 'Normal closure');
      }
      
      wsRef.current = null;
    }
    
    updateConnectionStatus('disconnected');
    reconnectAttemptsRef.current = 0;
  }, [updateConnectionStatus]);
  
  // Send message
  const sendMessage = useCallback(async (message: WebSocketMessage): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        // Queue message if not connected
        messageQueueRef.current.push(message);
        
        if (!isConnected) {
          reject(new Error('WebSocket not connected'));
          return;
        }
      }
      
      try {
        wsRef.current?.send(JSON.stringify(message));
        resolve();
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
        reject(error);
      }
    });
  }, [isConnected]);
  
  // Reconnect manually
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setTimeout(connect, 1000);
  }, [disconnect, connect]);
  
  // Send ping to keep connection alive
  const sendPing = useCallback(() => {
    if (isConnected) {
      sendMessage({
        type: 'ping',
        data: { timestamp: new Date().toISOString() }
      }).catch(console.error);
    }
  }, [isConnected, sendMessage]);
  
  // Initialize connection on mount
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);
  
  // Set up ping interval to keep connection alive
  useEffect(() => {
    if (!isConnected) return;
    
    const pingInterval = setInterval(sendPing, 30000); // Ping every 30 seconds
    
    return () => {
      clearInterval(pingInterval);
    };
  }, [isConnected, sendPing]);
  
  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Page is hidden, reduce activity
        return;
      }
      
      // Page is visible, ensure connection is active
      if (!isConnected && autoReconnect) {
        reconnect();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isConnected, autoReconnect, reconnect]);
  
  return {
    connectionStatus,
    isConnected,
    sendMessage,
    connect,
    disconnect,
    reconnect,
    queuedMessages: messageQueueRef.current.length
  };
};