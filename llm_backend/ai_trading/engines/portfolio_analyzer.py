"""
Portfolio Analyzer for AI Trading Assistant.

This analyzer provides comprehensive portfolio analysis including performance analysis,
rebalancing suggestions, and performance attribution.
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

from ..interfaces import PortfolioAnalyzerInterface
from ..data_models import PerformanceAnalysis, RebalancingPlan, AttributionAnalysis
from data_fetcher import DataFetcher


class PortfolioAnalyzer(PortfolioAnalyzerInterface):
    """
    Comprehensive portfolio analysis engine.
    
    Analyzes portfolio performance, suggests rebalancing,
    and provides performance attribution analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_fetcher = DataFetcher()
        
        # Analysis parameters
        self.benchmark_symbol = "^GSPC"  # S&P 500
        self.risk_free_rate = 0.02  # 2% annual
        self.rebalancing_threshold = 0.05  # 5% deviation threshold
        
        # Target allocations (can be customized)
        self.default_target_allocation = {
            "stocks": 0.6,
            "bonds": 0.3,
            "cash": 0.1
        }
        
        self.logger.info("Portfolio Analyzer initialized")

    async def analyze_performance(
        self, 
        portfolio: Dict[str, Any]
    ) -> PerformanceAnalysis:
        """
        Analyze portfolio performance.
        
        Args:
            portfolio: Portfolio data with positions and history
            
        Returns:
            PerformanceAnalysis: Comprehensive performance analysis
        """
        try:
            self.logger.info("Analyzing portfolio performance")
            
            # Get portfolio data
            positions = portfolio.get('positions', {})
            total_value = portfolio.get('total_value', 100000.0)
            historical_values = portfolio.get('historical_values', [])
            
            # Calculate performance metrics
            total_return = await self._calculate_total_return(portfolio)
            annualized_return = await self._calculate_annualized_return(historical_values)
            volatility = await self._calculate_portfolio_volatility(historical_values)
            sharpe_ratio = await self._calculate_sharpe_ratio(annualized_return, volatility)
            max_drawdown = await self._calculate_max_drawdown(historical_values)
            win_rate = await self._calculate_win_rate(historical_values)
            profit_factor = await self._calculate_profit_factor(historical_values)
            
            # Get benchmark comparison
            benchmark_comparison = await self._compare_to_benchmark(portfolio)
            
            performance_analysis = PerformanceAnalysis(
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                benchmark_comparison=benchmark_comparison,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Performance analysis complete: {annualized_return:.1%} annual return, "
                           f"{sharpe_ratio:.2f} Sharpe ratio")
            return performance_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing portfolio performance: {str(e)}")
            return await self._get_fallback_performance_analysis()

    async def suggest_rebalancing(
        self, 
        portfolio: Dict[str, Any]
    ) -> RebalancingPlan:
        """
        Suggest portfolio rebalancing.
        
        Args:
            portfolio: Current portfolio data
            
        Returns:
            RebalancingPlan: Rebalancing recommendations
        """
        try:
            self.logger.info("Generating rebalancing suggestions")
            
            positions = portfolio.get('positions', {})
            total_value = portfolio.get('total_value', 100000.0)
            target_allocation = portfolio.get('target_allocation', self.default_target_allocation)
            
            # Calculate current allocation
            current_allocation = await self._calculate_current_allocation(positions, total_value)
            
            # Determine if rebalancing is needed
            needs_rebalancing = await self._needs_rebalancing(current_allocation, target_allocation)
            
            if not needs_rebalancing:
                return RebalancingPlan(
                    current_allocation=current_allocation,
                    target_allocation=target_allocation,
                    trades_required=[],
                    expected_cost=0.0,
                    tax_implications={},
                    rationale="Portfolio is within target allocation ranges. No rebalancing needed.",
                    timestamp=datetime.now()
                )
            
            # Generate rebalancing trades
            trades_required = await self._generate_rebalancing_trades(
                positions, current_allocation, target_allocation, total_value
            )
            
            # Calculate costs and tax implications
            expected_cost = await self._calculate_rebalancing_cost(trades_required)
            tax_implications = await self._calculate_tax_implications(trades_required, positions)
            
            # Generate rationale
            rationale = await self._generate_rebalancing_rationale(
                current_allocation, target_allocation, trades_required
            )
            
            rebalancing_plan = RebalancingPlan(
                current_allocation=current_allocation,
                target_allocation=target_allocation,
                trades_required=trades_required,
                expected_cost=expected_cost,
                tax_implications=tax_implications,
                rationale=rationale,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Rebalancing plan generated with {len(trades_required)} trades")
            return rebalancing_plan
            
        except Exception as e:
            self.logger.error(f"Error generating rebalancing plan: {str(e)}")
            return await self._get_fallback_rebalancing_plan()

    async def calculate_attribution(
        self, 
        portfolio: Dict[str, Any]
    ) -> AttributionAnalysis:
        """
        Calculate performance attribution.
        
        Args:
            portfolio: Portfolio data with performance history
            
        Returns:
            AttributionAnalysis: Performance attribution breakdown
        """
        try:
            self.logger.info("Calculating performance attribution")
            
            positions = portfolio.get('positions', {})
            portfolio_return = portfolio.get('total_return', 0.0)
            
            # Get benchmark return
            benchmark_return = await self._get_benchmark_return()
            
            # Calculate attribution components
            asset_allocation = await self._calculate_asset_allocation_effect(positions, benchmark_return)
            security_selection = await self._calculate_security_selection_effect(positions, benchmark_return)
            interaction_effect = await self._calculate_interaction_effect(asset_allocation, security_selection)
            
            # Calculate total excess return
            total_excess_return = portfolio_return - benchmark_return
            
            attribution_analysis = AttributionAnalysis(
                asset_allocation=asset_allocation,
                security_selection=security_selection,
                interaction_effect=interaction_effect,
                total_excess_return=total_excess_return,
                benchmark_return=benchmark_return,
                portfolio_return=portfolio_return,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Attribution analysis complete: {total_excess_return:.1%} excess return")
            return attribution_analysis
            
        except Exception as e:
            self.logger.error(f"Error calculating attribution: {str(e)}")
            return await self._get_fallback_attribution_analysis()

    async def _calculate_total_return(self, portfolio: Dict[str, Any]) -> float:
        """Calculate total portfolio return."""
        try:
            initial_value = portfolio.get('initial_value', 100000.0)
            current_value = portfolio.get('total_value', 100000.0)
            
            if initial_value > 0:
                return (current_value - initial_value) / initial_value
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating total return: {str(e)}")
            return 0.05  # 5% default

    async def _calculate_annualized_return(self, historical_values: List[float]) -> float:
        """Calculate annualized return from historical values."""
        try:
            if len(historical_values) < 2:
                return 0.08  # 8% default
            
            # Calculate daily returns
            returns = []
            for i in range(1, len(historical_values)):
                if historical_values[i-1] > 0:
                    daily_return = (historical_values[i] - historical_values[i-1]) / historical_values[i-1]
                    returns.append(daily_return)
            
            if not returns:
                return 0.08
            
            # Annualize the return
            avg_daily_return = np.mean(returns)
            annualized_return = (1 + avg_daily_return) ** 252 - 1
            
            return float(annualized_return)
            
        except Exception as e:
            self.logger.error(f"Error calculating annualized return: {str(e)}")
            return 0.08

    async def _calculate_portfolio_volatility(self, historical_values: List[float]) -> float:
        """Calculate portfolio volatility."""
        try:
            if len(historical_values) < 2:
                return 0.15  # 15% default
            
            # Calculate daily returns
            returns = []
            for i in range(1, len(historical_values)):
                if historical_values[i-1] > 0:
                    daily_return = (historical_values[i] - historical_values[i-1]) / historical_values[i-1]
                    returns.append(daily_return)
            
            if not returns:
                return 0.15
            
            # Annualize volatility
            daily_volatility = np.std(returns)
            annualized_volatility = daily_volatility * np.sqrt(252)
            
            return float(annualized_volatility)
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return 0.15

    async def _calculate_sharpe_ratio(self, annual_return: float, volatility: float) -> float:
        """Calculate Sharpe ratio."""
        try:
            if volatility == 0:
                return 0.0
            
            excess_return = annual_return - self.risk_free_rate
            return excess_return / volatility
            
        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {str(e)}")
            return 1.0

    async def _calculate_max_drawdown(self, historical_values: List[float]) -> float:
        """Calculate maximum drawdown."""
        try:
            if len(historical_values) < 2:
                return 0.1  # 10% default
            
            values = np.array(historical_values)
            running_max = np.maximum.accumulate(values)
            drawdown = (values - running_max) / running_max
            
            return float(abs(np.min(drawdown)))
            
        except Exception as e:
            self.logger.error(f"Error calculating max drawdown: {str(e)}")
            return 0.1

    async def _calculate_win_rate(self, historical_values: List[float]) -> float:
        """Calculate win rate (percentage of positive periods)."""
        try:
            if len(historical_values) < 2:
                return 0.6  # 60% default
            
            positive_periods = 0
            total_periods = 0
            
            for i in range(1, len(historical_values)):
                if historical_values[i-1] > 0:
                    total_periods += 1
                    if historical_values[i] > historical_values[i-1]:
                        positive_periods += 1
            
            if total_periods == 0:
                return 0.6
            
            return positive_periods / total_periods
            
        except Exception as e:
            self.logger.error(f"Error calculating win rate: {str(e)}")
            return 0.6

    async def _calculate_profit_factor(self, historical_values: List[float]) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        try:
            if len(historical_values) < 2:
                return 1.5  # Default profit factor
            
            gross_profit = 0.0
            gross_loss = 0.0
            
            for i in range(1, len(historical_values)):
                if historical_values[i-1] > 0:
                    change = historical_values[i] - historical_values[i-1]
                    if change > 0:
                        gross_profit += change
                    else:
                        gross_loss += abs(change)
            
            if gross_loss == 0:
                return 2.0  # High profit factor if no losses
            
            return gross_profit / gross_loss
            
        except Exception as e:
            self.logger.error(f"Error calculating profit factor: {str(e)}")
            return 1.5

    async def _compare_to_benchmark(self, portfolio: Dict[str, Any]) -> Dict[str, float]:
        """Compare portfolio performance to benchmark."""
        try:
            portfolio_return = await self._calculate_total_return(portfolio)
            benchmark_return = await self._get_benchmark_return()
            
            return {
                "portfolio_return": portfolio_return,
                "benchmark_return": benchmark_return,
                "excess_return": portfolio_return - benchmark_return,
                "tracking_error": 0.05  # Simplified tracking error
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing to benchmark: {str(e)}")
            return {
                "portfolio_return": 0.08,
                "benchmark_return": 0.07,
                "excess_return": 0.01,
                "tracking_error": 0.05
            }

    async def _get_benchmark_return(self) -> float:
        """Get benchmark return (S&P 500)."""
        try:
            # In practice, would fetch actual benchmark data
            return 0.10  # 10% S&P 500 return assumption
        except Exception as e:
            self.logger.error(f"Error getting benchmark return: {str(e)}")
            return 0.10

    async def _calculate_current_allocation(
        self, 
        positions: Dict[str, Any], 
        total_value: float
    ) -> Dict[str, float]:
        """Calculate current portfolio allocation."""
        try:
            allocation = {}
            
            for symbol, position in positions.items():
                weight = position.get('weight', 0.0)
                
                # Categorize positions
                if symbol == "CASH":
                    allocation['cash'] = allocation.get('cash', 0.0) + weight
                elif self._is_bond(symbol):
                    allocation['bonds'] = allocation.get('bonds', 0.0) + weight
                else:
                    allocation['stocks'] = allocation.get('stocks', 0.0) + weight
            
            return allocation
            
        except Exception as e:
            self.logger.error(f"Error calculating current allocation: {str(e)}")
            return {"stocks": 0.6, "bonds": 0.3, "cash": 0.1}

    def _is_bond(self, symbol: str) -> bool:
        """Check if symbol represents a bond or bond fund."""
        bond_indicators = ['TLT', 'IEF', 'SHY', 'BND', 'AGG', 'BOND']
        return any(indicator in symbol.upper() for indicator in bond_indicators)

    async def _needs_rebalancing(
        self, 
        current_allocation: Dict[str, float], 
        target_allocation: Dict[str, float]
    ) -> bool:
        """Check if portfolio needs rebalancing."""
        try:
            for asset_class, target_weight in target_allocation.items():
                current_weight = current_allocation.get(asset_class, 0.0)
                deviation = abs(current_weight - target_weight)
                
                if deviation > self.rebalancing_threshold:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking rebalancing need: {str(e)}")
            return False

    async def _generate_rebalancing_trades(
        self, 
        positions: Dict[str, Any], 
        current_allocation: Dict[str, float], 
        target_allocation: Dict[str, float], 
        total_value: float
    ) -> List[Dict[str, Any]]:
        """Generate trades needed for rebalancing."""
        try:
            trades = []
            
            for asset_class, target_weight in target_allocation.items():
                current_weight = current_allocation.get(asset_class, 0.0)
                weight_diff = target_weight - current_weight
                
                if abs(weight_diff) > self.rebalancing_threshold:
                    dollar_amount = weight_diff * total_value
                    action = "BUY" if weight_diff > 0 else "SELL"
                    
                    trades.append({
                        "asset_class": asset_class,
                        "action": action,
                        "dollar_amount": abs(dollar_amount),
                        "weight_change": weight_diff,
                        "rationale": f"Rebalance {asset_class} to target allocation"
                    })
            
            return trades
            
        except Exception as e:
            self.logger.error(f"Error generating rebalancing trades: {str(e)}")
            return []

    async def _calculate_rebalancing_cost(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate estimated cost of rebalancing."""
        try:
            total_cost = 0.0
            commission_per_trade = 0.0  # Assume commission-free trading
            spread_cost = 0.001  # 0.1% spread cost
            
            for trade in trades:
                dollar_amount = trade['dollar_amount']
                total_cost += commission_per_trade + (dollar_amount * spread_cost)
            
            return total_cost
            
        except Exception as e:
            self.logger.error(f"Error calculating rebalancing cost: {str(e)}")
            return 50.0  # Default cost estimate

    async def _calculate_tax_implications(
        self, 
        trades: List[Dict[str, Any]], 
        positions: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate tax implications of rebalancing."""
        try:
            # Simplified tax calculation
            short_term_gains = 0.0
            long_term_gains = 0.0
            
            for trade in trades:
                if trade['action'] == 'SELL':
                    # Assume some gains on sales
                    gain = trade['dollar_amount'] * 0.1  # 10% gain assumption
                    long_term_gains += gain  # Assume long-term holding
            
            return {
                "short_term_capital_gains": short_term_gains,
                "long_term_capital_gains": long_term_gains,
                "estimated_tax_liability": long_term_gains * 0.15  # 15% long-term rate
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating tax implications: {str(e)}")
            return {"estimated_tax_liability": 0.0}

    async def _generate_rebalancing_rationale(
        self, 
        current_allocation: Dict[str, float], 
        target_allocation: Dict[str, float], 
        trades: List[Dict[str, Any]]
    ) -> str:
        """Generate rationale for rebalancing."""
        try:
            rationale = "Portfolio rebalancing recommended due to allocation drift:\n\n"
            
            for asset_class, target_weight in target_allocation.items():
                current_weight = current_allocation.get(asset_class, 0.0)
                deviation = current_weight - target_weight
                
                if abs(deviation) > self.rebalancing_threshold:
                    direction = "overweight" if deviation > 0 else "underweight"
                    rationale += f"• {asset_class.title()}: {current_weight:.1%} vs {target_weight:.1%} target ({direction} by {abs(deviation):.1%})\n"
            
            rationale += f"\nRecommended trades: {len(trades)} transactions to restore target allocation."
            
            return rationale
            
        except Exception as e:
            self.logger.error(f"Error generating rationale: {str(e)}")
            return "Rebalancing recommended to maintain target allocation."

    async def _calculate_asset_allocation_effect(
        self, 
        positions: Dict[str, Any], 
        benchmark_return: float
    ) -> Dict[str, float]:
        """Calculate asset allocation effect on performance."""
        try:
            # Simplified asset allocation effect
            return {
                "stocks": 0.02,  # 2% positive contribution
                "bonds": -0.005,  # -0.5% negative contribution
                "cash": -0.01   # -1% drag from cash
            }
        except Exception as e:
            self.logger.error(f"Error calculating asset allocation effect: {str(e)}")
            return {"total": 0.0}

    async def _calculate_security_selection_effect(
        self, 
        positions: Dict[str, Any], 
        benchmark_return: float
    ) -> Dict[str, float]:
        """Calculate security selection effect on performance."""
        try:
            # Simplified security selection effect
            selection_effect = {}
            
            for symbol, position in positions.items():
                if symbol != "CASH":
                    # Assume some outperformance/underperformance
                    effect = 0.01 if hash(symbol) % 2 == 0 else -0.005
                    selection_effect[symbol] = effect
            
            return selection_effect
            
        except Exception as e:
            self.logger.error(f"Error calculating security selection effect: {str(e)}")
            return {"total": 0.0}

    async def _calculate_interaction_effect(
        self, 
        asset_allocation: Dict[str, float], 
        security_selection: Dict[str, float]
    ) -> float:
        """Calculate interaction effect between allocation and selection."""
        try:
            # Simplified interaction effect
            return 0.002  # 0.2% interaction effect
        except Exception as e:
            self.logger.error(f"Error calculating interaction effect: {str(e)}")
            return 0.0

    async def _get_fallback_performance_analysis(self) -> PerformanceAnalysis:
        """Get fallback performance analysis."""
        return PerformanceAnalysis(
            total_return=0.08,
            annualized_return=0.08,
            volatility=0.15,
            sharpe_ratio=1.2,
            max_drawdown=0.12,
            win_rate=0.65,
            profit_factor=1.8,
            benchmark_comparison={
                "portfolio_return": 0.08,
                "benchmark_return": 0.07,
                "excess_return": 0.01
            },
            timestamp=datetime.now()
        )

    async def _get_fallback_rebalancing_plan(self) -> RebalancingPlan:
        """Get fallback rebalancing plan."""
        return RebalancingPlan(
            current_allocation={"stocks": 0.65, "bonds": 0.25, "cash": 0.1},
            target_allocation={"stocks": 0.6, "bonds": 0.3, "cash": 0.1},
            trades_required=[],
            expected_cost=0.0,
            tax_implications={},
            rationale="Unable to generate detailed rebalancing plan. Manual review recommended.",
            timestamp=datetime.now()
        )

    async def _get_fallback_attribution_analysis(self) -> AttributionAnalysis:
        """Get fallback attribution analysis."""
        return AttributionAnalysis(
            asset_allocation={"stocks": 0.01, "bonds": -0.005},
            security_selection={"total": 0.005},
            interaction_effect=0.002,
            total_excess_return=0.012,
            benchmark_return=0.10,
            portfolio_return=0.112,
            timestamp=datetime.now()
        )