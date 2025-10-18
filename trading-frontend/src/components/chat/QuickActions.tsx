'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  PieChart, 
  AlertTriangle, 
  BarChart3, 
  Target,
  Zap,
  Activity
} from 'lucide-react';
import Button from '@/components/ui/Button';

interface QuickAction {
  id: string;
  text: string;
  category: string;
  description: string;
  icon: React.ReactNode;
}

interface QuickActionsProps {
  contextType?: string;
  onActionSelect: (action: string) => void;
  className?: string;
}

const QuickActions: React.FC<QuickActionsProps> = ({
  contextType = 'general',
  onActionSelect,
  className = ''
}) => {
  const [suggestions, setSuggestions] = useState<QuickAction[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Default quick actions based on context
  const getDefaultActions = (context: string): QuickAction[] => {
    const baseActions: QuickAction[] = [
      {
        id: 'portfolio_summary',
        text: 'How is my portfolio performing?',
        category: 'portfolio',
        description: 'Get an overview of your current portfolio performance',
        icon: <PieChart className="w-4 h-4" />
      },
      {
        id: 'market_outlook',
        text: "What's the current market outlook?",
        category: 'market',
        description: 'Get insights on current market conditions and trends',
        icon: <TrendingUp className="w-4 h-4" />
      },
      {
        id: 'recent_signals',
        text: 'Explain my recent trading signals',
        category: 'signals',
        description: 'Get explanations for recent buy/sell signals',
        icon: <Target className="w-4 h-4" />
      },
      {
        id: 'risk_assessment',
        text: 'What are my current risk exposures?',
        category: 'risk',
        description: 'Analyze your portfolio\'s risk profile',
        icon: <AlertTriangle className="w-4 h-4" />
      }
    ];
    
    // Context-specific actions
    const contextActions: Record<string, QuickAction[]> = {
      portfolio: [
        {
          id: 'diversification',
          text: 'How well diversified is my portfolio?',
          category: 'portfolio',
          description: 'Analyze portfolio diversification across sectors',
          icon: <BarChart3 className="w-4 h-4" />
        },
        {
          id: 'performance_attribution',
          text: "What's driving my portfolio performance?",
          category: 'portfolio',
          description: 'Identify key contributors to returns',
          icon: <Activity className="w-4 h-4" />
        }
      ],
      signals: [
        {
          id: 'signal_confidence',
          text: 'How confident should I be in recent signals?',
          category: 'signals',
          description: 'Assess the reliability of recent trading signals',
          icon: <Zap className="w-4 h-4" />
        },
        {
          id: 'signal_timing',
          text: 'Is this a good time to act on signals?',
          category: 'signals',
          description: 'Evaluate market timing for signal execution',
          icon: <Target className="w-4 h-4" />
        }
      ],
      market: [
        {
          id: 'sector_analysis',
          text: 'Which sectors are performing well?',
          category: 'market',
          description: 'Analyze sector performance and trends',
          icon: <BarChart3 className="w-4 h-4" />
        },
        {
          id: 'volatility_analysis',
          text: 'How volatile is the current market?',
          category: 'market',
          description: 'Assess current market volatility levels',
          icon: <Activity className="w-4 h-4" />
        }
      ]
    };
    
    // Combine base actions with context-specific ones
    const contextSpecific = contextActions[context] || [];
    return [...baseActions, ...contextSpecific];
  };
  
  // Load suggestions from API or use defaults
  useEffect(() => {
    const loadSuggestions = async () => {
      setLoading(true);
      
      try {
        // Try to fetch from API
        const response = await fetch(`/api/v1/chat/suggestions?context_type=${contextType}`);
        
        if (response.ok) {
          const data = await response.json();
          const apiSuggestions = data.suggestions.map((suggestion: any) => ({
            ...suggestion,
            icon: getIconForCategory(suggestion.category)
          }));
          setSuggestions(apiSuggestions);
        } else {
          // Fallback to default actions
          setSuggestions(getDefaultActions(contextType));
        }
      } catch (error) {
        console.error('Failed to load suggestions:', error);
        // Fallback to default actions
        setSuggestions(getDefaultActions(contextType));
      } finally {
        setLoading(false);
      }
    };
    
    loadSuggestions();
  }, [contextType]);
  
  // Get icon for category
  const getIconForCategory = (category: string): React.ReactNode => {
    const iconMap: Record<string, React.ReactNode> = {
      portfolio: <PieChart className="w-4 h-4" />,
      market: <TrendingUp className="w-4 h-4" />,
      signals: <Target className="w-4 h-4" />,
      risk: <AlertTriangle className="w-4 h-4" />,
      performance: <Activity className="w-4 h-4" />,
      analysis: <BarChart3 className="w-4 h-4" />,
      general: <Zap className="w-4 h-4" />
    };
    
    return iconMap[category] || <Zap className="w-4 h-4" />;
  };
  
  // Group actions by category
  const groupedActions = suggestions.reduce((groups, action) => {
    const category = action.category;
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(action);
    return groups;
  }, {} as Record<string, QuickAction[]>);
  
  if (loading) {
    return (
      <div className={`space-y-3 ${className}`}>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Quick Actions
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-12 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }
  
  return (
    <div className={`space-y-3 ${className}`}>
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Quick Actions
      </h4>
      
      <div className="space-y-4">
        {Object.entries(groupedActions).map(([category, actions]) => (
          <div key={category}>
            <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
              {category}
            </h5>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {actions.map((action, index) => (
                <motion.div
                  key={action.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onActionSelect(action.text)}
                    className="w-full justify-start text-left h-auto p-3 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-200 dark:hover:border-blue-700"
                  >
                    <div className="flex items-start gap-2 w-full">
                      <div className="flex-shrink-0 mt-0.5 text-blue-500">
                        {action.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                          {action.text}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                          {action.description}
                        </div>
                      </div>
                    </div>
                  </Button>
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      {/* Custom Input Prompt */}
      <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
          Or ask me anything about your trading and portfolio
        </p>
      </div>
    </div>
  );
};

export default QuickActions;