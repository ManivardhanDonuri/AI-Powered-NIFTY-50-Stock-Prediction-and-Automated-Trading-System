
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel, Field

from ..services.llm_service import LLMServiceManager, TradingContext
from ..services.trading_context_provider import TradingContextProvider
from ..services.news_sentiment_analyzer import NewsSentimentAnalyzer, SentimentData
from ..config import get_settings

router = APIRouter()

class PortfolioAnalysisResponse(BaseModel):
    analysis: str
    key_insights: List[str]
    risk_assessment: str
    recommendations: List[str]
    confidence: float
    timestamp: datetime

class MarketOutlookResponse(BaseModel):
    outlook: str
    sentiment_summary: str
    key_factors: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    confidence: float
    timestamp: datetime

class SignalExplanationRequest(BaseModel):
    signal_data: Dict[str, Any]
    symbol: str
    include_context: bool = True

class SignalExplanationResponse(BaseModel):
    explanation: str
    reasoning: List[str]
    confidence_assessment: str
    risk_factors: List[str]
    recommended_action: str
    timestamp: datetime

class NewsSentimentResponse(BaseModel):
    symbol: str
    overall_sentiment: float
    sentiment_trend: str
    confidence: float
    news_count: int
    key_themes: List[str]
    summary: str
    last_updated: datetime

def get_llm_service(request: Request) -> LLMServiceManager:
    if not hasattr(request.app.state, 'llm_service'):
        raise HTTPException(status_code=500, detail="LLM service not initialized")
    return request.app.state.llm_service

def get_context_provider(request: Request) -> TradingContextProvider:
    if not hasattr(request.app.state, 'context_provider'):
        raise HTTPException(status_code=500, detail="Context provider not initialized")
    return request.app.state.context_provider

def get_sentiment_analyzer() -> NewsSentimentAnalyzer:
    settings = get_settings()
    return NewsSentimentAnalyzer(settings)

