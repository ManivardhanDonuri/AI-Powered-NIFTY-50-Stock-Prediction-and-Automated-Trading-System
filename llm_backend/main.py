
import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import get_settings
from .routers import chat, ai_insights, health
from .services.llm_service import LLMServiceManager
from .services.trading_context_provider import TradingContextProvider
from .websocket.chat_websocket import ChatWebSocketHandler
from .database.chat_db import ChatDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

llm_service: LLMServiceManager = None
context_provider: TradingContextProvider = None
chat_websocket_handler: ChatWebSocketHandler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_service, context_provider, chat_websocket_handler

    logger.info("Starting LLM Backend Service...")

    try:
        settings = get_settings()

        context_provider = TradingContextProvider(settings.trading_config_path)
        llm_service = LLMServiceManager(settings)

        chat_db = ChatDatabase()
        chat_websocket_handler = ChatWebSocketHandler(llm_service, context_provider, chat_db)

        app.state.llm_service = llm_service
        app.state.context_provider = context_provider
        app.state.chat_websocket_handler = chat_websocket_handler

        logger.info("LLM Backend Service started successfully")

    except Exception as e:
        logger.error(f"Failed to start LLM Backend Service: {str(e)}")
        raise

    yield

    logger.info("Shutting down LLM Backend Service...")

    if llm_service:
        await llm_service.shutdown()

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

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
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