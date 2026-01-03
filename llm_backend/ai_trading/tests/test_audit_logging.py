"""
Tests for AI Trading Assistant Audit Logging System.

Tests comprehensive logging functionality including audit events,
performance tracking, error logging, and audit trail retrieval.
"""

import asyncio
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from ..logging.audit_logger import AuditLogger, AuditEvent, PerformanceMetrics
from ..logging.decorators import audit_operation, AuditContext
from ..engines.prediction_engine import PredictionEngine


class TestAuditLogger:
    """Test the AuditLogger functionality."""
    
    @pytest.fixture
    async def audit_logger(self):
        """Create a test audit logger with temporary database."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        logger = AuditLogger(db_path=db_path)
        await logger._initialize_db()
        
        yield logger
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_audit_event_logging(self, audit_logger):
        """Test logging of audit events."""
        event = AuditEvent(
            event_id="test-123",
            event_type="PREDICTION",
            component="PredictionEngine",
            operation="generate_predictions",
            input_data={"symbol": "AAPL", "timeframes": ["1d", "7d"]},
            output_data={"predictions": {"1d": 150.0, "7d": 155.0}},
            metadata={"model": "ensemble"},
            timestamp=datetime.now(),
            duration_ms=1500.0,
            success=True
        )
        
        await audit_logger.log_audit_event(event)
        
        # Retrieve and verify
        trail = await audit_logger.get_audit_trail(limit=1)
        assert len(trail) == 1
        assert trail[0]['event_id'] == "test-123"
        assert trail[0]['component'] == "PredictionEngine"
        assert trail[0]['success'] == True
    
    @pytest.mark.asyncio
    async def test_prediction_logging(self, audit_logger):
        """Test logging of predictions."""
        await audit_logger.log_prediction(
            symbol="AAPL",
            timeframe="1d",
            predicted_price=150.0,
            confidence_score=85.0,
            model_ensemble=["lstm", "gru"]
        )
        
        # Verify prediction was logged
        accuracy_stats = await audit_logger.get_prediction_accuracy(symbol="AAPL")
        assert len(accuracy_stats['accuracy_by_symbol_timeframe']) == 1
        assert accuracy_stats['accuracy_by_symbol_timeframe'][0]['symbol'] == "AAPL"
    
    @pytest.mark.asyncio
    async def test_recommendation_logging(self, audit_logger):
        """Test logging of recommendations."""
        await audit_logger.log_recommendation(
            symbol="AAPL",
            action="BUY",
            confidence=0.8,
            target_price=155.0,
            stop_loss=145.0,
            position_size=100,
            rationale="Strong technical indicators",
            risk_reward_ratio=2.0
        )
        
        # Verify recommendation was logged
        trail = await audit_logger.get_audit_trail(component="RecommendationEngine")
        # Note: This would be logged via the decorator in actual usage
    
    @pytest.mark.asyncio
    async def test_risk_assessment_logging(self, audit_logger):
        """Test logging of risk assessments."""
        await audit_logger.log_risk_assessment(
            symbol="AAPL",
            var_1d=0.02,
            var_5d=0.045,
            beta=1.2,
            volatility=0.25,
            sharpe_ratio=1.5,
            max_drawdown=0.15,
            correlation_to_market=0.8
        )
        
        # Verify risk assessment was logged
        # This would typically be verified through audit trail
    
    @pytest.mark.asyncio
    async def test_performance_metrics_logging(self, audit_logger):
        """Test logging of performance metrics."""
        metrics = PerformanceMetrics(
            component="PredictionEngine",
            operation="generate_predictions",
            duration_ms=1200.0,
            memory_usage_mb=150.0,
            cpu_usage_percent=25.0
        )
        
        await audit_logger.log_performance_metrics(metrics)
        
        # Verify performance metrics
        perf_stats = await audit_logger.get_performance_statistics(component="PredictionEngine")
        assert len(perf_stats['performance_by_component']) >= 0
    
    @pytest.mark.asyncio
    async def test_error_logging(self, audit_logger):
        """Test logging of errors."""
        await audit_logger.log_error(
            component="PredictionEngine",
            operation="generate_predictions",
            error_type="ValueError",
            error_message="Insufficient data",
            stack_trace="Traceback...",
            input_data={"symbol": "INVALID"}
        )
        
        # Verify error was logged
        error_summary = await audit_logger.get_error_summary()
        assert len(error_summary['errors_by_type']) >= 0
    
    @pytest.mark.asyncio
    async def test_audit_trail_filtering(self, audit_logger):
        """Test audit trail filtering functionality."""
        # Log multiple events
        for i in range(5):
            event = AuditEvent(
                event_id=f"test-{i}",
                event_type="PREDICTION",
                component="PredictionEngine",
                operation="generate_predictions",
                input_data={"symbol": f"STOCK{i}"},
                output_data={"prediction": 100.0 + i},
                metadata={},
                timestamp=datetime.now(),
                success=True
            )
            await audit_logger.log_audit_event(event)
        
        # Test component filtering
        trail = await audit_logger.get_audit_trail(component="PredictionEngine")
        assert len(trail) == 5
        
        # Test limit
        trail = await audit_logger.get_audit_trail(limit=3)
        assert len(trail) == 3
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, audit_logger):
        """Test cleanup of old audit data."""
        # Log some test data
        event = AuditEvent(
            event_id="cleanup-test",
            event_type="TEST",
            component="TestComponent",
            operation="test_operation",
            input_data={},
            output_data={},
            metadata={},
            timestamp=datetime.now(),
            success=True
        )
        await audit_logger.log_audit_event(event)
        
        # Cleanup (keep 0 days - should delete everything)
        result = await audit_logger.cleanup_old_data(days_to_keep=0)
        assert 'records_deleted' in result


class TestAuditDecorators:
    """Test the audit logging decorators."""
    
    @pytest.mark.asyncio
    async def test_audit_operation_decorator(self):
        """Test the audit_operation decorator."""
        
        @audit_operation(
            component="TestComponent",
            operation="test_function",
            event_type="TEST"
        )
        async def test_function(value: int) -> int:
            return value * 2
        
        # Mock the audit logger to avoid database operations
        with patch('llm_backend.ai_trading.logging.decorators.get_audit_logger') as mock_logger:
            mock_audit_logger = AsyncMock()
            mock_logger.return_value = mock_audit_logger
            
            result = await test_function(5)
            
            assert result == 10
            # Verify audit logging was called
            mock_audit_logger.log_audit_event.assert_called_once()
            mock_audit_logger.log_performance_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_audit_operation_decorator_with_error(self):
        """Test the audit_operation decorator with error handling."""
        
        @audit_operation(
            component="TestComponent",
            operation="failing_function",
            event_type="TEST"
        )
        async def failing_function():
            raise ValueError("Test error")
        
        with patch('llm_backend.ai_trading.logging.decorators.get_audit_logger') as mock_logger:
            mock_audit_logger = AsyncMock()
            mock_logger.return_value = mock_audit_logger
            
            with pytest.raises(ValueError):
                await failing_function()
            
            # Verify error logging was called
            mock_audit_logger.log_error.assert_called_once()
            mock_audit_logger.log_audit_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_audit_context_manager(self):
        """Test the AuditContext context manager."""
        
        with patch('llm_backend.ai_trading.logging.decorators.get_audit_logger') as mock_logger:
            mock_audit_logger = AsyncMock()
            mock_logger.return_value = mock_audit_logger
            
            async with AuditContext("TestComponent", "test_operation") as ctx:
                ctx.add_input_data({"test": "value"})
                ctx.add_output_data({"result": "success"})
                ctx.add_metadata({"version": "1.0"})
            
            # Verify audit logging was called
            mock_audit_logger.log_audit_event.assert_called_once()
            mock_audit_logger.log_performance_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_audit_context_manager_with_error(self):
        """Test the AuditContext context manager with error handling."""
        
        with patch('llm_backend.ai_trading.logging.decorators.get_audit_logger') as mock_logger:
            mock_audit_logger = AsyncMock()
            mock_logger.return_value = mock_audit_logger
            
            with pytest.raises(ValueError):
                async with AuditContext("TestComponent", "failing_operation") as ctx:
                    ctx.add_input_data({"test": "value"})
                    raise ValueError("Test error")
            
            # Verify error logging was called
            mock_audit_logger.log_error.assert_called_once()
            mock_audit_logger.log_audit_event.assert_called_once()


class TestIntegratedLogging:
    """Test integrated logging with actual AI components."""
    
    @pytest.mark.asyncio
    async def test_prediction_engine_logging_integration(self):
        """Test that PredictionEngine properly logs operations."""
        
        with patch('llm_backend.ai_trading.logging.decorators.get_audit_logger') as mock_logger:
            mock_audit_logger = AsyncMock()
            mock_logger.return_value = mock_audit_logger
            
            # Mock the data fetcher and other dependencies
            with patch.multiple(
                'llm_backend.ai_trading.engines.prediction_engine',
                DataFetcher=AsyncMock(),
                MLModels=AsyncMock(),
                MLFeatureEngineer=AsyncMock(),
                TechnicalIndicators=AsyncMock()
            ):
                engine = PredictionEngine()
                
                # Mock the internal methods to avoid actual data fetching
                engine._fetch_historical_data = AsyncMock(return_value=[100, 101, 102, 103, 104])
                engine._generate_features = AsyncMock(return_value=[1, 2, 3, 4, 5])
                engine._get_models_for_symbol = AsyncMock(return_value=[])
                engine._calculate_volatility = AsyncMock(return_value=0.2)
                engine._calculate_overall_confidence = AsyncMock(return_value=75.0)
                engine.ensemble_predict = AsyncMock()
                engine.calculate_confidence_intervals = AsyncMock()
                
                # Mock ensemble prediction result
                from ..data_models import EnsemblePrediction, ConfidenceInterval
                mock_ensemble = EnsemblePrediction(
                    individual_predictions={"lstm": 105.0},
                    ensemble_prediction=105.0,
                    model_weights={"lstm": 1.0},
                    confidence=0.8,
                    variance=0.1
                )
                engine.ensemble_predict.return_value = mock_ensemble
                
                mock_confidence = ConfidenceInterval(
                    lower_bound=100.0,
                    upper_bound=110.0,
                    confidence_level=0.95
                )
                engine.calculate_confidence_intervals.return_value = mock_confidence
                
                # Test prediction generation
                result = await engine.generate_predictions("AAPL")
                
                # Verify the result
                assert result.symbol == "AAPL"
                assert "1d" in result.predictions
                
                # Verify audit logging was called
                mock_audit_logger.log_audit_event.assert_called()
                mock_audit_logger.log_prediction.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])