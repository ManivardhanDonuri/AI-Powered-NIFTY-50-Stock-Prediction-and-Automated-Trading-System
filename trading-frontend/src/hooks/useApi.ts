import { useState, useEffect, useCallback } from 'react';
import apiService from '@/services/api';
import { Stock, TradingSignal, MLModel } from '@/types/trading';

// Generic hook for API calls
export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// Hook for stocks data
export function useStocks() {
  return useApi(() => apiService.getStocks());
}

// Hook for specific stock
export function useStock(symbol: string) {
  return useApi(() => apiService.getStockPrice(symbol), [symbol]);
}

// Hook for trading signals
export function useTradingSignals(filters?: {
  symbol?: string;
  type?: string;
  dateFrom?: string;
  dateTo?: string;
}) {
  return useApi(() => apiService.getTradingSignals(filters), [filters]);
}

// Hook for ML models
export function useModels() {
  return useApi(() => apiService.getModels());
}

// Hook for portfolio data
export function usePortfolio() {
  return useApi(() => apiService.getPortfolio());
}

// Hook for system status
export function useSystemStatus() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiService.getSystemStatus();
      setStatus(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch system status');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    
    // Poll system status every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const startSystem = useCallback(async () => {
    try {
      await apiService.startSystem();
      await fetchStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start system');
    }
  }, [fetchStatus]);

  const stopSystem = useCallback(async () => {
    try {
      await apiService.stopSystem();
      await fetchStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop system');
    }
  }, [fetchStatus]);

  const restartSystem = useCallback(async () => {
    try {
      await apiService.restartSystem();
      await fetchStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to restart system');
    }
  }, [fetchStatus]);

  return {
    status,
    loading,
    error,
    refetch: fetchStatus,
    startSystem,
    stopSystem,
    restartSystem,
  };
}

// Hook for configuration management
export function useConfig() {
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const fetchConfig = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiService.getConfig();
      setConfig(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch configuration');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const updateConfig = useCallback(async (newConfig: any) => {
    try {
      setSaving(true);
      setError(null);
      await apiService.updateConfig(newConfig);
      setConfig({ ...config, ...newConfig });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update configuration');
      throw err;
    } finally {
      setSaving(false);
    }
  }, [config]);

  return {
    config,
    loading,
    error,
    saving,
    refetch: fetchConfig,
    updateConfig,
  };
}

// Hook for model training
export function useModelTraining() {
  const [trainingProgress, setTrainingProgress] = useState<any>(null);
  const [isTraining, setIsTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startTraining = useCallback(async (config: any) => {
    try {
      setError(null);
      setIsTraining(true);
      const result = await apiService.startTraining(config);
      
      // Poll training progress
      const pollProgress = async () => {
        try {
          const progress = await apiService.getTrainingProgress(result.trainingId);
          setTrainingProgress(progress);
          
          if (progress.status === 'COMPLETED' || progress.status === 'FAILED') {
            setIsTraining(false);
            return;
          }
          
          setTimeout(pollProgress, 2000); // Poll every 2 seconds
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to get training progress');
          setIsTraining(false);
        }
      };
      
      pollProgress();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start training');
      setIsTraining(false);
    }
  }, []);

  const stopTraining = useCallback(async (trainingId: string) => {
    try {
      await apiService.stopTraining(trainingId);
      setIsTraining(false);
      setTrainingProgress(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop training');
    }
  }, []);

  return {
    trainingProgress,
    isTraining,
    error,
    startTraining,
    stopTraining,
  };
}

// Hook for data export
export function useDataExport() {
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportData = useCallback(async (
    type: 'signals' | 'trades' | 'portfolio',
    format: 'csv' | 'xlsx' | 'json',
    filters?: any
  ) => {
    try {
      setExporting(true);
      setError(null);
      
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
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${type}-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setExporting(false);
    }
  }, []);

  return {
    exporting,
    error,
    exportData,
  };
}

// Hook for health check
export function useHealthCheck() {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [checking, setChecking] = useState(false);

  const checkHealth = useCallback(async () => {
    try {
      setChecking(true);
      const healthy = await apiService.healthCheck();
      setIsHealthy(healthy);
    } catch {
      setIsHealthy(false);
    } finally {
      setChecking(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    
    // Check health every minute
    const interval = setInterval(checkHealth, 60000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    isHealthy,
    checking,
    checkHealth,
  };
}