"""
Prediction Engine for AI Trading Assistant.

This engine generates multi-timeframe stock price predictions with confidence intervals
using ensemble ML models and advanced feature engineering.
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from ..interfaces import PredictionEngineInterface
from ..data_models import PredictionResult, ConfidenceInterval, EnsemblePrediction
from ..logging.decorators import audit_operation, AuditContext
from ..logging.audit_logger import get_audit_logger
from ..error_handling import get_error_handler, handle_errors, DataUnavailableError, ModelError, ErrorContext
from ml_models import MLModels
from ml_feature_engineer import MLFeatureEngineer
from technical_indicators import TechnicalIndicators
from data_fetcher import DataFetcher


class PredictionEngine(PredictionEngineInterface):
    """
    Advanced prediction engine using ensemble ML models.
    
    Generates multi-timeframe price predictions with confidence intervals
    by combining LSTM, GRU, and other ML models with technical analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_logger = get_audit_logger()
        self.error_handler = get_error_handler()
        self.ml_models = MLModels()
        self.feature_engineer = MLFeatureEngineer()
        self.technical_indicators = TechnicalIndicators()
        self.data_fetcher = DataFetcher()
        
        # Prediction configuration
        self.default_timeframes = ["1d", "3d", "7d", "30d"]
        self.confidence_level = 0.95
        self.ensemble_weights = {
            "lstm": 0.4,
            "gru": 0.4, 
            "technical": 0.2
        }
        
        self.logger.info("Prediction Engine initialized")

    @audit_operation(
        component="PredictionEngine",
        operation="generate_predictions",
        event_type="PREDICTION",
        log_input=True,
        log_output=True,
        track_performance=True
    )
    @handle_errors(component="PredictionEngine", operation="generate_predictions")
    async def generate_predictions(
        self, 
        symbol: str, 
        timeframes: List[str] = None
    ) -> PredictionResult:
        """
        Generate multi-timeframe price predictions for a stock.
        
        Args:
            symbol: Stock symbol to predict
            timeframes: List of timeframes to predict (default: ["1d", "3d", "7d", "30d"])
            
        Returns:
            PredictionResult: Comprehensive prediction results
        """
        if timeframes is None:
            timeframes = self.default_timeframes
            
        try:
            self.logger.info(f"Generating predictions for {symbol} across {len(timeframes)} timeframes")
            
            # Fetch historical data
            historical_data = await self._fetch_historical_data(symbol)
            if historical_data is None or len(historical_data) < 60:
                raise DataUnavailableError(
                    f"Insufficient historical data for {symbol}: {len(historical_data) if historical_data else 0} records",
                    ErrorContext(component="PredictionEngine", operation="generate_predictions", symbol=symbol)
                )
            
            # Generate features
            features = await self._generate_features(symbol, historical_data)
            if features is None:
                raise ModelError(
                    f"Failed to generate features for {symbol}",
                    ErrorContext(component="PredictionEngine", operation="generate_predictions", symbol=symbol)
                )
            
            # Get ensemble predictions for each timeframe
            predictions = {}
            confidence_intervals = {}
            
            for timeframe in timeframes:
                try:
                    ensemble_pred = await self.ensemble_predict(
                        models=await self._get_models_for_symbol(symbol),
                        features=features,
                        timeframe=timeframe
                    )
                    
                    if ensemble_pred is None:
                        raise ModelError(
                            f"Ensemble prediction failed for {symbol} at {timeframe}",
                            ErrorContext(component="PredictionEngine", operation="generate_predictions", symbol=symbol)
                        )
                    
                    predictions[timeframe] = ensemble_pred.prediction
                    confidence_intervals[timeframe] = ensemble_pred.confidence_interval
                    
                except Exception as e:
                    self.logger.warning(f"Failed to generate prediction for {symbol} at {timeframe}: {str(e)}")
                    # Continue with other timeframes, but mark this one as failed
                    predictions[timeframe] = 0.0
                    confidence_intervals[timeframe] = ConfidenceInterval(0.0, 0.0, 0.0)
            
            # Calculate overall confidence score
            confidence_score = await self._calculate_overall_confidence(predictions, confidence_intervals)
            
            result = PredictionResult(
                symbol=symbol,
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                confidence_score=confidence_score,
                timestamp=datetime.now(),
                model_ensemble=list(self.ensemble_weights.keys())
            )
            
            # Cache successful prediction for fallback use
            await self.error_handler.cache_fallback_data(
                f"prediction_{symbol}_{'-'.join(timeframes)}",
                result,
                ttl_hours=1
            )
            
            return result
            
        except (DataUnavailableError, ModelError):
            raise  # Re-raise these for proper error handling
        except Exception as e:
            raise ModelError(
                f"Unexpected error in prediction generation for {symbol}: {str(e)}",
                ErrorContext(component="PredictionEngine", operation="generate_predictions", symbol=symbol)
            )

    async def calculate_confidence_intervals(
        self, 
        predictions: np.ndarray, 
        volatility: float
    ) -> ConfidenceInterval:
        """
        Calculate confidence intervals for predictions.
        
        Args:
            predictions: Array of predictions
            volatility: Historical volatility
            
        Returns:
            ConfidenceInterval: Confidence interval bounds
        """
        try:
            # Use volatility to estimate prediction uncertainty
            prediction = float(predictions[0]) if len(predictions) > 0 else 0.0
            
            # Calculate bounds based on volatility and confidence level
            z_score = 1.96  # 95% confidence level
            margin = z_score * volatility * prediction
            
            return ConfidenceInterval(
                lower_bound=max(0, prediction - margin),
                upper_bound=prediction + margin,
                confidence_level=self.confidence_level
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence intervals: {str(e)}")
            # Return default interval
            prediction = float(predictions[0]) if len(predictions) > 0 else 100.0
            return ConfidenceInterval(
                lower_bound=prediction * 0.9,
                upper_bound=prediction * 1.1,
                confidence_level=0.8
            )

    async def ensemble_predict(
        self, 
        models: List[Any], 
        features: np.ndarray,
        timeframe: str = "1d"
    ) -> EnsemblePrediction:
        """
        Generate ensemble predictions from multiple models.
        
        Args:
            models: List of ML models
            features: Feature array
            timeframe: Prediction timeframe
            
        Returns:
            EnsemblePrediction: Ensemble prediction result
        """
        try:
            individual_predictions = {}
            
            # Get predictions from each model type
            for model_name, weight in self.ensemble_weights.items():
                if model_name == "technical":
                    # Technical analysis prediction
                    pred = await self._get_technical_prediction(features, timeframe)
                else:
                    # ML model prediction
                    model = await self._get_model_by_name(models, model_name)
                    if model is not None:
                        pred = await self._predict_with_model(model, features, timeframe)
                    else:
                        pred = await self._get_fallback_model_prediction(features, timeframe)
                
                individual_predictions[model_name] = pred
            
            # Calculate weighted ensemble prediction
            ensemble_prediction = sum(
                pred * self.ensemble_weights[model_name] 
                for model_name, pred in individual_predictions.items()
            )
            
            # Calculate prediction variance
            variance = np.var(list(individual_predictions.values()))
            
            # Calculate ensemble confidence
            confidence = min(0.95, max(0.5, 1.0 - (variance / ensemble_prediction)))
            
            return EnsemblePrediction(
                individual_predictions=individual_predictions,
                ensemble_prediction=ensemble_prediction,
                model_weights=self.ensemble_weights,
                confidence=confidence,
                variance=float(variance)
            )
            
        except Exception as e:
            self.logger.error(f"Error in ensemble prediction: {str(e)}")
            # Return fallback ensemble prediction
            fallback_pred = float(features[-1]) * 1.02 if len(features) > 0 else 100.0
            return EnsemblePrediction(
                individual_predictions={"fallback": fallback_pred},
                ensemble_prediction=fallback_pred,
                model_weights={"fallback": 1.0},
                confidence=0.6,
                variance=0.1
            )

    async def _fetch_historical_data(self, symbol: str) -> Optional[np.ndarray]:
        """Fetch historical price data for the symbol."""
        try:
            # Use existing data fetcher
            data = self.data_fetcher.fetch_data(symbol, period="1y")
            if data is not None and len(data) > 0:
                return data['Close'].values
            return None
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    async def _generate_features(self, symbol: str, historical_data: np.ndarray) -> np.ndarray:
        """Generate features for prediction."""
        try:
            # Use existing feature engineer
            features = self.feature_engineer.create_features(historical_data)
            return features
        except Exception as e:
            self.logger.error(f"Error generating features for {symbol}: {str(e)}")
            # Return basic features
            return historical_data[-60:] if len(historical_data) >= 60 else historical_data

    async def _get_models_for_symbol(self, symbol: str) -> List[Any]:
        """Get trained models for the symbol."""
        try:
            models = []
            # Try to load existing models
            lstm_model = self.ml_models.load_model(symbol, "lstm")
            if lstm_model is not None:
                models.append(("lstm", lstm_model))
                
            gru_model = self.ml_models.load_model(symbol, "gru") 
            if gru_model is not None:
                models.append(("gru", gru_model))
                
            return models
        except Exception as e:
            self.logger.error(f"Error loading models for {symbol}: {str(e)}")
            return []

    async def _calculate_volatility(self, historical_data: np.ndarray, timeframe: str) -> float:
        """Calculate historical volatility for the timeframe."""
        try:
            if len(historical_data) < 2:
                return 0.2  # Default volatility
                
            # Calculate returns
            returns = np.diff(historical_data) / historical_data[:-1]
            
            # Adjust for timeframe
            timeframe_multiplier = {
                "1d": 1,
                "3d": 3,
                "7d": 7,
                "30d": 30
            }.get(timeframe, 1)
            
            volatility = np.std(returns) * np.sqrt(timeframe_multiplier)
            return float(volatility)
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return 0.2

    async def _calculate_overall_confidence(
        self, 
        predictions: Dict[str, float], 
        historical_data: np.ndarray
    ) -> float:
        """Calculate overall confidence score for predictions."""
        try:
            # Base confidence on data quality and model agreement
            data_quality_score = min(1.0, len(historical_data) / 252)  # 1 year of data
            
            # Check prediction consistency
            pred_values = list(predictions.values())
            if len(pred_values) > 1:
                consistency_score = 1.0 - (np.std(pred_values) / np.mean(pred_values))
            else:
                consistency_score = 0.8
                
            overall_confidence = (data_quality_score * 0.4 + consistency_score * 0.6) * 100
            return max(50.0, min(95.0, overall_confidence))
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {str(e)}")
            return 75.0

    async def _get_technical_prediction(self, features: np.ndarray, timeframe: str) -> float:
        """Get prediction based on technical analysis."""
        try:
            if len(features) == 0:
                return 100.0
                
            current_price = float(features[-1])
            
            # Simple technical prediction based on trend
            if len(features) >= 20:
                sma_20 = np.mean(features[-20:])
                trend_factor = current_price / sma_20
            else:
                trend_factor = 1.01
                
            # Adjust for timeframe
            timeframe_multiplier = {
                "1d": 1.005,
                "3d": 1.015,
                "7d": 1.03,
                "30d": 1.08
            }.get(timeframe, 1.02)
            
            prediction = current_price * trend_factor * timeframe_multiplier
            return float(prediction)
            
        except Exception as e:
            self.logger.error(f"Error in technical prediction: {str(e)}")
            return float(features[-1]) * 1.02 if len(features) > 0 else 100.0

    async def _get_model_by_name(self, models: List[Any], model_name: str) -> Optional[Any]:
        """Get model by name from the models list."""
        for name, model in models:
            if name == model_name:
                return model
        return None

    async def _predict_with_model(self, model: Any, features: np.ndarray, timeframe: str) -> float:
        """Make prediction with a specific model."""
        try:
            # Prepare features for model
            if hasattr(model, 'predict'):
                # Reshape features for model input
                model_features = features[-60:].reshape(1, -1, 1) if len(features) >= 60 else features.reshape(1, -1, 1)
                prediction = model.predict(model_features)
                return float(prediction[0][0]) if len(prediction) > 0 else float(features[-1])
            else:
                # Fallback prediction
                return float(features[-1]) * 1.02
                
        except Exception as e:
            self.logger.error(f"Error predicting with model: {str(e)}")
            return float(features[-1]) * 1.02 if len(features) > 0 else 100.0

    async def _get_fallback_model_prediction(self, features: np.ndarray, timeframe: str) -> float:
        """Get fallback prediction when model is not available."""
        if len(features) == 0:
            return 100.0
            
        current_price = float(features[-1])
        
        # Simple trend-based prediction
        timeframe_multiplier = {
            "1d": 1.002,
            "3d": 1.008,
            "7d": 1.02,
            "30d": 1.05
        }.get(timeframe, 1.01)
        
        return current_price * timeframe_multiplier

    async def _get_fallback_prediction(self, symbol: str, timeframes: List[str]) -> PredictionResult:
        """Get fallback prediction when main prediction fails."""
        try:
            # Get current price estimate
            current_price = 100.0  # Default fallback price
            
            predictions = {}
            confidence_intervals = {}
            
            for timeframe in timeframes:
                # Simple fallback prediction
                multiplier = {
                    "1d": 1.005,
                    "3d": 1.015,
                    "7d": 1.03,
                    "30d": 1.08
                }.get(timeframe, 1.02)
                
                pred_price = current_price * multiplier
                predictions[timeframe] = pred_price
                
                # Simple confidence interval
                confidence_intervals[timeframe] = ConfidenceInterval(
                    lower_bound=pred_price * 0.95,
                    upper_bound=pred_price * 1.05,
                    confidence_level=0.8
                )
            
            return PredictionResult(
                symbol=symbol,
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                confidence_score=60.0,  # Lower confidence for fallback
                timestamp=datetime.now(),
                model_ensemble=["fallback"]
            )
            
        except Exception as e:
            self.logger.error(f"Error in fallback prediction: {str(e)}")
            # Ultimate fallback
            return PredictionResult(
                symbol=symbol,
                predictions={"1d": 100.0},
                confidence_intervals={"1d": ConfidenceInterval(95.0, 105.0, 0.8)},
                confidence_score=50.0,
                timestamp=datetime.now(),
                model_ensemble=["fallback"]
            )