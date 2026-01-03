
import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from ..config import get_settings

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    services: Dict[str, Any]

class StatusResponse(BaseModel):
    service: str
    version: str
    status: str
    timestamp: datetime
    uptime_seconds: float
    configuration: Dict[str, Any]
    services: Dict[str, Any]

_start_time = time.time()

@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    uptime = time.time() - _start_time

    services = {}

    if hasattr(request.app.state, 'llm_service') and request.app.state.llm_service:
        try:
            llm_status = await request.app.state.llm_service.get_health_status()
            services['llm_service'] = llm_status
        except Exception as e:
            services['llm_service'] = {'status': 'error', 'error': str(e)}
    else:
        services['llm_service'] = {'status': 'not_initialized'}

    if hasattr(request.app.state, 'context_provider') and request.app.state.context_provider:
        try:
            context_status = request.app.state.context_provider.get_health_status()
            services['context_provider'] = context_status
        except Exception as e:
            services['context_provider'] = {'status': 'error', 'error': str(e)}
    else:
        services['context_provider'] = {'status': 'not_initialized'}

    # Check Ollama service status
    if hasattr(request.app.state, 'ollama_service') and request.app.state.ollama_service:
        try:
            ollama_status = await request.app.state.ollama_service.get_stats()
            services['ollama_service'] = ollama_status
        except Exception as e:
            services['ollama_service'] = {'status': 'error', 'error': str(e)}
    else:
        services['ollama_service'] = {'status': 'not_initialized'}

    overall_status = "healthy"
    for service_status in services.values():
        if service_status.get('status') in ['error', 'not_initialized']:
            overall_status = "degraded"
            break

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(),
        version="1.0.0",
        uptime_seconds=uptime,
        services=services
    )

@router.get("/status", response_model=StatusResponse)
async def detailed_status(request: Request):
    settings = get_settings()
    uptime = time.time() - _start_time

    services = {}

    if hasattr(request.app.state, 'llm_service') and request.app.state.llm_service:
        try:
            services['llm_service'] = await request.app.state.llm_service.get_health_status()
        except Exception as e:
            services['llm_service'] = {'status': 'error', 'error': str(e)}

    if hasattr(request.app.state, 'context_provider') and request.app.state.context_provider:
        try:
            services['context_provider'] = request.app.state.context_provider.get_health_status()
        except Exception as e:
            services['context_provider'] = {'status': 'error', 'error': str(e)}

    # Check Ollama service status
    if hasattr(request.app.state, 'ollama_service') and request.app.state.ollama_service:
        try:
            services['ollama_service'] = await request.app.state.ollama_service.get_stats()
        except Exception as e:
            services['ollama_service'] = {'status': 'error', 'error': str(e)}

    configuration = {
        'host': settings.host,
        'port': settings.port,
        'debug': settings.debug,
        'ollama_model': settings.ollama_model,
        'ollama_host': settings.ollama_host,
        'ollama_port': settings.ollama_port,
        'rate_limit_rpm': settings.rate_limit_requests_per_minute,
        'cache_ttl_seconds': settings.cache_ttl_seconds,
        'database_url': settings.database_url.split('://')[0] + '://***',
    }

    return StatusResponse(
        service="Trading System LLM Backend",
        version="1.0.0",
        status="running",
        timestamp=datetime.now(),
        uptime_seconds=uptime,
        configuration=configuration,
        services=services
    )

@router.get("/ping")
async def ping():
    return {"message": "pong", "timestamp": datetime.now()}