"""
Ollama Service Recovery and Health Management.

This module provides specialized error recovery, health monitoring, and fallback
mechanisms specifically for the Ollama local LLM service.
"""

import asyncio
import logging
import time
import subprocess
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json

from .error_handling import ErrorHandler, OllamaError, ErrorContext, ErrorSeverity


class OllamaServiceState(Enum):
    """Ollama service states."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    RECOVERING = "RECOVERING"
    FAILED = "FAILED"


@dataclass
class OllamaHealthStatus:
    """Ollama service health status."""
    state: OllamaServiceState
    response_time: float
    model_loaded: bool
    memory_usage: float
    cpu_usage: float
    error_rate: float
    last_successful_request: Optional[datetime]
    last_error: Optional[str]
    uptime: timedelta
    timestamp: datetime


class OllamaRecoveryService:
    """
    Specialized recovery service for Ollama LLM.
    
    Provides health monitoring, automatic recovery, performance optimization,
    and graceful degradation for the local Ollama service.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url
        self.error_handler = ErrorHandler()
        
        # Health monitoring
        self.health_status = OllamaHealthStatus(
            state=OllamaServiceState.UNAVAILABLE,
            response_time=0.0,
            model_loaded=False,
            memory_usage=0.0,
            cpu_usage=0.0,
            error_rate=0.0,
            last_successful_request=None,
            last_error=None,
            uptime=timedelta(0),
            timestamp=datetime.now()
        )
        
        # Recovery configuration
        self.recovery_config = {
            'max_retry_attempts': 3,
            'retry_delay': 5,  # seconds
            'health_check_interval': 30,  # seconds
            'performance_threshold': 10.0,  # seconds
            'memory_threshold': 80.0,  # percentage
            'error_rate_threshold': 0.3,  # 30%
            'recovery_timeout': 300  # 5 minutes
        }
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'recovery_attempts': 0,
            'successful_recoveries': 0,
            'average_response_time': 0.0,
            'uptime_percentage': 0.0
        }
        
        # Background tasks
        self._health_monitor_task = None
        self._recovery_task = None
        self._is_monitoring = False

    async def start_monitoring(self):
        """Start background health monitoring."""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
        self.logger.info("Ollama health monitoring started")

    async def stop_monitoring(self):
        """Stop background health monitoring."""
        self._is_monitoring = False
        
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
        
        if self._recovery_task:
            self._recovery_task.cancel()
            try:
                await self._recovery_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Ollama health monitoring stopped")

    async def check_health(self) -> OllamaHealthStatus:
        """
        Perform comprehensive health check of Ollama service.
        
        Returns:
            OllamaHealthStatus: Current health status
        """
        start_time = time.time()
        
        try:
            # Test basic connectivity
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        response_time = time.time() - start_time
                        data = await response.json()
                        
                        # Check if models are loaded
                        models = data.get('models', [])
                        model_loaded = len(models) > 0
                        
                        # Get system metrics
                        memory_usage, cpu_usage = await self._get_system_metrics()
                        
                        # Calculate error rate
                        error_rate = self._calculate_error_rate()
                        
                        # Determine service state
                        state = self._determine_service_state(
                            response_time, model_loaded, memory_usage, cpu_usage, error_rate
                        )
                        
                        self.health_status = OllamaHealthStatus(
                            state=state,
                            response_time=response_time,
                            model_loaded=model_loaded,
                            memory_usage=memory_usage,
                            cpu_usage=cpu_usage,
                            error_rate=error_rate,
                            last_successful_request=datetime.now(),
                            last_error=None,
                            uptime=self._calculate_uptime(),
                            timestamp=datetime.now()
                        )
                        
                        return self.health_status
                    
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )
        
        except Exception as e:
            error_message = str(e)
            self.health_status = OllamaHealthStatus(
                state=OllamaServiceState.UNAVAILABLE,
                response_time=time.time() - start_time,
                model_loaded=False,
                memory_usage=0.0,
                cpu_usage=0.0,
                error_rate=1.0,
                last_successful_request=self.health_status.last_successful_request,
                last_error=error_message,
                uptime=timedelta(0),
                timestamp=datetime.now()
            )
            
            self.logger.error(f"Ollama health check failed: {error_message}")
            return self.health_status

    async def attempt_recovery(self) -> bool:
        """
        Attempt to recover Ollama service.
        
        Returns:
            bool: True if recovery successful, False otherwise
        """
        if self._recovery_task and not self._recovery_task.done():
            self.logger.info("Recovery already in progress")
            return False
        
        self._recovery_task = asyncio.create_task(self._recovery_process())
        return await self._recovery_task

    async def _recovery_process(self) -> bool:
        """Execute the recovery process."""
        self.stats['recovery_attempts'] += 1
        self.logger.info("Starting Ollama service recovery")
        
        try:
            # Step 1: Check if Ollama process is running
            if not await self._is_ollama_process_running():
                self.logger.info("Ollama process not running, attempting to start")
                if not await self._start_ollama_process():
                    self.logger.error("Failed to start Ollama process")
                    return False
            
            # Step 2: Wait for service to be ready
            if not await self._wait_for_service_ready():
                self.logger.error("Ollama service did not become ready")
                return False
            
            # Step 3: Load default model if needed
            if not await self._ensure_model_loaded():
                self.logger.warning("Could not load default model, but service is running")
            
            # Step 4: Verify recovery with test request
            if await self._verify_recovery():
                self.stats['successful_recoveries'] += 1
                self.logger.info("Ollama service recovery successful")
                return True
            else:
                self.logger.error("Recovery verification failed")
                return False
        
        except Exception as e:
            self.logger.error(f"Recovery process failed: {str(e)}")
            return False

    async def _is_ollama_process_running(self) -> bool:
        """Check if Ollama process is running."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'ollama' in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking Ollama process: {str(e)}")
            return False

    async def _start_ollama_process(self) -> bool:
        """Attempt to start Ollama process."""
        try:
            # Try to start Ollama service
            process = await asyncio.create_subprocess_exec(
                'ollama', 'serve',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Give it time to start
            await asyncio.sleep(5)
            
            # Check if process is still running
            if process.returncode is None:
                self.logger.info("Ollama process started successfully")
                return True
            else:
                stdout, stderr = await process.communicate()
                self.logger.error(f"Ollama failed to start: {stderr.decode()}")
                return False
        
        except FileNotFoundError:
            self.logger.error("Ollama executable not found. Please ensure Ollama is installed.")
            return False
        except Exception as e:
            self.logger.error(f"Error starting Ollama process: {str(e)}")
            return False

    async def _wait_for_service_ready(self, timeout: int = 60) -> bool:
        """Wait for Ollama service to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=2)) as response:
                        if response.status == 200:
                            return True
            except:
                pass
            
            await asyncio.sleep(2)
        
        return False

    async def _ensure_model_loaded(self) -> bool:
        """Ensure a default model is loaded."""
        try:
            # Try to load a default model (llama3.2 or llama2)
            models_to_try = ['llama3.2', 'llama2', 'mistral']
            
            for model in models_to_try:
                try:
                    async with aiohttp.ClientSession() as session:
                        payload = {
                            "model": model,
                            "prompt": "Hello",
                            "stream": False
                        }
                        
                        async with session.post(
                            f"{self.base_url}/api/generate",
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            if response.status == 200:
                                self.logger.info(f"Model {model} loaded successfully")
                                return True
                except:
                    continue
            
            self.logger.warning("Could not load any default model")
            return False
        
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return False

    async def _verify_recovery(self) -> bool:
        """Verify that recovery was successful with a test request."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "llama3.2",
                    "prompt": "Test recovery",
                    "stream": False
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        
        except Exception as e:
            self.logger.error(f"Recovery verification failed: {str(e)}")
            return False

    async def _get_system_metrics(self) -> tuple[float, float]:
        """Get system memory and CPU usage."""
        try:
            # Get overall system metrics
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            return memory.percent, cpu
        
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {str(e)}")
            return 0.0, 0.0

    def _calculate_error_rate(self) -> float:
        """Calculate current error rate."""
        total = self.stats['total_requests']
        if total == 0:
            return 0.0
        
        failed = self.stats['failed_requests']
        return failed / total

    def _determine_service_state(
        self, 
        response_time: float, 
        model_loaded: bool, 
        memory_usage: float, 
        cpu_usage: float, 
        error_rate: float
    ) -> OllamaServiceState:
        """Determine service state based on metrics."""
        if response_time > self.recovery_config['performance_threshold']:
            return OllamaServiceState.DEGRADED
        
        if memory_usage > self.recovery_config['memory_threshold']:
            return OllamaServiceState.DEGRADED
        
        if error_rate > self.recovery_config['error_rate_threshold']:
            return OllamaServiceState.DEGRADED
        
        if not model_loaded:
            return OllamaServiceState.DEGRADED
        
        return OllamaServiceState.HEALTHY

    def _calculate_uptime(self) -> timedelta:
        """Calculate service uptime."""
        if self.health_status.last_successful_request:
            return datetime.now() - self.health_status.last_successful_request
        return timedelta(0)

    async def _health_monitor_loop(self):
        """Background health monitoring loop."""
        while self._is_monitoring:
            try:
                await self.check_health()
                
                # Trigger recovery if needed
                if self.health_status.state == OllamaServiceState.UNAVAILABLE:
                    if not self._recovery_task or self._recovery_task.done():
                        asyncio.create_task(self.attempt_recovery())
                
                await asyncio.sleep(self.recovery_config['health_check_interval'])
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitor error: {str(e)}")
                await asyncio.sleep(self.recovery_config['health_check_interval'])

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            'health_status': {
                'state': self.health_status.state.value,
                'response_time': self.health_status.response_time,
                'model_loaded': self.health_status.model_loaded,
                'memory_usage': self.health_status.memory_usage,
                'cpu_usage': self.health_status.cpu_usage,
                'error_rate': self.health_status.error_rate,
                'uptime': str(self.health_status.uptime),
                'last_error': self.health_status.last_error
            },
            'statistics': self.stats.copy(),
            'configuration': self.recovery_config.copy(),
            'timestamp': datetime.now().isoformat()
        }

    async def optimize_performance(self) -> Dict[str, Any]:
        """Attempt to optimize Ollama performance."""
        optimizations = []
        
        try:
            # Check memory usage
            if self.health_status.memory_usage > 70:
                optimizations.append("High memory usage detected - consider restarting service")
            
            # Check response time
            if self.health_status.response_time > 5.0:
                optimizations.append("Slow response time - consider using smaller model")
            
            # Check error rate
            if self.health_status.error_rate > 0.2:
                optimizations.append("High error rate - service may need restart")
            
            return {
                'optimizations_suggested': optimizations,
                'current_performance': {
                    'response_time': self.health_status.response_time,
                    'memory_usage': self.health_status.memory_usage,
                    'error_rate': self.health_status.error_rate
                },
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Performance optimization check failed: {str(e)}")
            return {
                'error': str(e),
                'optimizations_suggested': [],
                'timestamp': datetime.now().isoformat()
            }

    def update_request_stats(self, success: bool, response_time: float):
        """Update request statistics."""
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        # Update average response time
        total_successful = self.stats['successful_requests']
        if total_successful > 0:
            current_avg = self.stats['average_response_time']
            self.stats['average_response_time'] = (
                (current_avg * (total_successful - 1) + response_time) / total_successful
            )


# Global recovery service instance
_recovery_service: Optional[OllamaRecoveryService] = None


def get_ollama_recovery_service() -> OllamaRecoveryService:
    """Get or create global Ollama recovery service instance."""
    global _recovery_service
    if _recovery_service is None:
        _recovery_service = OllamaRecoveryService()
    return _recovery_service


async def initialize_ollama_recovery(base_url: str = "http://localhost:11434") -> OllamaRecoveryService:
    """Initialize and start Ollama recovery service."""
    global _recovery_service
    _recovery_service = OllamaRecoveryService(base_url)
    await _recovery_service.start_monitoring()
    return _recovery_service