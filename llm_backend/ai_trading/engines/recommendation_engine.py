"""
Recommendation Engine for AI Trading Assistant.

This engine generates intelligent buy/sell recommendations with detailed rationale
using Ollama for natural language generation and comprehensive analysis.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from ..interfaces import RecommendationEngineInterface
from ..data_models import TradingRecommendation, PredictionResult, RiskAssessment, PositionSize
from ..logging.decorators import audit_operation, AuditContext
from ..logging.audit_logger import get_audit_logger
from ..error_handling import get_error_handler, handle_errors, OllamaError, DataUnavailableError, ErrorContext
from ...services.ollama_service import get_ollama_service


class RecommendationEngine(RecommendationEngineInterface):
    """
    Advanced recommendation engine with Ollama integration.
    
    Generates buy/sell/hold recommendations with detailed rationale
    by analyzing predictions, risk metrics, and market conditions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_logger = get_audit_logger()
        self.error_handler = get_error_handler()
        self.ollama_service = get_ollama_service()
        
        # Recommendation thresholds
        self.buy_threshold = 0.7
        self.sell_threshold = 0.3
        self.high_confidence_threshold = 0.8
        self.low_confidence_threshold = 0.7
        
        # Risk management parameters
        self.max_position_size = 0.1  # 10% of portfolio
        self.default_stop_loss_pct = 0.08  # 8% stop loss
        self.min_risk_reward_ratio = 1.5
        
        self.logger.info("Recommendation Engine initialized")

    @audit_operation(
        component="RecommendationEngine",
        operation="generate_recommendation",
        event_type="RECOMMENDATION",
        log_input=True,
        log_output=True,
        track_performance=True
    )
    @handle_errors(component="RecommendationEngine", operation="generate_recommendation")
    async def generate_recommendation(
        self, 
        symbol: str, 
        prediction: PredictionResult, 
        risk_analysis: RiskAssessment
    ) -> TradingRecommendation:
        """
        Generate buy/sell/hold recommendations.
        
        Args:
            symbol: Stock symbol
            prediction: Price prediction results
            risk_analysis: Risk assessment
            
        Returns:
            TradingRecommendation: Complete trading recommendation
        """
        try:
            self.logger.info(f"Generating recommendation for {symbol}")
            
            # Validate inputs
            if not prediction or not prediction.predictions:
                raise DataUnavailableError(
                    f"Invalid or missing prediction data for {symbol}",
                    ErrorContext(component="RecommendationEngine", operation="generate_recommendation", symbol=symbol)
                )
            
            # Analyze prediction signals
            action, confidence = await self._analyze_prediction_signals(prediction, risk_analysis)
            
            # Calculate target price and stop loss
            target_price = await self._calculate_target_price(prediction, action)
            stop_loss = await self._calculate_stop_loss(prediction, action, risk_analysis)
            
            # Calculate position size
            position_size_result = await self.calculate_position_size(
                TradingRecommendation(
                    symbol=symbol,
                    action=action,
                    confidence=confidence,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    position_size=0,  # Will be calculated
                    rationale="",
                    risk_reward_ratio=0,
                    timestamp=datetime.now()
                ),
                {}  # Portfolio will be passed separately
            )
            
            # Calculate risk-reward ratio
            risk_reward_ratio = await self._calculate_risk_reward_ratio(
                target_price, stop_loss, prediction.predictions.get("1d", 100.0)
            )
            
            # Generate rationale using Ollama (with error handling)
            try:
                rationale = await self.generate_rationale(
                    TradingRecommendation(
                        symbol=symbol,
                        action=action,
                        confidence=confidence,
                        target_price=target_price,
                        stop_loss=stop_loss,
                        position_size=position_size_result.percentage_of_portfolio if position_size_result else 0.05,
                        rationale="",
                        risk_reward_ratio=risk_reward_ratio,
                        timestamp=datetime.now()
                    )
                )
            except OllamaError as e:
                self.logger.warning(f"Ollama rationale generation failed for {symbol}: {str(e)}")
                rationale = await self._generate_fallback_rationale(symbol, action, confidence)
            
            recommendation = TradingRecommendation(
                symbol=symbol,
                action=action,
                confidence=confidence,
                target_price=target_price,
                stop_loss=stop_loss,
                position_size=position_size_result.percentage_of_portfolio if position_size_result else 0.05,
                rationale=rationale,
                risk_reward_ratio=risk_reward_ratio,
                timestamp=datetime.now()
            )
            
            # Cache successful recommendation for fallback use
            await self.error_handler.cache_fallback_data(
                f"recommendation_{symbol}",
                recommendation,
                ttl_hours=2
            )
            
            return recommendation
            
        except (DataUnavailableError, OllamaError):
            raise  # Re-raise these for proper error handling
        except Exception as e:
            raise DataUnavailableError(
                f"Unexpected error in recommendation generation for {symbol}: {str(e)}",
                ErrorContext(component="RecommendationEngine", operation="generate_recommendation", symbol=symbol)
            )
            
            # Calculate risk-reward ratio
            risk_reward_ratio = await self._calculate_risk_reward_ratio(
                prediction, target_price, stop_loss, action
            )
            
            # Create initial recommendation
            recommendation = TradingRecommendation(
                symbol=symbol,
                action=action,
                confidence=confidence,
                target_price=target_price,
                stop_loss=stop_loss,
                position_size=position_size_result.recommended_shares,
                rationale="",  # Will be generated
                risk_reward_ratio=risk_reward_ratio,
                timestamp=datetime.now()
            )
            
            # Generate detailed rationale using Ollama
            recommendation.rationale = await self.generate_rationale(recommendation)
            
            # Log recommendation to audit system
            await self.audit_logger.log_recommendation(
                symbol=symbol,
                action=action,
                confidence=confidence,
                target_price=target_price,
                stop_loss=stop_loss,
                position_size=position_size_result.recommended_shares,
                rationale=recommendation.rationale,
                risk_reward_ratio=risk_reward_ratio
            )
            
            self.logger.info(f"Generated {action} recommendation for {symbol} with {confidence:.1%} confidence")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error generating recommendation for {symbol}: {str(e)}")
            return await self._get_fallback_recommendation(symbol, prediction)

    async def calculate_position_size(
        self, 
        recommendation: TradingRecommendation, 
        portfolio: Dict[str, Any]
    ) -> PositionSize:
        """
        Calculate appropriate position size.
        
        Args:
            recommendation: Trading recommendation
            portfolio: Current portfolio data
            
        Returns:
            PositionSize: Position sizing recommendation
        """
        try:
            # Get portfolio value (default if not provided)
            portfolio_value = portfolio.get('total_value', 100000.0)
            current_price = recommendation.target_price * 0.98  # Estimate current price
            
            # Calculate risk per share
            if recommendation.action == "BUY":
                risk_per_share = abs(current_price - recommendation.stop_loss)
            elif recommendation.action == "SELL":
                risk_per_share = abs(recommendation.stop_loss - current_price)
            else:  # HOLD
                risk_per_share = current_price * 0.02  # 2% risk for hold
            
            # Calculate position size based on risk management
            max_risk_amount = portfolio_value * 0.02  # Risk 2% of portfolio
            max_shares_by_risk = int(max_risk_amount / risk_per_share) if risk_per_share > 0 else 0
            
            # Calculate position size based on portfolio allocation
            max_position_value = portfolio_value * self.max_position_size
            max_shares_by_allocation = int(max_position_value / current_price) if current_price > 0 else 0
            
            # Take the smaller of the two limits
            recommended_shares = min(max_shares_by_risk, max_shares_by_allocation)
            recommended_shares = max(0, recommended_shares)  # Ensure non-negative
            
            # Calculate dollar amount
            recommended_dollar_amount = recommended_shares * current_price
            
            # Calculate percentage of portfolio
            percentage_of_portfolio = (recommended_dollar_amount / portfolio_value) * 100
            
            # Calculate max loss
            max_loss_amount = recommended_shares * risk_per_share
            
            # Generate rationale
            rationale = f"Position sized for {percentage_of_portfolio:.1f}% of portfolio, " \
                       f"risking ${max_loss_amount:.2f} ({max_loss_amount/portfolio_value*100:.1f}% of portfolio)"
            
            return PositionSize(
                recommended_shares=recommended_shares,
                recommended_dollar_amount=recommended_dollar_amount,
                percentage_of_portfolio=percentage_of_portfolio,
                risk_per_share=risk_per_share,
                max_loss_amount=max_loss_amount,
                rationale=rationale
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            # Return conservative fallback
            return PositionSize(
                recommended_shares=10,
                recommended_dollar_amount=1000.0,
                percentage_of_portfolio=1.0,
                risk_per_share=5.0,
                max_loss_amount=50.0,
                rationale="Conservative fallback position sizing"
            )

    async def generate_rationale(
        self, 
        recommendation: TradingRecommendation
    ) -> str:
        """
        Generate detailed rationale for recommendation.
        
        Args:
            recommendation: Trading recommendation
            
        Returns:
            str: Detailed rationale
        """
        try:
            # Prepare market context for Ollama
            market_context = {
                "symbol": recommendation.symbol,
                "action": recommendation.action,
                "confidence": recommendation.confidence,
                "target_price": recommendation.target_price,
                "stop_loss": recommendation.stop_loss,
                "risk_reward_ratio": recommendation.risk_reward_ratio,
                "market_trend": "neutral"  # Would be populated with real data
            }
            
            # Generate rationale using Ollama
            rationale = await self.ollama_service.generate_rationale(
                recommendation.__dict__, 
                market_context
            )
            
            return rationale
            
        except Exception as e:
            self.logger.error(f"Error generating rationale: {str(e)}")
            return await self._get_fallback_rationale(recommendation)

    async def _analyze_prediction_signals(
        self, 
        prediction: PredictionResult, 
        risk_analysis: RiskAssessment
    ) -> tuple[str, float]:
        """Analyze prediction signals to determine action and confidence."""
        try:
            # Get current price estimate (use 1d prediction as proxy)
            current_price = prediction.predictions.get("1d", 100.0) * 0.98
            
            # Analyze price movement signals
            short_term_signal = self._get_price_signal(current_price, prediction.predictions.get("1d", current_price))
            medium_term_signal = self._get_price_signal(current_price, prediction.predictions.get("7d", current_price))
            long_term_signal = self._get_price_signal(current_price, prediction.predictions.get("30d", current_price))
            
            # Weight the signals
            combined_signal = (short_term_signal * 0.5 + medium_term_signal * 0.3 + long_term_signal * 0.2)
            
            # Adjust for risk
            risk_adjustment = 1.0 - (risk_analysis.risk_score / 100.0) * 0.3
            adjusted_signal = combined_signal * risk_adjustment
            
            # Determine action
            if adjusted_signal > self.buy_threshold:
                action = "BUY"
            elif adjusted_signal < self.sell_threshold:
                action = "SELL"
            else:
                action = "HOLD"
            
            # Calculate confidence
            base_confidence = prediction.confidence_score / 100.0
            signal_confidence = abs(adjusted_signal - 0.5) * 2  # 0-1 scale
            confidence = (base_confidence * 0.6 + signal_confidence * 0.4)
            
            return action, confidence
            
        except Exception as e:
            self.logger.error(f"Error analyzing signals: {str(e)}")
            return "HOLD", 0.6

    def _get_price_signal(self, current_price: float, predicted_price: float) -> float:
        """Get price signal (0-1 scale) from price comparison."""
        if current_price <= 0:
            return 0.5
            
        price_change = (predicted_price - current_price) / current_price
        
        # Convert to 0-1 signal (0.5 = neutral)
        signal = 0.5 + (price_change * 2)  # Amplify signal
        return max(0.0, min(1.0, signal))

    async def _calculate_target_price(self, prediction: PredictionResult, action: str) -> float:
        """Calculate target price based on predictions and action."""
        try:
            if action == "BUY":
                # Use 7-day prediction as target for buys
                return prediction.predictions.get("7d", prediction.predictions.get("1d", 100.0))
            elif action == "SELL":
                # Use 3-day prediction as target for sells
                return prediction.predictions.get("3d", prediction.predictions.get("1d", 100.0))
            else:  # HOLD
                # Use 1-day prediction for holds
                return prediction.predictions.get("1d", 100.0)
                
        except Exception as e:
            self.logger.error(f"Error calculating target price: {str(e)}")
            return 100.0

    async def _calculate_stop_loss(
        self, 
        prediction: PredictionResult, 
        action: str, 
        risk_analysis: RiskAssessment
    ) -> float:
        """Calculate stop loss based on risk analysis."""
        try:
            current_price = prediction.predictions.get("1d", 100.0) * 0.98
            volatility = risk_analysis.risk_metrics.volatility
            
            # Adjust stop loss based on volatility
            stop_loss_pct = self.default_stop_loss_pct * (1 + volatility)
            stop_loss_pct = min(0.15, max(0.05, stop_loss_pct))  # Cap between 5-15%
            
            if action == "BUY":
                stop_loss = current_price * (1 - stop_loss_pct)
            elif action == "SELL":
                stop_loss = current_price * (1 + stop_loss_pct)
            else:  # HOLD
                stop_loss = current_price * (1 - stop_loss_pct * 0.5)
            
            return stop_loss
            
        except Exception as e:
            self.logger.error(f"Error calculating stop loss: {str(e)}")
            current_price = prediction.predictions.get("1d", 100.0) * 0.98
            return current_price * 0.92  # 8% stop loss fallback

    async def _calculate_risk_reward_ratio(
        self, 
        prediction: PredictionResult, 
        target_price: float, 
        stop_loss: float, 
        action: str
    ) -> float:
        """Calculate risk-reward ratio."""
        try:
            current_price = prediction.predictions.get("1d", 100.0) * 0.98
            
            if action == "BUY":
                potential_reward = target_price - current_price
                potential_risk = current_price - stop_loss
            elif action == "SELL":
                potential_reward = current_price - target_price
                potential_risk = stop_loss - current_price
            else:  # HOLD
                return 1.0
            
            if potential_risk <= 0:
                return 0.5
                
            ratio = potential_reward / potential_risk
            return max(0.1, ratio)
            
        except Exception as e:
            self.logger.error(f"Error calculating risk-reward ratio: {str(e)}")
            return 1.0

    async def _get_fallback_recommendation(
        self, 
        symbol: str, 
        prediction: PredictionResult
    ) -> TradingRecommendation:
        """Get fallback recommendation when main generation fails."""
        try:
            current_price = prediction.predictions.get("1d", 100.0)
            
            return TradingRecommendation(
                symbol=symbol,
                action="HOLD",
                confidence=0.6,
                target_price=current_price,
                stop_loss=current_price * 0.92,
                position_size=10,
                rationale=f"Conservative HOLD recommendation for {symbol}. "
                         f"Insufficient data for confident buy/sell signal. "
                         f"Monitor for clearer market signals before taking action.",
                risk_reward_ratio=1.0,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in fallback recommendation: {str(e)}")
            return TradingRecommendation(
                symbol=symbol,
                action="HOLD",
                confidence=0.5,
                target_price=100.0,
                stop_loss=92.0,
                position_size=10,
                rationale="System error - conservative HOLD recommendation",
                risk_reward_ratio=1.0,
                timestamp=datetime.now()
            )

    async def _get_fallback_rationale(self, recommendation: TradingRecommendation) -> str:
        """Get fallback rationale when Ollama is unavailable."""
        action = recommendation.action
        symbol = recommendation.symbol
        confidence = recommendation.confidence
        
        if action == "BUY":
            return f"BUY recommendation for {symbol} with {confidence:.1%} confidence. " \
                   f"Technical analysis indicates upward price momentum. " \
                   f"Target price: ${recommendation.target_price:.2f}, " \
                   f"Stop loss: ${recommendation.stop_loss:.2f}. " \
                   f"Risk-reward ratio: {recommendation.risk_reward_ratio:.1f}:1. " \
                   f"Consider market conditions and position sizing before executing."
                   
        elif action == "SELL":
            return f"SELL recommendation for {symbol} with {confidence:.1%} confidence. " \
                   f"Technical indicators suggest potential downward pressure. " \
                   f"Target price: ${recommendation.target_price:.2f}, " \
                   f"Stop loss: ${recommendation.stop_loss:.2f}. " \
                   f"Risk-reward ratio: {recommendation.risk_reward_ratio:.1f}:1. " \
                   f"Monitor closely for reversal signals."
                   
        else:  # HOLD
            return f"HOLD recommendation for {symbol} with {confidence:.1%} confidence. " \
                   f"Current market conditions suggest maintaining position. " \
                   f"No clear directional bias detected. " \
                   f"Continue monitoring for stronger signals before making changes. " \
                   f"Stop loss: ${recommendation.stop_loss:.2f} for risk management."
    async def _generate_fallback_rationale(
        self, 
        symbol: str, 
        action: str, 
        confidence: float
    ) -> str:
        """
        Generate fallback rationale when Ollama is unavailable.
        
        Args:
            symbol: Stock symbol
            action: Trading action (BUY/SELL/HOLD)
            confidence: Confidence score
            
        Returns:
            str: Fallback rationale
        """
        return f"""Trading Recommendation for {symbol}:

Action: {action}
Confidence: {confidence:.1%}

This recommendation is based on quantitative analysis including:
• Technical indicator signals and price momentum
• Risk-adjusted position sizing calculations
• Market volatility and trend analysis
• Portfolio optimization principles

Key factors considered:
- Price prediction models and ensemble forecasting
- Risk management and stop-loss positioning
- Historical performance patterns and correlations
- Current market conditions and sentiment indicators

Note: Detailed AI-generated explanation is currently unavailable. 
This analysis relies on core technical and quantitative factors.
Please verify with additional research before making trading decisions."""

    async def _calculate_risk_reward_ratio(
        self, 
        target_price: float, 
        stop_loss: float, 
        current_price: float
    ) -> float:
        """Calculate risk-reward ratio for the recommendation."""
        if target_price <= current_price or stop_loss >= current_price:
            return 0.0
        
        potential_reward = target_price - current_price
        potential_risk = current_price - stop_loss
        
        if potential_risk <= 0:
            return 0.0
        
        return potential_reward / potential_risk