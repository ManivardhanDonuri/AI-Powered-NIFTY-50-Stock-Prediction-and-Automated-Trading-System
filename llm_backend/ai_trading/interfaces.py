"""
Core interfaces for AI Trading Assistant components.

These interfaces define the contracts that all AI trading components must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np

from .data_models import (
    PredictionResult, TradingRecommendation, RiskMetrics, ComparisonResult,
    SentimentAnalysis, PerformanceAnalysis, RebalancingPlan, AttributionAnalysis,
    MarketEvent, RiskAlert, PortfolioRisk, ConfidenceInterval, EnsemblePrediction,
    PositionSize, RiskAssessment, ChartData, CorrelationMatrix, RankingResult
)


class PredictionEngineInterface(ABC):
    """Interface for stock price prediction engines."""
    
    @abstractmethod
    async def generate_predictions(
        self, 
        symbol: str, 
        timeframes: List[str] = ["1d", "3d", "7d", "30d"]
    ) -> PredictionResult:
        """Generate multi-timeframe price predictions for a stock."""
        pass
    
    @abstractmethod
    async def calculate_confidence_intervals(
        self, 
        predictions: np.ndarray, 
        volatility: float
    ) -> ConfidenceInterval:
        """Calculate confidence intervals for predictions."""
        pass
    
    @abstractmethod
    async def ensemble_predict(
        self, 
        models: List[Any], 
        features: np.ndarray
    ) -> EnsemblePrediction:
        """Generate ensemble predictions from multiple models."""
        pass


class RecommendationEngineInterface(ABC):
    """Interface for trading recommendation engines."""
    
    @abstractmethod
    async def generate_recommendation(
        self, 
        symbol: str, 
        prediction: PredictionResult, 
        risk_analysis: RiskAssessment
    ) -> TradingRecommendation:
        """Generate buy/sell/hold recommendations."""
        pass
    
    @abstractmethod
    async def calculate_position_size(
        self, 
        recommendation: TradingRecommendation, 
        portfolio: Dict[str, Any]
    ) -> PositionSize:
        """Calculate appropriate position size."""
        pass
    
    @abstractmethod
    async def generate_rationale(
        self, 
        recommendation: TradingRecommendation
    ) -> str:
        """Generate detailed rationale for recommendation."""
        pass


class RiskAnalyzerInterface(ABC):
    """Interface for risk analysis components."""
    
    @abstractmethod
    async def calculate_risk_metrics(
        self, 
        symbol: str, 
        portfolio: Dict[str, Any]
    ) -> RiskMetrics:
        """Calculate comprehensive risk metrics."""
        pass
    
    @abstractmethod
    async def assess_portfolio_risk(
        self, 
        portfolio: Dict[str, Any]
    ) -> PortfolioRisk:
        """Assess overall portfolio risk."""
        pass
    
    @abstractmethod
    async def generate_risk_alerts(
        self, 
        risk_metrics: RiskMetrics
    ) -> List[RiskAlert]:
        """Generate risk alerts based on metrics."""
        pass


class MarketContextAnalyzerInterface(ABC):
    """Interface for market context analysis."""
    
    @abstractmethod
    async def analyze_news_sentiment(
        self, 
        symbol: str, 
        timeframe: str = "24h"
    ) -> SentimentAnalysis:
        """Analyze news sentiment for a stock."""
        pass
    
    @abstractmethod
    async def detect_market_events(
        self, 
        market_data: Dict[str, Any]
    ) -> List[MarketEvent]:
        """Detect significant market events."""
        pass
    
    @abstractmethod
    async def update_context(
        self, 
        context_data: Dict[str, Any]
    ) -> None:
        """Update market context with new data."""
        pass


class PortfolioAnalyzerInterface(ABC):
    """Interface for portfolio analysis components."""
    
    @abstractmethod
    async def analyze_performance(
        self, 
        portfolio: Dict[str, Any]
    ) -> PerformanceAnalysis:
        """Analyze portfolio performance."""
        pass
    
    @abstractmethod
    async def suggest_rebalancing(
        self, 
        portfolio: Dict[str, Any]
    ) -> RebalancingPlan:
        """Suggest portfolio rebalancing."""
        pass
    
    @abstractmethod
    async def calculate_attribution(
        self, 
        portfolio: Dict[str, Any]
    ) -> AttributionAnalysis:
        """Calculate performance attribution."""
        pass


class ComparativeAnalyzerInterface(ABC):
    """Interface for comparative stock analysis."""
    
    @abstractmethod
    async def compare_stocks(
        self, 
        symbols: List[str], 
        metrics: List[str], 
        timeframe: str
    ) -> ComparisonResult:
        """Compare multiple stocks across metrics."""
        pass
    
    @abstractmethod
    async def generate_comparison_chart(
        self, 
        comparison_data: ComparisonResult, 
        chart_type: str
    ) -> ChartData:
        """Generate comparison charts."""
        pass
    
    @abstractmethod
    async def calculate_correlations(
        self, 
        symbols: List[str], 
        timeframe: str
    ) -> CorrelationMatrix:
        """Calculate correlation matrix for stocks."""
        pass
    
    @abstractmethod
    async def rank_opportunities(
        self, 
        comparison_data: ComparisonResult
    ) -> RankingResult:
        """Rank trading opportunities."""
        pass


class LearningAdaptationEngineInterface(ABC):
    """Interface for learning and adaptation components."""
    
    @abstractmethod
    async def track_prediction_accuracy(
        self, 
        symbol: str, 
        timeframe: str
    ) -> Dict[str, Any]:
        """Track prediction accuracy by comparing predictions with actual prices."""
        pass
    
    @abstractmethod
    async def evaluate_retraining_need(
        self, 
        symbol: str = None
    ) -> Dict[str, Any]:
        """Evaluate if models need retraining based on accuracy thresholds."""
        pass
    
    @abstractmethod
    async def trigger_model_retraining(
        self, 
        symbol: str, 
        model_types: List[str] = None
    ) -> Dict[str, Any]:
        """Trigger automatic model retraining for a symbol."""
        pass
    
    @abstractmethod
    async def identify_performance_patterns(
        self, 
        symbol: str = None
    ) -> Dict[str, Any]:
        """Identify patterns in prediction performance to guide model improvements."""
        pass
    
    @abstractmethod
    async def adjust_model_parameters(
        self, 
        symbol: str, 
        adjustments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust model parameters based on performance analysis."""
        pass