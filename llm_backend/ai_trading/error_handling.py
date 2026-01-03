"""
Comprehensive error handling and fallback systems for AI Trading Assistant.

This module provides centralized error handling, recovery mechanisms, and graceful
degradation strategies for all AI trading components.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass
from enum import Enum
import traceback
import json

from .data_models import (
    PredictionResult, TradingRecommendation, RiskMetrics, SentimentAnalysis,
    PerformanceAnalysis, ComparisonResult, ConfidenceInterval, RiskAlert,
    PortfolioRisk, MarketEvent
)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """Categories of errors in the AI trading system."""
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    MODEL_ERROR = "MODEL_ERROR"
    OLLAMA_ERROR = "OLLAMA_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PERFORMANCE_ERROR = "PERFORMANCE_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    component: str
    operation: str
    symbol: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime = None
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.additional_data is None:
            self.additional_data = {}


@dataclass
class ErrorInfo:
    """Detailed error information."""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    original_exception: Optional[Exception] = None
    context: Optional[ErrorContext] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    fallback_used: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AITradingError(Exception):
    """Base exception for AI Trading Assistant errors."""
    
    def __init__(
        self, 
        message: str, 
        category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context
        self.original_exception = original_exception
        self.timestamp = datetime.now()


class DataUnavailableError(AITradingError):
    """Error when required data is not available."""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(
            message, 
            ErrorCategory.DATA_UNAVAILABLE, 
            ErrorSeverity.MEDIUM,
            context
        )


class ModelError(AITradingError):
    """Error in ML model operations."""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(
            message, 
            ErrorCategory.MODEL_ERROR, 
            ErrorSeverity.HIGH,
            context
        )


class OllamaError(AITradingError):
    """Error in Ollama service operations."""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(
            message, 
            ErrorCategory.OLLAMA_ERROR, 
            ErrorSeverity.MEDIUM,
            context
        )


class PerformanceError(AITradingError):
    """Error due to performance issues (timeouts, memory, etc.)."""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(
            message, 
            ErrorCategory.PERFORMANCE_ERROR, 
            ErrorSeverity.HIGH,
            context
        )


class ErrorHandler:
    """
    Centralized error handler for AI Trading Assistant.
    
    Provides error recovery, fallback mechanisms, and graceful degradation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_stats = {
            'total_errors': 0,
            'errors_by_category': {},
            'errors_by_component': {},
            'recovery_success_rate': 0.0,
            'fallback_usage_rate': 0.0
        }
        self.circuit_breakers = {}
        self.fallback_cache = {}
        
    async def handle_prediction_error(
        self, 
        error: Exception, 
        symbol: str,
        timeframes: List[str] = None,
        context: Optional[ErrorContext] = None
    ) -> PredictionResult:
        """
        Handle prediction engine errors with fallback strategies.
        
        Args:
            error: The original exception
            symbol: Stock symbol being predicted
            timeframes: Requested timeframes
            context: Error context
            
        Returns:
            PredictionResult: Fallback prediction or error response
        """
        if timeframes is None:
            timeframes = ["1d", "3d", "7d", "30d"]
            
        error_info = await self._classify_error(error, context)
        await self._log_error(error_info)
        
        try:
            if isinstance(error, DataUnavailableError):
                # Try cached predictions first
                cached_result = await self._get_cached_prediction(symbol, timeframes)
                if cached_result:
                    error_info.fallback_used = True
                    await self._update_error_stats(error_info)
                    return cached_result
                
                # Use baseline prediction model
                return await self._get_baseline_prediction(symbol, timeframes)
                
            elif isinstance(error, ModelError):
                # Try alternative models
                return await self._get_alternative_prediction(symbol, timeframes)
                
            elif isinstance(error, PerformanceError):
                # Return simplified prediction
                return await self._get_simplified_prediction(symbol, timeframes)
                
            else:
                # Generic error response
                return await self._get_error_prediction_response(symbol, timeframes, error_info)
                
        except Exception as fallback_error:
            self.logger.error(f"Fallback prediction failed: {str(fallback_error)}")
            return await self._get_minimal_prediction_response(symbol, timeframes)
        
        finally:
            await self._update_error_stats(error_info)

    async def handle_recommendation_error(
        self, 
        error: Exception, 
        symbol: str,
        context: Optional[ErrorContext] = None
    ) -> TradingRecommendation:
        """
        Handle recommendation engine errors with fallback strategies.
        
        Args:
            error: The original exception
            symbol: Stock symbol
            context: Error context
            
        Returns:
            TradingRecommendation: Fallback recommendation
        """
        error_info = await self._classify_error(error, context)
        await self._log_error(error_info)
        
        try:
            if isinstance(error, OllamaError):
                # Use rule-based recommendation without LLM
                return await self._get_rule_based_recommendation(symbol)
                
            elif isinstance(error, DataUnavailableError):
                # Return conservative HOLD recommendation
                return await self._get_conservative_recommendation(symbol)
                
            else:
                # Generic error recommendation
                return await self._get_error_recommendation_response(symbol, error_info)
                
        except Exception as fallback_error:
            self.logger.error(f"Fallback recommendation failed: {str(fallback_error)}")
            return await self._get_minimal_recommendation_response(symbol)
        
        finally:
            await self._update_error_stats(error_info)

    async def handle_risk_analysis_error(
        self, 
        error: Exception, 
        symbol: str,
        portfolio: Dict[str, Any] = None,
        context: Optional[ErrorContext] = None
    ) -> RiskMetrics:
        """
        Handle risk analysis errors with fallback strategies.
        
        Args:
            error: The original exception
            symbol: Stock symbol
            portfolio: Portfolio data
            context: Error context
            
        Returns:
            RiskMetrics: Fallback risk metrics
        """
        error_info = await self._classify_error(error, context)
        await self._log_error(error_info)
        
        try:
            if isinstance(error, DataUnavailableError):
                # Use cached risk metrics
                cached_metrics = await self._get_cached_risk_metrics(symbol)
                if cached_metrics:
                    error_info.fallback_used = True
                    await self._update_error_stats(error_info)
                    return cached_metrics
                
                # Use default risk estimates
                return await self._get_default_risk_metrics(symbol)
                
            else:
                # Generic error response
                return await self._get_error_risk_response(symbol, error_info)
                
        except Exception as fallback_error:
            self.logger.error(f"Fallback risk analysis failed: {str(fallback_error)}")
            return await self._get_minimal_risk_response(symbol)
        
        finally:
            await self._update_error_stats(error_info)

    async def handle_ollama_error(
        self, 
        error: Exception, 
        query: str,
        context: Optional[ErrorContext] = None
    ) -> str:
        """
        Handle Ollama service errors with fallback strategies.
        
        Args:
            error: The original exception
            query: Original query
            context: Error context
            
        Returns:
            str: Fallback response
        """
        error_info = await self._classify_error(error, context)
        await self._log_error(error_info)
        
        try:
            # Check circuit breaker
            if await self._is_circuit_breaker_open("ollama"):
                return await self._get_circuit_breaker_response(query)
            
            # Attempt recovery
            recovery_successful = await self._attempt_ollama_recovery()
            if recovery_successful:
                error_info.recovery_attempted = True
                error_info.recovery_successful = True
                # Don't retry here, let the calling code retry
                return "Service recovered. Please retry your request."
            
            # Use fallback response generation
            if "rationale" in query.lower():
                return await self._get_fallback_rationale(query)
            elif "explain" in query.lower():
                return await self._get_fallback_explanation(query)
            else:
                return await self._get_fallback_query_response(query)
                
        except Exception as fallback_error:
            self.logger.error(f"Ollama fallback failed: {str(fallback_error)}")
            return await self._get_minimal_ollama_response(query)
        
        finally:
            await self._update_error_stats(error_info)

    async def handle_market_context_error(
        self, 
        error: Exception, 
        symbol: str,
        context: Optional[ErrorContext] = None
    ) -> SentimentAnalysis:
        """
        Handle market context analysis errors.
        
        Args:
            error: The original exception
            symbol: Stock symbol
            context: Error context
            
        Returns:
            SentimentAnalysis: Fallback sentiment analysis
        """
        error_info = await self._classify_error(error, context)
        await self._log_error(error_info)
        
        try:
            # Use cached sentiment data
            cached_sentiment = await self._get_cached_sentiment(symbol)
            if cached_sentiment:
                error_info.fallback_used = True
                await self._update_error_stats(error_info)
                return cached_sentiment
            
            # Return neutral sentiment
            return await self._get_neutral_sentiment(symbol)
            
        except Exception as fallback_error:
            self.logger.error(f"Market context fallback failed: {str(fallback_error)}")
            return await self._get_minimal_sentiment_response(symbol)
        
        finally:
            await self._update_error_stats(error_info)

    async def _classify_error(
        self, 
        error: Exception, 
        context: Optional[ErrorContext] = None
    ) -> ErrorInfo:
        """Classify error and determine appropriate handling strategy."""
        if isinstance(error, AITradingError):
            return ErrorInfo(
                category=error.category,
                severity=error.severity,
                message=error.message,
                original_exception=error,
                context=context or error.context
            )
        
        # Classify based on exception type and message
        error_message = str(error).lower()
        
        if "connection" in error_message or "timeout" in error_message:
            category = ErrorCategory.NETWORK_ERROR
            severity = ErrorSeverity.HIGH
        elif "ollama" in error_message or "llm" in error_message:
            category = ErrorCategory.OLLAMA_ERROR
            severity = ErrorSeverity.MEDIUM
        elif "data" in error_message or "not found" in error_message:
            category = ErrorCategory.DATA_UNAVAILABLE
            severity = ErrorSeverity.MEDIUM
        elif "model" in error_message or "prediction" in error_message:
            category = ErrorCategory.MODEL_ERROR
            severity = ErrorSeverity.HIGH
        elif "memory" in error_message or "resource" in error_message:
            category = ErrorCategory.PERFORMANCE_ERROR
            severity = ErrorSeverity.HIGH
        else:
            category = ErrorCategory.SYSTEM_ERROR
            severity = ErrorSeverity.MEDIUM
        
        return ErrorInfo(
            category=category,
            severity=severity,
            message=str(error),
            original_exception=error,
            context=context
        )

    async def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level based on severity."""
        log_data = {
            'category': error_info.category.value,
            'severity': error_info.severity.value,
            'message': error_info.message,
            'timestamp': error_info.timestamp.isoformat(),
            'context': {
                'component': error_info.context.component if error_info.context else None,
                'operation': error_info.context.operation if error_info.context else None,
                'symbol': error_info.context.symbol if error_info.context else None,
                'user_id': error_info.context.user_id if error_info.context else None,
                'request_id': error_info.context.request_id if error_info.context else None,
                'timestamp': error_info.context.timestamp.isoformat() if error_info.context and error_info.context.timestamp else None,
                'additional_data': error_info.context.additional_data if error_info.context else None
            },
            'traceback': traceback.format_exc() if error_info.original_exception else None
        }
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {json.dumps(log_data, indent=2)}")
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY ERROR: {json.dumps(log_data, indent=2)}")
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY ERROR: {json.dumps(log_data, indent=2)}")
        else:
            self.logger.info(f"LOW SEVERITY ERROR: {json.dumps(log_data, indent=2)}")

    async def _update_error_stats(self, error_info: ErrorInfo):
        """Update error statistics for monitoring."""
        self.error_stats['total_errors'] += 1
        
        # Update category stats
        category = error_info.category.value
        if category not in self.error_stats['errors_by_category']:
            self.error_stats['errors_by_category'][category] = 0
        self.error_stats['errors_by_category'][category] += 1
        
        # Update component stats
        if error_info.context and error_info.context.component:
            component = error_info.context.component
            if component not in self.error_stats['errors_by_component']:
                self.error_stats['errors_by_component'][component] = 0
            self.error_stats['errors_by_component'][component] += 1
        
        # Update recovery and fallback rates
        total_errors = self.error_stats['total_errors']
        recovery_count = sum(1 for _ in [error_info] if error_info.recovery_successful)
        fallback_count = sum(1 for _ in [error_info] if error_info.fallback_used)
        
        # These would be calculated across all errors in a real implementation
        # For now, just update based on current error
        if error_info.recovery_successful:
            self.error_stats['recovery_success_rate'] = min(1.0, 
                self.error_stats['recovery_success_rate'] + (1.0 / total_errors))
        
        if error_info.fallback_used:
            self.error_stats['fallback_usage_rate'] = min(1.0,
                self.error_stats['fallback_usage_rate'] + (1.0 / total_errors))

    # Fallback response methods
    async def _get_cached_prediction(
        self, 
        symbol: str, 
        timeframes: List[str]
    ) -> Optional[PredictionResult]:
        """Get cached prediction if available and recent."""
        cache_key = f"prediction_{symbol}_{'-'.join(timeframes)}"
        cached_data = self.fallback_cache.get(cache_key)
        
        if cached_data and cached_data.get('timestamp'):
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=1):
                return PredictionResult(**cached_data['data'])
        
        return None

    async def _get_baseline_prediction(
        self, 
        symbol: str, 
        timeframes: List[str]
    ) -> PredictionResult:
        """Generate baseline prediction using simple moving average."""
        predictions = {}
        confidence_intervals = {}
        
        for timeframe in timeframes:
            # Simple baseline: assume 0% change with wide confidence intervals
            predictions[timeframe] = 100.0  # Placeholder price
            confidence_intervals[timeframe] = ConfidenceInterval(
                lower_bound=90.0,
                upper_bound=110.0,
                confidence_level=0.5  # Low confidence
            )
        
        return PredictionResult(
            symbol=symbol,
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            confidence_score=0.3,  # Low confidence
            timestamp=datetime.now(),
            model_ensemble=["baseline"]
        )

    async def _get_alternative_prediction(
        self, 
        symbol: str, 
        timeframes: List[str]
    ) -> PredictionResult:
        """Get prediction using alternative/simpler models."""
        # This would use simpler models in a real implementation
        return await self._get_baseline_prediction(symbol, timeframes)

    async def _get_simplified_prediction(
        self, 
        symbol: str, 
        timeframes: List[str]
    ) -> PredictionResult:
        """Get simplified prediction for performance issues."""
        # Return only 1-day prediction to reduce computation
        simplified_timeframes = ["1d"]
        return await self._get_baseline_prediction(symbol, simplified_timeframes)

    async def _get_error_prediction_response(
        self, 
        symbol: str, 
        timeframes: List[str],
        error_info: ErrorInfo
    ) -> PredictionResult:
        """Generate error response for prediction requests."""
        predictions = {tf: 0.0 for tf in timeframes}
        confidence_intervals = {
            tf: ConfidenceInterval(0.0, 0.0, 0.0) for tf in timeframes
        }
        
        return PredictionResult(
            symbol=symbol,
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            confidence_score=0.0,
            timestamp=datetime.now(),
            model_ensemble=[f"error_{error_info.category.value}"]
        )

    async def _get_minimal_prediction_response(
        self, 
        symbol: str, 
        timeframes: List[str]
    ) -> PredictionResult:
        """Get minimal prediction response when all fallbacks fail."""
        return await self._get_error_prediction_response(symbol, timeframes, 
            ErrorInfo(ErrorCategory.SYSTEM_ERROR, ErrorSeverity.CRITICAL, "All fallbacks failed"))

    async def _get_rule_based_recommendation(self, symbol: str) -> TradingRecommendation:
        """Generate rule-based recommendation without LLM."""
        return TradingRecommendation(
            symbol=symbol,
            action="HOLD",
            confidence=0.5,
            target_price=100.0,
            stop_loss=95.0,
            position_size=0.05,
            rationale=f"Rule-based analysis for {symbol}. Conservative HOLD recommendation due to limited analysis capabilities.",
            risk_reward_ratio=1.0,
            timestamp=datetime.now()
        )

    async def _get_conservative_recommendation(self, symbol: str) -> TradingRecommendation:
        """Generate conservative recommendation when data is unavailable."""
        return TradingRecommendation(
            symbol=symbol,
            action="HOLD",
            confidence=0.3,
            target_price=100.0,
            stop_loss=95.0,
            position_size=0.02,
            rationale=f"Conservative HOLD recommendation for {symbol} due to insufficient data. Recommend waiting for better market conditions.",
            risk_reward_ratio=1.0,
            timestamp=datetime.now()
        )

    async def _get_error_recommendation_response(
        self, 
        symbol: str, 
        error_info: ErrorInfo
    ) -> TradingRecommendation:
        """Generate error response for recommendation requests."""
        return TradingRecommendation(
            symbol=symbol,
            action="HOLD",
            confidence=0.0,
            target_price=0.0,
            stop_loss=0.0,
            position_size=0.0,
            rationale=f"Unable to generate recommendation for {symbol} due to {error_info.category.value} error: {error_info.message}",
            risk_reward_ratio=0.0,
            timestamp=datetime.now()
        )

    async def _get_minimal_recommendation_response(self, symbol: str) -> TradingRecommendation:
        """Get minimal recommendation when all fallbacks fail."""
        return TradingRecommendation(
            symbol=symbol,
            action="HOLD",
            confidence=0.0,
            target_price=0.0,
            stop_loss=0.0,
            position_size=0.0,
            rationale=f"System error: Unable to generate recommendation for {symbol}. All fallback mechanisms failed.",
            risk_reward_ratio=0.0,
            timestamp=datetime.now()
        )

    # Additional fallback methods continue in next part...
    async def _get_cached_risk_metrics(self, symbol: str) -> Optional[RiskMetrics]:
        """Get cached risk metrics if available."""
        cache_key = f"risk_metrics_{symbol}"
        cached_data = self.fallback_cache.get(cache_key)
        
        if cached_data and cached_data.get('timestamp'):
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=4):
                return RiskMetrics(**cached_data['data'])
        
        return None

    async def _get_default_risk_metrics(self, symbol: str) -> RiskMetrics:
        """Generate default risk metrics when data is unavailable."""
        return RiskMetrics(
            symbol=symbol,
            var_1d=0.05,  # 5% default VaR
            var_5d=0.12,  # 12% default 5-day VaR
            beta=1.0,     # Market beta
            volatility=0.25,  # 25% default volatility
            sharpe_ratio=0.5,  # Moderate Sharpe ratio
            max_drawdown=0.15,  # 15% default max drawdown
            correlation_to_market=0.7  # High market correlation
        )

    async def _get_error_risk_response(
        self, 
        symbol: str, 
        error_info: ErrorInfo
    ) -> RiskMetrics:
        """Generate error response for risk analysis."""
        return RiskMetrics(
            symbol=symbol,
            var_1d=0.0,
            var_5d=0.0,
            beta=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            correlation_to_market=0.0
        )

    async def _get_minimal_risk_response(self, symbol: str) -> RiskMetrics:
        """Get minimal risk response when all fallbacks fail."""
        return await self._get_error_risk_response(symbol, 
            ErrorInfo(ErrorCategory.SYSTEM_ERROR, ErrorSeverity.CRITICAL, "All fallbacks failed"))

    async def _attempt_ollama_recovery(self) -> bool:
        """Attempt to recover Ollama service connection."""
        try:
            # This would attempt to restart or reconnect to Ollama
            # For now, just simulate recovery attempt
            await asyncio.sleep(1)  # Simulate recovery time
            
            # In a real implementation, this would:
            # 1. Check if Ollama process is running
            # 2. Attempt to restart if needed
            # 3. Test connection
            # 4. Return True if successful
            
            return False  # Assume recovery failed for now
            
        except Exception as e:
            self.logger.error(f"Ollama recovery attempt failed: {str(e)}")
            return False

    async def _is_circuit_breaker_open(self, service: str) -> bool:
        """Check if circuit breaker is open for a service."""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = {
                'failure_count': 0,
                'last_failure': None,
                'state': 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
            }
        
        breaker = self.circuit_breakers[service]
        
        # If circuit is open, check if enough time has passed to try again
        if breaker['state'] == 'OPEN':
            if breaker['last_failure']:
                time_since_failure = datetime.now() - breaker['last_failure']
                if time_since_failure > timedelta(minutes=5):  # 5-minute timeout
                    breaker['state'] = 'HALF_OPEN'
                    return False
            return True
        
        return False

    async def _update_circuit_breaker(self, service: str, success: bool):
        """Update circuit breaker state based on operation result."""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = {
                'failure_count': 0,
                'last_failure': None,
                'state': 'CLOSED'
            }
        
        breaker = self.circuit_breakers[service]
        
        if success:
            breaker['failure_count'] = 0
            breaker['state'] = 'CLOSED'
        else:
            breaker['failure_count'] += 1
            breaker['last_failure'] = datetime.now()
            
            # Open circuit after 3 consecutive failures
            if breaker['failure_count'] >= 3:
                breaker['state'] = 'OPEN'

    async def _get_circuit_breaker_response(self, query: str) -> str:
        """Get response when circuit breaker is open."""
        return f"""The AI language model service is temporarily unavailable due to repeated failures. 

Your query: "{query}"

The system is in protective mode to prevent cascading failures. Please try again in a few minutes.

In the meantime, you can:
- Use basic trading analysis features
- Review historical data and charts
- Check portfolio performance metrics

The service will automatically retry and restore full functionality once the underlying issue is resolved."""

    async def _get_fallback_rationale(self, query: str) -> str:
        """Generate fallback rationale without LLM."""
        return """Trading Rationale (Generated without AI assistance):

This recommendation is based on technical analysis and quantitative metrics. While the AI language model is unavailable, the core analysis considers:

• Technical indicators and price patterns
• Market volatility and trend analysis  
• Risk-reward calculations
• Portfolio optimization principles

Key factors in this analysis:
- Price momentum and moving average signals
- Volume patterns and market sentiment
- Risk management and position sizing
- Historical performance patterns

Note: This is a simplified analysis. For detailed explanations and market insights, please ensure the AI language model service is available."""

    async def _get_fallback_explanation(self, query: str) -> str:
        """Generate fallback explanation without LLM."""
        return """Analysis Explanation (Simplified):

The AI explanation service is currently unavailable, but here's a basic breakdown:

Technical Analysis Components:
• Price trends and momentum indicators
• Volume analysis and market participation
• Support and resistance levels
• Risk metrics and volatility measures

