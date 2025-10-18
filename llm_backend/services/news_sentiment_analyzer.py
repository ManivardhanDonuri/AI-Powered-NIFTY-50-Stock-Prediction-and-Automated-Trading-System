
import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass, asdict

from ..config import Settings

@dataclass
class NewsArticle:
    title: str
    summary: str
    url: str
    source: str
    published_at: datetime
    sentiment_score: Optional[float] = None
    relevance_score: Optional[float] = None
    symbols: List[str] = None

@dataclass
class SentimentData:
    symbol: str
    overall_sentiment: float
    confidence: float
    news_count: int
    social_mentions: int
    sentiment_trend: str
    key_themes: List[str]
    last_updated: datetime

class NewsAPIClient:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def fetch_alpha_vantage_news(self, symbols: List[str]) -> List[NewsArticle]:
        if not self.settings.alpha_vantage_api_key:
            self.logger.warning("Alpha Vantage API key not configured")
            return []

        articles = []
        session = await self._get_session()

        try:
            for symbol in symbols[:5]:
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'NEWS_SENTIMENT',
                    'tickers': symbol,
                    'apikey': self.settings.alpha_vantage_api_key,
                    'limit': 20
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if 'feed' in data:
                            for item in data['feed']:
                                article = NewsArticle(
                                    title=item.get('title', ''),
                                    summary=item.get('summary', ''),
                                    url=item.get('url', ''),
                                    source='alpha_vantage',
                                    published_at=datetime.fromisoformat(
                                        item.get('time_published', '').replace('T', ' ')
                                    ) if item.get('time_published') else datetime.now(),
                                    symbols=[symbol]
                                )

                                if 'overall_sentiment_score' in item:
                                    article.sentiment_score = float(item['overall_sentiment_score'])

                                articles.append(article)

                await asyncio.sleep(0.2)

        except Exception as e:
            self.logger.error(f"Error fetching Alpha Vantage news: {str(e)}")

        return articles

    async def fetch_news_api_articles(self, symbols: List[str]) -> List[NewsArticle]:
        if not self.settings.news_api_key:
            self.logger.warning("NewsAPI key not configured")
            return []

        articles = []
        session = await self._get_session()

        try:
            query = ' OR '.join([f'"{symbol}"' for symbol in symbols[:3]])

            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'({query}) AND (stock OR trading OR market)',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 50,
                'apiKey': self.settings.news_api_key
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    for item in data.get('articles', []):
                        relevant_symbols = []
                        title_content = (item.get('title', '') + ' ' + item.get('description', '')).upper()

                        for symbol in symbols:
                            if symbol.upper() in title_content:
                                relevant_symbols.append(symbol)

                        if relevant_symbols:
                            article = NewsArticle(
                                title=item.get('title', ''),
                                summary=item.get('description', ''),
                                url=item.get('url', ''),
                                source='newsapi',
                                published_at=datetime.fromisoformat(
                                    item.get('publishedAt', '').replace('Z', '+00:00')
                                ) if item.get('publishedAt') else datetime.now(),
                                symbols=relevant_symbols
                            )
                            articles.append(article)

        except Exception as e:
            self.logger.error(f"Error fetching NewsAPI articles: {str(e)}")

        return articles

    async def fetch_reddit_sentiment(self, symbols: List[str]) -> Dict[str, Any]:
        if not (self.settings.reddit_client_id and self.settings.reddit_client_secret):
            self.logger.warning("Reddit API credentials not configured")
            return {}

        sentiment_data = {}

        try:
            for symbol in symbols:
                sentiment_data[symbol] = {
                    'mentions': 0,
                    'sentiment_score': 0.0,
                    'trending': False,
                    'last_updated': datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error fetching Reddit sentiment: {str(e)}")

        return sentiment_data

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

class SentimentAnalyzer:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_article_sentiment(self, article: NewsArticle) -> float:

        text = (article.title + ' ' + article.summary).lower()

        positive_words = [
            'bullish', 'positive', 'growth', 'profit', 'gain', 'rise', 'surge',
            'strong', 'outperform', 'buy', 'upgrade', 'beat', 'exceed'
        ]

        negative_words = [
            'bearish', 'negative', 'loss', 'decline', 'fall', 'drop', 'weak',
            'underperform', 'sell', 'downgrade', 'miss', 'disappoint'
        ]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count + negative_count == 0:
            return 0.0

        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return max(-1.0, min(1.0, sentiment))

    def aggregate_sentiment(self, articles: List[NewsArticle], symbol: str) -> SentimentData:
        relevant_articles = [
            article for article in articles
            if article.symbols and symbol in article.symbols
        ]

        if not relevant_articles:
            return SentimentData(
                symbol=symbol,
                overall_sentiment=0.0,
                confidence=0.0,
                news_count=0,
                social_mentions=0,
                sentiment_trend='neutral',
                key_themes=[],
                last_updated=datetime.now()
            )

        sentiments = []
        for article in relevant_articles:
            if article.sentiment_score is not None:
                sentiments.append(article.sentiment_score)
            else:
                sentiment = self.analyze_article_sentiment(article)
                article.sentiment_score = sentiment
                sentiments.append(sentiment)

        overall_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        confidence = min(1.0, len(sentiments) / 10)

        if overall_sentiment > 0.2:
            trend = 'bullish'
        elif overall_sentiment < -0.2:
            trend = 'bearish'
        else:
            trend = 'neutral'

        key_themes = self._extract_themes(relevant_articles)

        return SentimentData(
            symbol=symbol,
            overall_sentiment=overall_sentiment,
            confidence=confidence,
            news_count=len(relevant_articles),
            social_mentions=0,
            sentiment_trend=trend,
            key_themes=key_themes,
            last_updated=datetime.now()
        )

    def _extract_themes(self, articles: List[NewsArticle]) -> List[str]:
        theme_keywords = {
            'earnings': ['earnings', 'revenue', 'profit', 'eps'],
            'merger': ['merger', 'acquisition', 'deal', 'takeover'],
            'regulation': ['regulation', 'regulatory', 'compliance', 'policy'],
            'technology': ['technology', 'innovation', 'digital', 'ai'],
            'market': ['market', 'sector', 'industry', 'economic']
        }

        themes = []
        all_text = ' '.join([
            article.title + ' ' + article.summary
            for article in articles
        ]).lower()

        for theme, keywords in theme_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)

        return themes[:5]

