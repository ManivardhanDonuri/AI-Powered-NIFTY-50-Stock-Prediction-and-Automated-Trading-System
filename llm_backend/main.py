
import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import get_settings
from .routers import chat, ai_insights, health, ai_trading
from .services.llm_service import LLMServiceManager
from .services.ollama_service import initialize_ollama_service, get_ollama_service, OllamaConfig
from .services.trading_context_provider import TradingContextProvider
from .websocket.chat_websocket import ChatWebSocketHandler
from .database.chat_db import ChatDatabase
from .ai_trading.startup import initialize_ai_trading_system, shutdown_ai_trading_system
from .ai_trading.error_handling import AITradingError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

llm_service: LLMServiceManager = None
context_provider: TradingContextProvider = None
chat_websocket_handler: ChatWebSocketHandler = None
ollama_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_service, context_provider, chat_websocket_handler, ollama_service

    logger.info("Starting LLM Backend Service...")

    try:
        settings = get_settings()

        # Initialize Ollama service
        ollama_config = OllamaConfig(
            model_name=settings.ollama_model,
            host=settings.ollama_host,
            port=settings.ollama_port,
            timeout=settings.ollama_timeout,
            max_tokens=settings.ollama_max_tokens,
            temperature=settings.ollama_temperature
        )
        
        ollama_initialized = await initialize_ollama_service(ollama_config)
        
        # Initialize AI Trading Assistant error handling and recovery systems
        ai_trading_initialized = await initialize_ai_trading_system(
            ollama_config=ollama_config,
            start_monitoring=True
        )
        
        if ai_trading_initialized:
            logger.info("AI Trading Assistant error handling and recovery systems initialized")
        else:
            logger.warning("AI Trading Assistant initialization failed - some features may be limited")
        if ollama_initialized:
            logger.info("Ollama service initialized successfully")
            ollama_service = get_ollama_service()
        else:
            logger.warning("Ollama service initialization failed, continuing with fallback")

        context_provider = TradingContextProvider(settings.trading_config_path)
        llm_service = LLMServiceManager(settings)

        chat_db = ChatDatabase()
        chat_websocket_handler = ChatWebSocketHandler(llm_service, context_provider, chat_db)

        app.state.llm_service = llm_service
        app.state.ollama_service = ollama_service
        app.state.context_provider = context_provider
        app.state.chat_db = chat_db
        app.state.chat_websocket_handler = chat_websocket_handler

        logger.info("LLM Backend Service started successfully")

    except Exception as e:
        logger.error(f"Failed to start LLM Backend Service: {str(e)}")
        raise

    yield

    logger.info("Shutting down LLM Backend Service...")

    # Shutdown AI Trading Assistant systems
    try:
        await shutdown_ai_trading_system()
        logger.info("AI Trading Assistant systems shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down AI Trading Assistant: {str(e)}")

    if llm_service:
        await llm_service.shutdown()
        
    if ollama_service:
        await ollama_service.shutdown()

    logger.info("LLM Backend Service shutdown complete")

app = FastAPI(
    title="Trading System LLM Backend",
    description="AI-powered backend for trading system with LLM integration",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(ai_insights.router, prefix="/api/v1/ai-insights", tags=["ai-insights"])
app.include_router(ai_trading.router, prefix="/api/v1/ai-trading", tags=["ai-trading"])

@app.exception_handler(AITradingError)
async def ai_trading_exception_handler(request: Request, exc: AITradingError):
    """Handle AI Trading specific errors."""
    logger.error(f"AI Trading Error: {exc.message} (Category: {exc.category.value}, Severity: {exc.severity.value})")
    
    status_code = 500 if exc.severity.value in ['HIGH', 'CRITICAL'] else 400
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.message,
            "category": exc.category.value,
            "severity": exc.severity.value,
            "timestamp": exc.timestamp.isoformat(),
            "fallback_available": True,
            "component": exc.context.component if exc.context else None
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    if not hasattr(app.state, 'chat_websocket_handler'):
        await websocket.close(code=1011, reason="Service not available")
        return

    await app.state.chat_websocket_handler.handle_websocket(websocket, user_id)

@app.get("/")
async def root():
    return {
        "service": "Trading System LLM Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "websocket": "/ws/chat/{user_id}"
    }

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "llm_backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )