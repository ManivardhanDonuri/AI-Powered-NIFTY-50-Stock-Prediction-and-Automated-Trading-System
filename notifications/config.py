
import json
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class NotificationConfig:
    enabled: bool = False
    telegram_enabled: bool = False
    telegram_config: Dict[str, Any] = None
    preferences: Dict[str, Any] = None
    delivery_config: Dict[str, Any] = None

    def __post_init__(self):
        if self.telegram_config is None:
            self.telegram_config = {}
        if self.preferences is None:
            self.preferences = {}
        if self.delivery_config is None:
            self.delivery_config = {}

class NotificationConfigManager:

    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self._config = None

    def load_config(self) -> NotificationConfig:

        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)

            notifications_config = config_data.get('notifications', {})

            telegram_config = notifications_config.get('telegram', {})
            telegram_config['bot_token'] = self._get_env_var(
                'TELEGRAM_BOT_TOKEN',
                telegram_config.get('bot_token')
            )
            telegram_config['chat_id'] = self._get_env_var(
                'TELEGRAM_CHAT_ID',
                telegram_config.get('chat_id')
            )

            self._config = NotificationConfig(
                enabled=notifications_config.get('enabled', False),
                telegram_enabled=telegram_config.get('enabled', False),
                telegram_config=telegram_config,
                preferences=notifications_config.get('preferences', {}),
                delivery_config=notifications_config.get('delivery', {})
            )

            self.logger.info("Notification configuration loaded successfully")
            return self._config

        except Exception as e:
            self.logger.error(f"Error loading notification configuration: {str(e)}")
            return NotificationConfig()

    def _get_env_var(self, env_name: str, default_value: Optional[str] = None) -> Optional[str]:

        value = os.getenv(env_name, default_value)
        if value and value.startswith('${') and value.endswith('}'):
            actual_env_name = value[2:-1]
            return os.getenv(actual_env_name, default_value)
        return value

    def validate_config(self, config: NotificationConfig) -> Dict[str, Any]:

        errors = []
        warnings = []

        if not config.enabled:
            warnings.append("Notifications are disabled")
            return {'valid': True, 'errors': errors, 'warnings': warnings}

        if config.telegram_enabled:
            if not config.telegram_config.get('bot_token'):
                errors.append("Telegram bot token is required when Telegram is enabled")
            if not config.telegram_config.get('chat_id'):
                errors.append("Telegram chat ID is required when Telegram is enabled")

        if config.enabled and not config.telegram_enabled:
            warnings.append("Notifications are enabled but no services are configured")

        preferences = config.preferences
        min_confidence = preferences.get('min_confidence', 0.7)
        if not 0 <= min_confidence <= 1:
            errors.append("Minimum confidence must be between 0 and 1")

        delivery = config.delivery_config
        max_retries = delivery.get('max_retries', 3)
        if max_retries < 0:
            errors.append("Maximum retries must be non-negative")

        queue_size = delivery.get('queue_size', 100)
        if queue_size <= 0:
            errors.append("Queue size must be positive")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def get_config(self) -> NotificationConfig:

        if self._config is None:
            self._config = self.load_config()
        return self._config

    def create_default_config_template(self) -> Dict[str, Any]:

        return {
            "notifications": {
                "enabled": True,
                "telegram": {
                    "enabled": True,
                    "bot_token": "${TELEGRAM_BOT_TOKEN}",
                    "chat_id": "${TELEGRAM_CHAT_ID}",
                    "rate_limit": 30
                },
                "whatsapp": {
                    "enabled": True,
                    "method": "business_api",
                    "access_token": "${WHATSAPP_ACCESS_TOKEN}",
                    "phone_number_id": "${WHATSAPP_PHONE_ID}",
                    "recipient": "${WHATSAPP_RECIPIENT}"
                },
                "preferences": {
                    "signal_types": ["BUY", "SELL"],
                    "min_confidence": 0.7,
                    "stocks": ["ALL"],
                    "quiet_hours": {
                        "enabled": True,
                        "start": "22:00",
                        "end": "08:00"
                    }
                },
                "delivery": {
                    "max_retries": 3,
                    "retry_delay": 5,
                    "queue_size": 100,
                    "batch_size": 5
                }
            }
        }