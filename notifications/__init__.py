"""
Trading System Notifications Module

This module provides real-time notification capabilities for the ML-enhanced trading system,
supporting Telegram and WhatsApp delivery of trading signals and portfolio updates.
"""

from .notification_manager import NotificationManager
from .base_service import BaseNotificationService
from .telegram_service import TelegramService
from .whatsapp_service import WhatsAppService
from .message_formatter import MessageFormatter
from .delivery_queue import DeliveryQueue

__version__ = "1.0.0"
__author__ = "Trading System"

__all__ = [
    'NotificationManager',
    'BaseNotificationService', 
    'TelegramService',
    'WhatsAppService',
    'MessageFormatter',
    'DeliveryQueue'
]