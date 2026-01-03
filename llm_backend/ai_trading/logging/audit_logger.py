"""
Audit Logger for AI Trading Assistant.
"""

import asyncio
import logging
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AuditEvent:
    """Audit event data structure."""
    event_id: str
    event_type: str
    component: str
    operation: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Performance tracking data structure."""
    component: str
    operation: str
    duration_ms: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AuditLogger:
    """Comprehensive audit logging system for AI Trading Assistant."""
    
    def __init__(self, db_path: str = "llm_chat.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        self._initialized = False
        self.logger.info("Audit Logger initialized")

    async def _initialize_db(self):
        """Initialize audit database tables."""
        if self._initialized:
            return
            
        async with self._lock:
            if self._initialized:
                return
                
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Create predictions tracking table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id TEXT PRIMARY KEY,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        predicted_price REAL NOT NULL,
                        confidence_score REAL NOT NULL,
                        actual_price REAL,
                        accuracy REAL,
                        model_ensemble TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        validated_at TIMESTAMP
                    )
                ''')

                conn.commit()
                conn.close()
                
                self._initialized = True
                self.logger.info("Audit database initialized successfully")

            except Exception as e:
                self.logger.error(f"Error initializing audit database: {str(e)}")
                raise

    async def _execute_query(self, query: str, params: tuple = (), fetch: bool = False):
        """Execute database query with proper error handling."""
        await self._initialize_db()
        
        async with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(query, params)

                if fetch:
                    result = cursor.fetchall()
                    conn.close()
                    return result
                else:
                    conn.commit()
                    conn.close()
                    return cursor.rowcount

            except Exception as e:
                self.logger.error(f"Database query error: {str(e)}")
                if 'conn' in locals():
                    conn.close()
                raise

    async def log_audit_event(self, event: AuditEvent):
        """Log an audit event."""
        try:
            # For now, just log to console
            self.logger.info(f"Audit event: {event.event_id} - {event.operation}")
        except Exception as e:
            self.logger.error(f"Error logging audit event: {str(e)}")

    async def log_prediction(
        self, 
        symbol: str, 
        timeframe: str, 
        predicted_price: float, 
        confidence_score: float,
        model_ensemble: List[str]
    ):
        """Log a prediction for accuracy tracking."""
        try:
            prediction_id = str(uuid.uuid4())
            query = '''
                INSERT INTO predictions 
                (id, symbol, timeframe, predicted_price, confidence_score, model_ensemble)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (
                prediction_id,
                symbol,
                timeframe,
                predicted_price,
                confidence_score,
                json.dumps(model_ensemble)
            )
            
            await self._execute_query(query, params)
            self.logger.debug(f"Logged prediction: {symbol} {timeframe} -> {predicted_price}")
            
        except Exception as e:
            self.logger.error(f"Error logging prediction: {str(e)}")

    async def log_performance_metrics(self, metrics: PerformanceMetrics):
        """Log performance metrics."""
        try:
            # For now, just log to console
            self.logger.info(f"Performance: {metrics.component}.{metrics.operation} - {metrics.duration_ms}ms")
        except Exception as e:
            self.logger.error(f"Error logging performance metrics: {str(e)}")

    async def log_error(
        self,
        component: str,
        operation: str,
        error_type: str,
        error_message: str,
        stack_trace: str = None,
        input_data: Dict[str, Any] = None
    ):
        """Log an error."""
        try:
            # For now, just log to console
            self.logger.error(f"Error in {component}.{operation}: {error_message}")
        except Exception as e:
            self.logger.error(f"Error logging error: {str(e)}")

    async def update_prediction_accuracy(self, symbol: str, timeframe: str, actual_price: float):
        """Update prediction with actual price and calculate accuracy."""
        try:
            # For now, just log the update
            self.logger.info(f"Updating prediction accuracy for {symbol} {timeframe}: {actual_price}")
        except Exception as e:
            self.logger.error(f"Error updating prediction accuracy: {str(e)}")

    async def get_prediction_accuracy(
        self, 
        symbol: str = None, 
        timeframe: str = None, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get prediction accuracy statistics."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Base query conditions
            conditions = ["created_at >= ?"]
            params = [cutoff_date]
            
            if symbol:
                conditions.append("symbol = ?")
                params.append(symbol)
            if timeframe:
                conditions.append("timeframe = ?")
                params.append(timeframe)
            
            where_clause = " AND ".join(conditions)
            
            # Get accuracy statistics
            query = f'''
                SELECT 
                    symbol,
                    timeframe,
                    COUNT(*) as total_predictions,
                    COUNT(CASE WHEN actual_price IS NOT NULL THEN 1 END) as validated_predictions,
                    AVG(CASE WHEN actual_price IS NOT NULL THEN accuracy END) as avg_accuracy,
                    MIN(CASE WHEN actual_price IS NOT NULL THEN accuracy END) as min_accuracy,
                    MAX(CASE WHEN actual_price IS NOT NULL THEN accuracy END) as max_accuracy,
                    AVG(confidence_score) as avg_confidence
                FROM predictions 
                WHERE {where_clause}
                GROUP BY symbol, timeframe
                ORDER BY symbol, timeframe
            '''
            
            result = await self._execute_query(query, tuple(params), fetch=True)
            
            accuracy_by_symbol_timeframe = []
            for row in result:
                accuracy_by_symbol_timeframe.append({
                    'symbol': row['symbol'],
                    'timeframe': row['timeframe'],
                    'total_predictions': row['total_predictions'],
                    'validated_predictions': row['validated_predictions'],
                    'avg_accuracy': row['avg_accuracy'],
                    'min_accuracy': row['min_accuracy'],
                    'max_accuracy': row['max_accuracy'],
                    'avg_confidence': row['avg_confidence']
                })
            
            return {
                'accuracy_by_symbol_timeframe': accuracy_by_symbol_timeframe,
                'overall_statistics': {},
                'analysis_period_days': days,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting prediction accuracy: {str(e)}")
            return {
                'accuracy_by_symbol_timeframe': [],
                'overall_statistics': {},
                'analysis_period_days': days,
                'timestamp': datetime.now().isoformat()
            }

    async def get_performance_statistics(
        self, 
        component: str = None, 
        days: int = 7
    ) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'performance_by_component': [],
            'analysis_period_days': days,
            'timestamp': datetime.now().isoformat()
        }

    async def get_error_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get error summary statistics."""
        return {
            'errors_by_type': [],
            'analysis_period_days': days,
            'timestamp': datetime.now().isoformat()
        }

    async def get_audit_trail(
        self,
        component: str = None,
        operation: str = None,
        event_type: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit trail with filtering."""
        return []

    async def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, int]:
        """Clean up old audit data."""
        return {'records_deleted': 0}


# Global audit logger instance
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger