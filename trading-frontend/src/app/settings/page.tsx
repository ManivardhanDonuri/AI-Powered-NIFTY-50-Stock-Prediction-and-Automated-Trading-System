'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Alert from '@/components/ui/Alert';
import { Save, RotateCcw, Plus, Trash2 } from 'lucide-react';
import { TradingConfig, TelegramConfig } from '@/types/config';
import { notificationService } from '@/services/notifications';
import { useConfiguration } from '@/hooks/useApiIntegration';


export default function SettingsPage() {
  // API integration
  const { config: apiConfig, updateConfig } = useConfiguration();
  
  const [config, setConfig] = useState<TradingConfig>(apiConfig || {
    trading: {
      stocks: ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS'],
      rsiPeriod: 14,
      smaShort: 20,
      smaLong: 50,
      rsiOversold: 30,
      rsiOverbought: 70,
      lookbackDays: 365,
    },
    ml: {
      enabled: true,
      models: ['LSTM', 'GRU'],
      sequenceLength: 60,
      predictionHorizon: 1,
      trainTestSplit: 0.8,
      validationSplit: 0.2,
      epochs: 50,
      batchSize: 32,
      learningRate: 0.001,
      dropoutRate: 0.2,
      lstmUnits: 50,
      gruUnits: 50,
      features: ['Close', 'SMA_20', 'SMA_50', 'RSI', 'Volume', 'Returns'],
      modelSavePath: 'models/',
      scalerSavePath: 'scalers/',
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

  const [telegramConfig, setTelegramConfig] = useState<TelegramConfig>({
    botToken: '',
    chatId: '',
    notifications: {
      signals: true,
      trades: true,
      errors: true,
      training: false,
    },
  });

  const [newStock, setNewStock] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [telegramTesting, setTelegramTesting] = useState(false);

  // Update config when API data loads
  useEffect(() => {
    if (apiConfig) {
      setConfig(apiConfig);
    }
  }, [apiConfig]);

  const updateTradingConfig = (section: keyof TradingConfig, field: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: {
        ...(prev[section] || {}),
        [field]: value,
      },
    }));
    setHasChanges(true);
  };

  const updateTelegramConfig = (field: keyof TelegramConfig | string, value: any) => {
    if (field === 'notifications') {
      setTelegramConfig(prev => ({
        ...prev,
        notifications: {
          ...prev.notifications,
          ...value,
        },
      }));
    } else {
      setTelegramConfig(prev => ({
        ...prev,
        [field]: value,
      }));
    }
    setHasChanges(true);
  };

  const addStock = () => {
    if (newStock && !(config.trading?.stocks || []).includes(newStock)) {
      updateTradingConfig('trading', 'stocks', [...(config.trading?.stocks || []), newStock]);
      setNewStock('');
    }
  };

  const removeStock = (stock: string) => {
    updateTradingConfig('trading', 'stocks', (config.trading?.stocks || []).filter(s => s !== stock));
  };

  const handleSave = async () => {
    setSaveStatus('saving');
    try {
      await updateConfig(config);
      setSaveStatus('saved');
      setHasChanges(false);
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const handleReset = () => {
    // Reset to default values
    setHasChanges(false);
    setSaveStatus('idle');
  };

  const testTelegramConnection = async () => {
    setTelegramTesting(true);
    
    // Configure notification service
    notificationService.configureTelegram(telegramConfig.botToken, telegramConfig.chatId);
    
    try {
      const success = await notificationService.testTelegramConnection();
      if (success) {
        notificationService.addNotification({
          type: 'system',
          title: 'Telegram Test Successful',
          message: 'Telegram integration is working correctly!',
          timestamp: new Date(),
          severity: 'success',
        });
      } else {
        notificationService.addNotification({
          type: 'system',
          title: 'Telegram Test Failed',
          message: 'Please check your bot token and chat ID.',
          timestamp: new Date(),
          severity: 'error',
        });
      }
    } catch (error) {
      notificationService.addNotification({
        type: 'system',
        title: 'Telegram Test Error',
        message: 'Failed to test Telegram connection.',
        timestamp: new Date(),
        severity: 'error',
      });
    }
    
    setTelegramTesting(false);
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Configure your trading system parameters and preferences
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button 
              variant="outline" 
              onClick={handleReset}
              disabled={!hasChanges}
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset
            </Button>
            <Button 
              onClick={handleSave}
              disabled={!hasChanges}
              loading={saveStatus === 'saving'}
            >
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </Button>
          </div>
        </div>

        {/* Save Status */}
        {saveStatus === 'saved' && (
          <Alert type="success" message="Settings saved successfully!" />
        )}
        {saveStatus === 'error' && (
          <Alert type="error" message="Failed to save settings. Please try again." />
        )}

        {/* Trading Configuration */}
        <Card>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Trading Configuration
          </h3>

          {/* Stock Symbols */}
          <div className="mb-6">
            <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Stock Symbols</h4>
            <div className="flex flex-wrap gap-2 mb-4">
              {(config.trading?.stocks || []).map((stock) => (
                <div key={stock} className="flex items-center space-x-2 bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400 px-3 py-1 rounded-full">
                  <span className="text-sm font-medium">{stock}</span>
                  <button
                    onClick={() => removeStock(stock)}
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex space-x-2">
              <Input
                placeholder="Add stock symbol (e.g., WIPRO.NS)"
                value={newStock}
                onChange={(e) => setNewStock(e.target.value.toUpperCase())}
                onKeyDown={(e) => e.key === 'Enter' && addStock()}
              />
              <Button onClick={addStock} disabled={!newStock}>
                <Plus className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Technical Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Input
              label="RSI Period"
              type="number"
              value={config.trading?.rsiPeriod || 14}
              onChange={(e) => updateTradingConfig('trading', 'rsiPeriod', parseInt(e.target.value))}
              helperText="Period for RSI calculation"
            />
            <Input
              label="Short SMA"
              type="number"
              value={config.trading?.smaShort || 20}
              onChange={(e) => updateTradingConfig('trading', 'smaShort', parseInt(e.target.value))}
              helperText="Short-term moving average"
            />
            <Input
              label="Long SMA"
              type="number"
              value={config.trading?.smaLong || 50}
              onChange={(e) => updateTradingConfig('trading', 'smaLong', parseInt(e.target.value))}
              helperText="Long-term moving average"
            />
            <Input
              label="RSI Oversold"
              type="number"
              value={config.trading?.rsiOversold || 30}
              onChange={(e) => updateTradingConfig('trading', 'rsiOversold', parseInt(e.target.value))}
              helperText="RSI oversold threshold"
            />
            <Input
              label="RSI Overbought"
              type="number"
              value={config.trading?.rsiOverbought || 70}
              onChange={(e) => updateTradingConfig('trading', 'rsiOverbought', parseInt(e.target.value))}
              helperText="RSI overbought threshold"
            />
            <Input
              label="Lookback Days"
              type="number"
              value={config.trading?.lookbackDays || 365}
              onChange={(e) => updateTradingConfig('trading', 'lookbackDays', parseInt(e.target.value))}
              helperText="Historical data period"
            />
          </div>
        </Card>



        {/* Signal Configuration */}
        <Card>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Signal Generation
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Signal Mode
              </label>
              <select
                value={config.signals?.mode || 'hybrid'}
                onChange={(e) => updateTradingConfig('signals', 'mode', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="rule">Rule-based Only</option>
                <option value="ml">ML Only</option>
                <option value="hybrid">Hybrid (Rule + ML)</option>
              </select>
            </div>

            {config.signals?.mode === 'hybrid' && (
              <>
                <Input
                  label="Rule Weight"
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={config.signals?.ruleWeight || 0.4}
                  onChange={(e) => updateTradingConfig('signals', 'ruleWeight', parseFloat(e.target.value))}
                  helperText="Weight for rule-based signals"
                />
                <Input
                  label="ML Weight"
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={config.signals?.mlWeight || 0.6}
                  onChange={(e) => updateTradingConfig('signals', 'mlWeight', parseFloat(e.target.value))}
                  helperText="Weight for ML signals"
                />
              </>
            )}

            <Input
              label="Confidence Threshold"
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={config.signals?.confidenceThreshold || 0.7}
              onChange={(e) => updateTradingConfig('signals', 'confidenceThreshold', parseFloat(e.target.value))}
              helperText="Minimum confidence for signals"
            />
          </div>
        </Card>

        {/* Telegram Configuration */}
        <Card>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
            Telegram Notifications
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <Input
              label="Bot Token"
              type="password"
              value={telegramConfig.botToken}
              onChange={(e) => updateTelegramConfig('botToken', e.target.value)}
              helperText="Telegram bot token from @BotFather"
            />
            <Input
              label="Chat ID"
              value={telegramConfig.chatId}
              onChange={(e) => updateTelegramConfig('chatId', e.target.value)}
              helperText="Your Telegram chat ID"
            />
          </div>

          <div>
            <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Notification Types</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(telegramConfig.notifications).map(([key, value]) => (
                <label key={key} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={(e) => updateTelegramConfig('notifications', { [key]: e.target.checked })}
                    className="rounded border-gray-300 dark:border-gray-600"
                  />
                  <span className="text-sm text-gray-900 dark:text-white capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {telegramConfig.botToken && telegramConfig.chatId && (
            <div className="mt-4">
              <Button 
                variant="outline" 
                onClick={testTelegramConnection}
                loading={telegramTesting}
                disabled={telegramTesting}
              >
                {telegramTesting ? 'Testing...' : 'Test Connection'}
              </Button>
            </div>
          )}
        </Card>



        {/* Warning */}
        {hasChanges && (
          <Alert
            type="warning"
            title="Unsaved Changes"
            message="You have unsaved changes. Some changes may require restarting the trading system to take effect."
          />
        )}
      </div>
    </DashboardLayout>
  );
}