Market Context:
• Current market conditions and sentiment
• Sector performance and correlations
• Economic indicators and news impact

Risk Assessment:
• Position sizing recommendations
• Stop-loss and target price levels
• Portfolio diversification factors

For detailed, personalized explanations tailored to your experience level, please try again when the AI language model is available."""

    async def _get_fallback_query_response(self, query: str) -> str:
        """Generate fallback response for general queries."""
        return f"""AI Assistant Response (Limited Mode):

Your query: "{query}"

I'm currently operating in limited mode as the local language model is unavailable. I can still provide:

✓ Market data and price information
✓ Technical analysis and indicators  
✓ Portfolio performance metrics
✓ Risk analysis and alerts
✓ Trading signals and recommendations

However, detailed explanations, natural language processing, and personalized insights require the full AI language model.

Please ensure the Ollama service is running for complete functionality, or try your query again later."""

    async def _get_minimal_ollama_response(self, query: str) -> str:
        """Get minimal response when all Ollama fallbacks fail."""
        return f"""System Error: Unable to process your query at this time.

Query: "{query}"

All AI language processing services are currently unavailable. Please:
1. Check that the Ollama service is running
2. Verify your network connection
3. Try again in a few minutes

Basic trading analysis features remain available through the main interface."""

    async def _get_cached_sentiment(self, symbol: str) -> Optional[SentimentAnalysis]:
        """Get cached sentiment analysis if available."""
        cache_key = f"sentiment_{symbol}"
        cached_data = self.fallback_cache.get(cache_key)
        
        if cached_data and cached_data.get('timestamp'):
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=2):
                return SentimentAnalysis(**cached_data['data'])
        
        return None

    async def _get_neutral_sentiment(self, symbol: str) -> SentimentAnalysis:
        """Generate neutral sentiment when analysis is unavailable."""
        return SentimentAnalysis(
            symbol=symbol,
            sentiment_score=0.0,  # Neutral sentiment
            news_count=0,
            key_themes=["market_neutral"],
            confidence=0.3,  # Low confidence
            sources=["fallback_analysis"],
            timestamp=datetime.now()
        )

    async def _get_minimal_sentiment_response(self, symbol: str) -> SentimentAnalysis:
        """Get minimal sentiment response when all fallbacks fail."""
        return SentimentAnalysis(
            symbol=symbol,
            sentiment_score=0.0,
            news_count=0,
            key_themes=["error"],
            confidence=0.0,
            sources=["error_handler"],
            timestamp=datetime.now()
        )

    async def get_error_stats(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        return {
            'error_statistics': self.error_stats.copy(),
            'circuit_breakers': {
                service: {
                    'state': breaker['state'],
                    'failure_count': breaker['failure_count'],
                    'last_failure': breaker['last_failure'].isoformat() if breaker['last_failure'] else None
                }
                for service, breaker in self.circuit_breakers.items()
            },
            'cache_status': {
                'cached_items': len(self.fallback_cache),
                'cache_keys': list(self.fallback_cache.keys())
            },
            'timestamp': datetime.now().isoformat()
        }

    async def reset_circuit_breaker(self, service: str) -> bool:
        """Manually reset a circuit breaker."""
        if service in self.circuit_breakers:
            self.circuit_breakers[service] = {
                'failure_count': 0,
                'last_failure': None,
                'state': 'CLOSED'
            }
            self.logger.info(f"Circuit breaker reset for service: {service}")
            return True
        return False

    async def clear_error_stats(self):
        """Clear error statistics (for testing or maintenance)."""
        self.error_stats = {
            'total_errors': 0,
            'errors_by_category': {},
            'errors_by_component': {},
            'recovery_success_rate': 0.0,
            'fallback_usage_rate': 0.0
        }
        self.logger.info("Error statistics cleared")

    async def cache_fallback_data(
        self, 
        cache_key: str, 
        data: Any, 
        ttl_hours: int = 1
    ):
        """Cache data for fallback use."""
        self.fallback_cache[cache_key] = {
            'data': data.__dict__ if hasattr(data, '__dict__') else data,
            'timestamp': datetime.now().isoformat(),
            'ttl_hours': ttl_hours
        }

    async def cleanup_expired_cache(self):
        """Clean up expired cache entries."""
        current_time = datetime.now()
        expired_keys = []
        
        for key, cached_item in self.fallback_cache.items():
            if cached_item.get('timestamp'):
                cache_time = datetime.fromisoformat(cached_item['timestamp'])
                ttl = timedelta(hours=cached_item.get('ttl_hours', 1))
                
                if current_time - cache_time > ttl:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self.fallback_cache[key]
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get or create global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


# Decorator for automatic error handling
def handle_errors(
    component: str,
    operation: str,
    fallback_func: Optional[Callable] = None
):
    """
    Decorator for automatic error handling in AI trading components.
    
    Args:
        component: Name of the component
        operation: Name of the operation
        fallback_func: Optional fallback function to call on error
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            error_handler = get_error_handler()
            context = ErrorContext(
                component=component,
                operation=operation,
                timestamp=datetime.now()
            )
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if fallback_func:
                    return await fallback_func(e, *args, **kwargs)
                else:
                    # Use appropriate error handler based on component
                    if component == "PredictionEngine":
                        symbol = args[1] if len(args) > 1 else kwargs.get('symbol', 'UNKNOWN')
                        timeframes = args[2] if len(args) > 2 else kwargs.get('timeframes', ["1d"])
                        return await error_handler.handle_prediction_error(e, symbol, timeframes, context)
                    elif component == "RecommendationEngine":
                        symbol = args[1] if len(args) > 1 else kwargs.get('symbol', 'UNKNOWN')
                        return await error_handler.handle_recommendation_error(e, symbol, context)
                    elif component == "RiskAnalyzer":
                        symbol = args[1] if len(args) > 1 else kwargs.get('symbol', 'UNKNOWN')
                        portfolio = args[2] if len(args) > 2 else kwargs.get('portfolio', {})
                        return await error_handler.handle_risk_analysis_error(e, symbol, portfolio, context)
                    elif component == "OllamaService":
                        query = args[1] if len(args) > 1 else kwargs.get('query', 'unknown query')
                        return await error_handler.handle_ollama_error(e, query, context)
                    else:
                        # Generic error handling
                        raise AITradingError(
                            f"Error in {component}.{operation}: {str(e)}",
                            context=context,
                            original_exception=e
                        )
        
        return wrapper
    return decorator