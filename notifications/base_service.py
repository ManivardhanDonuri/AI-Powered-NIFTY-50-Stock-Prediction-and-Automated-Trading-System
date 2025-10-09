"""
Base notification service interface

Defines the common interface that all notification services must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class NotificationMessage:
    """Data structure for notification messages."""
    message_id: str
    platform: str
    recipient: str
    content: str
    priority: str = 'normal'
    created_at: datetime = None
    attempts: int = 0
    status: str = 'pending'
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass 
class SignalNotificationData:
    """Data structure for trading signal notifications."""
    symbol: str
    signal_type: str
    price: float
    confidence: float
    ml_probability: float
    reason: str
    timestamp: datetime
    model_predictions: Dict[str, float] = None
    
    def __post_init__(self):
        if self.model_predictions is None:
            self.model_predictions = {}

class BaseNotificationService(ABC):
    """Abstract base class for notification services."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the notification service with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_enabled = config.get('enabled', False)
        self.rate_limit = config.get('rate_limit', 30)
        self._last_message_time = None
        self._message_count = 0
        
    @abstractmethod
    def send_message(self, message: NotificationMessage) -> bool:
        """
        Send a notification message.
        
        Args:
            message: NotificationMessage object containing message details
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate the connection to the notification service.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_service_name(self) -> str:
        """
        Get the name of the notification service.
        
        Returns:
            str: Service name (e.g., 'telegram', 'whatsapp')
        """
        pass
    
    def is_rate_limited(self) -> bool:
        """
        Check if the service is currently rate limited.
        
        Returns:
            bool: True if rate limited, False otherwise
        """
        now = datetime.now()
        
        # Reset counter if more than a minute has passed
        if (self._last_message_time is None or 
            (now - self._last_message_time).seconds >= 60):
            self._message_count = 0
            self._last_message_time = now
            
        return self._message_count >= self.rate_limit
    
    def increment_message_count(self):
        """Increment the message count for rate limiting."""
        self._message_count += 1
        self._last_message_time = datetime.now()
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of the notification service.
        
        Returns:
            dict: Health status information
        """
        return {
            'service': self.get_service_name(),
            'enabled': self.is_enabled,
            'rate_limited': self.is_rate_limited(),
            'message_count': self._message_count,
            'last_message_time': self._last_message_time
        }