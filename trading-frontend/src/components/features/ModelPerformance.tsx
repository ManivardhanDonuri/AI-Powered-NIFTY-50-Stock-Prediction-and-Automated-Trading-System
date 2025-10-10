'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Target, Award, Calendar, Settings } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import ProgressBar from '@/components/ui/ProgressBar';
import { MLModel } from '@/types/trading';
import { formatPercentage, formatCurrency } from '@/utils/formatters';
import { cn } from '@/utils/cn';

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
      if (value >= 0.8) return 'text-[var(--color-success)]';
      if (value >= 0.7) return 'text-[var(--color-warning)]';
      return 'text-[var(--color-error)]';
    }
    if (type === 'returns') {
      if (value >= 0.15) return 'text-[var(--color-success)]';
      if (value >= 0.05) return 'text-[var(--color-warning)]';
      return 'text-[var(--color-error)]';
    }
    if (type === 'sharpe') {
      if (value >= 1.5) return 'text-[var(--color-success)]';
      if (value >= 1.0) return 'text-[var(--color-warning)]';
      return 'text-[var(--color-error)]';
    }
    return 'text-[var(--color-text-muted)]';
  };

  const MetricCard = ({ title, value, subtitle, icon: Icon, color }: {
    title: string;
    value: string;
    subtitle: string;
    icon: any;
    color: string;
  }) => (
    <Card variant="outlined" padding="sm" className="bg-[var(--color-surface)]">
      <div className="flex items-center justify-between mb-[var(--spacing-sm)]">
        <Icon className="w-5 h-5 text-[var(--color-text-muted)]" />
        <span className={cn('text-2xl font-bold', color)}>{value}</span>
      </div>
      <div className="text-sm font-medium text-[var(--color-text-primary)]">{title}</div>
      <div className="text-xs text-[var(--color-text-muted)]">{subtitle}</div>
    </Card>
  );

  if (showComparison && selectedModels.length > 0) {
    const comparisonModels = models.filter(model => selectedModels.includes(model.id));
    
    return (
      <Card variant="elevated" padding="lg">
        <div className="flex items-center justify-between mb-[var(--spacing-xl)]">
          <h3 className="text-xl font-semibold text-[var(--color-text-primary)]">
            Model Comparison
          </h3>
          <Button 
            variant="outline" 
            size="md"
            onClick={() => setSelectedModels([])}
          >
            Clear Selection
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--color-border)]">
                <th className="text-left py-3 px-4 font-medium text-[var(--color-text-primary)]">Model</th>
                <th className="text-center py-3 px-4 font-medium text-[var(--color-text-primary)]">Accuracy</th>
                <th className="text-center py-3 px-4 font-medium text-[var(--color-text-primary)]">Precision</th>
                <th className="text-center py-3 px-4 font-medium text-[var(--color-text-primary)]">Recall</th>
                <th className="text-center py-3 px-4 font-medium text-[var(--color-text-primary)]">F1-Score</th>
                <th className="text-center py-3 px-4 font-medium text-[var(--color-text-primary)]">Returns</th>
                <th className="text-center py-3 px-4 font-medium text-[var(--color-text-primary)]">Sharpe</th>
              </tr>
            </thead>
            <tbody>
              {comparisonModels.map((model, index) => (
                <motion.tr
                  key={model.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border-b border-[var(--color-border)]"
                >
                  <td className="py-4 px-4">
                    <div>
                      <div className="font-medium text-[var(--color-text-primary)]">{model.name}</div>
                      <div className="text-sm text-[var(--color-text-muted)]">{model.symbol}</div>
                    </div>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className={getPerformanceColor(model.performance.accuracy, 'accuracy')}>
                      {formatPercentage(model.performance.accuracy * 100)}
                    </span>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className="text-[var(--color-text-primary)]">
                      {formatPercentage(model.performance.precision * 100)}
                    </span>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className="text-[var(--color-text-primary)]">
                      {formatPercentage(model.performance.recall * 100)}
                    </span>
                  </td>
                  <td className="text-center py-4 px-4">
                    <span className="text-[var(--color-text-primary)]">
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
        <div className="mt-[var(--spacing-xl)] pt-[var(--spacing-xl)] border-t border-[var(--color-border)]">
          <h4 className="text-lg font-medium text-[var(--color-text-primary)] mb-[var(--spacing-md)]">Best Performers</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-[var(--spacing-md)]">
            <Card variant="outlined" padding="md" className="text-center bg-[var(--color-success)]/10">
              <Award className="w-6 h-6 text-[var(--color-success)] mx-auto mb-[var(--spacing-sm)]" />
              <div className="text-sm text-[var(--color-success)] mb-1">Highest Accuracy</div>
              <div className="font-medium text-[var(--color-text-primary)]">
                {comparisonModels.reduce((best, model) => 
                  model.performance.accuracy > best.performance.accuracy ? model : best
                ).name}
              </div>
            </Card>
            <Card variant="outlined" padding="md" className="text-center bg-[var(--color-info)]/10">
              <TrendingUp className="w-6 h-6 text-[var(--color-info)] mx-auto mb-[var(--spacing-sm)]" />
              <div className="text-sm text-[var(--color-info)] mb-1">Best Returns</div>
              <div className="font-medium text-[var(--color-text-primary)]">
                {comparisonModels.reduce((best, model) => 
                  (model.performance.backtestResults?.totalReturns || 0) > (best.performance.backtestResults?.totalReturns || 0) ? model : best
                ).name}
              </div>
            </Card>
            <Card variant="outlined" padding="md" className="text-center bg-[var(--color-accent)]/10">
              <Target className="w-6 h-6 text-[var(--color-accent)] mx-auto mb-[var(--spacing-sm)]" />
              <div className="text-sm text-[var(--color-accent)] mb-1">Best Sharpe Ratio</div>
              <div className="font-medium text-[var(--color-text-primary)]">
                {comparisonModels.reduce((best, model) => 
                  (model.performance.backtestResults?.sharpeRatio || 0) > (best.performance.backtestResults?.sharpeRatio || 0) ? model : best
                ).name}
              </div>
            </Card>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-[var(--spacing-xl)]">
      {/* Model Selection */}
      <Card variant="elevated" padding="lg">
        <div className="flex items-center justify-between mb-[var(--spacing-xl)]">
          <h3 className="text-xl font-semibold text-[var(--color-text-primary)]">
            Model Performance
          </h3>
          {models.length > 1 && (
            <Button 
              variant="outline" 
              size="md"
              onClick={() => setSelectedModels(models.slice(0, 3).map(m => m.id))}
            >
              Compare Models
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[var(--spacing-md)]">
          {models.map((model) => (
            <motion.div
              key={model.id}
              whileHover={{ scale: 1.02 }}
              className={cn(
                'p-[var(--spacing-md)] border rounded-[var(--radius-lg)] cursor-pointer transition-all',
                selectedModel?.id === model.id
                  ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10'
                  : selectedModels.includes(model.id)
                  ? 'border-[var(--color-success)] bg-[var(--color-success)]/10'
                  : 'border-[var(--color-border)] hover:border-[var(--color-border-hover)] bg-[var(--color-surface)]'
              )}
              onClick={() => {
                if (onModelSelect) onModelSelect(model);
                handleModelToggle(model.id);
              }}
            >
              <div className="flex items-center justify-between mb-[var(--spacing-sm)]">
                <h4 className="font-medium text-[var(--color-text-primary)]">{model.name}</h4>
                <span className={cn(
                  'px-2 py-1 text-xs rounded-full',
                  model.type === 'LSTM' 
                    ? 'bg-[var(--color-info)]/20 text-[var(--color-info)]'
                    : 'bg-[var(--color-accent)]/20 text-[var(--color-accent)]'
                )}>
                  {model.type}
                </span>
              </div>
              <div className="text-sm text-[var(--color-text-muted)] mb-3">{model.symbol}</div>
              <div className="space-y-[var(--spacing-sm)]">
                <div className="flex justify-between">
                  <span className="text-sm text-[var(--color-text-muted)]">Accuracy</span>
                  <span className={cn('text-sm font-medium', getPerformanceColor(model.performance.accuracy, 'accuracy'))}>
                    {formatPercentage(model.performance.accuracy * 100)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[var(--color-text-muted)]">Returns</span>
                  <span className={cn('text-sm font-medium', getPerformanceColor(model.performance.backtestResults?.totalReturns || 0, 'returns'))}>
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
        <Card variant="elevated" padding="lg">
          <div className="flex items-center justify-between mb-[var(--spacing-xl)]">
            <h3 className="text-xl font-semibold text-[var(--color-text-primary)]">
              {selectedModel.name} - Detailed Performance
            </h3>
            <div className="flex items-center space-x-2 text-sm text-[var(--color-text-muted)]">
              <Calendar className="w-4 h-4" />
              <span>Trained {selectedModel.trainedAt.toLocaleDateString()}</span>
            </div>
          </div>

          {/* Performance Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-[var(--spacing-md)] mb-[var(--spacing-xl)]">
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
              color="text-[var(--color-text-primary)]"
            />
            <MetricCard
              title="Recall"
              value={formatPercentage(selectedModel.performance.recall * 100)}
              subtitle="Sensitivity"
              icon={BarChart3}
              color="text-[var(--color-text-primary)]"
            />
            <MetricCard
              title="F1-Score"
              value={formatPercentage(selectedModel.performance.f1Score * 100)}
              subtitle="Harmonic mean"
              icon={TrendingUp}
              color="text-[var(--color-text-primary)]"
            />
          </div>

          {/* Training Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-[var(--spacing-xl)] mb-[var(--spacing-xl)]">
            <div>
              <h4 className="text-lg font-medium text-[var(--color-text-primary)] mb-[var(--spacing-md)]">Training Metrics</h4>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-[var(--color-text-secondary)]">Training Loss</span>
                    <span className="text-sm font-medium text-[var(--color-text-primary)]">
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
                    <span className="text-sm text-[var(--color-text-secondary)]">Validation Loss</span>
                    <span className="text-sm font-medium text-[var(--color-text-primary)]">
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
              <h4 className="text-lg font-medium text-[var(--color-text-primary)] mb-[var(--spacing-md)]">Model Parameters</h4>
              <div className="space-y-[var(--spacing-sm)] text-sm">
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">Sequence Length</span>
                  <span className="text-[var(--color-text-primary)]">{selectedModel.parameters.sequenceLength}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">Epochs</span>
                  <span className="text-[var(--color-text-primary)]">{selectedModel.parameters.epochs}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">Batch Size</span>
                  <span className="text-[var(--color-text-primary)]">{selectedModel.parameters.batchSize}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">Learning Rate</span>
                  <span className="text-[var(--color-text-primary)]">{selectedModel.parameters.learningRate}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">Units</span>
                  <span className="text-[var(--color-text-primary)]">{selectedModel.parameters.units}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Backtest Results */}
          {selectedModel.performance.backtestResults && (
            <div>
              <h4 className="text-lg font-medium text-[var(--color-text-primary)] mb-[var(--spacing-md)]">Backtest Results</h4>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-[var(--spacing-md)]">
                <Card variant="outlined" padding="sm" className="text-center bg-[var(--color-surface)]">
                  <div className="text-2xl font-bold text-[var(--color-success)]">
                    {formatPercentage(selectedModel.performance.backtestResults.totalReturns * 100)}
                  </div>
                  <div className="text-sm text-[var(--color-text-muted)]">Total Returns</div>
                </Card>
                <Card variant="outlined" padding="sm" className="text-center bg-[var(--color-surface)]">
                  <div className="text-2xl font-bold text-[var(--color-info)]">
                    {selectedModel.performance.backtestResults.sharpeRatio.toFixed(2)}
                  </div>
                  <div className="text-sm text-[var(--color-text-muted)]">Sharpe Ratio</div>
                </Card>
                <Card variant="outlined" padding="sm" className="text-center bg-[var(--color-surface)]">
                  <div className="text-2xl font-bold text-[var(--color-error)]">
                    {formatPercentage(selectedModel.performance.backtestResults.maxDrawdown * 100)}
                  </div>
                  <div className="text-sm text-[var(--color-text-muted)]">Max Drawdown</div>
                </Card>
                <Card variant="outlined" padding="sm" className="text-center bg-[var(--color-surface)]">
                  <div className="text-2xl font-bold text-[var(--color-accent)]">
                    {formatPercentage(selectedModel.performance.backtestResults.winRate * 100)}
                  </div>
                  <div className="text-sm text-[var(--color-text-muted)]">Win Rate</div>
                </Card>
                <Card variant="outlined" padding="sm" className="text-center bg-[var(--color-surface)]">
                  <div className="text-2xl font-bold text-[var(--color-text-primary)]">
                    {selectedModel.performance.backtestResults.totalTrades}
                  </div>
                  <div className="text-sm text-[var(--color-text-muted)]">Total Trades</div>
                </Card>
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