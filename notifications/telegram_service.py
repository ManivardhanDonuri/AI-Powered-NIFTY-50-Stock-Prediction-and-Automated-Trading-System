"""
Telegram notification service

Handles sending notifications via Telegram Bot API with rate limiting and error handling.
"""

import requests
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .base_service import BaseNotificationService, NotificationMessage
from .logger import get_notification_logger

class TelegramService(BaseNotificationService):
    """Telegram Bot API notification service."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Telegram service with configuration."""
        super().__init__(config)
        
        self.bot_token = config.get('bot_token')
        self.chat_id = config.get('chat_id')
        self.api_base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Rate limiting (Telegram allows 30 messages per second)
        self.rate_limit = config.get('rate_limit', 30)
        self.last_request_time = 0
        self.request_interval = 1.0 / self.rate_limit  # Minimum interval between requests
        
        # Request timeout and retry settings
        self.timeout = config.get('timeout', 10)
        self.max_retries = config.get('max_retries', 3)
        
        self.logger = get_notification_logger('telegram')
        
        if not self.bot_token or not self.chat_id:
            self.logger.error("Telegram bot token or chat ID not configured")
            self.is_enabled = False
        else:
            self.logger.info("Telegram service initialized successfully")
    
    def get_service_name(self) -> str:
        """Get the service name."""
        return 'telegram'
    
    def send_message(self, message: NotificationMessage) -> bool:
        """
        Send a message via Telegram Bot API.
        
        Args:
            message: NotificationMessage object
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.is_enabled:
            self.logger.warning("Telegram service is disabled")
            return False
        
        if self.is_rate_limited():
            self.logger.warning("Rate limit exceeded, message queued")
            return False
        
        try:
            # Respect rate limiting
            self._wait_for_rate_limit()
            
            # Prepare message data
            message_data = {
                'chat_id': self.chat_id,
                'text': message.content,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            # Send message with retries
            response = self._send_with_retries(message_data)
            
            if response and response.get('ok'):
                self.logger.info(f"Message sent successfully: {message.message_id}")
                self.increment_message_count()
                return True
            else:
                error_msg = response.get('description', 'Unknown error') if response else 'No response'
                self.logger.error(f"Failed to send message {message.message_id}: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception sending message {message.message_id}: {str(e)}")
            return False
    
    def _send_with_retries(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send message with retry logic.
        
        Args:
            message_data: Message data for Telegram API
            
        Returns:
            dict: API response or None if all retries failed
        """
        url = f"{self.api_base_url}/sendMessage"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=message_data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Too Many Requests
                    # Handle rate limiting from Telegram
                    retry_after = response.json().get('parameters', {}).get('retry_after', 1)
                    self.logger.warning(f"Rate limited by Telegram, waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    continue
                else:
                    self.logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request exception on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_interval:
            sleep_time = self.request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def validate_connection(self) -> bool:
        """
        Validate connection to Telegram Bot API.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        if not self.is_enabled:
            return False
        
        try:
            url = f"{self.api_base_url}/getMe"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    bot_name = bot_info.get('result', {}).get('username', 'Unknown')
                    self.logger.info(f"Connection validated for bot: @{bot_name}")
                    return True
            
            self.logger.error(f"Connection validation failed: HTTP {response.status_code}")
            return False
            
        except Exception as e:
            self.logger.error(f"Connection validation error: {str(e)}")
            return False
    
    def send_test_message(self) -> bool:
        """
        Send a test message to verify functionality.
        
        Returns:
            bool: True if test message sent successfully
        """
        test_message = NotificationMessage(
            message_id="test_" + str(int(time.time())),
            platform="telegram",
            recipient=self.chat_id,
            content="🤖 <b>Trading System Test</b>\n\nTelegram notifications are working correctly!",
            priority="normal"
        )
        
        return self.send_message(test_message)
    
    def get_chat_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the configured chat.
        
        Returns:
            dict: Chat information or None if failed
        """
        if not self.is_enabled:
            return None
        
        try:
            url = f"{self.api_base_url}/getChat"
            response = requests.get(
                url,
                params={'chat_id': self.chat_id},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get('result')
            
        except Exception as e:
            self.logger.error(f"Error getting chat info: {str(e)}")
        
        return None
    
    def format_html_message(self, text: str) -> str:
        """
        Format text for HTML parsing in Telegram.
        
        Args:
            text: Raw text to format
            
        Returns:
            str: HTML-formatted text
        """
        # Escape HTML special characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        return text
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status of the Telegram service."""
        base_status = super().get_health_status()
        
        # Add Telegram-specific status
        base_status.update({
            'bot_token_configured': bool(self.bot_token),
            'chat_id_configured': bool(self.chat_id),
            'api_base_url': self.api_base_url,
            'connection_valid': self.validate_connection() if self.is_enabled else False
        })
        
        return base_status