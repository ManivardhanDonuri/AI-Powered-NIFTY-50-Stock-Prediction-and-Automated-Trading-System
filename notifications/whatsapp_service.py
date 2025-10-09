"""
WhatsApp notification service

Handles sending notifications via WhatsApp Business API with fallback to web automation.
"""

import requests
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .base_service import BaseNotificationService, NotificationMessage
from .logger import get_notification_logger

class WhatsAppBusinessService(BaseNotificationService):
    """WhatsApp Business API notification service."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize WhatsApp Business API service."""
        super().__init__(config)
        
        self.access_token = config.get('access_token')
        self.phone_number_id = config.get('phone_number_id')
        self.recipient = config.get('recipient')
        self.api_version = config.get('api_version', 'v17.0')
        self.api_base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        
        # Request settings
        self.timeout = config.get('timeout', 15)
        self.max_retries = config.get('max_retries', 3)
        
        self.logger = get_notification_logger('whatsapp_business')
        
        if not all([self.access_token, self.phone_number_id, self.recipient]):
            self.logger.error("WhatsApp Business API credentials not fully configured")
            self.is_enabled = False
        else:
            self.logger.info("WhatsApp Business API service initialized successfully")
    
    def get_service_name(self) -> str:
        """Get the service name."""
        return 'whatsapp_business'
    
    def send_message(self, message: NotificationMessage) -> bool:
        """
        Send a message via WhatsApp Business API.
        
        Args:
            message: NotificationMessage object
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.is_enabled:
            self.logger.warning("WhatsApp Business API service is disabled")
            return False
        
        if self.is_rate_limited():
            self.logger.warning("Rate limit exceeded, message queued")
            return False
        
        try:
            # Prepare message data
            message_data = {
                "messaging_product": "whatsapp",
                "to": self.recipient,
                "type": "text",
                "text": {
                    "body": message.content
                }
            }
            
            # Send message with retries
            response = self._send_with_retries(message_data)
            
            if response and response.get('messages'):
                message_id = response['messages'][0].get('id')
                self.logger.info(f"Message sent successfully: {message_id}")
                self.increment_message_count()
                return True
            else:
                error_msg = response.get('error', {}).get('message', 'Unknown error') if response else 'No response'
                self.logger.error(f"Failed to send message {message.message_id}: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception sending message {message.message_id}: {str(e)}")
            return False
    
    def _send_with_retries(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send message with retry logic.
        
        Args:
            message_data: Message data for WhatsApp API
            
        Returns:
            dict: API response or None if all retries failed
        """
        url = f"{self.api_base_url}/messages"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=message_data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Too Many Requests
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.logger.warning(f"Rate limited by WhatsApp, waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    continue
                else:
                    self.logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}: {response.text}")
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
    
    def validate_connection(self) -> bool:
        """
        Validate connection to WhatsApp Business API.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        if not self.is_enabled:
            return False
        
        try:
            url = f"{self.api_base_url}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                phone_info = response.json()
                phone_number = phone_info.get('display_phone_number', 'Unknown')
                self.logger.info(f"Connection validated for phone: {phone_number}")
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
            platform="whatsapp",
            recipient=self.recipient,
            content="🤖 *Trading System Test*\n\nWhatsApp notifications are working correctly!",
            priority="normal"
        )
        
        return self.send_message(test_message)

class WhatsAppWebService(BaseNotificationService):
    """WhatsApp Web automation service as fallback."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize WhatsApp Web automation service."""
        super().__init__(config)
        
        self.recipient = config.get('recipient')
        self.session_path = config.get('session_path', './whatsapp_session')
        self.headless = config.get('headless', True)
        
        self.logger = get_notification_logger('whatsapp_web')
        
        # This is a fallback service, so we'll mark it as disabled by default
        # It can be enabled when Business API fails
        self.is_enabled = False
        self.logger.info("WhatsApp Web service initialized (disabled by default)")
    
    def get_service_name(self) -> str:
        """Get the service name."""
        return 'whatsapp_web'
    
    def send_message(self, message: NotificationMessage) -> bool:
        """
        Send a message via WhatsApp Web automation.
        
        Args:
            message: NotificationMessage object
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.is_enabled:
            self.logger.warning("WhatsApp Web service is disabled")
            return False
        
        try:
            # Import selenium here to avoid dependency issues if not installed
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.options import Options
            
            # Set up Chrome options
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'--user-data-dir={self.session_path}')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Navigate to WhatsApp Web
                driver.get('https://web.whatsapp.com')
                
                # Wait for the page to load
                wait = WebDriverWait(driver, 30)
                
                # Check if we need to scan QR code
                try:
                    qr_code = driver.find_element(By.CSS_SELECTOR, '[data-testid="qr-code"]')
                    if qr_code:
                        self.logger.error("QR code scan required. Please scan QR code manually first.")
                        return False
                except:
                    pass  # QR code not found, likely already logged in
                
                # Search for contact
                search_box = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list-search"]'))
                )
                search_box.clear()
                search_box.send_keys(self.recipient)
                time.sleep(2)
                
                # Click on the contact
                contact = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'[title="{self.recipient}"]'))
                )
                contact.click()
                
                # Find message input and send message
                message_box = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="conversation-compose-box-input"]'))
                )
                message_box.clear()
                message_box.send_keys(message.content)
                
                # Send message
                send_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="compose-btn-send"]')
                send_button.click()
                
                self.logger.info(f"Message sent successfully via WhatsApp Web: {message.message_id}")
                return True
                
            finally:
                driver.quit()
                
        except ImportError:
            self.logger.error("Selenium not installed. Cannot use WhatsApp Web automation.")
            return False
        except Exception as e:
            self.logger.error(f"Exception sending message via WhatsApp Web: {str(e)}")
            return False
    
    def validate_connection(self) -> bool:
        """
        Validate WhatsApp Web session.
        
        Returns:
            bool: True if session is valid, False otherwise
        """
        # For web automation, we'll just check if session directory exists
        import os
        return os.path.exists(self.session_path)

class WhatsAppService(BaseNotificationService):
    """Combined WhatsApp service with Business API and Web fallback."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize combined WhatsApp service."""
        super().__init__(config)
        
        self.method = config.get('method', 'business_api')
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        
        # Initialize both services
        self.business_service = WhatsAppBusinessService(config)
        self.web_service = WhatsAppWebService(config)
        
        # Set primary service based on configuration
        if self.method == 'business_api':
            self.primary_service = self.business_service
            self.fallback_service = self.web_service
        else:
            self.primary_service = self.web_service
            self.fallback_service = self.business_service
        
        self.logger = get_notification_logger('whatsapp')
        self.logger.info(f"WhatsApp service initialized with method: {self.method}")
    
    def get_service_name(self) -> str:
        """Get the service name."""
        return 'whatsapp'
    
    def send_message(self, message: NotificationMessage) -> bool:
        """
        Send message using primary service with fallback.
        
        Args:
            message: NotificationMessage object
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.is_enabled:
            return False
        
        # Check confidence threshold for WhatsApp
        if hasattr(message, 'metadata') and message.metadata:
            confidence = message.metadata.get('confidence', 1.0)
            if confidence < self.confidence_threshold:
                self.logger.info(f"Message confidence {confidence} below threshold {self.confidence_threshold}, skipping WhatsApp")
                return False
        
        # Try primary service first
        if self.primary_service.send_message(message):
            return True
        
        # Try fallback service
        self.logger.warning("Primary WhatsApp service failed, trying fallback")
        if self.fallback_service.is_enabled:
            return self.fallback_service.send_message(message)
        
        return False
    
    def validate_connection(self) -> bool:
        """Validate connection using primary service."""
        return self.primary_service.validate_connection()
    
    def send_test_message(self) -> bool:
        """Send test message using primary service."""
        return self.primary_service.send_test_message()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of both services."""
        base_status = super().get_health_status()
        
        base_status.update({
            'method': self.method,
            'confidence_threshold': self.confidence_threshold,
            'business_api_status': self.business_service.get_health_status(),
            'web_service_status': self.web_service.get_health_status()
        })
        
        return base_status