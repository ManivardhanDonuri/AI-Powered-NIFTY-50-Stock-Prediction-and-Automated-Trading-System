
import requests
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .base_service import BaseNotificationService, NotificationMessage
from .logger import get_notification_logger

class WhatsAppBusinessService(BaseNotificationService):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.access_token = config.get('access_token')
        self.phone_number_id = config.get('phone_number_id')
        self.recipient = config.get('recipient')
        self.api_version = config.get('api_version', 'v17.0')
        self.api_base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"

        self.timeout = config.get('timeout', 15)
        self.max_retries = config.get('max_retries', 3)

        self.logger = get_notification_logger('whatsapp_business')

        if not all([self.access_token, self.phone_number_id, self.recipient]):
            self.logger.error("WhatsApp Business API credentials not fully configured")
            self.is_enabled = False
        else:
            self.logger.info("WhatsApp Business API service initialized successfully")

    def get_service_name(self) -> str:
        return 'whatsapp_business'

    def send_message(self, message: NotificationMessage) -> bool:

        if not self.is_enabled:
            self.logger.warning("WhatsApp Business API service is disabled")
            return False

        if self.is_rate_limited():
            self.logger.warning("Rate limit exceeded, message queued")
            return False

        try:
            message_data = {
                "messaging_product": "whatsapp",
                "to": self.recipient,
                "type": "text",
                "text": {
                    "body": message.content
                }
            }

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
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.logger.warning(f"Rate limited by WhatsApp, waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    continue
                else:
                    self.logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}: {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)

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

        test_message = NotificationMessage(
            message_id="test_" + str(int(time.time())),
            platform="whatsapp",
            recipient=self.recipient,
            content="🤖 *Trading System Test*\n\nWhatsApp notifications are working correctly!",
            priority="normal"
        )

        return self.send_message(test_message)

class WhatsAppWebService(BaseNotificationService):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.recipient = config.get('recipient')
        self.session_path = config.get('session_path', './whatsapp_session')
        self.headless = config.get('headless', True)

        self.logger = get_notification_logger('whatsapp_web')

        self.is_enabled = False
        self.logger.info("WhatsApp Web service initialized (disabled by default)")

    def get_service_name(self) -> str:
        return 'whatsapp_web'

    def send_message(self, message: NotificationMessage) -> bool:

        if not self.is_enabled:
            self.logger.warning("WhatsApp Web service is disabled")
            return False

        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.options import Options

            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'--user-data-dir={self.session_path}')

            driver = webdriver.Chrome(options=chrome_options)

            try:
                driver.get('https://web.whatsapp.com')

                wait = WebDriverWait(driver, 30)

                try:
                    qr_code = driver.find_element(By.CSS_SELECTOR, '[data-testid="qr-code"]')
                    if qr_code:
                        self.logger.error("QR code scan required. Please scan QR code manually first.")
                        return False
                except:
                    pass

                search_box = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list-search"]'))
                )
                search_box.clear()
                search_box.send_keys(self.recipient)
                time.sleep(2)

                contact = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'[title="{self.recipient}"]'))
                )
                contact.click()

                message_box = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="conversation-compose-box-input"]'))
                )
                message_box.clear()
                message_box.send_keys(message.content)

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

        import os
        return os.path.exists(self.session_path)

class WhatsAppService(BaseNotificationService):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.method = config.get('method', 'business_api')
        self.confidence_threshold = config.get('confidence_threshold', 0.7)

        self.business_service = WhatsAppBusinessService(config)
        self.web_service = WhatsAppWebService(config)

        if self.method == 'business_api':
            self.primary_service = self.business_service
            self.fallback_service = self.web_service
        else:
            self.primary_service = self.web_service
            self.fallback_service = self.business_service

        self.logger = get_notification_logger('whatsapp')
        self.logger.info(f"WhatsApp service initialized with method: {self.method}")

    def get_service_name(self) -> str:
        return 'whatsapp'

    def send_message(self, message: NotificationMessage) -> bool:

        if not self.is_enabled:
            return False

        if hasattr(message, 'metadata') and message.metadata:
            confidence = message.metadata.get('confidence', 1.0)
            if confidence < self.confidence_threshold:
                self.logger.info(f"Message confidence {confidence} below threshold {self.confidence_threshold}, skipping WhatsApp")
                return False

        if self.primary_service.send_message(message):
            return True

        self.logger.warning("Primary WhatsApp service failed, trying fallback")
        if self.fallback_service.is_enabled:
            return self.fallback_service.send_message(message)

        return False

    def validate_connection(self) -> bool:
        return self.primary_service.validate_connection()

    def send_test_message(self) -> bool:
        return self.primary_service.send_test_message()

    def get_health_status(self) -> Dict[str, Any]:
        base_status = super().get_health_status()

        base_status.update({
            'method': self.method,
            'confidence_threshold': self.confidence_threshold,
            'business_api_status': self.business_service.get_health_status(),
            'web_service_status': self.web_service.get_health_status()
        })

        return base_status