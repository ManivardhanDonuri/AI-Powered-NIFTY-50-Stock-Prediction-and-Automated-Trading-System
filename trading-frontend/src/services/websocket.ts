import { io, Socket } from 'socket.io-client';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface PriceUpdate {
  symbol: string;
  price: number;
  change?: number;
  changePercent?: number;
  volume?: string;
  timestamp: string;
}

export interface TrainingProgress {
  modelId: string;
  epoch: number;
  totalEpochs: number;
  progress: number;
  loss: number;
  accuracy: number;
}

export interface TrainingComplete {
  modelId: string;
  symbol: string;
  modelType: string;
  accuracy: number;
  loss: number;
}

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  constructor() {
    // Only initialize connection in browser environment
    if (typeof window !== 'undefined') {
      // Delay connection to avoid immediate failures during SSR
      // Also check if API server is likely available before connecting
      setTimeout(() => this.checkServerAndConnect(), 2000);
    }
  }

  private async checkServerAndConnect() {
    try {
      // Try to ping the API server first
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003/api'}/health`.replace('/api/api', '/api'), {
        method: 'GET',
        timeout: 2000,
      } as any);
      
      if (response.ok) {
        console.log('API server is available, connecting WebSocket...');
        this.connect();
      } else {
        console.log('API server not available, skipping WebSocket connection');
        this.emit('connection_status', { 
          connected: false, 
          reason: 'API server not available' 
        });
      }
    } catch (error) {
      console.log('API server not available, skipping WebSocket connection');
      this.emit('connection_status', { 
        connected: false, 
        reason: 'API server not available' 
      });
    }
  }

  private connect() {
    // Only try to connect if we're in the browser and not already connected
    if (typeof window === 'undefined' || this.socket?.connected) {
      return;
    }

    const serverUrl = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000';
    
    this.socket = io(serverUrl, {
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: true,
      autoConnect: false, // Don't auto-connect
    });

    this.setupEventListeners();
    
    // Only connect if we haven't exceeded max attempts
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.socket.connect();
    }
  }

  private setupEventListeners() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.emit('connection_status', { connected: true });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.emit('connection_status', { connected: false, reason });
      
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, try to reconnect
        this.handleReconnect();
      }
    });

    this.socket.on('connect_error', (error) => {
      // Only log error on first attempt to reduce console spam
      if (this.reconnectAttempts === 0) {
        console.warn('WebSocket connection failed - API server may not be running');
      }
      
      this.emit('connection_error', { error: error.message });
      
      // Only attempt reconnect if we haven't exceeded max attempts
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.handleReconnect();
      } else {
        // Silently fail after max attempts to avoid console spam
        this.emit('connection_failed', { 
          message: 'API server not available' 
        });
      }
    });

    // Trading data events
    this.socket.on('price_update', (data: PriceUpdate) => {
      this.emit('price_update', data);
    });

    this.socket.on('signal_generated', (data: any) => {
      this.emit('signal_generated', data);
    });

    this.socket.on('trade_executed', (data: any) => {
      this.emit('trade_executed', data);
    });

    // Training events
    this.socket.on('training_progress', (data: TrainingProgress) => {
      this.emit('training_progress', data);
    });

    this.socket.on('training_complete', (data: TrainingComplete) => {
      this.emit('training_complete', data);
    });

    // System events
    this.socket.on('system_status', (data: any) => {
      this.emit('system_status', data);
    });

    this.socket.on('telegram_test_result', (data: any) => {
      this.emit('telegram_test_result', data);
    });

    // Generic message handler
    this.socket.on('message', (data: WebSocketMessage) => {
      this.emit('message', data);
    });
  }

  private handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      // Silently fail to avoid console spam
      this.emit('connection_failed', { 
        message: 'API server not available' 
      });
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    // Only log reconnection attempts occasionally to reduce spam
    if (this.reconnectAttempts <= 2) {
      console.log(`Attempting to reconnect to API server (attempt ${this.reconnectAttempts})`);
    }
    
    setTimeout(() => {
      if (this.socket) {
        this.socket.connect();
      }
    }, delay);
  }

  // Event subscription methods
  on(event: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    
    this.listeners.get(event)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      const eventListeners = this.listeners.get(event);
      if (eventListeners) {
        eventListeners.delete(callback);
        if (eventListeners.size === 0) {
          this.listeners.delete(event);
        }
      }
    };
  }

  off(event: string, callback?: (data: any) => void): void {
    if (!callback) {
      this.listeners.delete(event);
      return;
    }

    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.delete(callback);
      if (eventListeners.size === 0) {
        this.listeners.delete(event);
      }
    }
  }

  private emit(event: string, data: any): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${event}:`, error);
        }
      });
    }
  }

  // Subscription methods
  subscribeToSymbol(symbol: string): void {
    if (this.socket?.connected) {
      this.socket.emit('subscribe', { symbol });
    }
  }

  unsubscribeFromSymbol(symbol: string): void {
    if (this.socket?.connected) {
      this.socket.emit('unsubscribe', { symbol });
    }
  }

  subscribeToTraining(modelId: string): void {
    if (this.socket?.connected) {
      this.socket.emit('subscribe_training', { modelId });
    }
  }

  // Send messages to server
  send(event: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket not connected, message not sent:', event, data);
    }
  }

  // Connection status
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  // Disconnect
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.listeners.clear();
  }

  // Reconnect manually
  reconnect(): void {
    this.disconnect();
    this.reconnectAttempts = 0;
    this.connect();
  }

  // Get connection info
  getConnectionInfo() {
    return {
      connected: this.isConnected(),
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts,
      socketId: this.socket?.id,
    };
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;

// Convenience hooks for React components
export const useWebSocket = () => {
  return {
    subscribe: webSocketService.on.bind(webSocketService),
    unsubscribe: webSocketService.off.bind(webSocketService),
    send: webSocketService.send.bind(webSocketService),
    isConnected: webSocketService.isConnected.bind(webSocketService),
    subscribeToSymbol: webSocketService.subscribeToSymbol.bind(webSocketService),
    unsubscribeFromSymbol: webSocketService.unsubscribeFromSymbol.bind(webSocketService),
    getConnectionInfo: webSocketService.getConnectionInfo.bind(webSocketService),
  };
};