@router.get("/portfolio-summary", response_model=PortfolioAnalysisResponse)
async def get_portfolio_analysis(
    include_performance: bool = Query(True, description="Include performance metrics"),
    include_risk: bool = Query(True, description="Include risk analysis"),
    llm_service: LLMServiceManager = Depends(get_llm_service),
    context_provider: TradingContextProvider = Depends(get_context_provider)
):
    try:
        context_data = context_provider.aggregate_context('portfolio')

        query_parts = ["Analyze my current portfolio performance and provide detailed insights."]

        if include_performance:
            query_parts.append("Include performance metrics analysis and attribution.")

        if include_risk:
            query_parts.append("Include comprehensive risk assessment and recommendations.")

        query_parts.extend([
            "Provide specific, actionable recommendations.",
            "Highlight key strengths and areas for improvement.",
            "Consider current market conditions in your analysis."
        ])

        query = " ".join(query_parts)

        trading_context = TradingContext(
            portfolio=context_data.get('portfolio', {}),
            market=context_data.get('market', {}),
            signals=context_data.get('signals', []),
            performance=context_data.get('performance', {}),
            sentiment={},
            timestamp=datetime.now()
        )

        llm_response = await llm_service.process_query(query, trading_context)

        analysis_text = llm_response.content

        key_insights = _extract_key_points(analysis_text, "insights", "recommendations")
        recommendations = _extract_key_points(analysis_text, "recommendations", "risk")
        risk_assessment = _extract_section(analysis_text, "risk")

        return PortfolioAnalysisResponse(
            analysis=analysis_text,
            key_insights=key_insights,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            confidence=llm_response.confidence,
            timestamp=llm_response.timestamp
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio: {str(e)}")

@router.get("/market-outlook", response_model=MarketOutlookResponse)
async def get_market_outlook(
    symbols: Optional[List[str]] = Query(None, description="Specific symbols to analyze"),
    include_sentiment: bool = Query(True, description="Include sentiment analysis"),
    llm_service: LLMServiceManager = Depends(get_llm_service),
    context_provider: TradingContextProvider = Depends(get_context_provider)
):
    try:
        context_data = context_provider.aggregate_context('market')

        sentiment_data = {}
        if include_sentiment and symbols:
            sentiment_analyzer = get_sentiment_analyzer()
            sentiment_results = await sentiment_analyzer.analyze_multiple_symbols(symbols)
            sentiment_data = {symbol: data.__dict__ for symbol, data in sentiment_results.items()}

        query = "Provide a comprehensive market outlook based on current conditions. "

        if symbols:
            query += f"Focus on these symbols: {', '.join(symbols)}. "

        if include_sentiment:
            query += "Include sentiment analysis and news impact. "

        trading_context = TradingContext(
            portfolio=context_data.get('portfolio', {}),
            market=context_data.get('market', {}),
            signals=context_data.get('signals', []),
            performance=context_data.get('performance', {}),
            sentiment=sentiment_data,
            timestamp=datetime.now()
        )

        llm_response = await llm_service.process_query(query, trading_context)

        outlook_text = llm_response.content

        key_factors = _extract_key_points(outlook_text, "factors", "risk")
        risk_factors = _extract_key_points(outlook_text, "risk", "opportunities")
        opportunities = _extract_key_points(outlook_text, "opportunities", "recommendations")

        sentiment_summary = "No sentiment data available"
        if sentiment_data:
            avg_sentiment = sum(data['overall_sentiment'] for data in sentiment_data.values()) / len(sentiment_data)
            if avg_sentiment > 0.2:
                sentiment_summary = "Overall market sentiment is bullish"
            elif avg_sentiment < -0.2:
                sentiment_summary = "Overall market sentiment is bearish"
            else:
                sentiment_summary = "Market sentiment is neutral to mixed"

        return MarketOutlookResponse(
            outlook=outlook_text,
            sentiment_summary=sentiment_summary,
            key_factors=key_factors,
            risk_factors=risk_factors,
            opportunities=opportunities,
            confidence=llm_response.confidence,
            timestamp=llm_response.timestamp
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating market outlook: {str(e)}")

@router.post("/analyze-signal", response_model=SignalExplanationResponse)
async def analyze_trading_signal(
    request: SignalExplanationRequest,
    llm_service: LLMServiceManager = Depends(get_llm_service),
    context_provider: TradingContextProvider = Depends(get_context_provider)
):
    try:
        signal_data = request.signal_data
        symbol = request.symbol

        trading_context = None
        if request.include_context:
            context_data = context_provider.aggregate_context('signals')
            trading_context = TradingContext(
                portfolio=context_data.get('portfolio', {}),
                market=context_data.get('market', {}),
                signals=[signal_data],
                performance=context_data.get('performance', {}),
                sentiment={},
                timestamp=datetime.now()
            )
        else:
            trading_context = TradingContext(
                portfolio={},
                market={},
                signals=[signal_data],
                performance={},
                sentiment={},
                timestamp=datetime.now()
            )

        llm_response = await llm_service.process_query(query, trading_context)

        explanation_text = llm_response.content

        reasoning = _extract_key_points(explanation_text, "reasoning", "confidence")
        risk_factors = _extract_key_points(explanation_text, "risk", "recommended")
        confidence_assessment = _extract_section(explanation_text, "confidence")
        recommended_action = _extract_section(explanation_text, "recommended")

        return SignalExplanationResponse(
            explanation=explanation_text,
            reasoning=reasoning,
            confidence_assessment=confidence_assessment,
            risk_factors=risk_factors,
            recommended_action=recommended_action,
            timestamp=llm_response.timestamp
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing signal: {str(e)}")

@router.get("/news-sentiment/{symbol}", response_model=NewsSentimentResponse)
async def get_news_sentiment(
    symbol: str,
    force_refresh: bool = Query(False, description="Force refresh of cached data")
):
    try:
        sentiment_analyzer = get_sentiment_analyzer()

        if force_refresh:
            sentiment_analyzer.clear_cache()

        sentiment_data = await sentiment_analyzer.analyze_symbol_sentiment(symbol)

        summary = f"Sentiment analysis for {symbol} based on {sentiment_data.news_count} news articles. "

        if sentiment_data.sentiment_trend == 'bullish':
            summary += "News coverage is generally positive with bullish indicators."
        elif sentiment_data.sentiment_trend == 'bearish':
            summary += "News coverage shows bearish sentiment with negative indicators."
        else:
            summary += "News sentiment is neutral with mixed indicators."

        if sentiment_data.key_themes:
            summary += f" Key themes include: {', '.join(sentiment_data.key_themes)}."

        return NewsSentimentResponse(
            symbol=symbol,
            overall_sentiment=sentiment_data.overall_sentiment,
            sentiment_trend=sentiment_data.sentiment_trend,
            confidence=sentiment_data.confidence,
            news_count=sentiment_data.news_count,
            key_themes=sentiment_data.key_themes,
            summary=summary,
            last_updated=sentiment_data.last_updated
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting news sentiment: {str(e)}")

@router.get("/news-sentiment", response_model=List[NewsSentimentResponse])
async def get_multiple_news_sentiment(
    symbols: List[str] = Query(..., description="List of symbols to analyze"),
    force_refresh: bool = Query(False, description="Force refresh of cached data")
):
    try:
        sentiment_analyzer = get_sentiment_analyzer()

        if force_refresh:
            sentiment_analyzer.clear_cache()

        sentiment_results = await sentiment_analyzer.analyze_multiple_symbols(symbols)

        responses = []
        for symbol, sentiment_data in sentiment_results.items():
            summary = f"Sentiment analysis for {symbol} based on {sentiment_data.news_count} news articles. "

            if sentiment_data.sentiment_trend == 'bullish':
                summary += "News coverage is generally positive with bullish indicators."
            elif sentiment_data.sentiment_trend == 'bearish':
                summary += "News coverage shows bearish sentiment with negative indicators."
            else:
                summary += "News sentiment is neutral with mixed indicators."

            if sentiment_data.key_themes:
                summary += f" Key themes include: {', '.join(sentiment_data.key_themes)}."

            response = NewsSentimentResponse(
                symbol=symbol,
                overall_sentiment=sentiment_data.overall_sentiment,
                sentiment_trend=sentiment_data.sentiment_trend,
                confidence=sentiment_data.confidence,
                news_count=sentiment_data.news_count,
                key_themes=sentiment_data.key_themes,
                summary=summary,
                last_updated=sentiment_data.last_updated
            )
            responses.append(response)

        return responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting news sentiment: {str(e)}")

@router.get("/insights/summary")
async def get_insights_summary(
    llm_service: LLMServiceManager = Depends(get_llm_service),
    context_provider: TradingContextProvider = Depends(get_context_provider)
):
    try:
        context_data = context_provider.aggregate_context('general')

        trading_context = TradingContext(
            portfolio=context_data.get('portfolio', {}),
            market=context_data.get('market', {}),
            signals=context_data.get('signals', []),
            performance=context_data.get('performance', {}),
            sentiment={},
            timestamp=datetime.now()
        )

        llm_response = await llm_service.process_query(query, trading_context)

        return {
            'summary': llm_response.content,
            'confidence': llm_response.confidence,
            'cached': llm_response.cached,
            'response_time': llm_response.response_time,
            'timestamp': llm_response.timestamp.isoformat(),
            'context_data': {
                'portfolio_available': bool(context_data.get('portfolio')),
                'market_data_available': bool(context_data.get('market')),
                'signals_count': len(context_data.get('signals', [])),
                'performance_available': bool(context_data.get('performance'))
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights summary: {str(e)}")

def _extract_key_points(text: str, start_keyword: str, end_keyword: str) -> List[str]:
    points = []

    lines = text.split('\n')
    in_section = False

    for line in lines:
        line = line.strip()

        if start_keyword.lower() in line.lower():
            in_section = True
            continue

        if end_keyword.lower() in line.lower():
            in_section = False
            continue

        if in_section and line:
            if line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                clean_point = line.lstrip('•-*123456789. ').strip()
                if clean_point:
                    points.append(clean_point)

    if not points and start_keyword.lower() in text.lower():
        sentences = text.split('.')
        for sentence in sentences[:3]:
            if start_keyword.lower() in sentence.lower():
                points.append(sentence.strip())
                break

    return points[:5]

def _extract_section(text: str, keyword: str) -> str:
    lines = text.split('\n')
    section_lines = []
    in_section = False

    for line in lines:
        if keyword.lower() in line.lower():
            in_section = True
            section_lines.append(line)
            continue

        if in_section:
            if line.strip() and not line.startswith(' '):
                break
            section_lines.append(line)

    section_text = '\n'.join(section_lines).strip()

    if not section_text:
        return f"No specific {keyword} information available in the analysis."

    return section_text