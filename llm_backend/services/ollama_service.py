"""
Ollama Service for AI Trading Assistant

This service provides local LLM capabilities using Ollama for privacy and control.
Integrates with the existing trading system architecture.
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import aiohttp

from ..config import Settings
from ..ai_trading.error_handling import get_error_handler, handle_errors, OllamaError, ErrorContext
from ..ai_trading.ollama_recovery import get_ollama_recovery_service


@dataclass
class OllamaConfig:
    model_name: str = "llama3.2"
    host: str = "localhost"
    port: int = 11434
    timeout: int = 60  # Increased timeout for complex prompts
    max_tokens: int = 4000
    temperature: float = 0.7


@dataclass
class OllamaResponse:
    content: str
    model_used: str
    tokens_used: int
    response_time: float
    success: bool
    error_message: Optional[str] = None


class OllamaService:
    """
    Service for interfacing with local Ollama LLM instance.
    Provides natural language processing and rationale generation for trading analysis.
    """

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = f"http://{self.config.host}:{self.config.port}"
        
        # Error handling and recovery
        self.error_handler = get_error_handler()
        self.recovery_service = get_ollama_recovery_service()
        
        # Statistics tracking
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'average_response_time': 0.0,
            'total_tokens_used': 0
        }

    async def initialize_connection(
        self, 
        model_name: str = "llama3.2", 
        host: str = "localhost:11434"
    ) -> bool:
        """
        Initialize connection to local Ollama instance.
        
        Args:
            model_name: Name of the Ollama model to use
            host: Host and port for Ollama service
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Parse host and port
            if ":" in host:
                host_part, port_part = host.split(":")
                self.config.host = host_part
                self.config.port = int(port_part)
            else:
                self.config.host = host
                
            self.config.model_name = model_name
            self.base_url = f"http://{self.config.host}:{self.config.port}"
            
            # Test connection
            is_healthy = await self.health_check()
            if is_healthy:
                self.logger.info(f"Successfully connected to Ollama at {self.base_url}")
                return True
            else:
                self.logger.error(f"Failed to connect to Ollama at {self.base_url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing Ollama connection: {str(e)}")
            return False

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for API calls."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def health_check(self) -> bool:
        """
        Check if Ollama service is running and accessible.
        
        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            session = await self._get_session()
            async with session.get(self.base_url) as response:
                if response.status == 200:
                    text = await response.text()
                    return "Ollama is running" in text
                return False
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    @handle_errors(component="OllamaService", operation="generate_rationale")
    async def generate_rationale(
        self, 
        recommendation: Dict[str, Any], 
        market_context: Dict[str, Any]
    ) -> str:
        """
        Generate detailed rationale for trading recommendations using local LLM.
        
        Args:
            recommendation: Trading recommendation data
            market_context: Current market context and data
            
        Returns:
            str: Generated rationale explanation
        """
        try:
            # Check service health before proceeding
            health_status = await self.recovery_service.check_health()
            if health_status.state.value in ['UNAVAILABLE', 'FAILED']:
                raise OllamaError(
                    f"Ollama service is {health_status.state.value}",
                    ErrorContext(component="OllamaService", operation="generate_rationale")
                )
            
            # Build prompt for rationale generation
            prompt = self._build_rationale_prompt(recommendation, market_context)
            
            # Generate response using Ollama
            response = await self._generate_response(prompt)
            
            if response.success:
                return response.content
            else:
                raise OllamaError(
                    f"Rationale generation failed: {response.error_message}",
                    ErrorContext(component="OllamaService", operation="generate_rationale")
                )
                
        except OllamaError:
            raise  # Re-raise Ollama errors for proper handling
        except Exception as e:
            raise OllamaError(
                f"Unexpected error in rationale generation: {str(e)}",
                ErrorContext(component="OllamaService", operation="generate_rationale")
            )

    @handle_errors(component="OllamaService", operation="process_natural_language_query")
    async def process_natural_language_query(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> str:
        """
        Process natural language queries about trading and market analysis.
        
        Args:
            query: User's natural language query
            context: Trading context and data
            
        Returns:
            str: Generated response to the query
        """
        try:
            # Check service health
            health_status = await self.recovery_service.check_health()
            if health_status.state.value in ['UNAVAILABLE', 'FAILED']:
                raise OllamaError(
                    f"Ollama service is {health_status.state.value}",
                    ErrorContext(component="OllamaService", operation="process_natural_language_query")
                )
            
            # Build prompt for query processing
            prompt = self._build_query_prompt(query, context)
            
            # Generate response using Ollama
            response = await self._generate_response(prompt)
            
            if response.success:
                return response.content
            else:
                raise OllamaError(
                    f"Query processing failed: {response.error_message}",
                    ErrorContext(component="OllamaService", operation="process_natural_language_query")
                )
                
        except OllamaError:
            raise  # Re-raise Ollama errors for proper handling
        except Exception as e:
            raise OllamaError(
                f"Unexpected error in query processing: {str(e)}",
                ErrorContext(component="OllamaService", operation="process_natural_language_query")
            )

    @handle_errors(component="OllamaService", operation="explain_analysis")
    async def explain_analysis(
        self, 
        analysis_data: Dict[str, Any], 
        user_level: str = "intermediate"
    ) -> str:
        """
        Explain complex trading analysis in understandable terms.
        
        Args:
            analysis_data: Analysis results to explain
            user_level: User's experience level (beginner, intermediate, advanced)
            
        Returns:
            str: Clear explanation of the analysis
        """
        try:
            # Check service health
            health_status = await self.recovery_service.check_health()
            if health_status.state.value in ['UNAVAILABLE', 'FAILED']:
                raise OllamaError(
                    f"Ollama service is {health_status.state.value}",
                    ErrorContext(component="OllamaService", operation="explain_analysis")
                )
            
            # Build prompt for analysis explanation
            prompt = self._build_explanation_prompt(analysis_data, user_level)
            
            # Generate response using Ollama
            response = await self._generate_response(prompt)
            
            if response.success:
                return response.content
            else:
                raise OllamaError(
                    f"Analysis explanation failed: {response.error_message}",
                    ErrorContext(component="OllamaService", operation="explain_analysis")
                )
                
        except OllamaError:
            raise  # Re-raise Ollama errors for proper handling
        except Exception as e:
            raise OllamaError(
                f"Unexpected error in analysis explanation: {str(e)}",
                ErrorContext(component="OllamaService", operation="explain_analysis")
            )

    async def _generate_response(self, prompt: str) -> OllamaResponse:
        """
        Generate response from Ollama API.
        
        Args:
            prompt: Input prompt for the model
            
        Returns:
            OllamaResponse: Response from Ollama
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            session = await self._get_session()
            
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            url = f"{self.base_url}/api/generate"
            
            async with session.post(url, json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    self.stats['successful_requests'] += 1
                    self.stats['total_response_time'] += response_time
                    self.stats['average_response_time'] = (
                        self.stats['total_response_time'] / self.stats['successful_requests']
                    )
                    
                    # Get actual token counts from Ollama response
                    prompt_tokens = result.get('prompt_eval_count', 0)
                    completion_tokens = result.get('eval_count', 0)
                    total_tokens = prompt_tokens + completion_tokens
                    self.stats['total_tokens_used'] += total_tokens
                    
                    # Update recovery service stats
                    self.recovery_service.update_request_stats(True, response_time)
                    
                    return OllamaResponse(
                        content=result.get('response', ''),
                        model_used=result.get('model', self.config.model_name),
                        tokens_used=total_tokens,
                        response_time=response_time,
                        success=True
                    )
                else:
                    error_text = await response.text()
                    self.stats['failed_requests'] += 1
                    self.recovery_service.update_request_stats(False, response_time)
                    
                    self.logger.error(f"Ollama API error {response.status}: {error_text}")
                    
                    return OllamaResponse(
                        content="",
                        model_used=self.config.model_name,
                        tokens_used=0,
                        response_time=response_time,
                        success=False,
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.stats['failed_requests'] += 1
            self.recovery_service.update_request_stats(False, response_time)
            
            self.logger.error(f"Ollama API call failed: {str(e)}")
            
            # Trigger recovery attempt if connection-related error
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                asyncio.create_task(self.recovery_service.attempt_recovery())
            
            return OllamaResponse(
                content="",
                model_used=self.config.model_name,
                tokens_used=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )

    def _build_rationale_prompt(
        self, 
        recommendation: Dict[str, Any], 
        market_context: Dict[str, Any]
    ) -> str:
        """Build prompt for generating trading recommendation rationale."""
        symbol = recommendation.get('symbol', 'Unknown')
        action = recommendation.get('action', 'HOLD')
        confidence = recommendation.get('confidence', 0)
        target_price = recommendation.get('target_price', 0)
        
        prompt = f"""Generate a trading rationale for {symbol}:

Action: {action}
Confidence: {confidence:.1%}
Target Price: ${target_price}

Market Context: {market_context.get('market_trend', 'neutral')} trend

Provide a brief rationale covering:
1. Technical factors
2. Market conditions
3. Risk considerations
4. Expected outcome

Keep response concise and actionable."""
        
        return prompt

    def _build_query_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Build prompt for processing natural language queries."""
        prompt = f"""You are an AI Trading Assistant. Answer this trading question:

Question: {query}

Context: {context.get('sector', 'general market')} - {context.get('market_condition', 'normal')} conditions

Provide a helpful response with:
- Market insights
- Actionable advice
- Risk considerations

Keep response concise."""
        
        return prompt

    def _build_explanation_prompt(
        self, 
        analysis_data: Dict[str, Any], 
        user_level: str
    ) -> str:
        """Build prompt for explaining complex analysis."""
        level_map = {
            "beginner": "simple terms",
            "intermediate": "standard trading terms", 
            "advanced": "technical language"
        }
        
        level_desc = level_map.get(user_level, "standard trading terms")
        
        # Extract key metrics
        rsi = analysis_data.get('rsi', 'N/A')
        macd = analysis_data.get('macd', 'N/A')
        trend = analysis_data.get('moving_averages', 'N/A')
        
        prompt = f"""Explain this trading analysis in {level_desc}:

RSI: {rsi}
MACD: {macd}
Trend: {trend}

Explain what this means for a {user_level} trader:
1. What the indicators show
2. Trading implications
3. Next steps

Keep explanation appropriate for {user_level} level."""
        
        return prompt

    def _get_fallback_rationale(self, recommendation: Dict[str, Any]) -> str:
        """Provide fallback rationale when Ollama is unavailable."""
        action = recommendation.get('action', 'HOLD')
        symbol = recommendation.get('symbol', 'Unknown')
        confidence = recommendation.get('confidence', 0)
        
        return f"""Trading Recommendation Analysis for {symbol}:

Action: {action}
Confidence: {confidence:.1%}

This recommendation is based on technical analysis and current market conditions. 
The {action.lower()} signal suggests favorable risk-reward characteristics at current levels.

Key factors considered:
- Technical indicator alignment
- Market sentiment analysis
- Risk management principles
- Portfolio optimization

Note: Ollama service is currently unavailable. This is a simplified analysis.
Please verify with additional research before making trading decisions."""

    def _get_fallback_query_response(self, query: str) -> str:
        """Provide fallback response when Ollama is unavailable."""
        return f"""I'm your AI Trading Assistant, but I'm currently running in limited mode as the local language model is unavailable.

Your query: "{query}"

I can still help with basic trading analysis and market insights. For detailed natural language processing and complex analysis, please ensure the Ollama service is running.

Common topics I can assist with:
- Market analysis and trends
- Portfolio performance review
- Trading signal interpretation
- Risk management strategies

Please try your query again once the local language model is available."""

    def _get_fallback_explanation(self, analysis_data: Dict[str, Any]) -> str:
        """Provide fallback explanation when Ollama is unavailable."""
        return """Analysis Summary:

The provided data contains trading analysis results. While I cannot provide detailed explanations due to the local language model being unavailable, here are the key components:

- Technical indicators and signals
- Market performance metrics
- Risk assessment factors
- Portfolio allocation data

For detailed explanations tailored to your experience level, please ensure the Ollama service is running and try again.

Basic interpretation guidelines:
- Higher confidence scores indicate stronger signals
- Risk metrics help assess position sizing
- Performance data shows historical effectiveness"""

    async def get_stats(self) -> Dict[str, Any]:
        """Get service statistics and performance metrics."""
        return {
            'service_status': 'healthy' if await self.health_check() else 'degraded',
            'model_name': self.config.model_name,
            'base_url': self.base_url,
            'statistics': self.stats.copy(),
            'config': {
                'host': self.config.host,
                'port': self.config.port,
                'timeout': self.config.timeout,
                'max_tokens': self.config.max_tokens,
                'temperature': self.config.temperature
            }
        }

    async def shutdown(self):
        """Clean shutdown of the service."""
        if self.session and not self.session.closed:
            await self.session.close()
        self.logger.info("Ollama Service shutdown complete")


# Global instance for easy access
_ollama_service: Optional[OllamaService] = None


def get_ollama_service() -> OllamaService:
    """Get or create global Ollama service instance."""
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service


async def initialize_ollama_service(config: Optional[OllamaConfig] = None) -> bool:
    """Initialize the global Ollama service."""
    global _ollama_service
    _ollama_service = OllamaService(config)
    return await _ollama_service.initialize_connection()