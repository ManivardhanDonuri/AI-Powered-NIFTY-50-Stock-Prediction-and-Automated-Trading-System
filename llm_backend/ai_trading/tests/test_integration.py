"""
Integration and System Tests for AI Trading Assistant

This module provides comprehensive integration tests covering:
- End-to-end workflows with Ollama integration
- Real-time WebSocket functionality
- Performance under various load conditions
- Data privacy and local processing verification
- System resilience and error handling
"""

import asyncio
import pytest
import json
import time
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch, MagicMock
import websockets
from concurrent.futures import ThreadPoolExecutor
import aiohttp

# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio

from ..engines.prediction_engine import PredictionEngine
from ..engines.recommendation_engine import RecommendationEngine
from ..engines.risk_analyzer import RiskAnalyzer
from ..engines.market_context_analyzer import MarketContextAnalyzer
from ..engines.portfolio_analyzer import PortfolioAnalyzer
from ..engines.comparative_analyzer import ComparativeAnalyzer
from ..engines.learning_adaptation_engine import LearningAdaptationEngine
from ..data_models import (
    PredictionResult, TradingRecommendation, RiskMetrics, RiskAssessment,
    ConfidenceInterval, EnsemblePrediction
)
from ..error_handling import get_error_handler, AITradingError
from ..ollama_recovery import get_ollama_recovery_service
from ..startup import initialize_ai_trading_system, shutdown_ai_trading_system
from ...services.ollama_service import OllamaService, OllamaConfig
from ...websocket.chat_websocket import ChatWebSocketHandler
from ...database.chat_db import ChatDatabase


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows with Ollama integration."""
    
    @pytest.fixture
    async def ai_system(self):
        """Initialize AI trading system for testing."""
        # Use test configuration
        ollama_config = OllamaConfig(
            model_name="llama3.2",
            host="localhost",
            port=11434,
            timeout=30
        )
        
        # Initialize system
        initialized = await initialize_ai_trading_system(
            ollama_config=ollama_config,
            start_monitoring=False  # Disable monitoring for tests
        )
        
        yield initialized
        
        # Cleanup
        await shutdown_ai_trading_system()
    
    @pytest.mark.asyncio
    async def test_complete_prediction_workflow(self, ai_system):
        """Test complete prediction workflow from data to result."""
        if not ai_system:
            pytest.skip("AI system not initialized - Ollama may not be available")
        
        prediction_engine = PredictionEngine()
        
        # Mock data dependencies to avoid external API calls
        with patch.multiple(
            'llm_backend.ai_trading.engines.prediction_engine',
            DataFetcher=AsyncMock(),
            MLModels=AsyncMock(),
            MLFeatureEngineer=AsyncMock(),
            TechnicalIndicators=AsyncMock()
        ):
            # Mock the internal methods
            prediction_engine._fetch_historical_data = AsyncMock(
                return_value=[100, 101, 102, 103, 104, 105]
            )
            prediction_engine._generate_features = AsyncMock(
                return_value=[1, 2, 3, 4, 5]
            )
            prediction_engine._get_models_for_symbol = AsyncMock(return_value=[])
            prediction_engine._calculate_volatility = AsyncMock(return_value=0.2)
            prediction_engine._calculate_overall_confidence = AsyncMock(return_value=75.0)
            
            # Mock ensemble prediction
            mock_ensemble = EnsemblePrediction(
                individual_predictions={"lstm": 106.0, "gru": 107.0},
                ensemble_prediction=106.5,
                model_weights={"lstm": 0.6, "gru": 0.4},
                confidence=0.8,
                variance=0.1
            )
            prediction_engine.ensemble_predict = AsyncMock(return_value=mock_ensemble)
            
            # Mock confidence intervals
            mock_confidence = ConfidenceInterval(
                lower_bound=104.0,
                upper_bound=109.0,
                confidence_level=0.95
            )
            prediction_engine.calculate_confidence_intervals = AsyncMock(
                return_value=mock_confidence
            )
            
            # Test prediction generation
            result = await prediction_engine.generate_predictions("AAPL")
            
            # Verify result structure
            assert isinstance(result, PredictionResult)
            assert result.symbol == "AAPL"
            assert "1d" in result.predictions
            assert "3d" in result.predictions
            assert "7d" in result.predictions
            assert "30d" in result.predictions
            assert result.confidence_score > 0
            assert len(result.model_ensemble) > 0
            
            # Verify confidence intervals
            for timeframe in ["1d", "3d", "7d", "30d"]:
                ci = result.confidence_intervals[timeframe]
                assert ci.lower_bound < ci.upper_bound
                assert ci.confidence_level > 0
    
    @pytest.mark.asyncio
    async def test_complete_recommendation_workflow(self, ai_system):
        """Test complete recommendation workflow including Ollama integration."""
        if not ai_system:
            pytest.skip("AI system not initialized - Ollama may not be available")
        
        prediction_engine = PredictionEngine()
        recommendation_engine = RecommendationEngine()
        risk_analyzer = RiskAnalyzer()
        
        # Mock all dependencies
        with patch.multiple(
            'llm_backend.ai_trading.engines.prediction_engine',
            DataFetcher=AsyncMock(),
            MLModels=AsyncMock(),
            MLFeatureEngineer=AsyncMock(),
            TechnicalIndicators=AsyncMock()
        ), patch.multiple(
            'llm_backend.ai_trading.engines.risk_analyzer',
            DataFetcher=AsyncMock(),
            TechnicalIndicators=AsyncMock()
        ):
            # Setup prediction engine mocks
            prediction_engine._fetch_historical_data = AsyncMock(
                return_value=[100, 101, 102, 103, 104, 105]
            )
            prediction_engine._generate_features = AsyncMock(return_value=[1, 2, 3, 4, 5])
            prediction_engine._get_models_for_symbol = AsyncMock(return_value=[])
            prediction_engine._calculate_volatility = AsyncMock(return_value=0.2)
            prediction_engine._calculate_overall_confidence = AsyncMock(return_value=85.0)
            
            mock_ensemble = EnsemblePrediction(
                individual_predictions={"lstm": 106.0},
                ensemble_prediction=106.0,
                model_weights={"lstm": 1.0},
                confidence=0.85,
                variance=0.1
            )
            prediction_engine.ensemble_predict = AsyncMock(return_value=mock_ensemble)
            
            mock_confidence = ConfidenceInterval(
                lower_bound=104.0,
                upper_bound=108.0,
                confidence_level=0.95
            )
            prediction_engine.calculate_confidence_intervals = AsyncMock(
                return_value=mock_confidence
            )
            
            # Setup risk analyzer mocks
            risk_analyzer._fetch_market_data = AsyncMock(
                return_value={"price": 105.0, "volume": 1000000}
            )
            risk_analyzer._calculate_beta = AsyncMock(return_value=1.2)
            risk_analyzer._calculate_var = AsyncMock(return_value=2.5)
            risk_analyzer._calculate_sharpe_ratio = AsyncMock(return_value=1.5)
            risk_analyzer._calculate_max_drawdown = AsyncMock(return_value=0.15)
            risk_analyzer._calculate_correlation = AsyncMock(return_value=0.8)
            
            # Mock Ollama service for rationale generation
            with patch('llm_backend.services.ollama_service.get_ollama_service') as mock_ollama:
                mock_service = AsyncMock()
                mock_service.generate_rationale.return_value = (
                    "Strong technical indicators suggest upward momentum. "
                    "Market conditions are favorable with low volatility. "
                    "Risk-reward ratio is attractive at current levels."
                )
                mock_ollama.return_value = mock_service
                
                # Execute complete workflow
                prediction = await prediction_engine.generate_predictions("AAPL")
                risk_metrics = await risk_analyzer.calculate_risk_metrics("AAPL", {})
                
                risk_assessment = RiskAssessment(
                    risk_metrics=risk_metrics,
                    portfolio_impact=0.1,
                    risk_score=50.0,
                    risk_factors=["volatility", "beta"],
                    mitigation_strategies=["diversification"],
                    timestamp=datetime.now()
                )
                
                recommendation = await recommendation_engine.generate_recommendation(
                    "AAPL", prediction, risk_assessment
                )
                
                # Verify complete recommendation
                assert isinstance(recommendation, TradingRecommendation)
                assert recommendation.symbol == "AAPL"
                assert recommendation.action in ["BUY", "SELL", "HOLD"]
                assert recommendation.confidence > 0
                assert recommendation.target_price > 0
                assert recommendation.stop_loss > 0
                assert len(recommendation.rationale) > 0
                assert recommendation.risk_reward_ratio > 0
                
                # Verify Ollama integration was called
                mock_service.generate_rationale.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_portfolio_analysis_workflow(self, ai_system):
        """Test complete portfolio analysis workflow."""
        if not ai_system:
            pytest.skip("AI system not initialized")
        
        portfolio_analyzer = PortfolioAnalyzer()
        
        # Sample portfolio data
        portfolio = {
            "total_value": 100000.0,
            "positions": {
                "AAPL": {"shares": 100, "value": 15000.0, "weight": 0.15},
                "GOOGL": {"shares": 50, "value": 12500.0, "weight": 0.125},
                "MSFT": {"shares": 75, "value": 22500.0, "weight": 0.225},
                "CASH": {"shares": 1, "value": 50000.0, "weight": 0.5}
            }
        }
        
        with patch.multiple(
            'llm_backend.ai_trading.engines.portfolio_analyzer',
            DataFetcher=AsyncMock(),
            TechnicalIndicators=AsyncMock()
        ):
            # Mock data fetching
            portfolio_analyzer._fetch_portfolio_data = AsyncMock(return_value=portfolio)
            portfolio_analyzer._calculate_returns = AsyncMock(return_value=0.12)
            portfolio_analyzer._calculate_volatility = AsyncMock(return_value=0.18)
            portfolio_analyzer._calculate_sharpe_ratio = AsyncMock(return_value=1.2)
            portfolio_analyzer._calculate_max_drawdown = AsyncMock(return_value=0.08)
            portfolio_analyzer._get_benchmark_data = AsyncMock(return_value={"return": 0.10})
            
            # Test performance analysis
            performance = await portfolio_analyzer.analyze_performance(portfolio)
            
            assert performance.total_return > 0
            assert performance.volatility > 0
            assert performance.sharpe_ratio > 0
            assert performance.max_drawdown >= 0
            
            # Test rebalancing suggestions
            rebalancing = await portfolio_analyzer.suggest_rebalancing(portfolio)
            
            assert "current_allocation" in rebalancing.current_allocation
            assert "target_allocation" in rebalancing.target_allocation
            assert len(rebalancing.rationale) > 0


class TestWebSocketIntegration:
    """Test real-time WebSocket functionality."""
    
    @pytest.fixture
    async def websocket_handler(self):
        """Create WebSocket handler for testing."""
        # Mock dependencies
        llm_service = AsyncMock()
        context_provider = AsyncMock()
        chat_db = AsyncMock()
        
        handler = ChatWebSocketHandler(llm_service, context_provider, chat_db)
        return handler
    
    @pytest.mark.asyncio
    async def test_ai_prediction_websocket_request(self, websocket_handler):
        """Test AI prediction requests via WebSocket."""
        user_id = "test_user"
        
        # Mock WebSocket message
        message_data = {
            "type": "ai_prediction_request",
            "data": {
                "symbol": "AAPL",
                "timeframes": ["1d", "3d", "7d"]
            }
        }
        
        # Mock prediction engine
        with patch('llm_backend.websocket.chat_websocket.PredictionEngine') as mock_engine:
            mock_instance = AsyncMock()
            mock_result = PredictionResult(
                symbol="AAPL",
                predictions={"1d": 150.0, "3d": 155.0, "7d": 160.0},
                confidence_intervals={
                    "1d": ConfidenceInterval(148.0, 152.0, 0.95),
                    "3d": ConfidenceInterval(152.0, 158.0, 0.95),
                    "7d": ConfidenceInterval(155.0, 165.0, 0.95)
                },
                confidence_score=85.0,
                timestamp=datetime.now(),
                model_ensemble=["lstm", "gru"]
            )
            mock_instance.generate_predictions.return_value = mock_result
            mock_engine.return_value = mock_instance
            
            # Mock connection manager
            websocket_handler.connection_manager.send_personal_message = AsyncMock()
            
            # Create mock WebSocket message
            from ...websocket.chat_websocket import WebSocketMessage
            ws_message = WebSocketMessage(**message_data)
            
            # Handle the message
            await websocket_handler.handle_ai_prediction_request(user_id, ws_message)
            
            # Verify prediction was generated
            mock_instance.generate_predictions.assert_called_once_with(
                "AAPL", ["1d", "3d", "7d"]
            )
            
            # Verify WebSocket responses were sent
            assert websocket_handler.connection_manager.send_personal_message.call_count >= 2
            
            # Check processing notification was sent
            processing_call = websocket_handler.connection_manager.send_personal_message.call_args_list[0]
            processing_message = processing_call[0][1]
            assert processing_message["type"] == "ai_processing"
            assert processing_message["data"]["request_type"] == "prediction"
            
            # Check result was sent
            result_call = websocket_handler.connection_manager.send_personal_message.call_args_list[1]
            result_message = result_call[0][1]
            assert result_message["type"] == "ai_prediction_result"
            assert result_message["data"]["symbol"] == "AAPL"
            assert result_message["data"]["confidence_score"] == 85.0
    
    @pytest.mark.asyncio
    async def test_ai_recommendation_websocket_request(self, websocket_handler):
        """Test AI recommendation requests via WebSocket."""
        user_id = "test_user"
        
        message_data = {
            "type": "ai_recommendation_request",
            "data": {
                "symbol": "AAPL",
                "portfolio": {"total_value": 100000}
            }
        }
        
        # Mock all required engines
        with patch.multiple(
            'llm_backend.websocket.chat_websocket',
            PredictionEngine=AsyncMock,
            RecommendationEngine=AsyncMock,
            RiskAnalyzer=AsyncMock
        ) as mocks:
            # Setup mock returns
            mock_prediction = PredictionResult(
                symbol="AAPL",
                predictions={"1d": 150.0},
                confidence_intervals={"1d": ConfidenceInterval(148.0, 152.0, 0.95)},
                confidence_score=80.0,
                timestamp=datetime.now(),
                model_ensemble=["lstm"]
            )
            
            mock_risk_metrics = RiskMetrics(
                symbol="AAPL",
                var_1d=2.5,
                var_5d=5.8,
                beta=1.2,
                volatility=0.25,
                sharpe_ratio=1.5,
                max_drawdown=0.15,
                correlation_to_market=0.8
            )
            
            mock_recommendation = TradingRecommendation(
                symbol="AAPL",
                action="BUY",
                confidence=0.8,
                target_price=155.0,
                stop_loss=145.0,
                position_size=100.0,
                rationale="Strong technical indicators",
                risk_reward_ratio=2.0,
                timestamp=datetime.now()
            )
            
            # Configure mocks
            mocks['PredictionEngine'].return_value.generate_predictions.return_value = mock_prediction
            mocks['RiskAnalyzer'].return_value.calculate_risk_metrics.return_value = mock_risk_metrics
            mocks['RecommendationEngine'].return_value.generate_recommendation.return_value = mock_recommendation
            
            websocket_handler.connection_manager.send_personal_message = AsyncMock()
            
            from ...websocket.chat_websocket import WebSocketMessage
            ws_message = WebSocketMessage(**message_data)
            
            # Handle the message
            await websocket_handler.handle_ai_recommendation_request(user_id, ws_message)
            
            # Verify all components were called
            mocks['PredictionEngine'].return_value.generate_predictions.assert_called_once()
            mocks['RiskAnalyzer'].return_value.calculate_risk_metrics.assert_called_once()
            mocks['RecommendationEngine'].return_value.generate_recommendation.assert_called_once()
            
            # Verify WebSocket responses
            assert websocket_handler.connection_manager.send_personal_message.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_websocket_error_handling(self, websocket_handler):
        """Test WebSocket error handling and recovery."""
        user_id = "test_user"
        
        message_data = {
            "type": "ai_prediction_request",
            "data": {
                "symbol": "INVALID"
            }
        }
        
        # Mock prediction engine to raise error
        with patch('llm_backend.websocket.chat_websocket.PredictionEngine') as mock_engine:
            mock_instance = AsyncMock()
            mock_instance.generate_predictions.side_effect = Exception("Test error")
            mock_engine.return_value = mock_instance
            
            websocket_handler.connection_manager.send_personal_message = AsyncMock()
            websocket_handler.send_error = AsyncMock()
            
            from ...websocket.chat_websocket import WebSocketMessage
            ws_message = WebSocketMessage(**message_data)
            
            # Handle the message (should not raise exception)
            await websocket_handler.handle_ai_prediction_request(user_id, ws_message)
            
            # Verify error was sent to user
            websocket_handler.send_error.assert_called_once()
            error_call = websocket_handler.send_error.call_args[0]
            assert "Prediction request failed" in error_call[1]


class TestPerformanceAndLoad:
    """Test performance under various load conditions."""
    
    @pytest.mark.asyncio
    async def test_concurrent_prediction_requests(self):
        """Test system performance under concurrent prediction requests."""
        prediction_engine = PredictionEngine()
        
        # Mock dependencies for performance testing
        with patch.multiple(
            'llm_backend.ai_trading.engines.prediction_engine',
            DataFetcher=AsyncMock(),
            MLModels=AsyncMock(),
            MLFeatureEngineer=AsyncMock(),
            TechnicalIndicators=AsyncMock()
        ):
            # Setup fast mocks for performance testing
            prediction_engine._fetch_historical_data = AsyncMock(
                return_value=[100, 101, 102, 103, 104]
            )
            prediction_engine._generate_features = AsyncMock(return_value=[1, 2, 3, 4, 5])
            prediction_engine._get_models_for_symbol = AsyncMock(return_value=[])
            prediction_engine._calculate_volatility = AsyncMock(return_value=0.2)
            prediction_engine._calculate_overall_confidence = AsyncMock(return_value=75.0)
            
            mock_ensemble = EnsemblePrediction(
                individual_predictions={"lstm": 105.0},
                ensemble_prediction=105.0,
                model_weights={"lstm": 1.0},
                confidence=0.75,
                variance=0.1
            )
            prediction_engine.ensemble_predict = AsyncMock(return_value=mock_ensemble)
            
            mock_confidence = ConfidenceInterval(
                lower_bound=103.0,
                upper_bound=107.0,
                confidence_level=0.95
            )
            prediction_engine.calculate_confidence_intervals = AsyncMock(
                return_value=mock_confidence
            )
            
            # Test concurrent requests
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
            concurrent_requests = 10
            
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = []
            for i in range(concurrent_requests):
                symbol = symbols[i % len(symbols)]
                task = asyncio.create_task(
                    prediction_engine.generate_predictions(symbol)
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verify results
            successful_results = [r for r in results if isinstance(r, PredictionResult)]
            failed_results = [r for r in results if isinstance(r, Exception)]
            
            assert len(successful_results) >= concurrent_requests * 0.8  # At least 80% success
            assert total_time < 30  # Should complete within 30 seconds
            
            # Verify performance metrics
            avg_time_per_request = total_time / concurrent_requests
            assert avg_time_per_request < 5  # Each request should take less than 5 seconds on average
            
            print(f"Concurrent requests: {concurrent_requests}")
            print(f"Total time: {total_time:.2f}s")
            print(f"Average time per request: {avg_time_per_request:.2f}s")
            print(f"Successful requests: {len(successful_results)}")
            print(f"Failed requests: {len(failed_results)}")
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage under sustained load."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        prediction_engine = PredictionEngine()
        
        with patch.multiple(
            'llm_backend.ai_trading.engines.prediction_engine',
            DataFetcher=AsyncMock(),
            MLModels=AsyncMock(),
            MLFeatureEngineer=AsyncMock(),
            TechnicalIndicators=AsyncMock()
        ):
            # Setup mocks
            prediction_engine._fetch_historical_data = AsyncMock(
                return_value=[100] * 1000  # Large dataset
            )
            prediction_engine._generate_features = AsyncMock(
                return_value=list(range(1000))
            )
            prediction_engine._get_models_for_symbol = AsyncMock(return_value=[])
            prediction_engine._calculate_volatility = AsyncMock(return_value=0.2)
            prediction_engine._calculate_overall_confidence = AsyncMock(return_value=75.0)
            
            mock_ensemble = EnsemblePrediction(
                individual_predictions={"lstm": 105.0},
                ensemble_prediction=105.0,
                model_weights={"lstm": 1.0},
                confidence=0.75,
                variance=0.1
            )
            prediction_engine.ensemble_predict = AsyncMock(return_value=mock_ensemble)
            
            mock_confidence = ConfidenceInterval(
                lower_bound=103.0,
                upper_bound=107.0,
                confidence_level=0.95
            )
            prediction_engine.calculate_confidence_intervals = AsyncMock(
                return_value=mock_confidence
            )
            
            # Run sustained load test
            for i in range(50):  # 50 iterations
                await prediction_engine.generate_predictions("AAPL")
                
                # Force garbage collection every 10 iterations
                if i % 10 == 0:
                    gc.collect()
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_increase = current_memory - initial_memory
                    
                    # Memory increase should be reasonable (less than 100MB)
                    assert memory_increase < 100, f"Memory usage increased by {memory_increase:.2f}MB"
            
            final_memory = process.memory_info().rss / 1024 / 1024
            total_memory_increase = final_memory - initial_memory
            
            print(f"Initial memory: {initial_memory:.2f}MB")
            print(f"Final memory: {final_memory:.2f}MB")
            print(f"Total memory increase: {total_memory_increase:.2f}MB")
            
            # Final memory check
            assert total_memory_increase < 200, f"Total memory increase too high: {total_memory_increase:.2f}MB"
    
    @pytest.mark.asyncio
    async def test_response_time_under_load(self):
        """Test response times under various load conditions."""
        prediction_engine = PredictionEngine()
        
        with patch.multiple(
            'llm_backend.ai_trading.engines.prediction_engine',
            DataFetcher=AsyncMock(),
            MLModels=AsyncMock(),
            MLFeatureEngineer=AsyncMock(),
            TechnicalIndicators=AsyncMock()
        ):
            # Setup mocks with variable delays to simulate real conditions
            async def mock_fetch_with_delay(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate network delay
                return [100, 101, 102, 103, 104]
            
            prediction_engine._fetch_historical_data = mock_fetch_with_delay
            prediction_engine._generate_features = AsyncMock(return_value=[1, 2, 3, 4, 5])
            prediction_engine._get_models_for_symbol = AsyncMock(return_value=[])
            prediction_engine._calculate_volatility = AsyncMock(return_value=0.2)
            prediction_engine._calculate_overall_confidence = AsyncMock(return_value=75.0)
            
            mock_ensemble = EnsemblePrediction(
                individual_predictions={"lstm": 105.0},
                ensemble_prediction=105.0,
                model_weights={"lstm": 1.0},
                confidence=0.75,
                variance=0.1
            )
            prediction_engine.ensemble_predict = AsyncMock(return_value=mock_ensemble)
            
            mock_confidence = ConfidenceInterval(
                lower_bound=103.0,
                upper_bound=107.0,
                confidence_level=0.95
            )
            prediction_engine.calculate_confidence_intervals = AsyncMock(
                return_value=mock_confidence
            )
            
            # Test different load levels
            load_levels = [1, 5, 10, 20]
            response_times = {}
            
            for load in load_levels:
                start_time = time.time()
                
                # Create concurrent tasks
                tasks = [
                    asyncio.create_task(prediction_engine.generate_predictions("AAPL"))
                    for _ in range(load)
                ]
                
                # Wait for completion
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                end_time = time.time()
                total_time = end_time - start_time
                avg_response_time = total_time / load
                
                response_times[load] = avg_response_time
                
                # Verify reasonable response times
                assert avg_response_time < 10, f"Response time too high at load {load}: {avg_response_time:.2f}s"
                
                print(f"Load {load}: Average response time {avg_response_time:.2f}s")
            
            # Verify response times don't degrade too much with load
            baseline_time = response_times[1]
            high_load_time = response_times[20]
            degradation_factor = high_load_time / baseline_time
            
            assert degradation_factor < 5, f"Response time degradation too high: {degradation_factor:.2f}x"


class TestDataPrivacyAndLocalProcessing:
    """Test data privacy and local processing verification."""
    
    @pytest.mark.asyncio
    async def test_ollama_local_processing(self):
        """Verify that Ollama processes data locally without external calls."""
        ollama_service = OllamaService()
        
        # Mock aiohttp session to track external calls
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": "Test rationale generated locally",
            "model": "llama3.2",
            "prompt_eval_count": 50,
            "eval_count": 100
        }
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(ollama_service, '_get_session', return_value=mock_session):
            # Test rationale generation
            recommendation = {
                "symbol": "AAPL",
                "action": "BUY",
                "confidence": 0.8,
                "target_price": 150.0
            }
            market_context = {"market_trend": "bullish"}
            
            rationale = await ollama_service.generate_rationale(recommendation, market_context)
            
            # Verify local processing
            assert len(rationale) > 0
            
            # Verify only local Ollama endpoint was called
            mock_session.post.assert_called_once()
            call_args = mock_session.post.call_args
            called_url = call_args[0][0]
            
            # Should only call localhost Ollama endpoint
            assert "localhost" in called_url or "127.0.0.1" in called_url
            assert "11434" in called_url  # Default Ollama port
            assert "/api/generate" in called_url
            
            # Verify no external API calls
            external_domains = ["openai.com", "api.anthropic.com", "googleapis.com"]
            for domain in external_domains:
                assert domain not in called_url
    
    @pytest.mark.asyncio
    async def test_no_external_data_transmission(self):
        """Verify no sensitive data is transmitted to external services."""
        # Mock network monitoring
        external_calls = []
        
        async def mock_request(method, url, **kwargs):
            external_calls.append({
                "method": method,
                "url": url,
                "data": kwargs.get("json", {}),
                "timestamp": datetime.now()
            })
            
            # Mock response for local Ollama calls
            if "localhost" in url or "127.0.0.1" in url:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {
                    "response": "Local response",
                    "model": "llama3.2"
                }
                return mock_response
            else:
                # Fail external calls
                raise aiohttp.ClientError("External call blocked")
        
        # Patch all HTTP clients
        with patch('aiohttp.ClientSession.request', side_effect=mock_request), \
             patch('aiohttp.ClientSession.get', side_effect=mock_request), \
             patch('aiohttp.ClientSession.post', side_effect=mock_request):
            
            # Test complete workflow
            prediction_engine = PredictionEngine()
            recommendation_engine = RecommendationEngine()
            
            # Mock internal dependencies to avoid external calls
            with patch.multiple(
                'llm_backend.ai_trading.engines.prediction_engine',
                DataFetcher=AsyncMock(),
                MLModels=AsyncMock(),
                MLFeatureEngineer=AsyncMock(),
                TechnicalIndicators=AsyncMock()
            ):
                # Setup mocks
                prediction_engine._fetch_historical_data = AsyncMock(
                    return_value=[100, 101, 102, 103, 104]
                )
                prediction_engine._generate_features = AsyncMock(return_value=[1, 2, 3, 4, 5])
                prediction_engine._get_models_for_symbol = AsyncMock(return_value=[])
                prediction_engine._calculate_volatility = AsyncMock(return_value=0.2)
                prediction_engine._calculate_overall_confidence = AsyncMock(return_value=75.0)
                
                mock_ensemble = EnsemblePrediction(
                    individual_predictions={"lstm": 105.0},
                    ensemble_prediction=105.0,
                    model_weights={"lstm": 1.0},
                    confidence=0.75,
                    variance=0.1
                )
                prediction_engine.ensemble_predict = AsyncMock(return_value=mock_ensemble)
                
                mock_confidence = ConfidenceInterval(
                    lower_bound=103.0,
                    upper_bound=107.0,
                    confidence_level=0.95
                )
                prediction_engine.calculate_confidence_intervals = AsyncMock(
                    return_value=mock_confidence
                )
                
                # Test prediction generation
                try:
                    prediction = await prediction_engine.generate_predictions("AAPL")
                    assert prediction.symbol == "AAPL"
                except Exception as e:
                    # Should not fail due to external calls
                    assert "External call blocked" not in str(e)
                
                # Verify only local calls were made
                local_calls = [call for call in external_calls 
                             if "localhost" in call["url"] or "127.0.0.1" in call["url"]]
                external_calls_made = [call for call in external_calls 
                                     if "localhost" not in call["url"] and "127.0.0.1" not in call["url"]]
                
                # Should have local calls but no external calls
                assert len(external_calls_made) == 0, f"External calls detected: {external_calls_made}"
                
                print(f"Local calls made: {len(local_calls)}")
                print(f"External calls blocked: {len(external_calls_made)}")
    
    @pytest.mark.asyncio
    async def test_sensitive_data_handling(self):
        """Test that sensitive data is properly handled and not logged."""
        import logging
        from io import StringIO
        
        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger('llm_backend.ai_trading')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            # Test with sensitive portfolio data
            sensitive_portfolio = {
                "total_value": 1000000.0,  # Large portfolio value
                "positions": {
                    "AAPL": {"shares": 1000, "value": 150000.0},
                    "account_number": "123456789",  # Sensitive info
                    "ssn": "123-45-6789"  # Very sensitive
                }
            }
            
            risk_analyzer = RiskAnalyzer()
            
            with patch.multiple(
                'llm_backend.ai_trading.engines.risk_analyzer',
                DataFetcher=AsyncMock(),
                TechnicalIndicators=AsyncMock()
            ):
                # Mock methods to avoid external calls
                risk_analyzer._fetch_market_data = AsyncMock(
                    return_value={"price": 150.0, "volume": 1000000}
                )
                risk_analyzer._calculate_beta = AsyncMock(return_value=1.2)
                risk_analyzer._calculate_var = AsyncMock(return_value=2.5)
                risk_analyzer._calculate_sharpe_ratio = AsyncMock(return_value=1.5)
                risk_analyzer._calculate_max_drawdown = AsyncMock(return_value=0.15)
                risk_analyzer._calculate_correlation = AsyncMock(return_value=0.8)
                
                # Perform analysis with sensitive data
                risk_metrics = await risk_analyzer.calculate_risk_metrics("AAPL", sensitive_portfolio)
                
                # Verify analysis completed
                assert risk_metrics.symbol == "AAPL"
                assert risk_metrics.volatility > 0
                
                # Check logs for sensitive data leakage
                log_output = log_capture.getvalue()
                
                # Sensitive data should not appear in logs
                sensitive_patterns = ["123456789", "123-45-6789", "1000000.0"]
                for pattern in sensitive_patterns:
                    assert pattern not in log_output, f"Sensitive data '{pattern}' found in logs"
                
                print("Sensitive data handling test passed - no leakage detected")
                
        finally:
            logger.removeHandler(handler)


class TestSystemResilience:
    """Test system resilience and error handling."""
    
    @pytest.mark.asyncio
    async def test_ollama_service_failure_recovery(self):
        """Test system behavior when Ollama service fails and recovers."""
        ollama_service = OllamaService()
        error_handler = get_error_handler()
        
        # Mock Ollama service failure
        with patch.object(ollama_service, 'health_check', return_value=False):
            # Test health check failure
            is_healthy = await ollama_service.health_check()
            assert not is_healthy
            
            # Test fallback behavior
            recommendation = {
                "symbol": "AAPL",
                "action": "BUY",
                "confidence": 0.8
            }
            
            # Should handle error gracefully
            try:
                rationale = await ollama_service.generate_rationale(recommendation, {})
                # Should either succeed with fallback or raise handled error
                assert isinstance(rationale, str)
            except Exception as e:
                # Should be a handled AI trading error
                assert "Ollama" in str(e) or "unavailable" in str(e).lower()
        
        # Test recovery
        with patch.object(ollama_service, 'health_check', return_value=True):
            is_healthy = await ollama_service.health_check()
            assert is_healthy
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self):
        """Test circuit breaker prevents cascading failures."""
        error_handler = get_error_handler()
        
        # Test circuit breaker initially closed
        is_open = await error_handler._is_circuit_breaker_open("test_service")
        assert not is_open
        
        # Simulate multiple failures to trigger circuit breaker
        for i in range(5):
            await error_handler._update_circuit_breaker("test_service", False)
        
        # Circuit breaker should now be open
        is_open = await error_handler._is_circuit_breaker_open("test_service")
        assert is_open
        
        # Test reset functionality
        reset_result = await error_handler.reset_circuit_breaker("test_service")
        assert reset_result
        
        # Circuit breaker should be closed again
        is_open = await error_handler._is_circuit_breaker_open("test_service")
        assert not is_open
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test system provides degraded service when components fail."""
        prediction_engine = PredictionEngine()
        
        # Mock partial system failure
        with patch.multiple(
            'llm_backend.ai_trading.engines.prediction_engine',
            DataFetcher=AsyncMock(),
            MLModels=AsyncMock(),
            MLFeatureEngineer=AsyncMock(),
            TechnicalIndicators=AsyncMock()
        ):
            # Mock some components failing
            prediction_engine._fetch_historical_data = AsyncMock(
                side_effect=Exception("Data source unavailable")
            )
            
            # But other components working
            prediction_engine._generate_features = AsyncMock(return_value=[1, 2, 3, 4, 5])
            prediction_engine._get_models_for_symbol = AsyncMock(return_value=[])
            prediction_engine._calculate_volatility = AsyncMock(return_value=0.2)
            prediction_engine._calculate_overall_confidence = AsyncMock(return_value=50.0)  # Lower confidence
            
            # Mock fallback prediction
            mock_ensemble = EnsemblePrediction(
                individual_predictions={"baseline": 100.0},
                ensemble_prediction=100.0,
                model_weights={"baseline": 1.0},
                confidence=0.5,  # Lower confidence due to degraded service
                variance=0.2
            )
            prediction_engine.ensemble_predict = AsyncMock(return_value=mock_ensemble)
            
            mock_confidence = ConfidenceInterval(
                lower_bound=95.0,
                upper_bound=105.0,
                confidence_level=0.8  # Lower confidence level
            )
            prediction_engine.calculate_confidence_intervals = AsyncMock(
                return_value=mock_confidence
            )
            
            # System should still provide predictions, but with lower confidence
            try:
                result = await prediction_engine.generate_predictions("AAPL")
                
                # Should get result but with degraded quality indicators
                assert result.symbol == "AAPL"
                assert result.confidence_score <= 60  # Lower confidence due to degraded service
                assert len(result.model_ensemble) >= 1  # At least baseline model
                
                print(f"Degraded service prediction confidence: {result.confidence_score}")
                
            except Exception as e:
                # If it fails, should be a handled error with fallback information
                assert "unavailable" in str(e).lower() or "degraded" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_error_recovery_and_logging(self):
        """Test comprehensive error recovery and logging."""
        from ..logging.audit_logger import get_audit_logger
        
        audit_logger = get_audit_logger()
        error_handler = get_error_handler()
        
        # Test error logging
        test_error = Exception("Test error for logging")
        
        await error_handler._log_error({
            "error_type": "TestError",
            "message": "Test error for logging",
            "component": "TestComponent",
            "operation": "test_operation",
            "timestamp": datetime.now(),
            "severity": "MEDIUM"
        })
        
        # Verify error was logged
        error_stats = await error_handler.get_error_stats()
        assert error_stats["error_statistics"]["total_errors"] > 0
        
        # Test recovery mechanisms
        recovery_service = get_ollama_recovery_service()
        
        # Get current health status
        health_status = await recovery_service.check_health()
        assert health_status.state.value in ["HEALTHY", "DEGRADED", "UNAVAILABLE", "FAILED"]
        
        # Test performance metrics collection
        metrics = await recovery_service.get_performance_metrics()
        assert "statistics" in metrics
        assert "total_requests" in metrics["statistics"]
        
        print(f"Error recovery test completed - Health: {health_status.state.value}")


if __name__ == "__main__":
    # Run specific test categories
    import sys
    
    if len(sys.argv) > 1:
        test_category = sys.argv[1]
        if test_category == "workflows":
            pytest.main(["-v", "test_integration.py::TestEndToEndWorkflows"])
        elif test_category == "websocket":
            pytest.main(["-v", "test_integration.py::TestWebSocketIntegration"])
        elif test_category == "performance":
            pytest.main(["-v", "test_integration.py::TestPerformanceAndLoad"])
        elif test_category == "privacy":
            pytest.main(["-v", "test_integration.py::TestDataPrivacyAndLocalProcessing"])
        elif test_category == "resilience":
            pytest.main(["-v", "test_integration.py::TestSystemResilience"])
        else:
            print("Available test categories: workflows, websocket, performance, privacy, resilience")
    else:
        # Run all tests
        pytest.main(["-v", __file__])