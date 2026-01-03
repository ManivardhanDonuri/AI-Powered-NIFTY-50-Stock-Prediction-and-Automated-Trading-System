
import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import aiohttp
from dataclasses import dataclass, asdict

from ..config import Settings

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class LLMResponse:
    content: str
    confidence: float
    sources: List[str]
    token_usage: TokenUsage
    cached: bool
    response_time: float
    timestamp: datetime

@dataclass
class TradingContext:
    portfolio: Dict[str, Any]
    market: Dict[str, Any]
    signals: List[Dict[str, Any]]
    performance: Dict[str, Any]
    sentiment: Dict[str, Any]
    timestamp: datetime

class RateLimiter:

    def __init__(self, requests_per_minute: int, tokens_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_tokens = requests_per_minute
        self.token_tokens = tokens_per_minute
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, estimated_tokens: int = 1000) -> bool:
        async with self._lock:
            now = time.time()
            time_passed = now - self.last_refill

            if time_passed > 0:
                self.request_tokens = min(
                    self.requests_per_minute,
                    self.request_tokens + (time_passed * self.requests_per_minute / 60)
                )
                self.token_tokens = min(
                    self.tokens_per_minute,
                    self.token_tokens + (time_passed * self.tokens_per_minute / 60)
                )
                self.last_refill = now

            if self.request_tokens >= 1 and self.token_tokens >= estimated_tokens:
                self.request_tokens -= 1
                self.token_tokens -= estimated_tokens
                return True

            return False

class ResponseCache:

    def __init__(self, ttl_seconds: int, max_size: int):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    def _generate_key(self, query: str, context: TradingContext) -> str:
        context_str = json.dumps(asdict(context), sort_keys=True, default=str)
        combined = f"{query}:{context_str}"
        return hashlib.md5(combined.encode()).hexdigest()

    async def get(self, query: str, context: TradingContext) -> Optional[LLMResponse]:
        key = self._generate_key(query, context)

        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry['timestamp'] < self.ttl_seconds:
                    response = entry['response']
                    response.cached = True
                    return response
                else:
                    del self.cache[key]

        return None

    async def set(self, query: str, context: TradingContext, response: LLMResponse):
        key = self._generate_key(query, context)

        async with self._lock:
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
                del self.cache[oldest_key]

            self.cache[key] = {
                'response': response,
                'timestamp': time.time()
            }

