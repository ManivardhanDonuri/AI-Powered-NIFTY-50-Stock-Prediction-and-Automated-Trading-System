"""
Learning and Adaptation Engine for AI Trading Assistant.

This engine implements continuous learning capabilities including prediction accuracy tracking,
automatic model retraining triggers, performance pattern identification, and model adjustment mechanisms.
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from ..logging.decorators import audit_operation, AuditContext
from ..logging.audit_logger import get_audit_logger
from ..data_models import PredictionResult
from data_fetcher import DataFetcher
from ml_models import MLModels
from ml_trainer import MLTrainer


class LearningAdaptationEngine:
    """
    Learning and adaptation engine for continuous model improvement.
    
    Tracks prediction accuracy, identifies performance patterns, and triggers
    automatic model retraining when performance degrades.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_logger = get_audit_logger()
        self.data_fetcher = DataFetcher()
        self.ml_models = MLModels()
        self.ml_trainer = MLTrainer()
        
        # Learning configuration
        self.accuracy_threshold = 0.6  # 60% accuracy threshold
        self.evaluation_period_days = 30  # Period for accuracy evaluation
        self.min_predictions_for_evaluation = 10  # Minimum predictions needed
        self.retraining_cooldown_days = 7  # Minimum days between retraining
        self.performance_pattern_window = 90  # Days to analyze for patterns
        
        # Model adjustment parameters
        self.confidence_adjustment_factor = 0.1
        self.ensemble_weight_adjustment = 0.05
        
        self.logger.info("Learning and Adaptation Engine initialized")

    @audit_operation(
        component="LearningAdaptationEngine",
        operation="track_prediction_accuracy",
        event_type="LEARNING",
        log_input=True,
        log_output=True,
        track_performance=True
    )
    async def track_prediction_accuracy(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Track prediction accuracy by comparing predictions with actual prices.
        
        Args:
            symbol: Stock symbol to track
            timeframe: Prediction timeframe to track
            
        Returns:
            Dict containing accuracy tracking results
        """
        try:
            self.logger.info(f"Tracking prediction accuracy for {symbol} {timeframe}")
            
            # Get current price to validate recent predictions
            current_data = self.data_fetcher.fetch_data(symbol, period="5d")
            if current_data is None or len(current_data) == 0:
                raise ValueError(f"Unable to fetch current data for {symbol}")
            
            current_price = float(current_data['Close'].iloc[-1])
            
            # Update prediction accuracy in audit logger
            await self.audit_logger.update_prediction_accuracy(symbol, timeframe, current_price)
            
            # Get accuracy statistics
            accuracy_stats = await self.audit_logger.get_prediction_accuracy(
                symbol=symbol, 
                timeframe=timeframe, 
                days=self.evaluation_period_days
            )
            
            # Analyze accuracy trends
            accuracy_trend = await self._analyze_accuracy_trend(symbol, timeframe)
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': current_price,
                'accuracy_statistics': accuracy_stats,
                'accuracy_trend': accuracy_trend,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Accuracy tracking completed for {symbol} {timeframe}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error tracking prediction accuracy: {str(e)}")
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    @audit_operation(
        component="LearningAdaptationEngine",
        operation="evaluate_retraining_need",
        event_type="LEARNING",
        log_input=True,
        log_output=True,
        track_performance=True
    )
    async def evaluate_retraining_need(self, symbol: str = None) -> Dict[str, Any]:
        """
        Evaluate if models need retraining based on accuracy thresholds.
        
        Args:
            symbol: Specific symbol to evaluate, or None for all symbols
            
        Returns:
            Dict containing retraining evaluation results
        """
        try:
            self.logger.info(f"Evaluating retraining need for {symbol or 'all symbols'}")
            
            # Get accuracy statistics
            accuracy_stats = await self.audit_logger.get_prediction_accuracy(
                symbol=symbol, 
                days=self.evaluation_period_days
            )
            
            retraining_recommendations = []
            
            for stat in accuracy_stats['accuracy_by_symbol_timeframe']:
                symbol_name = stat['symbol']
                timeframe = stat['timeframe']
                avg_accuracy = stat['avg_accuracy']
                validated_predictions = stat['validated_predictions']
                
                # Check if retraining is needed
                needs_retraining = (
                    validated_predictions >= self.min_predictions_for_evaluation and
                    avg_accuracy is not None and
                    avg_accuracy < self.accuracy_threshold
                )
                
                if needs_retraining:
                    # Check cooldown period
                    last_retraining = await self._get_last_retraining_date(symbol_name)
                    cooldown_expired = (
                        last_retraining is None or
                        (datetime.now() - last_retraining).days >= self.retraining_cooldown_days
                    )
                    
                    recommendation = {
                        'symbol': symbol_name,
                        'timeframe': timeframe,
                        'current_accuracy': avg_accuracy,
                        'threshold': self.accuracy_threshold,
                        'validated_predictions': validated_predictions,
                        'needs_retraining': needs_retraining,
                        'cooldown_expired': cooldown_expired,
                        'recommended_action': 'retrain' if cooldown_expired else 'wait_cooldown'
                    }
                    
                    retraining_recommendations.append(recommendation)
            
            result = {
                'evaluation_period_days': self.evaluation_period_days,
                'accuracy_threshold': self.accuracy_threshold,
                'retraining_recommendations': retraining_recommendations,
                'total_symbols_evaluated': len(accuracy_stats['accuracy_by_symbol_timeframe']),
                'symbols_needing_retraining': len([r for r in retraining_recommendations if r['recommended_action'] == 'retrain']),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Retraining evaluation completed: {result['symbols_needing_retraining']} symbols need retraining")
            return result
            
        except Exception as e:
            self.logger.error(f"Error evaluating retraining need: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    @audit_operation(
        component="LearningAdaptationEngine",
        operation="trigger_model_retraining",
        event_type="LEARNING",
        log_input=True,
        log_output=True,
        track_performance=True
    )
    async def trigger_model_retraining(self, symbol: str, model_types: List[str] = None) -> Dict[str, Any]:
        """
        Trigger automatic model retraining for a symbol.
        
        Args:
            symbol: Stock symbol to retrain models for
            model_types: List of model types to retrain (default: ["LSTM", "GRU"])
            
        Returns:
            Dict containing retraining results
        """
        if model_types is None:
            model_types = ["LSTM", "GRU"]
            
        try:
            self.logger.info(f"Triggering model retraining for {symbol}: {model_types}")
            
            retraining_results = []
            
            for model_type in model_types:
                try:
                    # Retrain the model
                    model, model_info = self.ml_trainer.retrain_model(symbol, model_type)
                    
                    if model is not None and model_info is not None:
                        result = {
                            'symbol': symbol,
                            'model_type': model_type,
                            'status': 'success',
                            'accuracy': model_info.get('accuracy', 0),
                            'f1_score': model_info.get('f1_score', 0),
                            'training_date': datetime.now().isoformat()
                        }
                        
                        # Log the retraining event
                        await self.audit_logger.log_audit_event({
                            'event_id': f"retrain_{symbol}_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            'event_type': 'MODEL_RETRAINING',
                            'component': 'LearningAdaptationEngine',
                            'operation': 'trigger_model_retraining',
                            'input_data': {'symbol': symbol, 'model_type': model_type},
                            'output_data': result,
                            'metadata': {'accuracy_improvement': True},
                            'timestamp': datetime.now(),
                            'success': True
                        })
                        
                    else:
                        result = {
                            'symbol': symbol,
                            'model_type': model_type,
                            'status': 'failed',
                            'error': 'Model training failed',
                            'training_date': datetime.now().isoformat()
                        }
                    
                    retraining_results.append(result)
                    
                except Exception as model_error:
                    self.logger.error(f"Error retraining {model_type} for {symbol}: {str(model_error)}")
                    retraining_results.append({
                        'symbol': symbol,
                        'model_type': model_type,
                        'status': 'error',
                        'error': str(model_error),
                        'training_date': datetime.now().isoformat()
                    })
            
            # Calculate overall success rate
            successful_retrainings = len([r for r in retraining_results if r['status'] == 'success'])
            success_rate = successful_retrainings / len(retraining_results) if retraining_results else 0
            
            result = {
                'symbol': symbol,
                'model_types_requested': model_types,
                'retraining_results': retraining_results,
                'successful_retrainings': successful_retrainings,
                'success_rate': success_rate,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Model retraining completed for {symbol}: {successful_retrainings}/{len(model_types)} successful")
            return result
            
        except Exception as e:
            self.logger.error(f"Error triggering model retraining: {str(e)}")
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    @audit_operation(
        component="LearningAdaptationEngine",
        operation="identify_performance_patterns",
        event_type="LEARNING",
        log_input=True,
        log_output=True,
        track_performance=True
    )
    async def identify_performance_patterns(self, symbol: str = None) -> Dict[str, Any]:
        """
        Identify patterns in prediction performance to guide model improvements.
        
        Args:
            symbol: Specific symbol to analyze, or None for all symbols
            
        Returns:
            Dict containing identified performance patterns
        """
        try:
            self.logger.info(f"Identifying performance patterns for {symbol or 'all symbols'}")
            
            # Get extended accuracy statistics
            accuracy_stats = await self.audit_logger.get_prediction_accuracy(
                symbol=symbol, 
                days=self.performance_pattern_window
            )
            
            patterns = []
            
            for stat in accuracy_stats['accuracy_by_symbol_timeframe']:
                symbol_name = stat['symbol']
                timeframe = stat['timeframe']
                
                # Analyze accuracy trends over time
                trend_analysis = await self._analyze_detailed_accuracy_trend(symbol_name, timeframe)
                
                # Identify specific patterns
                pattern_analysis = {
                    'symbol': symbol_name,
                    'timeframe': timeframe,
                    'trend_direction': trend_analysis['trend_direction'],
                    'trend_strength': trend_analysis['trend_strength'],
                    'volatility_pattern': trend_analysis['volatility_pattern'],
                    'confidence_correlation': trend_analysis['confidence_correlation'],
                    'recommendations': []
                }
                
                # Generate recommendations based on patterns
                if trend_analysis['trend_direction'] == 'declining':
                    pattern_analysis['recommendations'].append('Consider model retraining')
                    pattern_analysis['recommendations'].append('Review feature engineering')
                
                if trend_analysis['volatility_pattern'] == 'high':
                    pattern_analysis['recommendations'].append('Adjust confidence intervals')
                    pattern_analysis['recommendations'].append('Consider ensemble weight rebalancing')
                
                if trend_analysis['confidence_correlation'] < 0.3:
                    pattern_analysis['recommendations'].append('Recalibrate confidence scoring')
                
                patterns.append(pattern_analysis)
            
            # Identify cross-symbol patterns
            cross_symbol_patterns = await self._identify_cross_symbol_patterns(accuracy_stats)
            
            result = {
                'analysis_period_days': self.performance_pattern_window,
                'individual_patterns': patterns,
                'cross_symbol_patterns': cross_symbol_patterns,
                'total_symbols_analyzed': len(patterns),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Performance pattern analysis completed for {len(patterns)} symbol-timeframe combinations")
            return result
            
        except Exception as e:
            self.logger.error(f"Error identifying performance patterns: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    @audit_operation(
        component="LearningAdaptationEngine",
        operation="adjust_model_parameters",
        event_type="LEARNING",
        log_input=True,
        log_output=True,
        track_performance=True
    )
    async def adjust_model_parameters(self, symbol: str, adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust model parameters based on performance analysis.
        
        Args:
            symbol: Stock symbol to adjust parameters for
            adjustments: Dictionary of parameter adjustments to apply
            
        Returns:
            Dict containing adjustment results
        """
        try:
            self.logger.info(f"Adjusting model parameters for {symbol}: {adjustments}")
            
            adjustment_results = []
            
            # Adjust ensemble weights if requested
            if 'ensemble_weights' in adjustments:
                weight_adjustments = adjustments['ensemble_weights']
                for model_name, adjustment in weight_adjustments.items():
                    # This would typically update model configuration
                    # For now, we'll log the intended adjustment
                    adjustment_results.append({
                        'parameter': f'ensemble_weight_{model_name}',
                        'adjustment': adjustment,
                        'status': 'logged'
                    })
            
            # Adjust confidence scoring if requested
            if 'confidence_adjustment' in adjustments:
                confidence_adjustment = adjustments['confidence_adjustment']
                adjustment_results.append({
                    'parameter': 'confidence_scoring',
                    'adjustment': confidence_adjustment,
                    'status': 'logged'
                })
            
            # Adjust prediction intervals if requested
            if 'interval_adjustment' in adjustments:
                interval_adjustment = adjustments['interval_adjustment']
                adjustment_results.append({
                    'parameter': 'confidence_intervals',
                    'adjustment': interval_adjustment,
                    'status': 'logged'
                })
            
            result = {
                'symbol': symbol,
                'requested_adjustments': adjustments,
                'adjustment_results': adjustment_results,
                'total_adjustments': len(adjustment_results),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Model parameter adjustments completed for {symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error adjusting model parameters: {str(e)}")
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def _analyze_accuracy_trend(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Analyze accuracy trend for a specific symbol and timeframe."""
        try:
            # This would typically query historical accuracy data
            # For now, return a basic trend analysis
            return {
                'trend_direction': 'stable',
                'trend_strength': 0.5,
                'recent_accuracy': 0.75,
                'accuracy_variance': 0.1
            }
        except Exception as e:
            self.logger.error(f"Error analyzing accuracy trend: {str(e)}")
            return {
                'trend_direction': 'unknown',
                'trend_strength': 0.0,
                'recent_accuracy': 0.0,
                'accuracy_variance': 0.0
            }

    async def _analyze_detailed_accuracy_trend(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Perform detailed accuracy trend analysis."""
        try:
            # This would typically perform more sophisticated trend analysis
            # For now, return a comprehensive analysis structure
            return {
                'trend_direction': 'stable',
                'trend_strength': 0.6,
                'volatility_pattern': 'medium',
                'confidence_correlation': 0.7,
                'seasonal_patterns': [],
                'outlier_count': 2
            }
        except Exception as e:
            self.logger.error(f"Error in detailed accuracy trend analysis: {str(e)}")
            return {
                'trend_direction': 'unknown',
                'trend_strength': 0.0,
                'volatility_pattern': 'unknown',
                'confidence_correlation': 0.0,
                'seasonal_patterns': [],
                'outlier_count': 0
            }

    async def _identify_cross_symbol_patterns(self, accuracy_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Identify patterns across multiple symbols."""
        try:
            # Analyze patterns across all symbols
            symbol_accuracies = []
            for stat in accuracy_stats['accuracy_by_symbol_timeframe']:
                if stat['avg_accuracy'] is not None:
                    symbol_accuracies.append(stat['avg_accuracy'])
            
            if symbol_accuracies:
                overall_trend = 'improving' if np.mean(symbol_accuracies) > 0.7 else 'declining'
                accuracy_variance = np.var(symbol_accuracies)
            else:
                overall_trend = 'unknown'
                accuracy_variance = 0.0
            
            return {
                'overall_trend': overall_trend,
                'accuracy_variance': float(accuracy_variance),
                'consistent_performers': [],
                'underperformers': [],
                'market_correlation_patterns': []
            }
        except Exception as e:
            self.logger.error(f"Error identifying cross-symbol patterns: {str(e)}")
            return {
                'overall_trend': 'unknown',
                'accuracy_variance': 0.0,
                'consistent_performers': [],
                'underperformers': [],
                'market_correlation_patterns': []
            }

    async def _get_last_retraining_date(self, symbol: str) -> Optional[datetime]:
        """Get the last retraining date for a symbol."""
        try:
            # This would typically query the audit trail for retraining events
            # For now, return None to allow retraining
            return None
        except Exception as e:
            self.logger.error(f"Error getting last retraining date: {str(e)}")
            return None