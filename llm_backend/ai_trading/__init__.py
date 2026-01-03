"""
AI Trading Assistant Module

This module contains all the AI trading components including prediction engines,
recommendation engines, risk analyzers, and other trading analysis tools.
"""

from .interfaces import *
from .data_models import *

__version__ = "1.0.0"
__all__ = [
    # Interfaces
    'PredictionEngineInterface',
    'RecommendationEngineInterface', 
    'RiskAnalyzerInterface',
    'MarketContextAnalyzerInterface',
    'PortfolioAnalyzerInterface',
    'ComparativeAnalyzerInterface',
    
    # Data Models
    'PredictionResult',
    'ConfidenceInterval',
    'TradingRecommendation',
    'RiskMetrics',
    'ComparisonResult',
    'SentimentAnalysis',
    'PerformanceAnalysis',
    'RebalancingPlan',
    'AttributionAnalysis',
    'MarketEvent',
    'RiskAlert',
    'PortfolioRisk',
    'EnsemblePrediction',
    'PositionSize',
    'RiskAssessment',
    'ChartData',
    'CorrelationMatrix',
    'RankingResult'
]