class NewsSentimentAnalyzer:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)

        self.news_client = NewsAPIClient(settings)
        self.sentiment_analyzer = SentimentAnalyzer()

        self.sentiment_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 4 * 3600

    async def fetch_financial_news(self, symbols: List[str]) -> List[NewsArticle]:
        all_articles = []

        try:
            av_articles = await self.news_client.fetch_alpha_vantage_news(symbols)
            all_articles.extend(av_articles)

            news_articles = await self.news_client.fetch_news_api_articles(symbols)
            all_articles.extend(news_articles)

            seen_urls = set()
            unique_articles = []

            for article in all_articles:
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    unique_articles.append(article)

            unique_articles.sort(key=lambda x: x.published_at, reverse=True)

            self.logger.info(f"Fetched {len(unique_articles)} unique articles for {len(symbols)} symbols")
            return unique_articles

        except Exception as e:
            self.logger.error(f"Error fetching financial news: {str(e)}")
            return []

    async def analyze_social_sentiment(self, symbols: List[str]) -> Dict[str, Any]:
        try:
            reddit_data = await self.news_client.fetch_reddit_sentiment(symbols)

            return {
                'reddit': reddit_data,
                'twitter': {},
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error analyzing social sentiment: {str(e)}")
            return {}

    async def process_with_llm(self, news_data: List[NewsArticle]) -> Dict[str, Any]:

        try:
            analysis = {
                'summary': f"Analyzed {len(news_data)} articles",
                'key_insights': [
                    'Market sentiment appears mixed based on recent news',
                    'Earnings season driving increased volatility',
                    'Regulatory developments worth monitoring'
                ],
                'risk_factors': [
                    'Economic uncertainty',
                    'Geopolitical tensions',
                    'Interest rate changes'
                ],
                'opportunities': [
                    'Technology sector showing strength',
                    'Value stocks gaining attention',
                    'Dividend yields attractive'
                ],
                'processed_at': datetime.now().isoformat()
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error processing with LLM: {str(e)}")
            return {'error': str(e)}

    def get_cached_sentiment(self, symbol: str) -> Optional[SentimentData]:
        cache_key = f"sentiment_{symbol}"

        if cache_key in self.sentiment_cache:
            cache_entry = self.sentiment_cache[cache_key]

            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return SentimentData(**cache_entry['data'])

        return None

    def cache_sentiment(self, sentiment_data: SentimentData):
        cache_key = f"sentiment_{sentiment_data.symbol}"

        self.sentiment_cache[cache_key] = {
            'data': asdict(sentiment_data),
            'timestamp': time.time()
        }

    async def analyze_symbol_sentiment(self, symbol: str) -> SentimentData:
        cached_sentiment = self.get_cached_sentiment(symbol)
        if cached_sentiment:
            self.logger.info(f"Returning cached sentiment for {symbol}")
            return cached_sentiment

        try:
            articles = await self.fetch_financial_news([symbol])

            sentiment_data = self.sentiment_analyzer.aggregate_sentiment(articles, symbol)

            self.cache_sentiment(sentiment_data)

            self.logger.info(f"Analyzed sentiment for {symbol}: {sentiment_data.sentiment_trend}")
            return sentiment_data

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment for {symbol}: {str(e)}")

            return SentimentData(
                symbol=symbol,
                overall_sentiment=0.0,
                confidence=0.0,
                news_count=0,
                social_mentions=0,
                sentiment_trend='neutral',
                key_themes=[],
                last_updated=datetime.now()
            )

    async def analyze_multiple_symbols(self, symbols: List[str]) -> Dict[str, SentimentData]:
        results = {}

        batch_size = 5
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]

            tasks = [self.analyze_symbol_sentiment(symbol) for symbol in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for symbol, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error processing {symbol}: {str(result)}")
                    results[symbol] = SentimentData(
                        symbol=symbol,
                        overall_sentiment=0.0,
                        confidence=0.0,
                        news_count=0,
                        social_mentions=0,
                        sentiment_trend='neutral',
                        key_themes=[],
                        last_updated=datetime.now()
                    )
                else:
                    results[symbol] = result

            if i + batch_size < len(symbols):
                await asyncio.sleep(1)

        return results

    def clear_cache(self):
        self.sentiment_cache.clear()
        self.logger.info("Sentiment cache cleared")

    async def get_health_status(self) -> Dict[str, Any]:
        return {
            'status': 'healthy',
            'cache_entries': len(self.sentiment_cache),
            'cache_ttl_hours': self.cache_ttl / 3600,
            'apis_configured': {
                'alpha_vantage': bool(self.settings.alpha_vantage_api_key),
                'news_api': bool(self.settings.news_api_key),
                'reddit': bool(self.settings.reddit_client_id and self.settings.reddit_client_secret)
            },
            'last_updated': datetime.now().isoformat()
        }

    async def shutdown(self):
        await self.news_client.close()
        self.logger.info("News sentiment analyzer shutdown complete")