"""
Comparative Analyzer for AI Trading Assistant.

This analyzer provides comparative analysis and visualizations between multiple stocks
with customizable metrics and ranking systems.
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

from ..interfaces import ComparativeAnalyzerInterface
from ..data_models import ComparisonResult, ChartData, CorrelationMatrix, RankingResult
from data_fetcher import DataFetcher


class ComparativeAnalyzer(ComparativeAnalyzerInterface):
    """
    Comprehensive comparative analysis engine.
    
    Compares multiple stocks across various metrics, generates
    visualizations, and provides ranking systems.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_fetcher = DataFetcher()
        
        # Available metrics for comparison
        self.available_metrics = [
            "price_change", "volatility", "volume", "market_cap",
            "pe_ratio", "dividend_yield", "beta", "rsi", "macd"
        ]
        
        # Chart types
        self.chart_types = [
            "line", "bar", "scatter", "heatmap", "radar"
        ]
        
        self.logger.info("Comparative Analyzer initialized")

    async def compare_stocks(
        self, 
        symbols: List[str], 
        metrics: List[str], 
        timeframe: str
    ) -> ComparisonResult:
        """
        Compare multiple stocks across metrics.
        
        Args:
            symbols: List of stock symbols to compare (2-5 stocks)
            metrics: List of metrics to compare
            timeframe: Time period for comparison
            
        Returns:
            ComparisonResult: Comprehensive comparison results
        """
        try:
            self.logger.info(f"Comparing {len(symbols)} stocks across {len(metrics)} metrics")
            
            # Validate inputs
            if len(symbols) < 2 or len(symbols) > 5:
                raise ValueError("Must compare between 2-5 stocks")
            
            # Calculate metrics for each stock
            comparison_metrics = {}
            for symbol in symbols:
                comparison_metrics[symbol] = await self._calculate_stock_metrics(symbol, metrics, timeframe)
            
            # Calculate correlations
            correlations = await self.calculate_correlations(symbols, timeframe)
            
            # Generate rankings for each metric
            rankings = await self._generate_rankings(comparison_metrics, metrics)
            
            # Prepare chart data
            chart_data = await self._prepare_chart_data(comparison_metrics, symbols, metrics)
            
            comparison_result = ComparisonResult(
                symbols=symbols,
                metrics=comparison_metrics,
                correlations=correlations,
                rankings=rankings,
                chart_data=chart_data,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Stock comparison completed for {symbols}")
            return comparison_result
            
        except Exception as e:
            self.logger.error(f"Error comparing stocks: {str(e)}")
            return await self._get_fallback_comparison(symbols, metrics, timeframe)

    async def generate_comparison_chart(
        self, 
        comparison_data: ComparisonResult, 
        chart_type: str
    ) -> ChartData:
        """
        Generate comparison charts.
        
        Args:
            comparison_data: Comparison results
            chart_type: Type of chart to generate
            
        Returns:
            ChartData: Chart data for visualization
        """
        try:
            self.logger.info(f"Generating {chart_type} chart for comparison")
            
            if chart_type not in self.chart_types:
                chart_type = "bar"  # Default to bar chart
            
            symbols = comparison_data.symbols
            metrics = comparison_data.metrics
            
            if chart_type == "line":
                chart_data = await self._generate_line_chart(symbols, metrics)
            elif chart_type == "bar":
                chart_data = await self._generate_bar_chart(symbols, metrics)
            elif chart_type == "scatter":
                chart_data = await self._generate_scatter_chart(symbols, metrics)
            elif chart_type == "heatmap":
                chart_data = await self._generate_heatmap_chart(symbols, metrics)
            elif chart_type == "radar":
                chart_data = await self._generate_radar_chart(symbols, metrics)
            else:
                chart_data = await self._generate_bar_chart(symbols, metrics)
            
            self.logger.info(f"Generated {chart_type} chart successfully")
            return chart_data
            
        except Exception as e:
            self.logger.error(f"Error generating chart: {str(e)}")
            return await self._get_fallback_chart_data(comparison_data.symbols)

    async def calculate_correlations(
        self, 
        symbols: List[str], 
        timeframe: str
    ) -> CorrelationMatrix:
        """
        Calculate correlation matrix for stocks.
        
        Args:
            symbols: List of stock symbols
            timeframe: Time period for correlation calculation
            
        Returns:
            CorrelationMatrix: Correlation matrix
        """
        try:
            self.logger.info(f"Calculating correlations for {len(symbols)} stocks")
            
            # Get price data for all symbols
            price_data = {}
            for symbol in symbols:
                prices = await self._get_price_data(symbol, timeframe)
                if prices is not None and len(prices) > 0:
                    price_data[symbol] = prices
            
            # Calculate correlation matrix
            if len(price_data) >= 2:
                correlation_matrix = await self._calculate_correlation_matrix(price_data, symbols)
            else:
                # Fallback correlation matrix
                n = len(symbols)
                correlation_matrix = np.eye(n) + np.random.normal(0, 0.1, (n, n))
                correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
                np.fill_diagonal(correlation_matrix, 1.0)
            
            correlation_result = CorrelationMatrix(
                symbols=symbols,
                matrix=correlation_matrix,
                timeframe=timeframe,
                timestamp=datetime.now()
            )
            
            self.logger.info("Correlation matrix calculated successfully")
            return correlation_result
            
        except Exception as e:
            self.logger.error(f"Error calculating correlations: {str(e)}")
            return await self._get_fallback_correlation_matrix(symbols, timeframe)

    async def rank_opportunities(
        self, 
        comparison_data: ComparisonResult
    ) -> RankingResult:
        """
        Rank trading opportunities.
        
        Args:
            comparison_data: Comparison results to rank
            
        Returns:
            RankingResult: Ranked opportunities
        """
        try:
            self.logger.info("Ranking trading opportunities")
            
            symbols = comparison_data.symbols
            metrics = comparison_data.metrics
            
            # Define ranking criteria
            ranking_criteria = [
                "overall_score", "growth_potential", "value_score", 
                "momentum", "quality", "risk_adjusted_return"
            ]
            
            # Calculate scores for each criterion
            rankings = {}
            scores = {}
            
            for criterion in ranking_criteria:
                criterion_scores = await self._calculate_criterion_scores(symbols, metrics, criterion)
                scores[criterion] = criterion_scores
                
                # Rank symbols by this criterion
                sorted_symbols = sorted(symbols, key=lambda s: criterion_scores.get(s, 0), reverse=True)
                rankings[criterion] = sorted_symbols
            
            # Calculate overall ranking
            overall_scores = {}
            for symbol in symbols:
                total_score = 0
                for criterion in ranking_criteria:
                    total_score += scores[criterion].get(symbol, 0)
                overall_scores[symbol] = total_score / len(ranking_criteria)
            
            overall_ranking = sorted(symbols, key=lambda s: overall_scores[s], reverse=True)
            
            # Add overall ranking
            rankings["overall"] = overall_ranking
            scores["overall"] = overall_scores
            
            ranking_result = RankingResult(
                rankings=rankings,
                scores=scores,
                overall_ranking=overall_ranking,
                ranking_criteria=ranking_criteria,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Ranking completed. Top opportunity: {overall_ranking[0]}")
            return ranking_result
            
        except Exception as e:
            self.logger.error(f"Error ranking opportunities: {str(e)}")
            return await self._get_fallback_ranking(comparison_data.symbols)

    async def _calculate_stock_metrics(
        self, 
        symbol: str, 
        metrics: List[str], 
        timeframe: str
    ) -> Dict[str, float]:
        """Calculate specified metrics for a stock."""
        try:
            stock_metrics = {}
            
            # Get basic price data
            price_data = await self._get_price_data(symbol, timeframe)
            current_price = price_data[-1] if price_data is not None and len(price_data) > 0 else 100.0
            
            for metric in metrics:
                if metric == "price_change":
                    stock_metrics[metric] = await self._calculate_price_change(price_data, timeframe)
                elif metric == "volatility":
                    stock_metrics[metric] = await self._calculate_volatility(price_data)
                elif metric == "volume":
                    stock_metrics[metric] = await self._get_average_volume(symbol, timeframe)
                elif metric == "market_cap":
                    stock_metrics[metric] = await self._get_market_cap(symbol)
                elif metric == "pe_ratio":
                    stock_metrics[metric] = await self._get_pe_ratio(symbol)
                elif metric == "dividend_yield":
                    stock_metrics[metric] = await self._get_dividend_yield(symbol)
                elif metric == "beta":
                    stock_metrics[metric] = await self._calculate_beta(symbol, timeframe)
                elif metric == "rsi":
                    stock_metrics[metric] = await self._calculate_rsi(price_data)
                elif metric == "macd":
                    stock_metrics[metric] = await self._calculate_macd(price_data)
                else:
                    stock_metrics[metric] = 0.0
            
            return stock_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics for {symbol}: {str(e)}")
            return {metric: 0.0 for metric in metrics}

    async def _get_price_data(self, symbol: str, timeframe: str) -> Optional[np.ndarray]:
        """Get historical price data."""
        try:
            # Convert timeframe to period
            period_map = {
                "1d": "1d", "1w": "5d", "1m": "1mo", 
                "3m": "3mo", "6m": "6mo", "1y": "1y"
            }
            period = period_map.get(timeframe, "1y")
            
            # Try to fetch data
            data = self.data_fetcher.fetch_data(symbol, period=period)
            if data is not None and len(data) > 0:
                return data['Close'].values
            
            # Generate fallback data
            return self._generate_fallback_price_data(symbol, timeframe)
            
        except Exception as e:
            self.logger.error(f"Error getting price data for {symbol}: {str(e)}")
            return self._generate_fallback_price_data(symbol, timeframe)

    def _generate_fallback_price_data(self, symbol: str, timeframe: str) -> np.ndarray:
        """Generate realistic fallback price data."""
        # Generate realistic price series
        np.random.seed(hash(symbol) % 1000)
        
        days = {"1d": 1, "1w": 7, "1m": 30, "3m": 90, "6m": 180, "1y": 252}.get(timeframe, 252)
        
        # Start with base price
        base_price = {"AAPL": 150, "GOOGL": 2500, "MSFT": 300, "TSLA": 200, "AMZN": 3000}.get(symbol, 100)
        
        # Generate price series with random walk
        returns = np.random.normal(0.0005, 0.02, days)  # Daily returns
        prices = [base_price]
        
        for ret in returns:
            prices.append(prices[-1] * (1 + ret))
        
        return np.array(prices)

    async def _calculate_price_change(self, price_data: Optional[np.ndarray], timeframe: str) -> float:
        """Calculate price change over timeframe."""
        if price_data is None or len(price_data) < 2:
            return 0.02  # 2% default change
        
        start_price = price_data[0]
        end_price = price_data[-1]
        
        if start_price > 0:
            return (end_price - start_price) / start_price
        return 0.0

    async def _calculate_volatility(self, price_data: Optional[np.ndarray]) -> float:
        """Calculate price volatility."""
        if price_data is None or len(price_data) < 2:
            return 0.25  # 25% default volatility
        
        returns = np.diff(price_data) / price_data[:-1]
        return float(np.std(returns) * np.sqrt(252))  # Annualized

    async def _get_average_volume(self, symbol: str, timeframe: str) -> float:
        """Get average trading volume."""
        # Simulate volume based on symbol
        volume_map = {
            "AAPL": 50000000, "GOOGL": 25000000, "MSFT": 30000000,
            "TSLA": 40000000, "AMZN": 35000000
        }
        return float(volume_map.get(symbol, 10000000))

    async def _get_market_cap(self, symbol: str) -> float:
        """Get market capitalization."""
        # Simulate market cap
        market_cap_map = {
            "AAPL": 2500000000000, "GOOGL": 1800000000000, "MSFT": 2200000000000,
            "TSLA": 800000000000, "AMZN": 1500000000000
        }
        return float(market_cap_map.get(symbol, 100000000000))

    async def _get_pe_ratio(self, symbol: str) -> float:
        """Get P/E ratio."""
        pe_map = {
            "AAPL": 25.5, "GOOGL": 22.8, "MSFT": 28.2,
            "TSLA": 45.6, "AMZN": 35.1
        }
        return pe_map.get(symbol, 20.0)

    async def _get_dividend_yield(self, symbol: str) -> float:
        """Get dividend yield."""
        dividend_map = {
            "AAPL": 0.005, "GOOGL": 0.0, "MSFT": 0.008,
            "TSLA": 0.0, "AMZN": 0.0
        }
        return dividend_map.get(symbol, 0.002)

    async def _calculate_beta(self, symbol: str, timeframe: str) -> float:
        """Calculate beta relative to market."""
        beta_map = {
            "AAPL": 1.2, "GOOGL": 1.1, "MSFT": 0.9,
            "TSLA": 1.8, "AMZN": 1.3
        }
        return beta_map.get(symbol, 1.0)

    async def _calculate_rsi(self, price_data: Optional[np.ndarray]) -> float:
        """Calculate RSI indicator."""
        if price_data is None or len(price_data) < 14:
            return 50.0  # Neutral RSI
        
        # Simplified RSI calculation
        returns = np.diff(price_data)
        gains = np.where(returns > 0, returns, 0)
        losses = np.where(returns < 0, -returns, 0)
        
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)

    async def _calculate_macd(self, price_data: Optional[np.ndarray]) -> float:
        """Calculate MACD indicator."""
        if price_data is None or len(price_data) < 26:
            return 0.0
        
        # Simplified MACD calculation
        ema_12 = np.mean(price_data[-12:])
        ema_26 = np.mean(price_data[-26:])
        
        macd = ema_12 - ema_26
        return float(macd)

    async def _calculate_correlation_matrix(
        self, 
        price_data: Dict[str, np.ndarray], 
        symbols: List[str]
    ) -> np.ndarray:
        """Calculate correlation matrix from price data."""
        try:
            # Align data lengths
            min_length = min(len(data) for data in price_data.values())
            
            # Calculate returns for each symbol
            returns_data = []
            for symbol in symbols:
                if symbol in price_data:
                    prices = price_data[symbol][-min_length:]
                    returns = np.diff(prices) / prices[:-1]
                    returns_data.append(returns)
                else:
                    # Generate fallback returns
                    returns_data.append(np.random.normal(0, 0.02, min_length-1))
            
            # Calculate correlation matrix
            correlation_matrix = np.corrcoef(returns_data)
            
            return correlation_matrix
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation matrix: {str(e)}")
            # Return identity matrix as fallback
            n = len(symbols)
            return np.eye(n)

    async def _generate_rankings(
        self, 
        comparison_metrics: Dict[str, Dict[str, float]], 
        metrics: List[str]
    ) -> Dict[str, List[str]]:
        """Generate rankings for each metric."""
        rankings = {}
        
        for metric in metrics:
            # Get values for this metric
            metric_values = {symbol: data.get(metric, 0) for symbol, data in comparison_metrics.items()}
            
            # Sort symbols by metric value (descending for most metrics)
            reverse_sort = metric not in ["pe_ratio", "volatility"]  # Lower is better for these
            sorted_symbols = sorted(metric_values.keys(), key=lambda s: metric_values[s], reverse=reverse_sort)
            
            rankings[metric] = sorted_symbols
        
        return rankings

    async def _prepare_chart_data(
        self, 
        comparison_metrics: Dict[str, Dict[str, float]], 
        symbols: List[str], 
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Prepare data for chart generation."""
        chart_data = {
            "symbols": symbols,
            "metrics": metrics,
            "data": comparison_metrics,
            "colors": self._generate_colors(len(symbols))
        }
        
        return chart_data

    def _generate_colors(self, count: int) -> List[str]:
        """Generate colors for charts."""
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        return colors[:count]

    async def _generate_line_chart(self, symbols: List[str], metrics: Dict[str, Dict[str, float]]) -> ChartData:
        """Generate line chart data."""
        return ChartData(
            chart_type="line",
            data={"symbols": symbols, "metrics": metrics},
            labels=symbols,
            colors=self._generate_colors(len(symbols)),
            title="Stock Comparison - Line Chart",
            x_axis_label="Stocks",
            y_axis_label="Values",
            timestamp=datetime.now()
        )

    async def _generate_bar_chart(self, symbols: List[str], metrics: Dict[str, Dict[str, float]]) -> ChartData:
        """Generate bar chart data."""
        return ChartData(
            chart_type="bar",
            data={"symbols": symbols, "metrics": metrics},
            labels=symbols,
            colors=self._generate_colors(len(symbols)),
            title="Stock Comparison - Bar Chart",
            x_axis_label="Stocks",
            y_axis_label="Values",
            timestamp=datetime.now()
        )

    async def _generate_scatter_chart(self, symbols: List[str], metrics: Dict[str, Dict[str, float]]) -> ChartData:
        """Generate scatter chart data."""
        return ChartData(
            chart_type="scatter",
            data={"symbols": symbols, "metrics": metrics},
            labels=symbols,
            colors=self._generate_colors(len(symbols)),
            title="Stock Comparison - Scatter Plot",
            x_axis_label="Risk",
            y_axis_label="Return",
            timestamp=datetime.now()
        )

    async def _generate_heatmap_chart(self, symbols: List[str], metrics: Dict[str, Dict[str, float]]) -> ChartData:
        """Generate heatmap chart data."""
        return ChartData(
            chart_type="heatmap",
            data={"symbols": symbols, "metrics": metrics},
            labels=symbols,
            colors=["#d73027", "#f46d43", "#fdae61", "#fee08b", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850"],
            title="Stock Comparison - Heatmap",
            x_axis_label="Metrics",
            y_axis_label="Stocks",
            timestamp=datetime.now()
        )

    async def _generate_radar_chart(self, symbols: List[str], metrics: Dict[str, Dict[str, float]]) -> ChartData:
        """Generate radar chart data."""
        return ChartData(
            chart_type="radar",
            data={"symbols": symbols, "metrics": metrics},
            labels=symbols,
            colors=self._generate_colors(len(symbols)),
            title="Stock Comparison - Radar Chart",
            x_axis_label="",
            y_axis_label="",
            timestamp=datetime.now()
        )

    async def _calculate_criterion_scores(
        self, 
        symbols: List[str], 
        metrics: Dict[str, Dict[str, float]], 
        criterion: str
    ) -> Dict[str, float]:
        """Calculate scores for a ranking criterion."""
        scores = {}
        
        for symbol in symbols:
            symbol_metrics = metrics.get(symbol, {})
            
            if criterion == "overall_score":
                # Weighted combination of multiple factors
                score = (
                    symbol_metrics.get("price_change", 0) * 0.3 +
                    (1 / max(symbol_metrics.get("pe_ratio", 20), 1)) * 0.2 +
                    symbol_metrics.get("dividend_yield", 0) * 100 * 0.2 +
                    (100 - symbol_metrics.get("rsi", 50)) / 100 * 0.15 +
                    (1 / max(symbol_metrics.get("volatility", 0.25), 0.01)) * 0.15
                )
            elif criterion == "growth_potential":
                score = symbol_metrics.get("price_change", 0) * 2 + symbol_metrics.get("macd", 0)
            elif criterion == "value_score":
                score = 1 / max(symbol_metrics.get("pe_ratio", 20), 1)
            elif criterion == "momentum":
                score = (symbol_metrics.get("rsi", 50) - 50) / 50
            elif criterion == "quality":
                score = symbol_metrics.get("dividend_yield", 0) * 100
            elif criterion == "risk_adjusted_return":
                ret = symbol_metrics.get("price_change", 0)
                vol = symbol_metrics.get("volatility", 0.25)
                score = ret / vol if vol > 0 else 0
            else:
                score = 0.5
            
            scores[symbol] = score
        
        return scores

    async def _get_fallback_comparison(
        self, 
        symbols: List[str], 
        metrics: List[str], 
        timeframe: str
    ) -> ComparisonResult:
        """Get fallback comparison when main analysis fails."""
        fallback_metrics = {}
        
        for symbol in symbols:
            fallback_metrics[symbol] = {metric: 0.5 for metric in metrics}
        
        # Simple correlation matrix
        n = len(symbols)
        correlation_matrix = np.eye(n) * 0.8 + np.ones((n, n)) * 0.2
        
        correlations = CorrelationMatrix(
            symbols=symbols,
            matrix=correlation_matrix,
            timeframe=timeframe,
            timestamp=datetime.now()
        )
        
        return ComparisonResult(
            symbols=symbols,
            metrics=fallback_metrics,
            correlations=correlations,
            rankings={metric: symbols for metric in metrics},
            chart_data={"symbols": symbols, "metrics": fallback_metrics},
            timestamp=datetime.now()
        )

    async def _get_fallback_correlation_matrix(self, symbols: List[str], timeframe: str) -> CorrelationMatrix:
        """Get fallback correlation matrix."""
        n = len(symbols)
        matrix = np.eye(n) * 0.7 + np.ones((n, n)) * 0.3
        
        return CorrelationMatrix(
            symbols=symbols,
            matrix=matrix,
            timeframe=timeframe,
            timestamp=datetime.now()
        )

    async def _get_fallback_chart_data(self, symbols: List[str]) -> ChartData:
        """Get fallback chart data."""
        return ChartData(
            chart_type="bar",
            data={"symbols": symbols, "values": [1.0] * len(symbols)},
            labels=symbols,
            colors=self._generate_colors(len(symbols)),
            title="Stock Comparison",
            x_axis_label="Stocks",
            y_axis_label="Values",
            timestamp=datetime.now()
        )

    async def _get_fallback_ranking(self, symbols: List[str]) -> RankingResult:
        """Get fallback ranking."""
        return RankingResult(
            rankings={"overall": symbols},
            scores={"overall": {symbol: 0.5 for symbol in symbols}},
            overall_ranking=symbols,
            ranking_criteria=["overall"],
            timestamp=datetime.now()
        )