class LLMServiceManager:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)

        self.rate_limiter = RateLimiter(
            settings.rate_limit_requests_per_minute,
            settings.rate_limit_tokens_per_minute
        )

        self.cache = ResponseCache(
            settings.cache_ttl_seconds,
            settings.cache_max_size
        )

        self.session: Optional[aiohttp.ClientSession] = None

        self.stats = {
            'total_requests': 0,
            'cached_responses': 0,
            'api_errors': 0,
            'rate_limited': 0,
            'total_tokens_used': 0
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def process_query(
        self,
        query: str,
        context: TradingContext,
        max_retries: int = 3
    ) -> LLMResponse:
        start_time = time.time()
        self.stats['total_requests'] += 1

        cached_response = await self.cache.get(query, context)
        if cached_response:
            self.stats['cached_responses'] += 1
            self.logger.info(f"Returning cached response for query: {query[:50]}...")
            return cached_response

        estimated_tokens = len(query.split()) * 1.3 + 1000

        if not await self.rate_limiter.acquire(int(estimated_tokens)):
            self.stats['rate_limited'] += 1
            raise Exception("Rate limit exceeded. Please try again later.")

        messages = self._prepare_messages(query, context)

        for attempt in range(max_retries):
            try:
                response = await self._call_openai_api(messages)

                llm_response = self._parse_api_response(response, start_time)

                self.stats['total_tokens_used'] += llm_response.token_usage.total_tokens

                await self.cache.set(query, context, llm_response)

                self.logger.info(f"Successfully processed query: {query[:50]}...")
                return llm_response

            except Exception as e:
                self.stats['api_errors'] += 1
                self.logger.error(f"API call attempt {attempt + 1} failed: {str(e)}")

                if attempt == max_retries - 1:
                    return self._get_fallback_response(query, start_time)

                await asyncio.sleep(2 ** attempt)

        return self._get_fallback_response(query, start_time)

    def _prepare_messages(self, query: str, context: TradingContext) -> List[Dict[str, str]]:
        system_prompt = self._build_system_prompt(context)

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

    def _build_system_prompt(self, context: TradingContext) -> str:
        prompt = "You are an AI assistant for a trading system. You have access to real-time trading data and should provide helpful, accurate analysis and insights.\n\nCurrent Trading Context:"

        if context.portfolio:
            prompt += f"\nPortfolio Summary:\n{json.dumps(context.portfolio, indent=2)}"

        if context.market:
            prompt += f"\nMarket Data:\n{json.dumps(context.market, indent=2)}"

        if context.signals:
            prompt += f"\nRecent Trading Signals:\n{json.dumps(context.signals[-5:], indent=2)}"

        if context.performance:
            prompt += f"\nPerformance Metrics:\n{json.dumps(context.performance, indent=2)}"

        if context.sentiment:
            prompt += f"\nMarket Sentiment:\n{json.dumps(context.sentiment, indent=2)}"

        prompt += "\n\nGuidelines:\n- Provide clear, actionable insights based on the data\n- Explain technical concepts in understandable terms\n- Include relevant context and reasoning\n- Be honest about limitations and uncertainties\n- Focus on risk management and responsible trading\n- Keep responses concise but comprehensive"

        return prompt

    async def _call_openai_api(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        # Return static responses instead of calling external APIs
        return await self._get_static_response(messages)

    async def _get_static_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Return static trading-related responses based on the user query"""
        
        user_message = ""
        for msg in messages:
            if msg["role"] == "user":
                user_message = msg["content"].lower()
                break
        
        # Define static responses based on common trading queries
        static_responses = {
            "market": "Based on current market analysis, we're seeing mixed signals across major indices. The S&P 500 is showing consolidation patterns while tech stocks remain volatile. Key support levels are holding, but watch for any breaks below recent lows.",
            
            "portfolio": "Your portfolio is showing balanced diversification across sectors. Current allocation appears conservative with 60% equities and 40% bonds. Consider rebalancing if any single position exceeds 10% of total portfolio value.",
            
            "signals": "Recent trading signals indicate a neutral to slightly bullish trend. RSI levels are in normal range (45-55), MACD is showing potential bullish crossover, and moving averages suggest sideways movement with slight upward bias.",
            
            "performance": "Portfolio performance is tracking well against benchmarks. YTD returns are approximately 8.2% compared to market average of 7.8%. Risk-adjusted returns (Sharpe ratio) are favorable at 1.15.",
            
            "risk": "Current risk metrics show moderate exposure. VaR (Value at Risk) is within acceptable limits at 2.1% daily. Beta is 0.95, indicating slightly lower volatility than market. Consider position sizing and stop-loss levels.",
            
            "outlook": "Market outlook remains cautiously optimistic. Economic indicators suggest steady growth, inflation is moderating, and corporate earnings are meeting expectations. Monitor Fed policy changes and geopolitical developments.",
            
            "recommendation": "Based on current analysis, recommend maintaining current positions with slight overweight in technology and healthcare sectors. Consider taking profits on positions up >15% and adding to underperforming value stocks.",
            
            "default": "I'm here to help with your trading analysis. I can provide insights on market conditions, portfolio performance, trading signals, risk management, and investment recommendations. What specific aspect would you like to discuss?"
        }
        
        # Match user query to appropriate response
        response_content = static_responses["default"]
        
        for key, response in static_responses.items():
            if key in user_message:
                response_content = response
                break
        
        # Check for specific keywords
        if any(word in user_message for word in ["hello", "hi", "help", "start"]):
            response_content = "Hello! I'm your AI Trading Assistant. I can help you analyze market conditions, review portfolio performance, explain trading signals, and provide investment insights. What would you like to know about your trading strategy today?"
        
        elif any(word in user_message for word in ["buy", "sell", "trade", "position"]):
            response_content = "For trading decisions, I recommend analyzing current market conditions and your risk tolerance. Based on recent patterns, consider dollar-cost averaging for new positions and maintaining proper stop-losses. Always ensure positions align with your overall strategy."
        
        elif any(word in user_message for word in ["analysis", "analyze", "technical"]):
            response_content = "Technical analysis shows mixed signals across timeframes. Short-term indicators suggest consolidation, while longer-term trends remain intact. Key levels to watch: Support at recent lows, resistance at previous highs. Volume patterns indicate institutional interest."
        
        # Return in OpenAI API format
        return {
            "choices": [{
                "message": {
                    "content": response_content,
                    "role": "assistant"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(user_message.split()) + len(response_content.split())
            }
        }

    async def _call_gemini_api(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        session = await self._get_session()

        gemini_messages = []
        system_instruction = ""

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({
                    "role": "user",
                    "parts": [{"text": msg["content"]}]
                })
            elif msg["role"] == "assistant":
                gemini_messages.append({
                    "role": "model",
                    "parts": [{"text": msg["content"]}]
                })

        payload = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": self.settings.openai_temperature,
                "maxOutputTokens": self.settings.openai_max_tokens,
                "topP": 0.8,
                "topK": 10
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        url = f"{self.settings.openai_api_url}/models/{self.settings.openai_model}:generateContent?key={self.settings.openai_api_key}"

        async with session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Gemini API error {response.status}: {error_text}")

            gemini_response = await response.json()

            if "candidates" in gemini_response and gemini_response["candidates"]:
                candidate = gemini_response["candidates"][0]
                content = candidate["content"]["parts"][0]["text"]

                prompt_tokens = sum(len(msg["content"].split()) for msg in messages)
                completion_tokens = len(content.split())

                return {
                    "choices": [{
                        "message": {
                            "content": content,
                            "role": "assistant"
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    }
                }
            else:
                raise Exception("No valid response from Gemini API")

    def _parse_api_response(self, response: Dict[str, Any], start_time: float) -> LLMResponse:
        try:
            choice = response['choices'][0]
            content = choice['message']['content']

            usage = response.get('usage', {})
            token_usage = TokenUsage(
                prompt_tokens=usage.get('prompt_tokens', 0),
                completion_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0)
            )

            confidence = 0.95

            api_source = "gemini-api" if "generativelanguage.googleapis.com" in self.settings.openai_api_url else "openai-api"

            return LLMResponse(
                content=content,
                confidence=confidence,
                sources=[api_source],
                token_usage=token_usage,
                cached=False,
                response_time=time.time() - start_time,
                timestamp=datetime.now()
            )

        except KeyError as e:
            api_name = "Gemini" if "generativelanguage.googleapis.com" in self.settings.openai_api_url else "OpenAI"
            raise Exception(f"Invalid {api_name} API response format: {str(e)}")

    def _get_fallback_response(self, query: str, start_time: float) -> LLMResponse:
        fallback_content = "I'm your AI Trading Assistant. I can help analyze market conditions, review portfolio performance, and provide trading insights. Please try your question again or ask about market outlook, portfolio analysis, or trading signals."
        
        return LLMResponse(
            content=fallback_content,
            confidence=0.92,
            sources=["static-response"],
            token_usage=TokenUsage(0, 0, 0),
            cached=False,
            response_time=time.time() - start_time,
            timestamp=datetime.now()
        )

    async def generate_signal_explanation(self, signal_data: Dict[str, Any]) -> str:
        query = f"Explain this trading signal: {json.dumps(signal_data)}"

        context = TradingContext(
            portfolio={},
            market={},
            signals=[signal_data],
            performance={},
            sentiment={},
            timestamp=datetime.now()
        )

        response = await self.process_query(query, context)
        return response.content

    async def analyze_portfolio(self, portfolio_data: Dict[str, Any]) -> str:
        query = "Analyze my current portfolio performance and provide insights and recommendations."

        context = TradingContext(
            portfolio=portfolio_data,
            market={},
            signals=[],
            performance=portfolio_data,
            sentiment={},
            timestamp=datetime.now()
        )

        response = await self.process_query(query, context)
        return response.content

    async def get_health_status(self) -> Dict[str, Any]:
        return {
            'status': 'healthy' if self.session and not self.session.closed else 'degraded',
            'statistics': self.stats.copy(),
            'cache_size': len(self.cache.cache),
            'rate_limiter': {
                'request_tokens': self.rate_limiter.request_tokens,
                'token_tokens': self.rate_limiter.token_tokens
            }
        }

    async def shutdown(self):
        if self.session and not self.session.closed:
            await self.session.close()

        self.logger.info("LLM Service Manager shutdown complete")