"""
Logging decorators and context managers for AI Trading Assistant.

Provides easy-to-use decorators for automatic logging of AI operations.
"""

import asyncio
import functools
import time
import traceback
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, Optional
import psutil
import os

from .audit_logger import get_audit_logger, AuditEvent, PerformanceMetrics


def audit_operation(
    component: str,
    operation: str = None,
    event_type: str = "OPERATION",
    log_input: bool = True,
    log_output: bool = True,
    track_performance: bool = True
):
    """
    Decorator for automatic audit logging of AI operations.
    
    Args:
        component: Component name (e.g., "PredictionEngine")
        operation: Operation name (defaults to function name)
        event_type: Type of event (PREDICTION, RECOMMENDATION, etc.)
        log_input: Whether to log input parameters
        log_output: Whether to log output data
        track_performance: Whether to track performance metrics
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            audit_logger = get_audit_logger()
            event_id = str(uuid.uuid4())
            op_name = operation or func.__name__
            start_time = time.time()
            
            # Get process info for performance tracking
            process = psutil.Process(os.getpid()) if track_performance else None
            start_memory = process.memory_info().rss / 1024 / 1024 if process else None  # MB
            start_cpu = process.cpu_percent() if process else None
            
            # Prepare input data
            input_data = {}
            if log_input:
                # Log args (skip 'self' for methods)
                if args and hasattr(args[0], '__class__'):
                    input_data['args'] = [str(arg) for arg in args[1:]]  # Skip self
                else:
                    input_data['args'] = [str(arg) for arg in args]
                    
                # Log kwargs (sanitize sensitive data)
                input_data['kwargs'] = {
                    k: _sanitize_value(v) for k, v in kwargs.items()
                }
            
            success = True
            error_message = None
            output_data = {}
            
            try:
                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Log output data
                if log_output and result is not None:
                    output_data = _sanitize_output(result)
                
                return result
                
            except Exception as e:
                success = False
                error_message = str(e)
                
                # Log the error
                await audit_logger.log_error(
                    component=component,
                    operation=op_name,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=traceback.format_exc(),
                    input_data=input_data
                )
                
                raise
                
            finally:
                # Calculate duration and performance metrics
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                
                end_memory = process.memory_info().rss / 1024 / 1024 if process else None  # MB
                end_cpu = process.cpu_percent() if process else None
                
                # Create audit event
                audit_event = AuditEvent(
                    event_id=event_id,
                    event_type=event_type,
                    component=component,
                    operation=op_name,
                    input_data=input_data,
                    output_data=output_data,
                    metadata={
                        'function_name': func.__name__,
                        'module': func.__module__
                    },
                    timestamp=datetime.now(),
                    duration_ms=duration_ms,
                    success=success,
                    error_message=error_message
                )
                
                # Log audit event
                await audit_logger.log_audit_event(audit_event)
                
                # Log performance metrics
                if track_performance:
                    performance_metrics = PerformanceMetrics(
                        component=component,
                        operation=op_name,
                        duration_ms=duration_ms,
                        memory_usage_mb=end_memory,
                        cpu_usage_percent=end_cpu,
                        timestamp=datetime.now()
                    )
                    await audit_logger.log_performance_metrics(performance_metrics)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions, create async wrapper
            return asyncio.create_task(async_wrapper(*args, **kwargs))
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class AuditContext:
    """
    Context manager for manual audit logging.
    
    Usage:
        async with AuditContext("PredictionEngine", "generate_predictions") as ctx:
            # Your code here
            ctx.add_input_data({"symbol": "AAPL"})
            result = await some_operation()
            ctx.add_output_data({"prediction": result})
    """
    
    def __init__(
        self,
        component: str,
        operation: str,
        event_type: str = "OPERATION",
        track_performance: bool = True
    ):
        self.component = component
        self.operation = operation
        self.event_type = event_type
        self.track_performance = track_performance
        
        self.event_id = str(uuid.uuid4())
        self.input_data = {}
        self.output_data = {}
        self.metadata = {}
        
        self.start_time = None
        self.process = None
        self.start_memory = None
        self.start_cpu = None
        
        self.audit_logger = get_audit_logger()
    
    async def __aenter__(self):
        self.start_time = time.time()
        
        if self.track_performance:
            self.process = psutil.Process(os.getpid())
            self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            self.start_cpu = self.process.cpu_percent()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        duration_ms = (end_time - self.start_time) * 1000
        
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        
        # Calculate performance metrics
        end_memory = None
        end_cpu = None
        if self.track_performance and self.process:
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = self.process.cpu_percent()
        
        # Create audit event
        audit_event = AuditEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            component=self.component,
            operation=self.operation,
            input_data=self.input_data,
            output_data=self.output_data,
            metadata=self.metadata,
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        
        # Log audit event
        await self.audit_logger.log_audit_event(audit_event)
        
        # Log performance metrics
        if self.track_performance:
            performance_metrics = PerformanceMetrics(
                component=self.component,
                operation=self.operation,
                duration_ms=duration_ms,
                memory_usage_mb=end_memory,
                cpu_usage_percent=end_cpu,
                timestamp=datetime.now()
            )
            await self.audit_logger.log_performance_metrics(performance_metrics)
        
        # Log error if one occurred
        if exc_type:
            await self.audit_logger.log_error(
                component=self.component,
                operation=self.operation,
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                stack_trace=traceback.format_exc(),
                input_data=self.input_data
            )
    
    def add_input_data(self, data: Dict[str, Any]):
        """Add input data to the audit log."""
        self.input_data.update(_sanitize_dict(data))
    
    def add_output_data(self, data: Dict[str, Any]):
        """Add output data to the audit log."""
        self.output_data.update(_sanitize_dict(data))
    
    def add_metadata(self, data: Dict[str, Any]):
        """Add metadata to the audit log."""
        self.metadata.update(data)


def _sanitize_value(value: Any) -> Any:
    """Sanitize a value for logging (remove sensitive data, limit size)."""
    if isinstance(value, str):
        # Limit string length
        if len(value) > 1000:
            return value[:1000] + "... [truncated]"
        return value
    elif isinstance(value, (list, tuple)):
        # Limit list/tuple size
        if len(value) > 10:
            return list(value[:10]) + ["... [truncated]"]
        return [_sanitize_value(item) for item in value]
    elif isinstance(value, dict):
        return _sanitize_dict(value)
    elif hasattr(value, '__dict__'):
        # For objects, convert to dict representation
        try:
            return _sanitize_dict(value.__dict__)
        except:
            return str(value)
    else:
        return value


def _sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize a dictionary for logging."""
    sanitized = {}
    for key, value in data.items():
        # Skip sensitive keys
        if any(sensitive in key.lower() for sensitive in ['password', 'token', 'key', 'secret']):
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = _sanitize_value(value)
    return sanitized


def _sanitize_output(result: Any) -> Dict[str, Any]:
    """Sanitize output data for logging."""
    if hasattr(result, '__dict__'):
        return _sanitize_dict(result.__dict__)
    elif isinstance(result, dict):
        return _sanitize_dict(result)
    elif isinstance(result, (list, tuple)):
        return {"result": _sanitize_value(result)}
    else:
        return {"result": _sanitize_value(result)}