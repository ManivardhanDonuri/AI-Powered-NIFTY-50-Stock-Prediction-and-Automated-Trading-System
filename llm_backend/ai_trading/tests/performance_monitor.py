"""
Performance Monitoring for AI Trading Assistant Integration Tests

This module provides real-time performance monitoring during integration tests
to track system resource usage, response times, and identify bottlenecks.
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import psutil
import threading
from collections import deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int
    response_times: List[float]
    error_count: int
    request_count: int


@dataclass
class ComponentMetrics:
    """Component-specific performance metrics."""
    component_name: str
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    throughput_per_second: float


class PerformanceMonitor:
    """Real-time performance monitoring system."""
    
    def __init__(self, monitoring_interval: float = 1.0, history_size: int = 300):
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Performance data storage
        self.metrics_history: deque = deque(maxlen=history_size)
        self.component_metrics: Dict[str, ComponentMetrics] = {}
        self.response_times: deque = deque(maxlen=1000)
        self.error_count = 0
        self.request_count = 0
        
        # System baseline
        self.baseline_metrics: Optional[PerformanceMetrics] = None
        
        # Monitoring state
        self.start_time = None
        self.last_disk_io = None
        self.last_network_io = None
        
        # Alerts and thresholds
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'response_time_ms': 5000.0,
            'error_rate': 0.1
        }
        self.alerts: List[Dict[str, Any]] = []
    
    def start_monitoring(self):
        """Start performance monitoring in background thread."""
        if self.is_monitoring:
            logger.warning("Performance monitoring already running")
            return
        
        self.is_monitoring = True
        self.start_time = datetime.now()
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        # Capture baseline metrics
        self._capture_baseline()
        
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("Performance monitoring stopped")
    
    def _capture_baseline(self):
        """Capture baseline system metrics."""
        try:
            metrics = self._collect_system_metrics()
            self.baseline_metrics = metrics
            logger.info("Baseline metrics captured")
        except Exception as e:
            logger.error(f"Failed to capture baseline metrics: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop running in background thread."""
        while self.is_monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Check for alerts
                self._check_alerts(metrics)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics."""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        if self.last_disk_io:
            disk_read_mb = (disk_io.read_bytes - self.last_disk_io.read_bytes) / (1024 * 1024)
            disk_write_mb = (disk_io.write_bytes - self.last_disk_io.write_bytes) / (1024 * 1024)
        else:
            disk_read_mb = 0
            disk_write_mb = 0
        self.last_disk_io = disk_io
        
        # Network I/O
        network_io = psutil.net_io_counters()
        if self.last_network_io:
            network_sent_mb = (network_io.bytes_sent - self.last_network_io.bytes_sent) / (1024 * 1024)
            network_recv_mb = (network_io.bytes_recv - self.last_network_io.bytes_recv) / (1024 * 1024)
        else:
            network_sent_mb = 0
            network_recv_mb = 0
        self.last_network_io = network_io
        
        # Network connections
        try:
            connections = len(psutil.net_connections())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            connections = 0
        
        # Recent response times
        recent_response_times = list(self.response_times)[-100:]  # Last 100 response times
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_connections=connections,
            response_times=recent_response_times,
            error_count=self.error_count,
            request_count=self.request_count
        )
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts based on thresholds."""
        alerts = []
        
        # CPU alert
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'HIGH_CPU',
                'message': f'CPU usage {metrics.cpu_percent:.1f}% exceeds threshold {self.alert_thresholds["cpu_percent"]}%',
                'value': metrics.cpu_percent,
                'threshold': self.alert_thresholds['cpu_percent'],
                'timestamp': metrics.timestamp
            })
        
        # Memory alert
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'HIGH_MEMORY',
                'message': f'Memory usage {metrics.memory_percent:.1f}% exceeds threshold {self.alert_thresholds["memory_percent"]}%',
                'value': metrics.memory_percent,
                'threshold': self.alert_thresholds['memory_percent'],
                'timestamp': metrics.timestamp
            })
        
        # Response time alert
        if metrics.response_times:
            avg_response_time = statistics.mean(metrics.response_times) * 1000  # Convert to ms
            if avg_response_time > self.alert_thresholds['response_time_ms']:
                alerts.append({
                    'type': 'HIGH_RESPONSE_TIME',
                    'message': f'Average response time {avg_response_time:.1f}ms exceeds threshold {self.alert_thresholds["response_time_ms"]}ms',
                    'value': avg_response_time,
                    'threshold': self.alert_thresholds['response_time_ms'],
                    'timestamp': metrics.timestamp
                })
        
        # Error rate alert
        if self.request_count > 0:
            error_rate = self.error_count / self.request_count
            if error_rate > self.alert_thresholds['error_rate']:
                alerts.append({
                    'type': 'HIGH_ERROR_RATE',
                    'message': f'Error rate {error_rate:.2%} exceeds threshold {self.alert_thresholds["error_rate"]:.2%}',
                    'value': error_rate,
                    'threshold': self.alert_thresholds['error_rate'],
                    'timestamp': metrics.timestamp
                })
        
        # Add new alerts
        for alert in alerts:
            self.alerts.append(alert)
            logger.warning(f"Performance Alert: {alert['message']}")
    
    def record_request(self, component: str, response_time: float, success: bool):
        """Record a request for performance tracking."""
        self.request_count += 1
        self.response_times.append(response_time)
        
        if not success:
            self.error_count += 1
        
        # Update component metrics
        if component not in self.component_metrics:
            self.component_metrics[component] = ComponentMetrics(
                component_name=component,
                avg_response_time=response_time,
                max_response_time=response_time,
                min_response_time=response_time,
                total_requests=1,
                successful_requests=1 if success else 0,
                failed_requests=0 if success else 1,
                error_rate=0.0 if success else 1.0,
                throughput_per_second=0.0
            )
        else:
            metrics = self.component_metrics[component]
            metrics.total_requests += 1
            
            if success:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1
            
            # Update response time statistics
            metrics.max_response_time = max(metrics.max_response_time, response_time)
            metrics.min_response_time = min(metrics.min_response_time, response_time)
            
            # Calculate running average
            total_time = metrics.avg_response_time * (metrics.total_requests - 1) + response_time
            metrics.avg_response_time = total_time / metrics.total_requests
            
            # Update error rate
            metrics.error_rate = metrics.failed_requests / metrics.total_requests
            
            # Calculate throughput (requests per second)
            if self.start_time:
                elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
                metrics.throughput_per_second = metrics.total_requests / max(elapsed_seconds, 1)
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent performance metrics."""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.metrics_history:
            return {"error": "No performance data available"}
        
        # Calculate summary statistics
        recent_metrics = list(self.metrics_history)[-60:]  # Last 60 data points
        
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        response_times = [rt for m in recent_metrics for rt in m.response_times]
        
        summary = {
            "monitoring_duration_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "overall_error_rate": self.error_count / max(self.request_count, 1),
            "system_metrics": {
                "cpu": {
                    "current": cpu_values[-1] if cpu_values else 0,
                    "average": statistics.mean(cpu_values) if cpu_values else 0,
                    "max": max(cpu_values) if cpu_values else 0,
                    "min": min(cpu_values) if cpu_values else 0
                },
                "memory": {
                    "current": memory_values[-1] if memory_values else 0,
                    "average": statistics.mean(memory_values) if memory_values else 0,
                    "max": max(memory_values) if memory_values else 0,
                    "min": min(memory_values) if memory_values else 0
                }
            },
            "response_times": {
                "count": len(response_times),
                "average_ms": statistics.mean(response_times) * 1000 if response_times else 0,
                "median_ms": statistics.median(response_times) * 1000 if response_times else 0,
                "p95_ms": self._percentile(response_times, 95) * 1000 if response_times else 0,
                "p99_ms": self._percentile(response_times, 99) * 1000 if response_times else 0,
                "max_ms": max(response_times) * 1000 if response_times else 0,
                "min_ms": min(response_times) * 1000 if response_times else 0
            },
            "component_metrics": {
                name: asdict(metrics) for name, metrics in self.component_metrics.items()
            },
            "alerts": self.alerts,
            "baseline_comparison": self._compare_to_baseline() if self.baseline_metrics else None
        }
        
        return summary
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _compare_to_baseline(self) -> Dict[str, Any]:
        """Compare current metrics to baseline."""
        if not self.baseline_metrics or not self.metrics_history:
            return {}
        
        current = self.metrics_history[-1]
        baseline = self.baseline_metrics
        
        return {
            "cpu_change_percent": current.cpu_percent - baseline.cpu_percent,
            "memory_change_percent": current.memory_percent - baseline.memory_percent,
            "memory_change_mb": current.memory_used_mb - baseline.memory_used_mb,
            "connections_change": current.active_connections - baseline.active_connections
        }
    
    def export_metrics(self, filename: str = None) -> str:
        """Export performance metrics to JSON file."""
        if filename is None:
            filename = f"performance_metrics_{int(time.time())}.json"
        
        # Convert metrics to serializable format
        export_data = {
            "summary": self.get_performance_summary(),
            "raw_metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "memory_used_mb": m.memory_used_mb,
                    "disk_io_read_mb": m.disk_io_read_mb,
                    "disk_io_write_mb": m.disk_io_write_mb,
                    "network_sent_mb": m.network_sent_mb,
                    "network_recv_mb": m.network_recv_mb,
                    "active_connections": m.active_connections,
                    "response_times": m.response_times,
                    "error_count": m.error_count,
                    "request_count": m.request_count
                }
                for m in self.metrics_history
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Performance metrics exported to {filename}")
        return filename
    
    def print_live_stats(self):
        """Print live performance statistics to console."""
        if not self.metrics_history:
            print("No performance data available")
            return
        
        current = self.metrics_history[-1]
        summary = self.get_performance_summary()
        
        print("\n" + "="*60)
        print("AI Trading Assistant - Live Performance Monitor")
        print("="*60)
        print(f"Monitoring Duration: {summary['monitoring_duration_seconds']:.1f}s")
        print(f"Total Requests: {summary['total_requests']}")
        print(f"Error Rate: {summary['overall_error_rate']:.2%}")
        print()
        
        print("System Resources:")
        print(f"  CPU: {current.cpu_percent:.1f}% (avg: {summary['system_metrics']['cpu']['average']:.1f}%)")
        print(f"  Memory: {current.memory_percent:.1f}% ({current.memory_used_mb:.1f} MB)")
        print(f"  Active Connections: {current.active_connections}")
        print()
        
        if summary['response_times']['count'] > 0:
            print("Response Times:")
            print(f"  Average: {summary['response_times']['average_ms']:.1f}ms")
            print(f"  Median: {summary['response_times']['median_ms']:.1f}ms")
            print(f"  95th percentile: {summary['response_times']['p95_ms']:.1f}ms")
            print(f"  99th percentile: {summary['response_times']['p99_ms']:.1f}ms")
            print()
        
        if self.component_metrics:
            print("Component Performance:")
            for name, metrics in self.component_metrics.items():
                print(f"  {name}:")
                print(f"    Requests: {metrics.total_requests}")
                print(f"    Avg Response: {metrics.avg_response_time*1000:.1f}ms")
                print(f"    Error Rate: {metrics.error_rate:.2%}")
                print(f"    Throughput: {metrics.throughput_per_second:.1f} req/s")
        
        if self.alerts:
            print(f"\nRecent Alerts ({len(self.alerts)}):")
            for alert in self.alerts[-5:]:  # Show last 5 alerts
                print(f"  {alert['type']}: {alert['message']}")
        
        print("="*60)


# Context manager for easy performance monitoring
class PerformanceMonitorContext:
    """Context manager for performance monitoring during tests."""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def __enter__(self):
        self.monitor.start_monitoring()
        return self.monitor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.monitor.stop_monitoring()


# Decorator for monitoring function performance
def monitor_performance(component_name: str, monitor: PerformanceMonitor):
    """Decorator to monitor function performance."""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    raise
                finally:
                    response_time = time.time() - start_time
                    monitor.record_request(component_name, response_time, success)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    raise
                finally:
                    response_time = time.time() - start_time
                    monitor.record_request(component_name, response_time, success)
            return sync_wrapper
    return decorator


if __name__ == "__main__":
    # Demo performance monitoring
    import asyncio
    
    async def demo_monitoring():
        monitor = PerformanceMonitor(monitoring_interval=0.5)
        
        with PerformanceMonitorContext(monitor):
            print("Starting performance monitoring demo...")
            
            # Simulate some work
            for i in range(10):
                start_time = time.time()
                
                # Simulate API call
                await asyncio.sleep(0.1 + (i * 0.01))  # Increasing response time
                
                response_time = time.time() - start_time
                success = i < 8  # Simulate some failures
                
                monitor.record_request("demo_api", response_time, success)
                
                if i % 3 == 0:
                    monitor.print_live_stats()
                
                await asyncio.sleep(0.5)
            
            # Final summary
            summary = monitor.get_performance_summary()
            print("\nFinal Performance Summary:")
            print(json.dumps(summary, indent=2, default=str))
            
            # Export metrics
            filename = monitor.export_metrics()
            print(f"\nMetrics exported to: {filename}")
    
    asyncio.run(demo_monitoring())