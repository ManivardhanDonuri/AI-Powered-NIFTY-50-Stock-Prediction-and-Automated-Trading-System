'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import ProgressBar from '@/components/ui/ProgressBar';
import { Brain, Play, Square, Settings, Database, TrendingUp } from 'lucide-react';
import { MODEL_TYPES, DEFAULT_STOCKS } from '@/utils/constants';
import { MOCK_ML_MODELS, createMockTrainingProgress } from '@/services/mockData';
import { TrainingConfig, TrainingProgress, MLModel } from '@/types/trading';

export default function TrainModelPage() {
  const [selectedStock, setSelectedStock] = useState('RELIANCE.NS');
  const [selectedModelType, setSelectedModelType] = useState<'LSTM' | 'GRU'>('LSTM');
  const [trainingConfig, setTrainingConfig] = useState<Partial<TrainingConfig>>({
    symbol: 'RELIANCE.NS',
    modelType: 'LSTM',
    parameters: {
      sequenceLength: 60,
      epochs: 50,
      batchSize: 32,
      learningRate: 0.001,
      dropoutRate: 0.2,
      units: 50,
    },
    dataRange: {
      startDate: '2023-01-01',
      endDate: '2024-12-31',
    },
  });
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState<TrainingProgress | null>(null);
  const [existingModels] = useState<MLModel[]>(MOCK_ML_MODELS);

  const handleStartTraining = () => {
    setIsTraining(true);
    setTrainingProgress(createMockTrainingProgress());
    
    // Simulate training progress
    const interval = setInterval(() => {
      setTrainingProgress(prev => {
        if (!prev) return null;
        
        const newEpoch = prev.epoch + 1;
        if (newEpoch >= prev.totalEpochs) {
          setIsTraining(false);
          clearInterval(interval);
          return { ...prev, epoch: prev.totalEpochs, status: 'COMPLETED' };
        }
        
        return {
          ...prev,
          epoch: newEpoch,
          loss: Math.max(0.001, prev.loss * 0.98),
          accuracy: Math.min(0.95, prev.accuracy + 0.005),
          estimatedTimeRemaining: Math.max(0, prev.estimatedTimeRemaining - 30),
        };
      });
    }, 1000);
  };

  const handleStopTraining = () => {
    setIsTraining(false);
    setTrainingProgress(prev => prev ? { ...prev, status: 'CANCELLED' } : null);
  };

  const updateConfig = (field: string, value: any) => {
    setTrainingConfig(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const updateParameters = (field: string, value: any) => {
    setTrainingConfig(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters!,
        [field]: value,
      },
    }));
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Train ML Model
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Configure and train machine learning models for stock price prediction
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Brain className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Training Configuration */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                Training Configuration
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Stock Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Stock Symbol
                  </label>
                  <select
                    value={selectedStock}
                    onChange={(e) => {
                      setSelectedStock(e.target.value);
                      updateConfig('symbol', e.target.value);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {DEFAULT_STOCKS.map(stock => (
                      <option key={stock.symbol} value={stock.symbol}>{stock.name}</option>
                    ))}
                  </select>
                </div>

                {/* Model Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Model Type
                  </label>
                  <select
                    value={selectedModelType}
                    onChange={(e) => {
                      const modelType = e.target.value as 'LSTM' | 'GRU';
                      setSelectedModelType(modelType);
                      updateConfig('modelType', modelType);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {MODEL_TYPES.map(type => (
                      <option key={type.id} value={type.id}>{type.name}</option>
                    ))}
                  </select>
                </div>

                {/* Training Parameters */}
                <Input
                  label="Sequence Length"
                  type="number"
                  value={trainingConfig.parameters?.sequenceLength || 60}
                  onChange={(e) => updateParameters('sequenceLength', parseInt(e.target.value))}
                  helperText="Number of time steps to look back"
                />

                <Input
                  label="Epochs"
                  type="number"
                  value={trainingConfig.parameters?.epochs || 50}
                  onChange={(e) => updateParameters('epochs', parseInt(e.target.value))}
                  helperText="Number of training iterations"
                />

                <Input
                  label="Batch Size"
                  type="number"
                  value={trainingConfig.parameters?.batchSize || 32}
                  onChange={(e) => updateParameters('batchSize', parseInt(e.target.value))}
                  helperText="Number of samples per batch"
                />

                <Input
                  label="Learning Rate"
                  type="number"
                  step="0.0001"
                  value={trainingConfig.parameters?.learningRate || 0.001}
                  onChange={(e) => updateParameters('learningRate', parseFloat(e.target.value))}
                  helperText="Model learning rate"
                />

                <Input
                  label="Dropout Rate"
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={trainingConfig.parameters?.dropoutRate || 0.2}
                  onChange={(e) => updateParameters('dropoutRate', parseFloat(e.target.value))}
                  helperText="Dropout rate for regularization"
                />

                <Input
                  label="Units"
                  type="number"
                  value={trainingConfig.parameters?.units || 50}
                  onChange={(e) => updateParameters('units', parseInt(e.target.value))}
                  helperText="Number of LSTM/GRU units"
                />
              </div>

              {/* Data Range */}
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Training Data Range
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Input
                    label="Start Date"
                    type="date"
                    value={trainingConfig.dataRange?.startDate || '2023-01-01'}
                    onChange={(e) => updateConfig('dataRange', {
                      ...trainingConfig.dataRange,
                      startDate: e.target.value
                    })}
                  />
                  <Input
                    label="End Date"
                    type="date"
                    value={trainingConfig.dataRange?.endDate || '2024-12-31'}
                    onChange={(e) => updateConfig('dataRange', {
                      ...trainingConfig.dataRange,
                      endDate: e.target.value
                    })}
                  />
                </div>
              </div>

              {/* Training Controls */}
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-4">
                  {!isTraining ? (
                    <Button
                      onClick={handleStartTraining}
                      className="flex items-center space-x-2"
                    >
                      <Play className="w-4 h-4" />
                      <span>Start Training</span>
                    </Button>
                  ) : (
                    <Button
                      onClick={handleStopTraining}
                      variant="danger"
                      className="flex items-center space-x-2"
                    >
                      <Square className="w-4 h-4" />
                      <span>Stop Training</span>
                    </Button>
                  )}
                </div>
              </div>
            </Card>

            {/* Training Progress */}
            {trainingProgress && (
              <Card>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                  Training Progress
                </h3>
                
                <div className="space-y-6">
                  <ProgressBar
                    value={trainingProgress.epoch}
                    max={trainingProgress.totalEpochs}
                    label={`Epoch ${trainingProgress.epoch}/${trainingProgress.totalEpochs}`}
                    color="blue"
                    showLabel
                  />

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {trainingProgress.loss.toFixed(4)}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Loss</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {(trainingProgress.accuracy * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Accuracy</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {Math.floor(trainingProgress.estimatedTimeRemaining / 60)}m
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">ETA</div>
                    </div>
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${
                        trainingProgress.status === 'TRAINING' ? 'text-blue-600 dark:text-blue-400' :
                        trainingProgress.status === 'COMPLETED' ? 'text-green-600 dark:text-green-400' :
                        'text-red-600 dark:text-red-400'
                      }`}>
                        {trainingProgress.status}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Status</div>
                    </div>
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Existing Models */}
          <div className="space-y-6">
            <Card>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                Existing Models
              </h3>
              
              <div className="space-y-4">
                {existingModels.map((model) => (
                  <div key={model.id} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {model.name}
                      </h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        model.type === 'LSTM' 
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                          : 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
                      }`}>
                        {model.type}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {model.symbol}
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-400">
                        Accuracy: {(model.accuracy * 100).toFixed(1)}%
                      </span>
                      <span className="text-gray-500 dark:text-gray-400">
                        {model.trainedAt.toLocaleDateString()}
                      </span>
                    </div>
                    <div className="mt-3 flex space-x-2">
                      <Button size="sm" variant="outline" className="flex-1">
                        Retrain
                      </Button>
                      <Button size="sm" variant="ghost" className="flex-1">
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Quick Stats */}
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Training Stats
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Total Models</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {existingModels.length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Avg Accuracy</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {(existingModels.reduce((acc, model) => acc + model.accuracy, 0) / existingModels.length * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Best Model</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {existingModels.reduce((best, model) => model.accuracy > best.accuracy ? model : best, existingModels[0])?.name}
                  </span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}