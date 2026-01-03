"""
AI Trading API Router

This module provides REST API endpoints for all AI trading features including
predictions, recommendations, risk analysis, and comparative analysis.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field

from ..ai_trading.engines.prediction_engine import PredictionEngine
from ..ai_trading.engines.recommendation_engine import RecommendationEngine
from ..ai_trading.engines.risk_analyzer import RiskAnalyzer
from ..ai_trading.engines.market_context_analyzer import MarketContextAnalyzer
from ..ai_trading.engines.portfolio_analyzer import PortfolioAnalyzer
from ..ai_trading.engines.comparative_analyzer import ComparativeAnalyzer
from ..ai_trading.engines.learning_adaptation_engine import LearningAdaptationEngine
from ..ai_trading.data_models import RiskAssessment, RiskMetrics
from ..ai_trading.logging.decorators import audit_operation, AuditContext
from ..ai_trading.logging.audit_logger import get_audit_logger
from ..ai_trading.error_handling import (
    get_error_handler, AITradingError, DataUnavailableError, 
    ModelError, OllamaError, PerformanceError, ErrorContext
)
from ..ai_trading.ollama_recovery import get_ollama_recovery_service
from ..services.ollama_service import get_ollama_service

router = APIRouter()
logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()
error_handler = get_error_handler()
ollama_recovery = get_ollama_recovery_service()

# Initialize engines
prediction_engine = PredictionEngine()
recommendation_engine = RecommendationEngine()
risk_analyzer = RiskAnalyzer()
market_context_analyzer = MarketContextAnalyzer()
portfolio_analyzer = PortfolioAnalyzer()
comparative_analyzer = ComparativeAnalyzer()
learning_adaptation_engine = LearningAdaptationEngine()


# Request/Response Models
class PredictionRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to predict")
    timeframes: Optional[List[str]] = Field(default=["1d", "3d", "7d", "30d"], description="Prediction timeframes")


class RecommendationRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol for recommendation")
    portfolio: Optional[Dict[str, Any]] = Field(default={}, description="Current portfolio data")


class RiskAnalysisRequest(BaseModel):
    symbol: Optional[str] = Field(default=None, description="Stock symbol for individual risk analysis")
    portfolio: Dict[str, Any] = Field(..., description="Portfolio data for risk analysis")


class ComparisonRequest(BaseModel):
    symbols: List[str] = Field(..., min_items=2, max_items=5, description="Stocks to compare (2-5)")
    metrics: List[str] = Field(default=["price_change", "volatility", "pe_ratio"], description="Metrics to compare")
    timeframe: str = Field(default="1y", description="Timeframe for comparison")


class ChartRequest(BaseModel):
    symbols: List[str] = Field(..., description="Symbols for chart")
    chart_type: str = Field(default="bar", description="Type of chart to generate")
    metrics: Optional[List[str]] = Field(default=None, description="Metrics to include")


class PortfolioAnalysisRequest(BaseModel):
    portfolio: Dict[str, Any] = Field(..., description="Portfolio data to analyze")
    analysis_type: str = Field(default="performance", description="Type of analysis: performance, rebalancing, attribution")


class MarketContextRequest(BaseModel):
    symbols: Optional[List[str]] = Field(default=None, description="Symbols for context analysis")
    timeframe: str = Field(default="24h", description="Timeframe for context analysis")


# API Endpoints

@router.post("/predictions")
async def generate_predictions(request: PredictionRequest):
    """
    Generate stock price predictions with confidence intervals.
    
    Returns multi-timeframe predictions using ensemble ML models.
    """
    async with AuditContext("API", "generate_predictions", "API_REQUEST") as ctx:
        try:
            ctx.add_input_data({"symbol": request.symbol, "timeframes": request.timeframes})
            logger.info(f"Generating predictions for {request.symbol}")
            
            prediction_result = await prediction_engine.generate_predictions(
                symbol=request.symbol,
                timeframes=request.timeframes
            )
            
            response_data = {
                "success": True,
                "data": {
                    "symbol": prediction_result.symbol,
                    "predictions": prediction_result.predictions,
                    "confidence_intervals": {
                        tf: {
                            "lower_bound": ci.lower_bound,
                            "upper_bound": ci.upper_bound,
                            "confidence_level": ci.confidence_level
                        }
                        for tf, ci in prediction_result.confidence_intervals.items()
                    },
                    "confidence_score": prediction_result.confidence_score,
                    "model_ensemble": prediction_result.model_ensemble,
                    "timestamp": prediction_result.timestamp.isoformat()
                }
            }
            
            ctx.add_output_data({"success": True, "symbol": request.symbol, "confidence_score": prediction_result.confidence_score})
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Prediction generation failed: {str(e)}")


@router.post("/recommendations")
async def generate_recommendation(request: RecommendationRequest):
    """
    Generate intelligent buy/sell recommendations with detailed rationale.
    
    Combines predictions, risk analysis, and market context for recommendations.
    """
    async with AuditContext("API", "generate_recommendation", "API_REQUEST") as ctx:
        try:
            ctx.add_input_data({"symbol": request.symbol, "portfolio_size": len(request.portfolio)})
            logger.info(f"Generating recommendation for {request.symbol}")
            
            # Get prediction first
            prediction_result = await prediction_engine.generate_predictions(request.symbol)
            
            # Get risk analysis
            risk_metrics = await risk_analyzer.calculate_risk_metrics(request.symbol, request.portfolio)
            risk_assessment = RiskAssessment(
                risk_metrics=risk_metrics,
                portfolio_impact=0.1,
                risk_score=50.0,
                risk_factors=["volatility", "beta"],
                mitigation_strategies=["diversification"],
                timestamp=datetime.now()
            )
            
            # Generate recommendation
            recommendation = await recommendation_engine.generate_recommendation(
                symbol=request.symbol,
                prediction=prediction_result,
                risk_analysis=risk_assessment
            )
            
            response_data = {
                "success": True,
                "data": {
                    "symbol": recommendation.symbol,
                    "action": recommendation.action,
                    "confidence": recommendation.confidence,
                    "target_price": recommendation.target_price,
                    "stop_loss": recommendation.stop_loss,
                    "position_size": recommendation.position_size,
                    "rationale": recommendation.rationale,
                    "risk_reward_ratio": recommendation.risk_reward_ratio,
                    "timestamp": recommendation.timestamp.isoformat()
                }
            }
            
            ctx.add_output_data({
                "success": True, 
                "symbol": request.symbol, 
                "action": recommendation.action,
                "confidence": recommendation.confidence
            })
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")


@router.post("/risk-analysis")
async def analyze_risk(request: RiskAnalysisRequest):
    """
    Perform comprehensive risk analysis for individual stocks or entire portfolio.
    
    Returns risk metrics, portfolio risk assessment, and risk alerts.
    """
    try:
        logger.info("Performing risk analysis")
        
        result = {}
        
        # Individual stock risk analysis
        if request.symbol:
            risk_metrics = await risk_analyzer.calculate_risk_metrics(request.symbol, request.portfolio)
            risk_alerts = await risk_analyzer.generate_risk_alerts(risk_metrics)
            
            result["individual_risk"] = {
                "symbol": risk_metrics.symbol,
                "var_1d": risk_metrics.var_1d,
                "var_5d": risk_metrics.var_5d,
                "beta": risk_metrics.beta,
                "volatility": risk_metrics.volatility,
                "sharpe_ratio": risk_metrics.sharpe_ratio,
                "max_drawdown": risk_metrics.max_drawdown,
                "correlation_to_market": risk_metrics.correlation_to_market,
                "risk_alerts": [
                    {
                        "type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "recommended_action": alert.recommended_action
                    }
                    for alert in risk_alerts
                ]
            }
        
        # Portfolio risk analysis
        portfolio_risk = await risk_analyzer.assess_portfolio_risk(request.portfolio)
        
        result["portfolio_risk"] = {
            "total_var": portfolio_risk.total_var,
            "concentration_risk": portfolio_risk.concentration_risk,
            "sector_exposure": portfolio_risk.sector_exposure,
            "correlation_risk": portfolio_risk.correlation_risk,
            "liquidity_risk": portfolio_risk.liquidity_risk,
            "overall_risk_score": portfolio_risk.overall_risk_score,
            "risk_alerts": [
                {
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "recommended_action": alert.recommended_action
                }
                for alert in portfolio_risk.risk_alerts
            ],
            "timestamp": portfolio_risk.timestamp.isoformat()
        }
        
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"Error in risk analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.post("/portfolio-analysis")
async def analyze_portfolio(request: PortfolioAnalysisRequest):
    """
    Comprehensive portfolio analysis including performance, rebalancing, and attribution.
    
    Returns detailed portfolio insights and optimization suggestions.
    """
    try:
        logger.info(f"Performing {request.analysis_type} portfolio analysis")
        
        result = {}
        
        if request.analysis_type in ["performance", "all"]:
            performance = await portfolio_analyzer.analyze_performance(request.portfolio)
            result["performance"] = {
                "total_return": performance.total_return,
                "annualized_return": performance.annualized_return,
                "volatility": performance.volatility,
                "sharpe_ratio": performance.sharpe_ratio,
                "max_drawdown": performance.max_drawdown,
                "win_rate": performance.win_rate,
                "profit_factor": performance.profit_factor,
                "benchmark_comparison": performance.benchmark_comparison,
                "timestamp": performance.timestamp.isoformat()
            }
        
        if request.analysis_type in ["rebalancing", "all"]:
            rebalancing = await portfolio_analyzer.suggest_rebalancing(request.portfolio)
            result["rebalancing"] = {
                "current_allocation": rebalancing.current_allocation,
                "target_allocation": rebalancing.target_allocation,
                "trades_required": rebalancing.trades_required,
                "expected_cost": rebalancing.expected_cost,
                "tax_implications": rebalancing.tax_implications,
                "rationale": rebalancing.rationale,
                "timestamp": rebalancing.timestamp.isoformat()
            }
        
        if request.analysis_type in ["attribution", "all"]:
            attribution = await portfolio_analyzer.calculate_attribution(request.portfolio)
            result["attribution"] = {
                "asset_allocation": attribution.asset_allocation,
                "security_selection": attribution.security_selection,
                "interaction_effect": attribution.interaction_effect,
                "total_excess_return": attribution.total_excess_return,
                "benchmark_return": attribution.benchmark_return,
                "portfolio_return": attribution.portfolio_return,
                "timestamp": attribution.timestamp.isoformat()
            }
        
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"Error in portfolio analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Portfolio analysis failed: {str(e)}")


@router.post("/compare-stocks")
async def compare_stocks(request: ComparisonRequest):
    """
    Compare multiple stocks across various metrics with customizable analysis.
    
    Returns comparative analysis, correlations, and rankings.
    """
    try:
        logger.info(f"Comparing {len(request.symbols)} stocks")
        
        # Perform comparison
        comparison_result = await comparative_analyzer.compare_stocks(
            symbols=request.symbols,
            metrics=request.metrics,
            timeframe=request.timeframe
        )
        
        # Generate rankings
        rankings = await comparative_analyzer.rank_opportunities(comparison_result)
        
        return {
            "success": True,
            "data": {
                "symbols": comparison_result.symbols,
                "metrics": comparison_result.metrics,
                "correlations": {
                    "symbols": comparison_result.correlations.symbols,
                    "matrix": comparison_result.correlations.matrix.tolist(),
                    "timeframe": comparison_result.correlations.timeframe
                },
                "rankings": rankings.rankings,
                "scores": rankings.scores,
                "overall_ranking": rankings.overall_ranking,
                "chart_data": comparison_result.chart_data,
                "timestamp": comparison_result.timestamp.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stock comparison failed: {str(e)}")


@router.post("/generate-chart")
async def generate_chart(request: ChartRequest):
    """
    Generate comparison charts for multiple stocks.
    
    Returns chart data for various visualization types.
    """
    try:
        logger.info(f"Generating {request.chart_type} chart for {len(request.symbols)} stocks")
        
        # First get comparison data
        comparison_result = await comparative_analyzer.compare_stocks(
            symbols=request.symbols,
            metrics=request.metrics or ["price_change", "volatility"],
            timeframe="1y"
        )
        
        # Generate chart
        chart_data = await comparative_analyzer.generate_comparison_chart(
            comparison_data=comparison_result,
            chart_type=request.chart_type
        )
        
        return {
            "success": True,
            "data": {
                "chart_type": chart_data.chart_type,
                "data": chart_data.data,
                "labels": chart_data.labels,
                "colors": chart_data.colors,
                "title": chart_data.title,
                "x_axis_label": chart_data.x_axis_label,
                "y_axis_label": chart_data.y_axis_label,
                "timestamp": chart_data.timestamp.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chart generation failed: {str(e)}")


@router.post("/market-context")
async def analyze_market_context(request: MarketContextRequest):
    """
    Analyze market context including news sentiment and market events.
    
    Returns sentiment analysis and detected market events.
    """
    try:
        logger.info("Analyzing market context")
        
        result = {}
        
        # Analyze sentiment for specific symbols
        if request.symbols:
            sentiment_results = {}
            for symbol in request.symbols:
                sentiment = await market_context_analyzer.analyze_news_sentiment(
                    symbol=symbol,
                    timeframe=request.timeframe
                )
                sentiment_results[symbol] = {
                    "sentiment_score": sentiment.sentiment_score,
                    "news_count": sentiment.news_count,
                    "key_themes": sentiment.key_themes,
                    "confidence": sentiment.confidence,
                    "sources": sentiment.sources,
                    "timestamp": sentiment.timestamp.isoformat()
                }
            result["sentiment_analysis"] = sentiment_results
        
        # Detect market events
        market_data = {"vix": 20.0}  # Simplified market data
        events = await market_context_analyzer.detect_market_events(market_data)
        
        result["market_events"] = [
            {
                "event_type": event.event_type,
                "description": event.description,
                "impact_level": event.impact_level,
                "affected_sectors": event.affected_sectors,
                "source": event.source,
                "timestamp": event.timestamp.isoformat()
            }
            for event in events
        ]
        
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"Error analyzing market context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market context analysis failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for AI trading services."""
    try:
        # Check Ollama service
        ollama_service = get_ollama_service()
        ollama_healthy = await ollama_service.health_check()
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "services": {
                    "prediction_engine": "operational",
                    "recommendation_engine": "operational",
                    "risk_analyzer": "operational",
                    "market_context_analyzer": "operational",
                    "portfolio_analyzer": "operational",
                    "comparative_analyzer": "operational",
                    "ollama_service": "healthy" if ollama_healthy else "degraded"
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/available-metrics")
async def get_available_metrics():
    """Get list of available metrics for comparison."""
    return {
        "success": True,
        "data": {
            "metrics": [
                "price_change", "volatility", "volume", "market_cap",
                "pe_ratio", "dividend_yield", "beta", "rsi", "macd"
            ],
            "chart_types": ["line", "bar", "scatter", "heatmap", "radar"],
            "timeframes": ["1d", "1w", "1m", "3m", "6m", "1y"]
        }
    }


# Background task for updating market context
async def update_market_context_task():
    """Background task to update market context periodically."""
    try:
        logger.info("Updating market context in background")
        
        # Update context with current market data
        context_data = {
            "last_update": datetime.now(),
            "market_status": "open",  # This would be determined by market hours
            "volatility_index": 20.0  # This would come from real data
        }
        
        await market_context_analyzer.update_context(context_data)
        
    except Exception as e:
        logger.error(f"Error updating market context: {str(e)}")


@router.post("/update-context")
async def trigger_context_update(background_tasks: BackgroundTasks):
    """Manually trigger market context update."""
    background_tasks.add_task(update_market_context_task)
    
    return {
        "success": True,
        "message": "Market context update triggered",
        "timestamp": datetime.now().isoformat()
    }


# Audit and Reporting Endpoints

class AuditTrailRequest(BaseModel):
    component: Optional[str] = Field(default=None, description="Filter by component")
    operation: Optional[str] = Field(default=None, description="Filter by operation")
    start_time: Optional[datetime] = Field(default=None, description="Start time filter")
    end_time: Optional[datetime] = Field(default=None, description="End time filter")
    limit: int = Field(default=100, description="Maximum number of records")


class PerformanceReportRequest(BaseModel):
    component: Optional[str] = Field(default=None, description="Filter by component")
    days: int = Field(default=7, description="Number of days to analyze")


class AccuracyReportRequest(BaseModel):
    symbol: Optional[str] = Field(default=None, description="Filter by symbol")
    timeframe: Optional[str] = Field(default=None, description="Filter by timeframe")
    days: int = Field(default=30, description="Number of days to analyze")


@router.post("/audit/trail")
async def get_audit_trail(request: AuditTrailRequest):
    """
    Get comprehensive audit trail with filtering options.
    
    Returns detailed audit events for compliance and analysis.
    """
    async with AuditContext("API", "get_audit_trail", "AUDIT_REQUEST") as ctx:
        try:
            ctx.add_input_data({
                "component": request.component,
                "operation": request.operation,
                "limit": request.limit
            })
            
            audit_trail = await audit_logger.get_audit_trail(
                component=request.component,
                operation=request.operation,
                start_time=request.start_time,
                end_time=request.end_time,
                limit=request.limit
            )
            
            response_data = {
                "success": True,
                "data": {
                    "audit_events": audit_trail,
                    "total_events": len(audit_trail),
                    "filters_applied": {
                        "component": request.component,
                        "operation": request.operation,
                        "start_time": request.start_time.isoformat() if request.start_time else None,
                        "end_time": request.end_time.isoformat() if request.end_time else None,
                        "limit": request.limit
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            ctx.add_output_data({"success": True, "events_returned": len(audit_trail)})
            return response_data
            
        except Exception as e:
            logger.error(f"Error getting audit trail: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Audit trail retrieval failed: {str(e)}")


@router.post("/audit/performance")
async def get_performance_report(request: PerformanceReportRequest):
    """
    Get performance statistics and metrics for AI operations.
    
    Returns detailed performance analysis for optimization.
    """
    async with AuditContext("API", "get_performance_report", "AUDIT_REQUEST") as ctx:
        try:
            ctx.add_input_data({"component": request.component, "days": request.days})
            
            performance_stats = await audit_logger.get_performance_statistics(
                component=request.component,
                days=request.days
            )
            
            response_data = {
                "success": True,
                "data": {
                    "performance_statistics": performance_stats,
                    "analysis_period": f"{request.days} days",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            ctx.add_output_data({"success": True, "components_analyzed": len(performance_stats.get('performance_by_component', []))})
            return response_data
            
        except Exception as e:
            logger.error(f"Error getting performance report: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Performance report generation failed: {str(e)}")


@router.post("/audit/accuracy")
async def get_accuracy_report(request: AccuracyReportRequest):
    """
    Get prediction accuracy statistics and analysis.
    
    Returns detailed accuracy metrics for model evaluation.
    """
    async with AuditContext("API", "get_accuracy_report", "AUDIT_REQUEST") as ctx:
        try:
            ctx.add_input_data({
                "symbol": request.symbol,
                "timeframe": request.timeframe,
                "days": request.days
            })
            
            accuracy_stats = await audit_logger.get_prediction_accuracy(
                symbol=request.symbol,
                timeframe=request.timeframe,
                days=request.days
            )
            
            response_data = {
                "success": True,
                "data": {
                    "accuracy_statistics": accuracy_stats,
                    "analysis_period": f"{request.days} days",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            ctx.add_output_data({"success": True, "accuracy_records": len(accuracy_stats.get('accuracy_by_symbol_timeframe', []))})
            return response_data
            
        except Exception as e:
            logger.error(f"Error getting accuracy report: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Accuracy report generation failed: {str(e)}")


@router.get("/audit/errors")
async def get_error_summary():
    """
    Get error summary and statistics.
    
    Returns error analysis for system monitoring.
    """
    async with AuditContext("API", "get_error_summary", "AUDIT_REQUEST") as ctx:
        try:
            error_summary = await audit_logger.get_error_summary(days=7)
            
            response_data = {
                "success": True,
                "data": {
                    "error_summary": error_summary,
                    "analysis_period": "7 days",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            ctx.add_output_data({"success": True, "error_types": len(error_summary.get('errors_by_type', []))})
            return response_data
            
        except Exception as e:
            logger.error(f"Error getting error summary: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Error summary generation failed: {str(e)}")


@router.post("/audit/cleanup")
async def cleanup_audit_data(days_to_keep: int = 90):
    """
    Clean up old audit data to manage database size.
    
    Removes audit records older than specified days.
    """
    async with AuditContext("API", "cleanup_audit_data", "MAINTENANCE") as ctx:
        try:
            ctx.add_input_data({"days_to_keep": days_to_keep})
            
            cleanup_result = await audit_logger.cleanup_old_data(days_to_keep=days_to_keep)
            
            response_data = {
                "success": True,
                "data": {
                    "cleanup_result": cleanup_result,
                    "days_kept": days_to_keep,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            ctx.add_output_data({"success": True, "records_deleted": cleanup_result.get('records_deleted', 0)})
            return response_data
            
        except Exception as e:
            logger.error(f"Error cleaning up audit data: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Audit data cleanup failed: {str(e)}")


@router.get("/audit/dashboard")
async def get_audit_dashboard():
    """
    Get comprehensive audit dashboard data.
    
    Returns summary statistics for monitoring and compliance.
    """
    async with AuditContext("API", "get_audit_dashboard", "AUDIT_REQUEST") as ctx:
        try:
            # Get various statistics
            performance_stats = await audit_logger.get_performance_statistics(days=7)
            accuracy_stats = await audit_logger.get_prediction_accuracy(days=30)
            error_summary = await audit_logger.get_error_summary(days=7)
            
            # Get recent audit trail
            recent_events = await audit_logger.get_audit_trail(limit=10)
            
            response_data = {
                "success": True,
                "data": {
                    "summary": {
                        "total_recent_events": len(recent_events),
                        "performance_components": len(performance_stats.get('performance_by_component', [])),
                        "accuracy_records": len(accuracy_stats.get('accuracy_by_symbol_timeframe', [])),
                        "error_types": len(error_summary.get('errors_by_type', []))
                    },
                    "performance_overview": performance_stats,
                    "accuracy_overview": accuracy_stats,
                    "error_overview": error_summary,
                    "recent_events": recent_events,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            ctx.add_output_data({"success": True, "dashboard_sections": 4})
            return response_data
            
        except Exception as e:
            logger.error(f"Error getting audit dashboard: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Audit dashboard generation failed: {str(e)}")


# Learning and Adaptation Endpoints

class AccuracyTrackingRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to track accuracy for")
    timeframe: str = Field(..., description="Prediction timeframe to track")


class RetrainingEvaluationRequest(BaseModel):
    symbol: Optional[str] = Field(default=None, description="Specific symbol to evaluate, or None for all")


class ModelRetrainingRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to retrain models for")
    model_types: Optional[List[str]] = Field(default=["LSTM", "GRU"], description="Model types to retrain")


class PerformancePatternRequest(BaseModel):
    symbol: Optional[str] = Field(default=None, description="Specific symbol to analyze, or None for all")


class ModelAdjustmentRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to adjust parameters for")
    adjustments: Dict[str, Any] = Field(..., description="Parameter adjustments to apply")


@router.post("/learning/track-accuracy")
async def track_prediction_accuracy(request: AccuracyTrackingRequest):
    """
    Track prediction accuracy by comparing predictions with actual prices.
    
    Validates recent predictions against actual market prices and updates accuracy metrics.
    """
    async with AuditContext("API", "track_prediction_accuracy", "LEARNING_REQUEST") as ctx:
        try:
            ctx.add_input_data({
                "symbol": request.symbol,
                "timeframe": request.timeframe
            })
            
            logger.info(f"Tracking prediction accuracy for {request.symbol} {request.timeframe}")
            
            accuracy_result = await learning_adaptation_engine.track_prediction_accuracy(
                symbol=request.symbol,
                timeframe=request.timeframe
            )
            
            response_data = {
                "success": True,
                "data": accuracy_result,
                "timestamp": datetime.now().isoformat()
            }
            
            ctx.add_output_data({
                "success": True, 
                "accuracy_tracked": True,
                "current_price": accuracy_result.get('current_price')
            })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error tracking prediction accuracy: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Accuracy tracking failed: {str(e)}")


@router.post("/learning/evaluate-retraining")
async def evaluate_retraining_need(request: RetrainingEvaluationRequest):
    """
    Evaluate if models need retraining based on accuracy thresholds.
    
    Analyzes prediction accuracy over time and recommends retraining when performance degrades.
    """
    async with AuditContext("API", "evaluate_retraining_need", "LEARNING_REQUEST") as ctx:
        try:
            ctx.add_input_data({"symbol": request.symbol})
            
            logger.info(f"Evaluating retraining need for {request.symbol or 'all symbols'}")
            
            evaluation_result = await learning_adaptation_engine.evaluate_retraining_need(
                symbol=request.symbol
            )
            
            response_data = {
                "success": True,
                "data": evaluation_result,
                "timestamp": datetime.now().isoformat()
            }
            
            ctx.add_output_data({
                "success": True,
                "symbols_evaluated": evaluation_result.get('total_symbols_evaluated', 0),
                "symbols_needing_retraining": evaluation_result.get('symbols_needing_retraining', 0)
            })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error evaluating retraining need: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Retraining evaluation failed: {str(e)}")


@router.post("/learning/trigger-retraining")
async def trigger_model_retraining(request: ModelRetrainingRequest, background_tasks: BackgroundTasks):
    """
    Trigger automatic model retraining for a symbol.
    
    Initiates retraining of ML models when accuracy falls below thresholds.
    """
    async with AuditContext("API", "trigger_model_retraining", "LEARNING_REQUEST") as ctx:
        try:
            ctx.add_input_data({
                "symbol": request.symbol,
                "model_types": request.model_types
            })
            
            logger.info(f"Triggering model retraining for {request.symbol}: {request.model_types}")
            
            # Run retraining in background to avoid timeout
            background_tasks.add_task(
                learning_adaptation_engine.trigger_model_retraining,
                request.symbol,
                request.model_types
            )
            
            response_data = {
                "success": True,
                "data": {
                    "symbol": request.symbol,
                    "model_types": request.model_types,
                    "status": "retraining_initiated",
                    "message": "Model retraining has been initiated in the background"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            ctx.add_output_data({
                "success": True,
                "retraining_initiated": True,
                "model_count": len(request.model_types)
            })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error triggering model retraining: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Model retraining failed: {str(e)}")


@router.post("/learning/performance-patterns")
async def identify_performance_patterns(request: PerformancePatternRequest):
    """
    Identify patterns in prediction performance to guide model improvements.
    
    Analyzes historical performance data to identify trends and optimization opportunities.
    """
    async with AuditContext("API", "identify_performance_patterns", "LEARNING_REQUEST") as ctx:
        try:
            ctx.add_input_data({"symbol": request.symbol})
            
            logger.info(f"Identifying performance patterns for {request.symbol or 'all symbols'}")
            
            pattern_result = await learning_adaptation_engine.identify_performance_patterns(
                symbol=request.symbol
            )
            
            response_data = {
                "success": True,
                "data": pattern_result,
                "timestamp": datetime.now().isoformat()
            }
            
            ctx.add_output_data({
                "success": True,
                "symbols_analyzed": pattern_result.get('total_symbols_analyzed', 0),
                "patterns_identified": len(pattern_result.get('individual_patterns', []))
            })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error identifying performance patterns: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Performance pattern analysis failed: {str(e)}")


@router.post("/learning/adjust-parameters")
async def adjust_model_parameters(request: ModelAdjustmentRequest):
    """
    Adjust model parameters based on performance analysis.
    
    Applies parameter adjustments to improve model performance based on identified patterns.
    """
    async with AuditContext("API", "adjust_model_parameters", "LEARNING_REQUEST") as ctx:
        try:
            ctx.add_input_data({
                "symbol": request.symbol,
                "adjustments": request.adjustments
            })
            
            logger.info(f"Adjusting model parameters for {request.symbol}")
            
            adjustment_result = await learning_adaptation_engine.adjust_model_parameters(
                symbol=request.symbol,
                adjustments=request.adjustments
            )
            
            response_data = {
                "success": True,
                "data": adjustment_result,
                "timestamp": datetime.now().isoformat()
            }
            
            ctx.add_output_data({
                "success": True,
                "adjustments_applied": adjustment_result.get('total_adjustments', 0)
            })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error adjusting model parameters: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Model parameter adjustment failed: {str(e)}")


@router.get("/learning/status")
async def get_learning_status():
    """
    Get overall learning and adaptation system status.
    
    Returns current status of the learning system including recent activities and performance metrics.
    """
    async with AuditContext("API", "get_learning_status", "LEARNING_REQUEST") as ctx:
        try:
            logger.info("Getting learning system status")
            
            # Get recent accuracy statistics
            accuracy_stats = await audit_logger.get_prediction_accuracy(days=7)
            
            # Get recent performance metrics
            performance_stats = await audit_logger.get_performance_statistics(
                component="LearningAdaptationEngine", 
                days=7
            )
            
            # Get recent audit events for learning activities
            learning_events = await audit_logger.get_audit_trail(
                component="LearningAdaptationEngine",
                limit=10
            )
            
            response_data = {
                "success": True,
                "data": {
                    "system_status": "active",
                    "recent_accuracy_stats": accuracy_stats,
                    "performance_metrics": performance_stats,
                    "recent_learning_activities": learning_events,
                    "learning_configuration": {
                        "accuracy_threshold": 0.6,
                        "evaluation_period_days": 30,
                        "retraining_cooldown_days": 7,
                        "performance_pattern_window": 90
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
            ctx.add_output_data({
                "success": True,
                "recent_activities": len(learning_events)
            })
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error getting learning status: {str(e)}")
            ctx.add_output_data({"success": False, "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Learning status retrieval failed: {str(e)}")

# Error handling middleware
async def handle_ai_trading_errors(request: Request, call_next):
    """Middleware to handle AI trading errors consistently."""
    try:
        response = await call_next(request)
        return response
    except AITradingError as e:
        logger.error(f"AI Trading Error: {e.message}")
        raise HTTPException(
            status_code=500 if e.severity.value in ['HIGH', 'CRITICAL'] else 400,
            detail={
                'error': e.message,
                'category': e.category.value,
                'severity': e.severity.value,
                'timestamp': e.timestamp.isoformat(),
                'fallback_available': True
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
        )


# Error status and recovery endpoints
@router.get("/error-status")
async def get_error_status():
    """Get comprehensive error statistics and system health."""
    try:
        error_stats = await error_handler.get_error_stats()
        ollama_metrics = await ollama_recovery.get_performance_metrics()
        
        return {
            'error_statistics': error_stats,
            'ollama_health': ollama_metrics,
            'system_status': 'operational',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recover-ollama")
async def recover_ollama_service():
    """Manually trigger Ollama service recovery."""
    try:
        recovery_result = await ollama_recovery.attempt_recovery()
        
        return {
            'recovery_attempted': True,
            'recovery_successful': recovery_result,
            'message': 'Ollama recovery successful' if recovery_result else 'Ollama recovery failed',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error during Ollama recovery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-circuit-breaker/{service}")
async def reset_circuit_breaker(service: str):
    """Reset circuit breaker for a specific service."""
    try:
        reset_result = await error_handler.reset_circuit_breaker(service)
        
        return {
            'service': service,
            'reset_successful': reset_result,
            'message': f'Circuit breaker reset for {service}' if reset_result else f'No circuit breaker found for {service}',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error resetting circuit breaker: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-check")
async def comprehensive_health_check():
    """Comprehensive health check for all AI trading components."""
    try:
        health_status = {
            'overall_status': 'healthy',
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check Ollama service
        try:
            ollama_health = await ollama_recovery.check_health()
            health_status['components']['ollama'] = {
                'status': ollama_health.state.value,
                'response_time': ollama_health.response_time,
                'model_loaded': ollama_health.model_loaded,
                'last_error': ollama_health.last_error
            }
            
            if ollama_health.state.value in ['UNAVAILABLE', 'FAILED']:
                health_status['overall_status'] = 'degraded'
        except Exception as e:
            health_status['components']['ollama'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            health_status['overall_status'] = 'degraded'
        
        # Check prediction engine
        try:
            # Simple test prediction
            test_result = await prediction_engine.generate_predictions("AAPL", ["1d"])
            health_status['components']['prediction_engine'] = {
                'status': 'healthy' if test_result.confidence_score > 0 else 'degraded'
            }
        except Exception as e:
            health_status['components']['prediction_engine'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            health_status['overall_status'] = 'degraded'
        
        # Check recommendation engine
        try:
            # Test with minimal data
            from ..ai_trading.data_models import PredictionResult, ConfidenceInterval
            test_prediction = PredictionResult(
                symbol="AAPL",
                predictions={"1d": 150.0},
                confidence_intervals={"1d": ConfidenceInterval(145.0, 155.0, 0.95)},
                confidence_score=0.8,
                timestamp=datetime.now(),
                model_ensemble=["test"]
            )
            test_risk = RiskAssessment(
                symbol="AAPL",
                risk_score=0.5,
                risk_factors=[],
                timestamp=datetime.now()
            )
            
            test_recommendation = await recommendation_engine.generate_recommendation(
                "AAPL", test_prediction, test_risk
            )
            health_status['components']['recommendation_engine'] = {
                'status': 'healthy' if test_recommendation.confidence > 0 else 'degraded'
            }
        except Exception as e:
            health_status['components']['recommendation_engine'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            health_status['overall_status'] = 'degraded'
        
        # Check risk analyzer
        try:
            test_risk_metrics = await risk_analyzer.calculate_risk_metrics("AAPL", {})
            health_status['components']['risk_analyzer'] = {
                'status': 'healthy' if test_risk_metrics.volatility > 0 else 'degraded'
            }
        except Exception as e:
            health_status['components']['risk_analyzer'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            health_status['overall_status'] = 'degraded'
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced prediction endpoint with error handling
@router.post("/predictions")
async def get_predictions(request: PredictionRequest):
    """Generate stock price predictions with comprehensive error handling."""
    try:
        context = ErrorContext(
            component="API",
            operation="get_predictions",
            symbol=request.symbol,
            request_id=f"pred_{datetime.now().timestamp()}"
        )
        
        result = await prediction_engine.generate_predictions(
            symbol=request.symbol,
            timeframes=request.timeframes
        )
        
        return {
            'success': True,
            'data': {
                'symbol': result.symbol,
                'predictions': result.predictions,
                'confidence_intervals': {
                    tf: {
                        'lower_bound': ci.lower_bound,
                        'upper_bound': ci.upper_bound,
                        'confidence_level': ci.confidence_level
                    }
                    for tf, ci in result.confidence_intervals.items()
                },
                'confidence_score': result.confidence_score,
                'model_ensemble': result.model_ensemble,
                'timestamp': result.timestamp.isoformat()
            },
            'metadata': {
                'request_id': context.request_id,
                'processing_time': datetime.now().isoformat()
            }
        }
        
    except DataUnavailableError as e:
        logger.warning(f"Data unavailable for prediction: {e.message}")
        raise HTTPException(
            status_code=404,
            detail={
                'error': 'Data unavailable',
                'message': e.message,
                'symbol': request.symbol,
                'fallback_available': True,
                'timestamp': datetime.now().isoformat()
            }
        )
    except ModelError as e:
        logger.error(f"Model error in prediction: {e.message}")
        raise HTTPException(
            status_code=500,
            detail={
                'error': 'Model error',
                'message': e.message,
                'symbol': request.symbol,
                'fallback_available': True,
                'timestamp': datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                'error': 'Internal server error',
                'message': str(e),
                'symbol': request.symbol,
                'timestamp': datetime.now().isoformat()
            }
        )


# Enhanced recommendation endpoint with error handling
@router.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Generate trading recommendations with comprehensive error handling."""
    try:
        context = ErrorContext(
            component="API",
            operation="get_recommendations",
            symbol=request.symbol,
            request_id=f"rec_{datetime.now().timestamp()}"
        )
        
        # First get prediction and risk analysis
        prediction = await prediction_engine.generate_predictions(request.symbol, ["1d", "3d", "7d"])
        risk_metrics = await risk_analyzer.calculate_risk_metrics(request.symbol, request.portfolio)
        
        # Create risk assessment from metrics
        risk_assessment = RiskAssessment(
            symbol=request.symbol,
            risk_score=min(risk_metrics.volatility * 2, 1.0),  # Simple risk score
            risk_factors=[
                f"Volatility: {risk_metrics.volatility:.2%}",
                f"Beta: {risk_metrics.beta:.2f}",
                f"Max Drawdown: {risk_metrics.max_drawdown:.2%}"
            ],
            timestamp=datetime.now()
        )
        
        recommendation = await recommendation_engine.generate_recommendation(
            symbol=request.symbol,
            prediction=prediction,
            risk_analysis=risk_assessment
        )
        
        return {
            'success': True,
            'data': {
                'symbol': recommendation.symbol,
                'action': recommendation.action,
                'confidence': recommendation.confidence,
                'target_price': recommendation.target_price,
                'stop_loss': recommendation.stop_loss,
                'position_size': recommendation.position_size,
                'rationale': recommendation.rationale,
                'risk_reward_ratio': recommendation.risk_reward_ratio,
                'timestamp': recommendation.timestamp.isoformat()
            },
            'metadata': {
                'request_id': context.request_id,
                'processing_time': datetime.now().isoformat(),
                'prediction_confidence': prediction.confidence_score,
                'risk_score': risk_assessment.risk_score
            }
        }
        
    except (DataUnavailableError, ModelError, OllamaError) as e:
        logger.warning(f"Error in recommendation generation: {e.message}")
        raise HTTPException(
            status_code=400 if isinstance(e, DataUnavailableError) else 500,
            detail={
                'error': e.category.value,
                'message': e.message,
                'symbol': request.symbol,
                'fallback_available': True,
                'timestamp': datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in recommendation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                'error': 'Internal server error',
                'message': str(e),
                'symbol': request.symbol,
                'timestamp': datetime.now().isoformat()
            }
        )


# Enhanced risk analysis endpoint
@router.post("/risk-analysis")
async def get_risk_analysis(symbol: str, portfolio: Optional[Dict[str, Any]] = None):
    """Get comprehensive risk analysis with error handling."""
    try:
        if portfolio is None:
            portfolio = {}
            
        context = ErrorContext(
            component="API",
            operation="get_risk_analysis",
            symbol=symbol,
            request_id=f"risk_{datetime.now().timestamp()}"
        )
        
        risk_metrics = await risk_analyzer.calculate_risk_metrics(symbol, portfolio)
        
        return {
            'success': True,
            'data': {
                'symbol': risk_metrics.symbol,
                'var_1d': risk_metrics.var_1d,
                'var_5d': risk_metrics.var_5d,
                'beta': risk_metrics.beta,
                'volatility': risk_metrics.volatility,
                'sharpe_ratio': risk_metrics.sharpe_ratio,
                'max_drawdown': risk_metrics.max_drawdown,
                'correlation_to_market': risk_metrics.correlation_to_market
            },
            'metadata': {
                'request_id': context.request_id,
                'processing_time': datetime.now().isoformat()
            }
        }
        
    except DataUnavailableError as e:
        logger.warning(f"Data unavailable for risk analysis: {e.message}")
        raise HTTPException(
            status_code=404,
            detail={
                'error': 'Data unavailable',
                'message': e.message,
                'symbol': symbol,
                'fallback_available': True,
                'timestamp': datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in risk analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                'error': 'Internal server error',
                'message': str(e),
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
        )