import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { TradingConfig, TelegramConfig } from '@/types/config';
import { Stock, TradingSignal, MLModel, TrainingConfig, TrainingProgress } from '@/types/trading';

class ApiService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Stock Data APIs
  async getStocks(): Promise<Stock[]> {
    const response = await this.client.get('/stocks');
    return response.data;
  }

  async getStockPrice(symbol: string): Promise<Stock> {
    const response = await this.client.get(`/stocks/${symbol}`);
    return response.data;
  }

  async getHistoricalData(symbol: string, timeframe: string) {
    const response = await this.client.get(`/stocks/${symbol}/historical`, {
      params: { timeframe }
    });
    return response.data;
  }

  // Trading Signals APIs
  async getTradingSignals(filters?: {
    symbol?: string;
    type?: string;
    dateFrom?: string;
    dateTo?: string;
  }): Promise<TradingSignal[]> {
    const response = await this.client.get('/signals', { params: filters });
    return response.data;
  }

  async getSignalById(id: string): Promise<TradingSignal> {
    const response = await this.client.get(`/signals/${id}`);
    return response.data;
  }

  // ML Models APIs
  async getModels(): Promise<MLModel[]> {
    const response = await this.client.get('/models');
    return response.data;
  }

  async getModelById(id: string): Promise<MLModel> {
    const response = await this.client.get(`/models/${id}`);
    return response.data;
  }

  async startTraining(config: TrainingConfig): Promise<{ trainingId: string }> {
    const response = await this.client.post('/models/train', config);
    return response.data;
  }

  async stopTraining(trainingId: string): Promise<void> {
    await this.client.post(`/models/train/${trainingId}/stop`);
  }

  async getTrainingProgress(trainingId: string): Promise<TrainingProgress> {
    const response = await this.client.get(`/models/train/${trainingId}/progress`);
    return response.data;
  }

  async deleteModel(id: string): Promise<void> {
    await this.client.delete(`/models/${id}`);
  }

  // Portfolio APIs
  async getPortfolio() {
    const response = await this.client.get('/portfolio');
    return response.data;
  }

  async getPositions() {
    const response = await this.client.get('/portfolio/positions');
    return response.data;
  }

  async getTrades(filters?: {
    symbol?: string;
    dateFrom?: string;
    dateTo?: string;
  }) {
    const response = await this.client.get('/portfolio/trades', { params: filters });
    return response.data;
  }

  // System Control APIs
  async getSystemStatus() {
    const response = await this.client.get('/system/status');
    return response.data;
  }

  async startSystem(): Promise<void> {
    await this.client.post('/system/start');
  }

  async stopSystem(): Promise<void> {
    await this.client.post('/system/stop');
  }

  async restartSystem(): Promise<void> {
    await this.client.post('/system/restart');
  }

  async getSystemLogs(limit?: number) {
    const response = await this.client.get('/system/logs', {
      params: { limit }
    });
    return response.data;
  }

  // Configuration APIs
  async getConfig(): Promise<TradingConfig> {
    const response = await this.client.get('/config');
    return response.data;
  }

  async updateConfig(config: Partial<TradingConfig>): Promise<void> {
    await this.client.put('/config', config);
  }

  async getTelegramConfig(): Promise<TelegramConfig> {
    const response = await this.client.get('/config/telegram');
    return response.data;
  }

  async updateTelegramConfig(config: TelegramConfig): Promise<void> {
    await this.client.put('/config/telegram', config);
  }

  async testTelegramConnection(): Promise<boolean> {
    const response = await this.client.post('/config/telegram/test');
    return response.data.success;
  }

  // Data Export APIs
  async exportSignals(format: 'csv' | 'xlsx' | 'json', filters?: any): Promise<Blob> {
    const response = await this.client.get('/export/signals', {
      params: { format, ...filters },
      responseType: 'blob'
    });
    return response.data;
  }

  async exportTrades(format: 'csv' | 'xlsx' | 'json', filters?: any): Promise<Blob> {
    const response = await this.client.get('/export/trades', {
      params: { format, ...filters },
      responseType: 'blob'
    });
    return response.data;
  }

  async exportPortfolio(format: 'csv' | 'xlsx' | 'json'): Promise<Blob> {
    const response = await this.client.get('/export/portfolio', {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  }

  // Utility methods
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  }

  // File upload for model imports, etc.
  async uploadFile(file: File, endpoint: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // Batch operations
  async batchRequest(requests: Array<{ method: string; url: string; data?: any }>): Promise<any[]> {
    const response = await this.client.post('/batch', { requests });
    return response.data;
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;

// Export types for use in components
export type { TradingConfig, TelegramConfig, Stock, TradingSignal, MLModel, TrainingConfig, TrainingProgress };