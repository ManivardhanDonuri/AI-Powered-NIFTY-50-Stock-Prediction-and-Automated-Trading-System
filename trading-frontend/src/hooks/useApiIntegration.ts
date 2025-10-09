import { useState, useEffect, useCallback } from 'react';
import apiService from '@/services/api';
import webSocketService from '@/services/websocket';
import { Stock, TradingSignal, MLModel } from '@/types/trading';

export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// Generic API hook
export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
): ApiState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const data = await apiCall();
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error.message : 'An error occurred',
      });
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    ...state,
    refetch: fetchData,
  };
}

// Stock data hooks
export function useStockPrice(symbol: string) {
  const [stockData, setStockData] = useState<Stock | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStockData = async () => {
      try {
        setLoading(true);
        const data = await apiService.getStockPrice(symbol);
        setStockData(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch stock data');
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchStockData();
      
      // Subscribe to real-time updates
      webSocketService.subscribeToSymbol(symbol);
      
      const unsubscribe = webSocketService.on('price_update', (update: any) => {
        if (update.symbol === symbol) {
          setStockData(prev => prev ? { ...prev, ...update } : null);
        }
      });

      return () => {
        webSocketService.unsubscribeFromSymbol(symbol);
        unsubscribe();
      };
    }
  }, [symbol]);

  return { stockData, loading, error };
}

// Trading signals hook
export function useTradingSignals(filters?: any) {
  return useApi(() => apiService.getTradingSignals(filters), [filters]);
}

// ML Models hook
export function useMLModels() {
  return useApi(() => apiService.getModels());
}

// System status hook
export function useSystemStatus() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await apiService.getSystemStatus();
        setStatus(data);
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();

    // Subscribe to status updates
    const unsubscribe = webSocketService.on('system_status', (update: any) => {
      setStatus(update);
    });

    // Poll for status updates every 30 seconds
    const interval = setInterval(fetchStatus, 30000);

    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, []);

  return { status, loading };
}

// Training progress hook
export function useTrainingProgress(modelId?: string) {
  const [progress, setProgress] = useState<any>(null);
  const [isTraining, setIsTraining] = useState(false);

  useEffect(() => {
    if (!modelId) return;

    webSocketService.subscribeToTraining(modelId);

    const progressUnsubscribe = webSocketService.on('training_progress', (data: any) => {
      if (data.modelId === modelId) {
        setProgress(data);
        setIsTraining(true);
      }
    });

    const completeUnsubscribe = webSocketService.on('training_complete', (data: any) => {
      if (data.modelId === modelId) {
        setProgress(data);
        setIsTraining(false);
      }
    });

    return () => {
      progressUnsubscribe();
      completeUnsubscribe();
    };
  }, [modelId]);

  return { progress, isTraining };
}

// Connection status hook
export function useConnectionStatus() {
  const [isConnected, setIsConnected] = useState(webSocketService.isConnected());
  const [connectionInfo, setConnectionInfo] = useState(webSocketService.getConnectionInfo());

  useEffect(() => {
    const unsubscribe = webSocketService.on('connection_status', (status: any) => {
      setIsConnected(status.connected);
      setConnectionInfo(webSocketService.getConnectionInfo());
    });

    // Update connection info periodically
    const interval = setInterval(() => {
      setIsConnected(webSocketService.isConnected());
      setConnectionInfo(webSocketService.getConnectionInfo());
    }, 5000);

    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, []);

  return { 
    isConnected, 
    connectionInfo,
    reconnect: webSocketService.reconnect.bind(webSocketService)
  };
}

// Configuration hook
export function useConfiguration() {
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setError(null);
        const data = await apiService.getConfig();
        setConfig(data);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch configuration';
        console.error('Failed to fetch configuration:', error);
        setError(errorMessage);
        
        // Set default config if API is not available
        setConfig({
          trading: {
            stocks: ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS'],
            rsiPeriod: 14,
            smaShort: 20,
            smaLong: 50,
            rsiOversold: 30,
            rsiOverbought: 70,
            lookbackDays: 365,
          },
          signals: {
            mode: 'hybrid',
            ruleWeight: 0.4,
            mlWeight: 0.6,
            mlThreshold: 0.6,
            confidenceThreshold: 0.7,
          },
          dashboard: {
            enabled: true,
            port: 8501,
            title: 'NIFTY 50 ML Trading Dashboard',
          },
        });
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  const updateConfig = useCallback(async (newConfig: any) => {
    setSaving(true);
    setError(null);
    try {
      await apiService.updateConfig(newConfig);
      setConfig(newConfig);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update configuration';
      console.error('Failed to update configuration:', error);
      setError(errorMessage);
      
      // Still update local config for offline functionality
      setConfig(newConfig);
      throw error;
    } finally {
      setSaving(false);
    }
  }, []);

  return { config, loading, saving, error, updateConfig };
}

// Export utilities
export function useDataExport() {
  const [exporting, setExporting] = useState(false);

  const exportData = useCallback(async (
    type: 'signals' | 'trades' | 'portfolio',
    format: 'csv' | 'xlsx' | 'json',
    filters?: any
  ) => {
    setExporting(true);
    try {
      let blob: Blob;
      
      switch (type) {
        case 'signals':
          blob = await apiService.exportSignals(format, filters);
          break;
        case 'trades':
          blob = await apiService.exportTrades(format, filters);
          break;
        case 'portfolio':
          blob = await apiService.exportPortfolio(format);
          break;
        default:
          throw new Error('Invalid export type');
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${type}_export.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      throw error;
    } finally {
      setExporting(false);
    }
  }, []);

  return { exportData, exporting };
}