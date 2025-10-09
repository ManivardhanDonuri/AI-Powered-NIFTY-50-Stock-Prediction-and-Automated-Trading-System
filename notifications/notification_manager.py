"""
Notification Manager - Central coordinator for all notification services

Orchestrates message delivery across Telegram and WhatsApp with user preferences and filtering.
"""

import uuid
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, time as dt_time

from .config import NotificationConfigManager, NotificationConfig
from .telegram_service import TelegramService
from .whatsapp_service import WhatsAppService
from .message_formatter import MessageFormatter
from .delivery_queue import DeliveryQueue
from .base_service import NotificationMessage, SignalNotificationData
from .logger import get_notification_logger, setup_notification_logging

class NotificationManager:
    """Central coordinator for all notification services."""
    
    def __init__(self, config_file: str = 'config.json'):
        """Initialize notification manager."""
        self.config_file = config_file
        
        # Setup logging
        self.logger = setup_notification_logging()
        
        # Load configuration
        self.config_manager = NotificationConfigManager(config_file)
        self.config = self.config_manager.load_config()
        
        # Validate configuration
        validation_result = self.config_manager.validate_config(self.config)
        if not validation_result['valid']:
            self.logger.error(f"Configuration validation failed: {validation_result['errors']}")
            self.config.enabled = False
        
        if validation_result['warnings']:
            for warning in validation_result['warnings']:
                self.logger.warning(warning)
        
        # Initialize components
        self.formatter = MessageFormatter(self.config.preferences)
        self.delivery_queue = DeliveryQueue(self.config.delivery_config)
        
        # Initialize services
        self.services = {}
        self._initialize_services()
        
        # Register services with delivery queue
        self._register_queue_services()
        
        # Start delivery queue processing
        if self.config.enabled:
            self.delivery_queue.start_processing()
        
        self.logger.info(f"Notification manager initialized (enabled: {self.config.enabled})")
    
    def _initialize_services(self):
        """Initialize notification services based on configuration."""
        if not self.config.enabled:
            return
        
        # Initialize Telegram service
        if self.config.telegram_enabled:
            try:
                self.services['telegram'] = TelegramService(self.config.telegram_config)
                if self.services['telegram'].validate_connection():
                    self.logger.info("Telegram service initialized and validated")
                else:
                    self.logger.error("Telegram service validation failed")
                    self.services['telegram'].is_enabled = False
            except Exception as e:
                self.logger.error(f"Failed to initialize Telegram service: {str(e)}")
        
        # Initialize WhatsApp service
        if self.config.whatsapp_enabled:
            try:
                self.services['whatsapp'] = WhatsAppService(self.config.whatsapp_config)
                if self.services['whatsapp'].validate_connection():
                    self.logger.info("WhatsApp service initialized and validated")
                else:
                    self.logger.error("WhatsApp service validation failed")
                    self.services['whatsapp'].is_enabled = False
            except Exception as e:
                self.logger.error(f"Failed to initialize WhatsApp service: {str(e)}")
    
    def _register_queue_services(self):
        """Register services with the delivery queue."""
        for service_name, service in self.services.items():
            if service.is_enabled:
                self.delivery_queue.register_service(
                    service_name, 
                    service.send_message
                )
    
    def send_signal_notification(
        self, 
        signal_data: SignalNotificationData, 
        symbol: str
    ) -> bool:
        """
        Send notification for a trading signal.
        
        Args:
            signal_data: Signal data to send
            symbol: Stock symbol
            
        Returns:
            bool: True if notification was queued successfully
        """
        if not self.config.enabled:
            return False
        
        # Apply user preferences filtering
        if not self._should_send_signal(signal_data, symbol):
            self.logger.info(f"Signal filtered out by preferences: {symbol} {signal_data.signal_type}")
            return False
        
        # Check quiet hours
        if self._is_quiet_hours():
            self.logger.info(f"Signal queued for later due to quiet hours: {symbol}")
            # Queue for after quiet hours
            delay_seconds = self._calculate_quiet_hours_delay()
            return self._queue_signal_messages(signal_data, delay_seconds)
        
        return self._queue_signal_messages(signal_data)
    
    def _queue_signal_messages(
        self, 
        signal_data: SignalNotificationData, 
        delay_seconds: int = 0
    ) -> bool:
        """Queue signal messages for all enabled platforms."""
        success = True
        
        # Send to Telegram if enabled
        if 'telegram' in self.services and self.services['telegram'].is_enabled:
            message = self._create_signal_message(signal_data, 'telegram')
            if not self.delivery_queue.enqueue_message(message, 'normal', delay_seconds):
                success = False
        
        # Send to WhatsApp if enabled and meets confidence threshold
        if 'whatsapp' in self.services and self.services['whatsapp'].is_enabled:
            whatsapp_threshold = self.config.whatsapp_config.get('confidence_threshold', 0.7)
            if signal_data.confidence >= whatsapp_threshold:
                message = self._create_signal_message(signal_data, 'whatsapp')
                message.metadata = {'confidence': signal_data.confidence}
                if not self.delivery_queue.enqueue_message(message, 'high', delay_seconds):
                    success = False
        
        return success
    
    def _create_signal_message(
        self, 
        signal_data: SignalNotificationData, 
        platform: str
    ) -> NotificationMessage:
        """Create a formatted signal message for the specified platform."""
        message_id = f"signal_{signal_data.symbol}_{int(time.time())}_{platform}"
        
        # Format message content
        content = self.formatter.format_signal_message(signal_data, platform)
        
        # Truncate if necessary
        content = self.formatter.truncate_message(content, platform)
        
        # Determine recipient
        if platform == 'telegram':
            recipient = self.config.telegram_config.get('chat_id')
        elif platform == 'whatsapp':
            recipient = self.config.whatsapp_config.get('recipient')
        else:
            recipient = 'unknown'
        
        return NotificationMessage(
            message_id=message_id,
            platform=platform,
            recipient=recipient,
            content=content,
            priority='normal',
            metadata={
                'signal_type': signal_data.signal_type,
                'symbol': signal_data.symbol,
                'confidence': signal_data.confidence
            }
        )
    
    def send_portfolio_summary(self, portfolio_data: Dict[str, Any]) -> bool:
        """
        Send portfolio performance summary.
        
        Args:
            portfolio_data: Portfolio performance data
            
        Returns:
            bool: True if notifications were queued successfully
        """
        if not self.config.enabled:
            return False
        
        success = True
        
        # Send to all enabled platforms
        for platform, service in self.services.items():
            if service.is_enabled:
                message = self._create_portfolio_message(portfolio_data, platform)
                if not self.delivery_queue.enqueue_message(message, 'low'):
                    success = False
        
        return success
    
    def _create_portfolio_message(
        self, 
        portfolio_data: Dict[str, Any], 
        platform: str
    ) -> NotificationMessage:
        """Create a formatted portfolio summary message."""
        message_id = f"portfolio_{int(time.time())}_{platform}"
        
        # Format message content
        content = self.formatter.format_portfolio_summary(portfolio_data, platform)
        
        # Truncate if necessary
        content = self.formatter.truncate_message(content, platform)
        
        # Determine recipient
        if platform == 'telegram':
            recipient = self.config.telegram_config.get('chat_id')
        elif platform == 'whatsapp':
            recipient = self.config.whatsapp_config.get('recipient')
        else:
            recipient = 'unknown'
        
        return NotificationMessage(
            message_id=message_id,
            platform=platform,
            recipient=recipient,
            content=content,
            priority='low',
            metadata={'type': 'portfolio_summary'}
        )
    
    def send_alert(
        self, 
        alert_type: str, 
        message: str, 
        priority: str = 'normal'
    ) -> bool:
        """
        Send system alert notification.
        
        Args:
            alert_type: Type of alert ('error', 'warning', 'info', 'success')
            message: Alert message
            priority: Message priority
            
        Returns:
            bool: True if alert was queued successfully
        """
        if not self.config.enabled:
            return False
        
        success = True
        
        # Send to all enabled platforms
        for platform, service in self.services.items():
            if service.is_enabled:
                alert_message = self._create_alert_message(alert_type, message, platform)
                queue_priority = 'urgent' if alert_type == 'error' else priority
                if not self.delivery_queue.enqueue_message(alert_message, queue_priority):
                    success = False
        
        return success
    
    def _create_alert_message(
        self, 
        alert_type: str, 
        message: str, 
        platform: str
    ) -> NotificationMessage:
        """Create a formatted alert message."""
        message_id = f"alert_{alert_type}_{int(time.time())}_{platform}"
        
        # Format message content
        content = self.formatter.format_alert_message(alert_type, message, platform)
        
        # Determine recipient
        if platform == 'telegram':
            recipient = self.config.telegram_config.get('chat_id')
        elif platform == 'whatsapp':
            recipient = self.config.whatsapp_config.get('recipient')
        else:
            recipient = 'unknown'
        
        return NotificationMessage(
            message_id=message_id,
            platform=platform,
            recipient=recipient,
            content=content,
            priority='normal',
            metadata={'type': 'alert', 'alert_type': alert_type}
        )
    
    def _should_send_signal(self, signal_data: SignalNotificationData, symbol: str) -> bool:
        """
        Check if signal should be sent based on user preferences.
        
        Args:
            signal_data: Signal data
            symbol: Stock symbol
            
        Returns:
            bool: True if signal should be sent
        """
        preferences = self.config.preferences
        
        # Check signal type filter
        allowed_types = preferences.get('signal_types', ['BUY', 'SELL'])
        if signal_data.signal_type not in allowed_types:
            return False
        
        # Check confidence threshold
        min_confidence = preferences.get('min_confidence', 0.0)
        if signal_data.confidence < min_confidence:
            return False
        
        # Check stock symbol filter
        allowed_stocks = preferences.get('stocks', ['ALL'])
        if 'ALL' not in allowed_stocks and symbol not in allowed_stocks:
            return False
        
        return True
    
    def _is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        quiet_hours = self.config.preferences.get('quiet_hours', {})
        if not quiet_hours.get('enabled', False):
            return False
        
        try:
            start_time = dt_time.fromisoformat(quiet_hours.get('start', '22:00'))
            end_time = dt_time.fromisoformat(quiet_hours.get('end', '08:00'))
            current_time = datetime.now().time()
            
            if start_time <= end_time:
                # Same day range (e.g., 14:00 to 18:00)
                return start_time <= current_time <= end_time
            else:
                # Overnight range (e.g., 22:00 to 08:00)
                return current_time >= start_time or current_time <= end_time
                
        except Exception as e:
            self.logger.error(f"Error checking quiet hours: {str(e)}")
            return False
    
    def _calculate_quiet_hours_delay(self) -> int:
        """Calculate delay in seconds until quiet hours end."""
        quiet_hours = self.config.preferences.get('quiet_hours', {})
        if not quiet_hours.get('enabled', False):
            return 0
        
        try:
            end_time = dt_time.fromisoformat(quiet_hours.get('end', '08:00'))
            now = datetime.now()
            
            # Calculate next end time
            end_datetime = datetime.combine(now.date(), end_time)
            if end_datetime <= now:
                # End time is tomorrow
                end_datetime = end_datetime.replace(day=end_datetime.day + 1)
            
            delay_seconds = int((end_datetime - now).total_seconds())
            return max(0, delay_seconds)
            
        except Exception as e:
            self.logger.error(f"Error calculating quiet hours delay: {str(e)}")
            return 0
    
    def test_notifications(self) -> Dict[str, bool]:
        """
        Test all notification services.
        
        Returns:
            dict: Test results for each service
        """
        results = {}
        
        for service_name, service in self.services.items():
            if service.is_enabled:
                try:
                    results[service_name] = service.send_test_message()
                except Exception as e:
                    self.logger.error(f"Error testing {service_name}: {str(e)}")
                    results[service_name] = False
            else:
                results[service_name] = False
        
        return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of notification system.
        
        Returns:
            dict: Health status information
        """
        service_status = {}
        for service_name, service in self.services.items():
            service_status[service_name] = service.get_health_status()
        
        return {
            'enabled': self.config.enabled,
            'services': service_status,
            'queue_status': self.delivery_queue.get_queue_status(),
            'configuration': {
                'telegram_enabled': self.config.telegram_enabled,
                'whatsapp_enabled': self.config.whatsapp_enabled,
                'quiet_hours_enabled': self.config.preferences.get('quiet_hours', {}).get('enabled', False),
                'min_confidence': self.config.preferences.get('min_confidence', 0.0)
            }
        }
    
    def update_preferences(self, new_preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences.
        
        Args:
            new_preferences: New preference settings
            
        Returns:
            bool: True if preferences were updated successfully
        """
        try:
            # Update configuration
            self.config.preferences.update(new_preferences)
            
            # Update formatter configuration
            self.formatter.config = self.config.preferences
            
            self.logger.info("Notification preferences updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating preferences: {str(e)}")
            return False
    
    def shutdown(self):
        """Shutdown notification manager and cleanup resources."""
        self.logger.info("Shutting down notification manager")
        
        # Stop delivery queue processing
        self.delivery_queue.stop_processing()
        
        # Log final statistics
        queue_status = self.delivery_queue.get_queue_status()
        self.logger.info(f"Final queue statistics: {queue_status['statistics']}")
        
        self.logger.info("Notification manager shutdown complete")