'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Target, Award, Calendar, Settings } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import ProgressBar from '@/components/ui/ProgressBar';
import { MLModel } from '@/types/trading';
import { formatPercentage, formatCurrency } from '@/utils/formatters';

interface ModelPerformanceProps {
  models: MLModel[];
  selectedModel?: MLModel;
  onModelSelect?: (model: MLModel) => void;
  showComparison?: boolean;
}

export default function ModelPerformance({ 
  models, 
  selectedModel, 
  onModelSelect, 
  showComparison = false 
}: ModelPerformanceProps) {
  const [selectedModels, setSelectedModels] = useState<string[]>([]);

  const handleModelToggle = (modelId: string) => {
    setSelectedModels(prev => 
      prev.includes(modelId) 
        ? prev.filter(id => id !== modelId)
        : [...prev, modelId].slice(0, 3) // Max 3 models for comparison
    );
  };

  const getPerformanceColor = (value: number, type: 'accuracy' | 'returns' | 'sharpe') => {
    if (type === 'accuracy') {
      if (value >= 0.8) return 'text-green-600 dark:text-green-400';
      if (value >= 0.7) return 'text-yellow-600 dark:text-yellow-400';
      return 'text-red-600 dark:text-red-400';
    }
    if (type === 'returns') {
      if (value >= 0.15) return 'text-green-600 dark:text-green-400';
      if (value >= 0.05) return 'text-yellow-600 dark:text-yellow-400';
      return 'text-red-600 dark:text-red-400';
    }
    if (type === 'sharpe') {
      if (value >= 1.5) return 'text-green-600 dark:text-green-400';
      if (value >= 1.0) return 'text-yellow-600 dark:text-yellow-400';
      return 'text-red-600 dark:text-red-400';
    }
    return 'text-gray-600 dark:text-gray-400';
  };

  const MetricCard = ({ title, value, subtitle, icon: Icon, color }: {
    title: string;
    value: string;
    subtitle: string;
    icon: any;
    color: string;
  }) => (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5 text-gray-400" />
        <span className={`text-2xl font-bold ${color}`}>{value}</span>
      </div>
      <div className="text-sm font-medium text-gray-900 dark:text-white">{title}</div>
      <div className="text-xs text-gray-500 dark:text-gray-400">{subtitle}</div>
    </div>
  );

  if (showComparison && selectedModels.length > 0) {
    const comparisonModels = models.filter(model => selectedModels.includes(model.id));
    
    return (
      <Card>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Model Comparison
          </h3>
          <Button 
            variant="outline" 
            onClick={() => setSelectedModels([])}
          >
            Clear Selection
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Model</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900 dark:text-white">Accuracy</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900 dark:text-white">Precision</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900 dark:text-white">Recall</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900 dark:text-white">F1-Score</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900 dark:text-white">Returns</th>
                <th className="text-center py-3 px-4 font-medium text-gray-900 dark:text-white">Sharpe</th>
              </tr>
            </thead>
            <tbody>
              {comparisonModels.map((model, index) => (
                <motion.tr
                  key={model.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border-b border-gray-100 dark:border-gray-800"
                >
                  <td className="py-4 px-4">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{model.name}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{model.symbol}</div>
                    </div>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className={getPerformanceColor(model.performance.accuracy, 'accuracy')}>
                      {formatPercentage(model.performance.accuracy * 100)}
                    </span>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className="text-gray-900 dark:text-white">
                      {formatPercentage(model.performance.precision * 100)}
                    </span>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className="text-gray-900 dark:text-white">
                      {formatPercentage(model.performance.recall * 100)}
                    </span>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className="text-gray-900 dark:text-white">
                      {formatPercentage(model.performance.f1Score * 100)}
                    </span>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className={getPerformanceColor(model.performance.backtestResults?.totalReturns || 0, 'returns')}>
                      {formatPercentage((model.performance.backtestResults?.totalReturns || 0) * 100)}
                    </span>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className={getPerformanceColor(model.performance.backtestResults?.sharpeRatio || 0, 'sharpe')}>
                      {model.performance.backtestResults?.sharpeRatio.toFixed(2) || 'N/A'}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Best Performers */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Best Performers</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <Award className="w-6 h-6 text-green-600 dark:text-green-400 mx-auto mb-2" />
              <div className="text-sm text-green-600 dark:text-green-400">Highest Accuracy</div>
              <div className="font-medium text-gray-900 dark:text-white">
                {comparisonModels.reduce((best, model) => 
                  model.performance.accuracy > best.performance.accuracy ? model : best
                ).name}
              </div>
            </div>
            <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
              <div className="text-sm text-blue-600 dark:text-blue-400">Best Returns</div>
              <div className="font-medium text-gray-900 dark:text-white">
                {comparisonModels.reduce((best, model) => 
                  (model.performance.backtestResults?.totalReturns || 0) > (best.performance.backtestResults?.totalReturns || 0) ? model : best
                ).name}
              </div>
            </div>
            <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <Target className="w-6 h-6 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
              <div className="text-sm text-purple-600 dark:text-purple-400">Best Sharpe Ratio</div>
              <div className="font-medium text-gray-900 dark:text-white">
                {comparisonModels.reduce((best, model) => 
                  (model.performance.backtestResults?.sharpeRatio || 0) > (best.performance.backtestResults?.sharpeRatio || 0) ? model : best
                ).name}
              </div>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Model Selection */}
      <Card>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Model Performance
          </h3>
          {models.length > 1 && (
            <Button 
              variant="outline" 
              onClick={() => setSelectedModels(models.slice(0, 3).map(m => m.id))}
            >
              Compare Models
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {models.map((model) => (
            <motion.div
              key={model.id}
              whileHover={{ scale: 1.02 }}
              className={`p-4 border rounded-lg cursor-pointer transition-all ${
                selectedModel?.id === model.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : selectedModels.includes(model.id)
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
              onClick={() => {
                if (onModelSelect) onModelSelect(model);
                handleModelToggle(model.id);
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 dark:text-white">{model.name}</h4>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  model.type === 'LSTM' 
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                    : 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
                }`}>
                  {model.type}
                </span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">{model.symbol}</div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500 dark:text-gray-400">Accuracy</span>
                  <span className={`text-sm font-medium ${getPerformanceColor(model.performance.accuracy, 'accuracy')}`}>
                    {formatPercentage(model.performance.accuracy * 100)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500 dark:text-gray-400">Returns</span>
                  <span className={`text-sm font-medium ${getPerformanceColor(model.performance.backtestResults?.totalReturns || 0, 'returns')}`}>
                    {formatPercentage((model.performance.backtestResults?.totalReturns || 0) * 100)}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Detailed Performance */}
      {selectedModel && (
        <Card>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
              {selectedModel.name} - Detailed Performance
            </h3>
            <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              <Calendar className="w-4 h-4" />
              <span>Trained {selectedModel.trainedAt.toLocaleDateString()}</span>
            </div>
          </div>

          {/* Performance Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <MetricCard
              title="Accuracy"
              value={formatPercentage(selectedModel.performance.accuracy * 100)}
              subtitle="Model accuracy"
              icon={Target}
              color={getPerformanceColor(selectedModel.performance.accuracy, 'accuracy')}
            />
            <MetricCard
              title="Precision"
              value={formatPercentage(selectedModel.performance.precision * 100)}
              subtitle="True positive rate"
              icon={Award}
              color="text-gray-900 dark:text-white"
            />
            <MetricCard
              title="Recall"
              value={formatPercentage(selectedModel.performance.recall * 100)}
              subtitle="Sensitivity"
              icon={BarChart3}
              color="text-gray-900 dark:text-white"
            />
            <MetricCard
              title="F1-Score"
              value={formatPercentage(selectedModel.performance.f1Score * 100)}
              subtitle="Harmonic mean"
              icon={TrendingUp}
              color="text-gray-900 dark:text-white"
            />
          </div>

          {/* Training Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Training Metrics</h4>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Training Loss</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {selectedModel.performance.trainingLoss.toFixed(4)}
                    </span>
                  </div>
                  <ProgressBar 
                    value={Math.max(0, 100 - selectedModel.performance.trainingLoss * 1000)} 
                    color="blue" 
                    size="sm"
                  />
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Validation Loss</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {selectedModel.performance.validationLoss.toFixed(4)}
                    </span>
                  </div>
                  <ProgressBar 
                    value={Math.max(0, 100 - selectedModel.performance.validationLoss * 1000)} 
                    color="purple" 
                    size="sm"
                  />
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Model Parameters</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Sequence Length</span>
                  <span className="text-gray-900 dark:text-white">{selectedModel.parameters.sequenceLength}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Epochs</span>
                  <span className="text-gray-900 dark:text-white">{selectedModel.parameters.epochs}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Batch Size</span>
                  <span className="text-gray-900 dark:text-white">{selectedModel.parameters.batchSize}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Learning Rate</span>
                  <span className="text-gray-900 dark:text-white">{selectedModel.parameters.learningRate}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Units</span>
                  <span className="text-gray-900 dark:text-white">{selectedModel.parameters.units}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Backtest Results */}
          {selectedModel.performance.backtestResults && (
            <div>
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Backtest Results</h4>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {formatPercentage(selectedModel.performance.backtestResults.totalReturns * 100)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Total Returns</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {selectedModel.performance.backtestResults.sharpeRatio.toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Sharpe Ratio</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {formatPercentage(selectedModel.performance.backtestResults.maxDrawdown * 100)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Max Drawdown</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    {formatPercentage(selectedModel.performance.backtestResults.winRate * 100)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Win Rate</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {selectedModel.performance.backtestResults.totalTrades}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Total Trades</div>
                </div>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Show Comparison */}
      {selectedModels.length > 0 && (
        <ModelPerformance 
          models={models} 
          showComparison={true} 
        />
      )}
    </div>
  );
}