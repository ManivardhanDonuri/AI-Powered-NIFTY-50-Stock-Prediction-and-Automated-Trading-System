"""
Pytest configuration and fixtures for AI Trading tests.
"""

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime
import numpy as np

from hypothesis import settings, Verbosity

# Configure Hypothesis for property-based testing
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.load_profile("default")


@pytest.fixture
def sample_portfolio():
    """Sample portfolio data for testing."""
    return {
        "total_value": 100000.0,
        "positions": {
            "AAPL": {"shares": 100, "value": 15000.0, "weight": 0.15},
            "GOOGL": {"shares": 50, "value": 12500.0, "weight": 0.125},
            "MSFT": {"shares": 75, "value": 22500.0, "weight": 0.225},
            "TSLA": {"shares": 25, "value": 5000.0, "weight": 0.05},
            "CASH": {"shares": 1, "value": 45000.0, "weight": 0.45}
        },
        "last_updated": datetime.now()
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "AAPL": {
            "price": 150.0,
            "volume": 1000000,
            "change": 2.5,
            "change_percent": 1.67,
            "high": 152.0,
            "low": 148.0,
            "open": 149.0
        },
        "market_trend": "bullish",
        "vix": 18.5,
        "timestamp": datetime.now()
    }


@pytest.fixture
def sample_prediction_result():
    """Sample prediction result for testing."""
    from ..data_models import PredictionResult, ConfidenceInterval
    
    return PredictionResult(
        symbol="AAPL",
        predictions={
            "1d": 152.0,
            "3d": 155.0,
            "7d": 160.0,
            "30d": 170.0
        },
        confidence_intervals={
            "1d": ConfidenceInterval(150.0, 154.0, 0.95),
            "3d": ConfidenceInterval(152.0, 158.0, 0.95),
            "7d": ConfidenceInterval(155.0, 165.0, 0.95),
            "30d": ConfidenceInterval(160.0, 180.0, 0.95)
        },
        confidence_score=85.0,
        timestamp=datetime.now(),
        model_ensemble=["lstm", "gru", "transformer"]
    )


@pytest.fixture
def sample_trading_recommendation():
    """Sample trading recommendation for testing."""
    from ..data_models import TradingRecommendation
    
    return TradingRecommendation(
        symbol="AAPL",
        action="BUY",
        confidence=0.85,
        target_price=160.0,
        stop_loss=140.0,
        position_size=100.0,
        rationale="Strong technical indicators and positive market sentiment",
        risk_reward_ratio=2.0,
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_risk_metrics():
    """Sample risk metrics for testing."""
    from ..data_models import RiskMetrics
    
    return RiskMetrics(
        symbol="AAPL",
        var_1d=2.5,
        var_5d=5.8,
        beta=1.2,
        volatility=0.25,
        sharpe_ratio=1.5,
        max_drawdown=0.15,
        correlation_to_market=0.8
    )


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()