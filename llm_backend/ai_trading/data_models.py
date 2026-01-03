"""
Data models for AI Trading Assistant.

This module contains all the data structures used throughout the AI trading system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import numpy as np


@dataclass
class ConfidenceInterval:
    """Confidence interval for predictions."""
    lower_bound: float
    upper_bound: float
    confidence_level: float


@dataclass
class PredictionResult:
    """Result of stock price prediction."""
    symbol: str
    predictions: Dict[str, float]  # timeframe -> price
    confidence_intervals: Dict[str, ConfidenceInterval]
    confidence_score: float
    timestamp: datetime
    model_ensemble: List[str]


@dataclass
class TradingRecommendation:
    """Trading recommendation with rationale."""
    symbol: str
    action: str  # "BUY", "SELL", "HOLD"
    confidence: float
    target_price: float
    stop_loss: float
    position_size: float
    rationale: str
    risk_reward_ratio: float
    timestamp: datetime


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics for a stock."""
    symbol: str
    var_1d: float  # Value at Risk (1 day)
    var_5d: float  # Value at Risk (5 days)
    beta: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    correlation_to_market: float


@dataclass
class SentimentAnalysis:
    """News sentiment analysis result."""
    symbol: str
    sentiment_score: float  # -1 to 1
    news_count: int
    key_themes: List[str]
    confidence: float
    sources: List[str]
    timestamp: datetime


@dataclass
class CorrelationMatrix:
    """Correlation matrix for multiple stocks."""
    symbols: List[str]
    matrix: np.ndarray
    timeframe: str
    timestamp: datetime


@dataclass
class ComparisonResult:
    """Result of comparative stock analysis."""
    symbols: List[str]
    metrics: Dict[str, Dict[str, float]]  # symbol -> metric -> value
    correlations: CorrelationMatrix
    rankings: Dict[str, List[str]]  # ranking_type -> ordered_symbols
    chart_data: Dict[str, Any]
    timestamp: datetime


@dataclass
class PerformanceAnalysis:
    """Portfolio performance analysis."""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    benchmark_comparison: Dict[str, float]
    timestamp: datetime


@dataclass
class RebalancingPlan:
    """Portfolio rebalancing recommendations."""
    current_allocation: Dict[str, float]
    target_allocation: Dict[str, float]
    trades_required: List[Dict[str, Any]]
    expected_cost: float
    tax_implications: Dict[str, float]
    rationale: str
    timestamp: datetime


@dataclass
class AttributionAnalysis:
    """Performance attribution analysis."""
    asset_allocation: Dict[str, float]
    security_selection: Dict[str, float]
    interaction_effect: float
    total_excess_return: float
    benchmark_return: float
    portfolio_return: float
    timestamp: datetime


@dataclass
class MarketEvent:
    """Significant market event."""
    event_type: str
    description: str
    impact_level: str  # "LOW", "MEDIUM", "HIGH"
    affected_sectors: List[str]
    timestamp: datetime
    source: str


@dataclass
class RiskAlert:
    """Risk alert notification."""
    alert_type: str
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    message: str
    affected_positions: List[str]
    recommended_action: str
    timestamp: datetime


@dataclass
class PortfolioRisk:
    """Overall portfolio risk assessment."""
    total_var: float
    concentration_risk: float
    sector_exposure: Dict[str, float]
    correlation_risk: float
    liquidity_risk: float
    overall_risk_score: float
    risk_alerts: List[RiskAlert]
    timestamp: datetime


@dataclass
class EnsemblePrediction:
    """Ensemble model prediction result."""
    individual_predictions: Dict[str, float]  # model_name -> prediction
    ensemble_prediction: float
    model_weights: Dict[str, float]
    confidence: float
    variance: float


@dataclass
class PositionSize:
    """Position sizing recommendation."""
    recommended_shares: int
    recommended_dollar_amount: float
    percentage_of_portfolio: float
    risk_per_share: float
    max_loss_amount: float
    rationale: str


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment."""
    risk_metrics: RiskMetrics
    portfolio_impact: float
    risk_score: float
    risk_factors: List[str]
    mitigation_strategies: List[str]
    timestamp: datetime


@dataclass
class ChartData:
    """Chart data for visualizations."""
    chart_type: str
    data: Dict[str, Any]
    labels: List[str]
    colors: List[str]
    title: str
    x_axis_label: str
    y_axis_label: str
    timestamp: datetime


@dataclass
class RankingResult:
    """Stock ranking result."""
    rankings: Dict[str, List[str]]  # criteria -> ordered_symbols
    scores: Dict[str, Dict[str, float]]  # symbol -> criteria -> score
    overall_ranking: List[str]
    ranking_criteria: List[str]
    timestamp: datetime


@dataclass
class TradingSignal:
    """Trading signal from analysis."""
    symbol: str
    signal_type: str  # "BUY", "SELL", "HOLD"
    strength: float  # 0-1
    source: str
    indicators: Dict[str, float]
    timestamp: datetime


@dataclass
class MarketCondition:
    """Current market condition assessment."""
    trend: str  # "BULLISH", "BEARISH", "SIDEWAYS"
    volatility_level: str  # "LOW", "MEDIUM", "HIGH"
    sentiment: float  # -1 to 1
    key_levels: Dict[str, float]  # support/resistance
    timestamp: datetime


@dataclass
class BacktestResult:
    """Backtesting result."""
    strategy_name: str
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    benchmark_return: float
    excess_return: float
    timestamp: datetime