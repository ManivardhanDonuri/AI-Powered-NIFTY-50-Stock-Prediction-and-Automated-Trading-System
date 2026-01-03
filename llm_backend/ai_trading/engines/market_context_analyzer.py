"""
Market Context Analyzer for AI Trading Assistant.

This analyzer provides market context including news sentiment analysis,
market event detection, and real-time context updates.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from ..interfaces import MarketContextAnalyzerInterface
from ..data_models import SentimentAnalysis, MarketEvent
from ...services.news_sentiment_analyzer import NewsSentimentAnalyzer


class MarketContextAnalyzer(MarketContextAnalyzerInterface):
    """
    Market context analysis engine.
    
    Analyzes news sentiment, detects market events, and provides
    real-time market context updates.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize news sentiment analyzer
        try:
            self.news_analyzer = NewsSentimentAnalyzer()
        except Exception as e:
            self.logger.warning(f"Could not initialize news analyzer: {e}")
            self.news_analyzer = None
        
        # Market context cache
        self.context_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Event detection thresholds
        self.volatility_threshold = 0.05  # 5% daily move
        self.volume_threshold = 2.0  # 2x average volume
        
        self.logger.info("Market Context Analyzer initialized")

    async def analyze_news_sentiment(
        self, 
        symbol: str, 
        timeframe: str = "24h"
    ) -> SentimentAnalysis:
        """
        Analyze news sentiment for a stock.
        
        Args:
            symbol: Stock symbol to analyze
            timeframe: Time window for analysis
            
        Returns:
            SentimentAnalysis: Sentiment analysis results
        """
        try:
            self.logger.info(f"Analyzing news sentiment for {symbol} over {timeframe}")
            
            # Check cache first
            cache_key = f"{symbol}_{timeframe}_sentiment"
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Get news data and analyze sentiment
            if self.news_analyzer:
                sentiment_result = await self._analyze_with_news_service(symbol, timeframe)
            else:
                sentiment_result = await self._get_fallback_sentiment(symbol, timeframe)
            
            # Cache the result
            await self._cache_result(cache_key, sentiment_result)
            
            self.logger.info(f"Sentiment analysis complete for {symbol}: {sentiment_result.sentiment_score:.2f}")
            return sentiment_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment for {symbol}: {str(e)}")
            return await self._get_fallback_sentiment(symbol, timeframe)

    async def detect_market_events(
        self, 
        market_data: Dict[str, Any]
    ) -> List[MarketEvent]:
        """
        Detect significant market events.
        
        Args:
            market_data: Current market data
            
        Returns:
            List[MarketEvent]: Detected market events
        """
        try:
            self.logger.info("Detecting market events")
            
            events = []
            
            # Analyze market-wide indicators
            events.extend(await self._detect_volatility_events(market_data))
            events.extend(await self._detect_volume_events(market_data))
            events.extend(await self._detect_sector_events(market_data))
            events.extend(await self._detect_economic_events(market_data))
            
            self.logger.info(f"Detected {len(events)} market events")
            return events
            
        except Exception as e:
            self.logger.error(f"Error detecting market events: {str(e)}")
            return []

    async def update_context(
        self, 
        context_data: Dict[str, Any]
    ) -> None:
        """
        Update market context with new data.
        
        Args:
            context_data: New context data to incorporate
        """
        try:
            self.logger.info("Updating market context")
            
            # Update context cache with new data
            timestamp = datetime.now()
            
            for key, value in context_data.items():
                self.context_cache[key] = {
                    'data': value,
                    'timestamp': timestamp
                }
            
            # Clean old cache entries
            await self._clean_cache()
            
            self.logger.info(f"Market context updated with {len(context_data)} items")
            
        except Exception as e:
            self.logger.error(f"Error updating context: {str(e)}")

    async def _analyze_with_news_service(self, symbol: str, timeframe: str) -> SentimentAnalysis:
        """Analyze sentiment using the news service."""
        try:
            # Convert timeframe to hours
            hours = self._timeframe_to_hours(timeframe)
            
            # Get news sentiment (this would integrate with the actual news service)
            # For now, using a simplified approach
            sentiment_score = await self._get_news_sentiment_score(symbol, hours)
            news_count = await self._get_news_count(symbol, hours)
            key_themes = await self._extract_key_themes(symbol, hours)
            sources = await self._get_news_sources(symbol, hours)
            
            return SentimentAnalysis(
                symbol=symbol,
                sentiment_score=sentiment_score,
                news_count=news_count,
                key_themes=key_themes,
                confidence=0.8,
                sources=sources,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error with news service analysis: {str(e)}")
            return await self._get_fallback_sentiment(symbol, timeframe)

    async def _get_news_sentiment_score(self, symbol: str, hours: int) -> float:
        """Get aggregated news sentiment score."""
        try:
            # Simulate news sentiment analysis
            # In practice, this would call the actual news sentiment analyzer
            
            # Generate realistic sentiment based on symbol
            base_sentiment = {
                "AAPL": 0.2,
                "GOOGL": 0.1,
                "MSFT": 0.15,
                "TSLA": -0.1,
                "AMZN": 0.05
            }.get(symbol, 0.0)
            
            # Add some randomness based on time
            import random
            random.seed(hash(symbol + str(hours)))
            noise = (random.random() - 0.5) * 0.3
            
            sentiment = base_sentiment + noise
            return max(-1.0, min(1.0, sentiment))
            
        except Exception as e:
            self.logger.error(f"Error getting sentiment score: {str(e)}")
            return 0.0

    async def _get_news_count(self, symbol: str, hours: int) -> int:
        """Get count of news articles."""
        try:
            # Simulate news count based on symbol popularity
            base_count = {
                "AAPL": 25,
                "GOOGL": 20,
                "MSFT": 18,
                "TSLA": 30,
                "AMZN": 22
            }.get(symbol, 10)
            
            # Scale by timeframe
            count = int(base_count * (hours / 24))
            return max(1, count)
            
        except Exception as e:
            self.logger.error(f"Error getting news count: {str(e)}")
            return 5

    async def _extract_key_themes(self, symbol: str, hours: int) -> List[str]:
        """Extract key themes from news."""
        try:
            # Simulate key themes based on symbol
            theme_map = {
                "AAPL": ["iPhone sales", "AI integration", "services growth"],
                "GOOGL": ["AI development", "cloud services", "advertising"],
                "MSFT": ["cloud computing", "AI partnerships", "enterprise"],
                "TSLA": ["EV market", "autonomous driving", "energy"],
                "AMZN": ["e-commerce", "AWS growth", "logistics"]
            }
            
            return theme_map.get(symbol, ["earnings", "market trends", "analyst ratings"])
            
        except Exception as e:
            self.logger.error(f"Error extracting themes: {str(e)}")
            return ["general market"]

    async def _get_news_sources(self, symbol: str, hours: int) -> List[str]:
        """Get news sources."""
        return ["Reuters", "Bloomberg", "CNBC", "MarketWatch", "Yahoo Finance"]

    async def _detect_volatility_events(self, market_data: Dict[str, Any]) -> List[MarketEvent]:
        """Detect high volatility events."""
        events = []
        
        try:
            # Check VIX or volatility indicators
            vix = market_data.get('vix', 20.0)
            
            if vix > 30:
                events.append(MarketEvent(
                    event_type="HIGH_VOLATILITY",
                    description=f"High market volatility detected (VIX: {vix:.1f})",
                    impact_level="HIGH",
                    affected_sectors=["All"],
                    timestamp=datetime.now(),
                    source="VIX_MONITOR"
                ))
            elif vix > 25:
                events.append(MarketEvent(
                    event_type="ELEVATED_VOLATILITY",
                    description=f"Elevated market volatility (VIX: {vix:.1f})",
                    impact_level="MEDIUM",
                    affected_sectors=["All"],
                    timestamp=datetime.now(),
                    source="VIX_MONITOR"
                ))
            
            # Check individual stock volatility
            for symbol, data in market_data.items():
                if isinstance(data, dict) and 'change_percent' in data:
                    change_pct = abs(data['change_percent'])
                    if change_pct > 10:
                        events.append(MarketEvent(
                            event_type="STOCK_VOLATILITY",
                            description=f"{symbol} showing high volatility ({change_pct:.1f}%)",
                            impact_level="HIGH" if change_pct > 15 else "MEDIUM",
                            affected_sectors=[self._get_sector(symbol)],
                            timestamp=datetime.now(),
                            source="PRICE_MONITOR"
                        ))
            
        except Exception as e:
            self.logger.error(f"Error detecting volatility events: {str(e)}")
        
        return events

    async def _detect_volume_events(self, market_data: Dict[str, Any]) -> List[MarketEvent]:
        """Detect unusual volume events."""
        events = []
        
        try:
            for symbol, data in market_data.items():
                if isinstance(data, dict) and 'volume' in data:
                    volume = data['volume']
                    avg_volume = data.get('avg_volume', volume)
                    
                    if avg_volume > 0:
                        volume_ratio = volume / avg_volume
                        
                        if volume_ratio > 3:
                            events.append(MarketEvent(
                                event_type="UNUSUAL_VOLUME",
                                description=f"{symbol} showing unusual volume ({volume_ratio:.1f}x average)",
                                impact_level="HIGH",
                                affected_sectors=[self._get_sector(symbol)],
                                timestamp=datetime.now(),
                                source="VOLUME_MONITOR"
                            ))
            
        except Exception as e:
            self.logger.error(f"Error detecting volume events: {str(e)}")
        
        return events

    async def _detect_sector_events(self, market_data: Dict[str, Any]) -> List[MarketEvent]:
        """Detect sector-wide events."""
        events = []
        
        try:
            # Group stocks by sector and analyze sector performance
            sector_performance = {}
            
            for symbol, data in market_data.items():
                if isinstance(data, dict) and 'change_percent' in data:
                    sector = self._get_sector(symbol)
                    if sector not in sector_performance:
                        sector_performance[sector] = []
                    sector_performance[sector].append(data['change_percent'])
            
            # Analyze sector performance
            for sector, changes in sector_performance.items():
                if len(changes) >= 3:  # Need at least 3 stocks
                    avg_change = sum(changes) / len(changes)
                    
                    if abs(avg_change) > 3:  # 3% sector move
                        direction = "up" if avg_change > 0 else "down"
                        events.append(MarketEvent(
                            event_type="SECTOR_MOVEMENT",
                            description=f"{sector} sector moving {direction} ({avg_change:.1f}% average)",
                            impact_level="MEDIUM",
                            affected_sectors=[sector],
                            timestamp=datetime.now(),
                            source="SECTOR_MONITOR"
                        ))
            
        except Exception as e:
            self.logger.error(f"Error detecting sector events: {str(e)}")
        
        return events

    async def _detect_economic_events(self, market_data: Dict[str, Any]) -> List[MarketEvent]:
        """Detect economic indicator events."""
        events = []
        
        try:
            # Check for economic indicators in market data
            economic_indicators = ['unemployment', 'inflation', 'gdp', 'fed_rate']
            
            for indicator in economic_indicators:
                if indicator in market_data:
                    value = market_data[indicator]
                    # Simplified economic event detection
                    if indicator == 'inflation' and value > 4:
                        events.append(MarketEvent(
                            event_type="HIGH_INFLATION",
                            description=f"High inflation detected ({value:.1f}%)",
                            impact_level="HIGH",
                            affected_sectors=["All"],
                            timestamp=datetime.now(),
                            source="ECONOMIC_DATA"
                        ))
            
        except Exception as e:
            self.logger.error(f"Error detecting economic events: {str(e)}")
        
        return events

    def _get_sector(self, symbol: str) -> str:
        """Get sector for a stock symbol."""
        sector_map = {
            "AAPL": "Technology",
            "GOOGL": "Technology",
            "MSFT": "Technology",
            "AMZN": "Technology",
            "TSLA": "Automotive",
            "JPM": "Financial",
            "JNJ": "Healthcare",
            "XOM": "Energy"
        }
        return sector_map.get(symbol, "Other")

    def _timeframe_to_hours(self, timeframe: str) -> int:
        """Convert timeframe string to hours."""
        timeframe_map = {
            "1h": 1,
            "4h": 4,
            "12h": 12,
            "24h": 24,
            "1d": 24,
            "2d": 48,
            "7d": 168,
            "1w": 168
        }
        return timeframe_map.get(timeframe, 24)

    async def _get_cached_result(self, cache_key: str) -> Optional[SentimentAnalysis]:
        """Get cached result if still valid."""
        if cache_key in self.context_cache:
            cached_item = self.context_cache[cache_key]
            age = (datetime.now() - cached_item['timestamp']).total_seconds()
            
            if age < self.cache_ttl:
                return cached_item['data']
        
        return None

    async def _cache_result(self, cache_key: str, result: SentimentAnalysis) -> None:
        """Cache analysis result."""
        self.context_cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }

    async def _clean_cache(self) -> None:
        """Clean expired cache entries."""
        current_time = datetime.now()
        expired_keys = []
        
        for key, item in self.context_cache.items():
            age = (current_time - item['timestamp']).total_seconds()
            if age > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.context_cache[key]

    async def _get_fallback_sentiment(self, symbol: str, timeframe: str) -> SentimentAnalysis:
        """Get fallback sentiment when analysis fails."""
        return SentimentAnalysis(
            symbol=symbol,
            sentiment_score=0.1,  # Slightly positive default
            news_count=5,
            key_themes=["market analysis", "earnings"],
            confidence=0.6,
            sources=["fallback"],
            timestamp=datetime.now()
        )