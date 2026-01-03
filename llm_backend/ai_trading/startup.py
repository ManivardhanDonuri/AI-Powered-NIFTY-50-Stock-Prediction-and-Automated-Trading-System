"""
Startup initialization for AI Trading Assistant error handling and recovery systems.

This module initializes all error handling, recovery services, and monitoring
components when the application starts.
"""

import asyncio
import logging
from typing import Optional

from .error_handling import get_error_handler, ErrorHandler
from .ollama_recovery import initialize_ollama_recovery, OllamaRecoveryService
from ..services.ollama_service import initialize_ollama_service, OllamaConfig


logger = logging.getLogger(__name__)


class AITradingStartup:
    """
    Startup manager for AI Trading Assistant.
    
    Handles initialization of error handling, recovery services,
    and health monitoring components.
    """
    
    def __init__(self):
        self.error_handler: Optional[ErrorHandler] = None
        self.ollama_recovery: Optional[OllamaRecoveryService] = None
        self.initialized = False
        
    async def initialize(
        self, 
        ollama_config: Optional[OllamaConfig] = None,
        start_monitoring: bool = True
    ) -> bool:
        """
        Initialize all AI Trading Assistant components.
        
        Args:
            ollama_config: Optional Ollama configuration
            start_monitoring: Whether to start background monitoring
            
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing AI Trading Assistant error handling and recovery systems...")
            
            # Initialize error handler
            self.error_handler = get_error_handler()
            logger.info("Error handler initialized")
            
            # Initialize Ollama service
            ollama_initialized = await initialize_ollama_service(ollama_config)
            if ollama_initialized:
                logger.info("Ollama service initialized successfully")
            else:
                logger.warning("Ollama service initialization failed - will use fallback mode")
            
            # Initialize Ollama recovery service
            if start_monitoring:
                self.ollama_recovery = await initialize_ollama_recovery()
                logger.info("Ollama recovery service initialized and monitoring started")
            
            # Perform initial health checks
            await self._perform_initial_health_checks()
            
            # Set up periodic maintenance tasks
            if start_monitoring:
                asyncio.create_task(self._periodic_maintenance())
            
            self.initialized = True
            logger.info("AI Trading Assistant initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Trading Assistant: {str(e)}")
            return False
    
    async def shutdown(self):
        """Gracefully shutdown all services."""
        try:
            logger.info("Shutting down AI Trading Assistant services...")
            
            if self.ollama_recovery:
                await self.ollama_recovery.stop_monitoring()
                logger.info("Ollama recovery service stopped")
            
            if self.error_handler:
                await self.error_handler.cleanup_expired_cache()
                logger.info("Error handler cache cleaned up")
            
            logger.info("AI Trading Assistant shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
    
    async def _perform_initial_health_checks(self):
        """Perform initial health checks on all components."""
        try:
            logger.info("Performing initial health checks...")
            
            # Check Ollama service
            if self.ollama_recovery:
                health_status = await self.ollama_recovery.check_health()
                logger.info(f"Ollama health status: {health_status.state.value}")
                
                if health_status.state.value == 'UNAVAILABLE':
                    logger.warning("Ollama service unavailable - attempting recovery")
                    recovery_result = await self.ollama_recovery.attempt_recovery()
                    if recovery_result:
                        logger.info("Ollama recovery successful")
                    else:
                        logger.warning("Ollama recovery failed - will operate in fallback mode")
            
            # Test error handler
            if self.error_handler:
                error_stats = await self.error_handler.get_error_stats()
                logger.info(f"Error handler operational - {error_stats['error_statistics']['total_errors']} total errors tracked")
            
            logger.info("Initial health checks completed")
            
        except Exception as e:
            logger.error(f"Error during initial health checks: {str(e)}")
    
    async def _periodic_maintenance(self):
        """Periodic maintenance tasks."""
        while self.initialized:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Clean up expired cache
                if self.error_handler:
                    await self.error_handler.cleanup_expired_cache()
                
                # Check system health
                if self.ollama_recovery:
                    health_status = await self.ollama_recovery.check_health()
                    
                    # Log performance warnings
                    if health_status.response_time > 10.0:
                        logger.warning(f"Ollama response time high: {health_status.response_time:.2f}s")
                    
                    if health_status.memory_usage > 80.0:
                        logger.warning(f"High memory usage: {health_status.memory_usage:.1f}%")
                    
                    if health_status.error_rate > 0.3:
                        logger.warning(f"High error rate: {health_status.error_rate:.1%}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic maintenance: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def get_system_status(self) -> dict:
        """Get comprehensive system status."""
        try:
            status = {
                'initialized': self.initialized,
                'timestamp': asyncio.get_event_loop().time(),
                'components': {}
            }
            
            if self.error_handler:
                error_stats = await self.error_handler.get_error_stats()
                status['components']['error_handler'] = {
                    'status': 'operational',
                    'statistics': error_stats['error_statistics']
                }
            
            if self.ollama_recovery:
                ollama_metrics = await self.ollama_recovery.get_performance_metrics()
                status['components']['ollama_recovery'] = {
                    'status': 'operational',
                    'health': ollama_metrics['health_status'],
                    'statistics': ollama_metrics['statistics']
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                'initialized': self.initialized,
                'error': str(e),
                'timestamp': asyncio.get_event_loop().time()
            }


# Global startup manager
_startup_manager: Optional[AITradingStartup] = None


def get_startup_manager() -> AITradingStartup:
    """Get or create global startup manager."""
    global _startup_manager
    if _startup_manager is None:
        _startup_manager = AITradingStartup()
    return _startup_manager


async def initialize_ai_trading_system(
    ollama_config: Optional[OllamaConfig] = None,
    start_monitoring: bool = True
) -> bool:
    """
    Initialize the complete AI Trading Assistant system.
    
    Args:
        ollama_config: Optional Ollama configuration
        start_monitoring: Whether to start background monitoring
        
    Returns:
        bool: True if initialization successful
    """
    startup_manager = get_startup_manager()
    return await startup_manager.initialize(ollama_config, start_monitoring)


async def shutdown_ai_trading_system():
    """Shutdown the AI Trading Assistant system."""
    startup_manager = get_startup_manager()
    await startup_manager.shutdown()


async def get_ai_trading_system_status() -> dict:
    """Get comprehensive AI Trading Assistant system status."""
    startup_manager = get_startup_manager()
    return await startup_manager.get_system_status()