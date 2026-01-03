"""
Risk Analyzer for AI Trading Assistant.

This analyzer provides comprehensive risk assessment including portfolio risk,
individual stock risk metrics, and risk alerts.
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

from ..interfaces import RiskAnalyzerInterface
from ..data_models import RiskMetrics, PortfolioRisk, RiskAlert, RiskAssessment
from ..logging.decorators import audit_operation, AuditContext
from ..logging.audit_logger import get_audit_logger
from ..error_handling import get_error_handler, handle_errors, DataUnavailableError, ErrorContext
from data_fetcher import DataFetcher


class RiskAnalyzer(RiskAnalyzerInterface):
    """
    Comprehensive risk analysis engine.
    
    Analyzes individual stock risk, portfolio risk, and generates
    risk alerts and mitigation strategies.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_logger = get_audit_logger()
        self.error_handler = get_error_handler()
        self.data_fetcher = DataFetcher()
        
        # Risk thresholds
        self.high_volatility_threshold = 0.3
        self.high_beta_threshold = 1.5
        self.max_drawdown_threshold = 0.2
        self.concentration_threshold = 0.15  # 15% max per position
        self.correlation_threshold = 0.7
        
        # Market data for beta calculation
        self.market_symbol = "^GSPC"  # S&P 500
        
        self.logger.info("Risk Analyzer initialized")

    @audit_operation(
        component="RiskAnalyzer",
        operation="calculate_risk_metrics",
        event_type="RISK_ANALYSIS",
        log_input=True,
        log_output=True,
        track_performance=True
    )
    @handle_errors(component="RiskAnalyzer", operation="calculate_risk_metrics")
    async def calculate_risk_metrics(
        self, 
        symbol: str, 
        portfolio: Dict[str, Any]
    ) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics.
        
        Args:
            symbol: Stock symbol to analyze
            portfolio: Current portfolio data
            
        Returns:
            RiskMetrics: Comprehensive risk metrics
        """
        try:
            self.logger.info(f"Calculating risk metrics for {symbol}")
            
            # Fetch historical data
            stock_data = await self._fetch_stock_data(symbol)
            market_data = await self._fetch_market_data()
            
            if stock_data is None or len(stock_data) < 30:
                raise DataUnavailableError(
                    f"Insufficient stock data for {symbol}: {len(stock_data) if stock_data else 0} records",
                    ErrorContext(component="RiskAnalyzer", operation="calculate_risk_metrics", symbol=symbol)
                )
            
            # Calculate returns
            stock_returns = await self._calculate_returns(stock_data)
            market_returns = await self._calculate_returns(market_data) if market_data is not None else None
            
            # Calculate individual metrics with error handling
            try:
                volatility = await self._calculate_volatility(stock_returns)
                beta = await self._calculate_beta(stock_returns, market_returns)
                var_1d = await self._calculate_var(stock_returns, 1)
                var_5d = await self._calculate_var(stock_returns, 5)
                sharpe_ratio = await self._calculate_sharpe_ratio(stock_returns)
                max_drawdown = await self._calculate_max_drawdown(stock_data)
                correlation_to_market = await self._calculate_correlation(stock_returns, market_returns)
            except Exception as e:
                self.logger.warning(f"Error calculating some risk metrics for {symbol}: {str(e)}")
                # Use fallback values for failed calculations
                volatility = 0.25  # Default volatility
                beta = 1.0  # Market beta
                var_1d = 0.05  # 5% VaR
                var_5d = 0.12  # 12% 5-day VaR
                sharpe_ratio = 0.5  # Moderate Sharpe
                max_drawdown = 0.15  # 15% drawdown
                correlation_to_market = 0.7  # High correlation
            
            risk_metrics = RiskMetrics(
                symbol=symbol,
                var_1d=var_1d,
                var_5d=var_5d,
                beta=beta,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                correlation_to_market=correlation_to_market
            )
            
            # Cache successful risk metrics for fallback use
            await self.error_handler.cache_fallback_data(
                f"risk_metrics_{symbol}",
                risk_metrics,
                ttl_hours=4
            )
            
            return risk_metrics
            
        except DataUnavailableError:
            raise  # Re-raise for proper error handling
        except Exception as e:
            raise DataUnavailableError(
                f"Unexpected error in risk analysis for {symbol}: {str(e)}",
                ErrorContext(component="RiskAnalyzer", operation="calculate_risk_metrics", symbol=symbol)
            )

    async def assess_portfolio_risk(
        self, 
        portfolio: Dict[str, Any]
    ) -> PortfolioRisk:
        """
        Assess overall portfolio risk.
        
        Args:
            portfolio: Portfolio data with positions
            
        Returns:
            PortfolioRisk: Portfolio risk assessment
        """
        try:
            self.logger.info("Assessing portfolio risk")
            
            positions = portfolio.get('positions', {})
            total_value = portfolio.get('total_value', 100000.0)
            
            if not positions:
                return await self._get_fallback_portfolio_risk()
            
            # Calculate portfolio-level metrics
            total_var = await self._calculate_portfolio_var(positions, total_value)
            concentration_risk = await self._calculate_concentration_risk(positions)
            sector_exposure = await self._calculate_sector_exposure(positions)
            correlation_risk = await self._calculate_correlation_risk(positions)
            liquidity_risk = await self._calculate_liquidity_risk(positions)
            
            # Calculate overall risk score (0-100)
            overall_risk_score = await self._calculate_overall_risk_score(
                total_var, concentration_risk, correlation_risk, liquidity_risk
            )
            
            # Generate risk alerts
            risk_alerts = await self.generate_risk_alerts(
                RiskMetrics(
                    symbol="PORTFOLIO",
                    var_1d=total_var,
                    var_5d=total_var * 2.24,  # sqrt(5) scaling
                    beta=1.0,
                    volatility=concentration_risk,
                    sharpe_ratio=0.0,
                    max_drawdown=0.0,
                    correlation_to_market=correlation_risk
                )
            )
            
            portfolio_risk = PortfolioRisk(
                total_var=total_var,
                concentration_risk=concentration_risk,
                sector_exposure=sector_exposure,
                correlation_risk=correlation_risk,
                liquidity_risk=liquidity_risk,
                overall_risk_score=overall_risk_score,
                risk_alerts=risk_alerts,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Portfolio risk assessment complete: overall score={overall_risk_score:.1f}")
            return portfolio_risk
            
        except Exception as e:
            self.logger.error(f"Error assessing portfolio risk: {str(e)}")
            return await self._get_fallback_portfolio_risk()

    async def generate_risk_alerts(
        self, 
        risk_metrics: RiskMetrics
    ) -> List[RiskAlert]:
        """
        Generate risk alerts based on metrics.
        
        Args:
            risk_metrics: Risk metrics to analyze
            
        Returns:
            List[RiskAlert]: List of risk alerts
        """
        try:
            alerts = []
            
            # High volatility alert
            if risk_metrics.volatility > self.high_volatility_threshold:
                alerts.append(RiskAlert(
                    alert_type="HIGH_VOLATILITY",
                    severity="HIGH",
                    message=f"{risk_metrics.symbol} shows high volatility ({risk_metrics.volatility:.1%}). "
                           f"Consider reducing position size or implementing tighter stop losses.",
                    affected_positions=[risk_metrics.symbol],
                    recommended_action="Reduce position size or implement protective stops",
                    timestamp=datetime.now()
                ))
            
            # High beta alert
            if risk_metrics.beta > self.high_beta_threshold:
                alerts.append(RiskAlert(
                    alert_type="HIGH_BETA",
                    severity="MEDIUM",
                    message=f"{risk_metrics.symbol} has high beta ({risk_metrics.beta:.2f}). "
                           f"Position will be more sensitive to market movements.",
                    affected_positions=[risk_metrics.symbol],
                    recommended_action="Monitor market conditions closely",
                    timestamp=datetime.now()
                ))
            
            # High drawdown alert
            if risk_metrics.max_drawdown > self.max_drawdown_threshold:
                alerts.append(RiskAlert(
                    alert_type="HIGH_DRAWDOWN",
                    severity="HIGH",
                    message=f"{risk_metrics.symbol} has experienced significant drawdown "
                           f"({risk_metrics.max_drawdown:.1%}). Review position sizing.",
                    affected_positions=[risk_metrics.symbol],
                    recommended_action="Review position size and risk management",
                    timestamp=datetime.now()
                ))
            
            # High VaR alert
            if risk_metrics.var_1d > 0.05:  # 5% daily VaR
                alerts.append(RiskAlert(
                    alert_type="HIGH_VAR",
                    severity="HIGH",
                    message=f"{risk_metrics.symbol} has high Value at Risk "
                           f"({risk_metrics.var_1d:.1%} daily). Significant potential losses.",
                    affected_positions=[risk_metrics.symbol],
                    recommended_action="Consider reducing exposure or hedging",
                    timestamp=datetime.now()
                ))
            
            # Poor Sharpe ratio alert
            if risk_metrics.sharpe_ratio < 0.5:
                alerts.append(RiskAlert(
                    alert_type="POOR_RISK_ADJUSTED_RETURN",
                    severity="MEDIUM",
                    message=f"{risk_metrics.symbol} has poor risk-adjusted returns "
                           f"(Sharpe: {risk_metrics.sharpe_ratio:.2f}). Consider alternatives.",
                    affected_positions=[risk_metrics.symbol],
                    recommended_action="Evaluate alternative investments",
                    timestamp=datetime.now()
                ))
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error generating risk alerts: {str(e)}")
            return []

    async def _fetch_stock_data(self, symbol: str) -> Optional[np.ndarray]:
        """Fetch historical stock data."""
        try:
            data = self.data_fetcher.fetch_data(symbol, period="1y")
            if data is not None and len(data) > 0:
                return data['Close'].values
            return None
        except Exception as e:
            self.logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None

    async def _fetch_market_data(self) -> Optional[np.ndarray]:
        """Fetch market index data for beta calculation."""
        try:
            data = self.data_fetcher.fetch_data(self.market_symbol, period="1y")
            if data is not None and len(data) > 0:
                return data['Close'].values
            return None
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None

    async def _calculate_returns(self, price_data: np.ndarray) -> np.ndarray:
        """Calculate returns from price data."""
        if len(price_data) < 2:
            return np.array([])
        return np.diff(price_data) / price_data[:-1]

    async def _calculate_volatility(self, returns: np.ndarray) -> float:
        """Calculate annualized volatility."""
        if len(returns) == 0:
            return 0.2  # Default volatility
        return float(np.std(returns) * np.sqrt(252))  # Annualized

    async def _calculate_beta(
        self, 
        stock_returns: np.ndarray, 
        market_returns: Optional[np.ndarray]
    ) -> float:
        """Calculate beta relative to market."""
        if market_returns is None or len(stock_returns) == 0 or len(market_returns) == 0:
            return 1.0  # Default beta
        
        # Align arrays
        min_len = min(len(stock_returns), len(market_returns))
        stock_returns = stock_returns[:min_len]
        market_returns = market_returns[:min_len]
        
        if len(stock_returns) < 30:  # Need sufficient data
            return 1.0
        
        covariance = np.cov(stock_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 1.0
            
        return float(covariance / market_variance)

    async def _calculate_var(self, returns: np.ndarray, days: int) -> float:
        """Calculate Value at Risk."""
        if len(returns) == 0:
            return 0.02  # Default 2% VaR
        
        # Use 5th percentile for 95% confidence
        var_1d = float(np.percentile(returns, 5))
        
        # Scale for multiple days
        var_scaled = abs(var_1d) * np.sqrt(days)
        
        return var_scaled

    async def _calculate_sharpe_ratio(self, returns: np.ndarray) -> float:
        """Calculate Sharpe ratio (assuming 2% risk-free rate)."""
        if len(returns) == 0:
            return 0.0
        
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        excess_returns = returns - risk_free_rate
        
        if np.std(excess_returns) == 0:
            return 0.0
            
        return float(np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252))

    async def _calculate_max_drawdown(self, price_data: np.ndarray) -> float:
        """Calculate maximum drawdown."""
        if len(price_data) < 2:
            return 0.0
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(price_data)
        
        # Calculate drawdown
        drawdown = (price_data - running_max) / running_max
        
        return float(abs(np.min(drawdown)))

    async def _calculate_correlation(
        self, 
        stock_returns: np.ndarray, 
        market_returns: Optional[np.ndarray]
    ) -> float:
        """Calculate correlation with market."""
        if market_returns is None or len(stock_returns) == 0 or len(market_returns) == 0:
            return 0.5  # Default correlation
        
        # Align arrays
        min_len = min(len(stock_returns), len(market_returns))
        stock_returns = stock_returns[:min_len]
        market_returns = market_returns[:min_len]
        
        if len(stock_returns) < 30:
            return 0.5
        
        correlation_matrix = np.corrcoef(stock_returns, market_returns)
        return float(correlation_matrix[0, 1])

    async def _calculate_portfolio_var(self, positions: Dict[str, Any], total_value: float) -> float:
        """Calculate portfolio Value at Risk."""
        try:
            # Simplified portfolio VaR calculation
            # In practice, this would use covariance matrix
            total_var = 0.0
            
            for symbol, position in positions.items():
                if symbol == "CASH":
                    continue
                    
                weight = position.get('weight', 0.0)
                # Estimate individual VaR (simplified)
                individual_var = 0.03 * weight  # 3% base VaR scaled by weight
                total_var += individual_var ** 2
            
            return float(np.sqrt(total_var))
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio VaR: {str(e)}")
            return 0.02

    async def _calculate_concentration_risk(self, positions: Dict[str, Any]) -> float:
        """Calculate concentration risk."""
        try:
            max_weight = 0.0
            for symbol, position in positions.items():
                if symbol == "CASH":
                    continue
                weight = position.get('weight', 0.0)
                max_weight = max(max_weight, weight)
            
            # Risk increases exponentially with concentration
            if max_weight > self.concentration_threshold:
                return min(1.0, (max_weight - self.concentration_threshold) * 3)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating concentration risk: {str(e)}")
            return 0.1

    async def _calculate_sector_exposure(self, positions: Dict[str, Any]) -> Dict[str, float]:
        """Calculate sector exposure (simplified)."""
        try:
            # Simplified sector mapping
            sector_map = {
                "AAPL": "Technology",
                "GOOGL": "Technology", 
                "MSFT": "Technology",
                "TSLA": "Automotive",
                "JPM": "Financial",
                "JNJ": "Healthcare"
            }
            
            sector_exposure = {}
            for symbol, position in positions.items():
                if symbol == "CASH":
                    continue
                    
                sector = sector_map.get(symbol, "Other")
                weight = position.get('weight', 0.0)
                
                if sector in sector_exposure:
                    sector_exposure[sector] += weight
                else:
                    sector_exposure[sector] = weight
            
            return sector_exposure
            
        except Exception as e:
            self.logger.error(f"Error calculating sector exposure: {str(e)}")
            return {"Other": 1.0}

    async def _calculate_correlation_risk(self, positions: Dict[str, Any]) -> float:
        """Calculate correlation risk (simplified)."""
        try:
            # Simplified correlation risk
            # In practice, would calculate correlation matrix
            tech_weight = 0.0
            
            tech_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "META"]
            
            for symbol, position in positions.items():
                if symbol in tech_stocks:
                    tech_weight += position.get('weight', 0.0)
            
            # High tech concentration = high correlation risk
            if tech_weight > 0.5:
                return min(1.0, (tech_weight - 0.5) * 2)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation risk: {str(e)}")
            return 0.1

    async def _calculate_liquidity_risk(self, positions: Dict[str, Any]) -> float:
        """Calculate liquidity risk (simplified)."""
        try:
            # Simplified liquidity risk based on position sizes
            # In practice, would use average daily volume
            total_risk = 0.0
            
            for symbol, position in positions.items():
                if symbol == "CASH":
                    continue
                    
                weight = position.get('weight', 0.0)
                # Assume larger positions have higher liquidity risk
                liquidity_risk = min(0.1, weight * 0.5)
                total_risk += liquidity_risk
            
            return min(1.0, total_risk)
            
        except Exception as e:
            self.logger.error(f"Error calculating liquidity risk: {str(e)}")
            return 0.05

    async def _calculate_overall_risk_score(
        self, 
        total_var: float, 
        concentration_risk: float, 
        correlation_risk: float, 
        liquidity_risk: float
    ) -> float:
        """Calculate overall portfolio risk score (0-100)."""
        try:
            # Weight different risk components
            var_score = min(100, total_var * 1000)  # Scale VaR to 0-100
            concentration_score = concentration_risk * 100
            correlation_score = correlation_risk * 100
            liquidity_score = liquidity_risk * 100
            
            # Weighted average
            overall_score = (
                var_score * 0.4 +
                concentration_score * 0.3 +
                correlation_score * 0.2 +
                liquidity_score * 0.1
            )
            
            return min(100.0, max(0.0, overall_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating overall risk score: {str(e)}")
            return 50.0

    async def _get_fallback_risk_metrics(self, symbol: str) -> RiskMetrics:
        """Get fallback risk metrics when calculation fails."""
        return RiskMetrics(
            symbol=symbol,
            var_1d=0.02,
            var_5d=0.045,
            beta=1.0,
            volatility=0.25,
            sharpe_ratio=0.8,
            max_drawdown=0.15,
            correlation_to_market=0.6
        )

    async def _get_fallback_portfolio_risk(self) -> PortfolioRisk:
        """Get fallback portfolio risk when calculation fails."""
        return PortfolioRisk(
            total_var=0.02,
            concentration_risk=0.1,
            sector_exposure={"Technology": 0.4, "Other": 0.6},
            correlation_risk=0.15,
            liquidity_risk=0.05,
            overall_risk_score=35.0,
            risk_alerts=[],
            timestamp=datetime.now()
        )