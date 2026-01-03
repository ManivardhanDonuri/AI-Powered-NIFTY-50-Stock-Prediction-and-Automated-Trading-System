"""
Test script for AI Trading Assistant error handling and fallback systems.

This script tests various error scenarios and verifies that the error handling
and recovery mechanisms work correctly.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from .error_handling import (
    get_error_handler, DataUnavailableError, ModelError, OllamaError,
    PerformanceError, ErrorContext, ErrorSeverity
)
from .ollama_recovery import get_ollama_recovery_service
from .startup import initialize_ai_trading_system, get_ai_trading_system_status

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_error_classification():
    """Test error classification and handling."""
    print("\n=== Testing Error Classification ===")
    
    error_handler = get_error_handler()
    
    # Test different error types
    test_errors = [
        DataUnavailableError("Test data unavailable", ErrorContext("TestComponent", "test_op")),
        ModelError("Test model error", ErrorContext("TestComponent", "test_op")),
        OllamaError("Test Ollama error", ErrorContext("TestComponent", "test_op")),
        PerformanceError("Test performance error", ErrorContext("TestComponent", "test_op")),
    ]
    
    for error in test_errors:
        print(f"Error: {error.message}")
        print(f"  Category: {error.category.value}")
        print(f"  Severity: {error.severity.value}")
        print(f"  Timestamp: {error.timestamp}")
        print()


async def test_prediction_error_handling():
    """Test prediction engine error handling."""
    print("\n=== Testing Prediction Error Handling ===")
    
    error_handler = get_error_handler()
    
    # Simulate prediction error
    test_error = DataUnavailableError(
        "Insufficient data for TESTSTOCK",
        ErrorContext("PredictionEngine", "generate_predictions", symbol="TESTSTOCK")
    )
    
    # Test fallback prediction
    fallback_result = await error_handler.handle_prediction_error(
        test_error, "TESTSTOCK", ["1d", "3d"]
    )
    
    print(f"Fallback prediction generated:")
    print(f"  Symbol: {fallback_result.symbol}")
    print(f"  Predictions: {fallback_result.predictions}")
    print(f"  Confidence: {fallback_result.confidence_score}")
    print(f"  Models: {fallback_result.model_ensemble}")


async def test_recommendation_error_handling():
    """Test recommendation engine error handling."""
    print("\n=== Testing Recommendation Error Handling ===")
    
    error_handler = get_error_handler()
    
    # Simulate recommendation error
    test_error = OllamaError(
        "Ollama service unavailable",
        ErrorContext("RecommendationEngine", "generate_recommendation", symbol="TESTSTOCK")
    )
    
    # Test fallback recommendation
    fallback_result = await error_handler.handle_recommendation_error(
        test_error, "TESTSTOCK"
    )
    
    print(f"Fallback recommendation generated:")
    print(f"  Symbol: {fallback_result.symbol}")
    print(f"  Action: {fallback_result.action}")
    print(f"  Confidence: {fallback_result.confidence}")
    print(f"  Rationale: {fallback_result.rationale[:100]}...")


async def test_ollama_error_handling():
    """Test Ollama service error handling."""
    print("\n=== Testing Ollama Error Handling ===")
    
    error_handler = get_error_handler()
    
    # Simulate Ollama connection error
    test_error = ConnectionError("Connection to Ollama failed")
    
    # Test fallback response
    fallback_response = await error_handler.handle_ollama_error(
        test_error, "Explain the trading recommendation for AAPL"
    )
    
    print(f"Fallback Ollama response:")
    print(f"  Response: {fallback_response[:200]}...")


async def test_circuit_breaker():
    """Test circuit breaker functionality."""
    print("\n=== Testing Circuit Breaker ===")
    
    error_handler = get_error_handler()
    
    # Test circuit breaker state
    is_open = await error_handler._is_circuit_breaker_open("ollama")
    print(f"Circuit breaker initially open: {is_open}")
    
    # Simulate failures to trigger circuit breaker
    for i in range(4):
        await error_handler._update_circuit_breaker("ollama", False)
        print(f"Failure {i+1} recorded")
    
    is_open_after_failures = await error_handler._is_circuit_breaker_open("ollama")
    print(f"Circuit breaker open after failures: {is_open_after_failures}")
    
    # Reset circuit breaker
    reset_result = await error_handler.reset_circuit_breaker("ollama")
    print(f"Circuit breaker reset: {reset_result}")


async def test_ollama_recovery():
    """Test Ollama recovery service."""
    print("\n=== Testing Ollama Recovery ===")
    
    recovery_service = get_ollama_recovery_service()
    
    # Check health status
    health_status = await recovery_service.check_health()
    print(f"Ollama health status:")
    print(f"  State: {health_status.state.value}")
    print(f"  Response time: {health_status.response_time:.3f}s")
    print(f"  Model loaded: {health_status.model_loaded}")
    print(f"  Memory usage: {health_status.memory_usage:.1f}%")
    print(f"  CPU usage: {health_status.cpu_usage:.1f}%")
    print(f"  Error rate: {health_status.error_rate:.1%}")
    
    # Get performance metrics
    metrics = await recovery_service.get_performance_metrics()
    print(f"\nPerformance metrics:")
    print(f"  Total requests: {metrics['statistics']['total_requests']}")
    print(f"  Recovery attempts: {metrics['statistics']['recovery_attempts']}")


async def test_error_statistics():
    """Test error statistics tracking."""
    print("\n=== Testing Error Statistics ===")
    
    error_handler = get_error_handler()
    
    # Generate some test errors
    test_errors = [
        DataUnavailableError("Test 1", ErrorContext("TestComponent", "test1")),
        ModelError("Test 2", ErrorContext("TestComponent", "test2")),
        OllamaError("Test 3", ErrorContext("TestComponent", "test3")),
    ]
    
    for error in test_errors:
        await error_handler._log_error(await error_handler._classify_error(error))
        await error_handler._update_error_stats(await error_handler._classify_error(error))
    
    # Get error statistics
    error_stats = await error_handler.get_error_stats()
    print(f"Error statistics:")
    print(f"  Total errors: {error_stats['error_statistics']['total_errors']}")
    print(f"  Errors by category: {error_stats['error_statistics']['errors_by_category']}")
    print(f"  Circuit breakers: {len(error_stats['circuit_breakers'])}")


async def test_system_initialization():
    """Test complete system initialization."""
    print("\n=== Testing System Initialization ===")
    
    # Test initialization
    init_result = await initialize_ai_trading_system(start_monitoring=False)
    print(f"System initialization successful: {init_result}")
    
    # Get system status
    system_status = await get_ai_trading_system_status()
    print(f"System status:")
    print(f"  Initialized: {system_status['initialized']}")
    print(f"  Components: {list(system_status.get('components', {}).keys())}")


async def run_all_tests():
    """Run all error handling tests."""
    print("Starting AI Trading Assistant Error Handling Tests")
    print("=" * 60)
    
    try:
        await test_error_classification()
        await test_prediction_error_handling()
        await test_recommendation_error_handling()
        await test_ollama_error_handling()
        await test_circuit_breaker()
        await test_ollama_recovery()
        await test_error_statistics()
        await test_system_initialization()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())