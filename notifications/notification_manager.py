
import uuid
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, time as dt_time

from .config import NotificationConfigManager, NotificationConfig
from .telegram_service import TelegramService
from .whatsapp_service import WhatsAppService
from .message_formatter import MessageFormatter
from .delivery_queue import DeliveryQueue
from .base_service import NotificationMessage, SignalNotificationData
from .logger import get_notification_logger, setup_notification_logging

sys.path.append(str(Path(__file__).parent.parent))
try:
    from ai_notification_enhancer import AINotificationEnhancer
    AI_ENHANCER_AVAILABLE = True
except ImportError:
    AI_ENHANCER_AVAILABLE = False

class NotificationManager:

    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file

        self.logger = setup_notification_logging()

        self.config_manager = NotificationConfigManager(config_file)
        self.config = self.config_manager.load_config()

        validation_result = self.config_manager.validate_config(self.config)
        if not validation_result['valid']:
            self.logger.error(f"Configuration validation failed: {validation_result['errors']}")
            self.config.enabled = False

        if validation_result['warnings']:
            for warning in validation_result['warnings']:
                self.logger.warning(warning)

        self.formatter = MessageFormatter(self.config.preferences)
        self.delivery_queue = DeliveryQueue(self.config.delivery_config)

        self.ai_enhancer = None
        if AI_ENHANCER_AVAILABLE and self.config.preferences.get('ai_enhanced', True):
            try:
                self.ai_enhancer = AINotificationEnhancer(config_file)
                self.logger.info("AI notification enhancer initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize AI enhancer: {str(e)}")

        self.services = {}
        self._initialize_services()

        self._register_queue_services()

        if self.config.enabled:
            self.delivery_queue.start_processing()

        self.logger.info(f"Notification manager initialized (enabled: {self.config.enabled}, AI: {bool(self.ai_enhancer)})")

    def _initialize_services(self):
        if not self.config.enabled:
            return

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

        if not self.config.enabled:
            return False

        if not self._should_send_signal(signal_data, symbol):
            self.logger.info(f"Signal filtered out by preferences: {symbol} {signal_data.signal_type}")
            return False

        if self._is_quiet_hours():
            self.logger.info(f"Signal queued for later due to quiet hours: {symbol}")
            delay_seconds = self._calculate_quiet_hours_delay()
            return self._queue_enhanced_signal_messages(signal_data, delay_seconds)

        return self._queue_enhanced_signal_messages(signal_data)

    def _queue_enhanced_signal_messages(
        self,
        signal_data: SignalNotificationData,
        delay_seconds: int = 0
    ) -> bool:
        success = True

        enhanced_notification = None
        if self.ai_enhancer:
            try:
                signal_dict = {
                    'symbol': signal_data.symbol,
                    'type': signal_data.signal_type,
                    'price': signal_data.price,
                    'confidence': signal_data.confidence,
                    'reason': getattr(signal_data, 'reason', 'Technical analysis'),
                    'timestamp': signal_data.timestamp.isoformat() if hasattr(signal_data, 'timestamp') else datetime.now().isoformat()
                }

                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    enhanced_notification = loop.run_until_complete(
                        self.ai_enhancer.enhance_signal_notification(signal_dict)
                    )
                except RuntimeError:
                    enhanced_notification = asyncio.run(
                        self.ai_enhancer.enhance_signal_notification(signal_dict)
                    )

                self.logger.info(f"Enhanced signal notification with AI for {signal_data.symbol}")

            except Exception as e:
                self.logger.warning(f"Failed to enhance signal with AI: {str(e)}")

        if 'telegram' in self.services and self.services['telegram'].is_enabled:
            message = self._create_enhanced_signal_message(signal_data, enhanced_notification, 'telegram')
            if not self.delivery_queue.enqueue_message(message, 'normal', delay_seconds):
                success = False

        if 'whatsapp' in self.services and self.services['whatsapp'].is_enabled:
            whatsapp_threshold = self.config.whatsapp_config.get('confidence_threshold', 0.7)
            if signal_data.confidence >= whatsapp_threshold:
                message = self._create_enhanced_signal_message(signal_data, enhanced_notification, 'whatsapp')
                message.metadata = {'confidence': signal_data.confidence, 'ai_enhanced': bool(enhanced_notification)}
                if not self.delivery_queue.enqueue_message(message, 'high', delay_seconds):
                    success = False

        return success

    def _queue_signal_messages(
        self,
        signal_data: SignalNotificationData,
        delay_seconds: int = 0
    ) -> bool:
        return self._queue_enhanced_signal_messages(signal_data, delay_seconds)

    def _create_enhanced_signal_message(
        self,
        signal_data: SignalNotificationData,
        enhanced_notification: Optional[Dict[str, Any]],
        platform: str
    ) -> NotificationMessage:
        message_id = f"signal_{signal_data.symbol}_{int(time.time())}_{platform}"

        if enhanced_notification and self.ai_enhancer:
            try:
                content = self.ai_enhancer.format_for_platform(enhanced_notification, platform)
            except Exception as e:
                self.logger.warning(f"Failed to format AI content for {platform}: {str(e)}")
                content = self.formatter.format_signal_message(signal_data, platform)
        else:
            content = self.formatter.format_signal_message(signal_data, platform)

        content = self.formatter.truncate_message(content, platform)

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
                'confidence': signal_data.confidence,
                'ai_enhanced': bool(enhanced_notification),
                'enhanced_data': enhanced_notification
            }
        )

    def _create_signal_message(
        self,
        signal_data: SignalNotificationData,
        platform: str
    ) -> NotificationMessage:
        return self._create_enhanced_signal_message(signal_data, None, platform)

    def send_portfolio_summary(self, portfolio_data: Dict[str, Any]) -> bool:

        if not self.config.enabled:
            return False

        success = True

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
        message_id = f"portfolio_{int(time.time())}_{platform}"

        content = self.formatter.format_portfolio_summary(portfolio_data, platform)

        content = self.formatter.truncate_message(content, platform)

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

        if not self.config.enabled:
            return False

        success = True

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
        message_id = f"alert_{alert_type}_{int(time.time())}_{platform}"

        content = self.formatter.format_alert_message(alert_type, message, platform)

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

        preferences = self.config.preferences

        allowed_types = preferences.get('signal_types', ['BUY', 'SELL'])
        if signal_data.signal_type not in allowed_types:
            return False

        min_confidence = preferences.get('min_confidence', 0.0)
        if signal_data.confidence < min_confidence:
            return False

        allowed_stocks = preferences.get('stocks', ['ALL'])
        if 'ALL' not in allowed_stocks and symbol not in allowed_stocks:
            return False

        return True

    def _is_quiet_hours(self) -> bool:
        quiet_hours = self.config.preferences.get('quiet_hours', {})
        if not quiet_hours.get('enabled', False):
            return False

        try:
            start_time = dt_time.fromisoformat(quiet_hours.get('start', '22:00'))
            end_time = dt_time.fromisoformat(quiet_hours.get('end', '08:00'))
            current_time = datetime.now().time()

            if start_time <= end_time:
                return start_time <= current_time <= end_time
            else:
                return current_time >= start_time or current_time <= end_time

        except Exception as e:
            self.logger.error(f"Error checking quiet hours: {str(e)}")
            return False

    def _calculate_quiet_hours_delay(self) -> int:
        quiet_hours = self.config.preferences.get('quiet_hours', {})
        if not quiet_hours.get('enabled', False):
            return 0

        try:
            end_time = dt_time.fromisoformat(quiet_hours.get('end', '08:00'))
            now = datetime.now()

            end_datetime = datetime.combine(now.date(), end_time)
            if end_datetime <= now:
                end_datetime = end_datetime.replace(day=end_datetime.day + 1)

            delay_seconds = int((end_datetime - now).total_seconds())
            return max(0, delay_seconds)

        except Exception as e:
            self.logger.error(f"Error calculating quiet hours delay: {str(e)}")
            return 0

    def test_notifications(self) -> Dict[str, bool]:

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

        try:
            self.config.preferences.update(new_preferences)

            self.formatter.config = self.config.preferences

            self.logger.info("Notification preferences updated")
            return True

        except Exception as e:
            self.logger.error(f"Error updating preferences: {str(e)}")
            return False

    def send_risk_alert(
        self,
        risk_type: str,
        risk_data: Dict[str, Any],
        severity: str = 'medium'
    ) -> bool:

        if not self.config.enabled:
            return False

        try:
            risk_dict = {
                'type': risk_type,
                'severity': severity,
                'symbols': risk_data.get('symbols', []),
                'metrics': risk_data,
                'timestamp': datetime.now().isoformat()
            }

            enhanced_alert = None
            if self.ai_enhancer:
                try:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        enhanced_alert = loop.run_until_complete(
                            self.ai_enhancer.generate_risk_alert(risk_dict)
                        )
                    except RuntimeError:
                        enhanced_alert = asyncio.run(
                            self.ai_enhancer.generate_risk_alert(risk_dict)
                        )

                    self.logger.info(f"Enhanced risk alert with AI: {risk_type}")

                except Exception as e:
                    self.logger.warning(f"Failed to enhance risk alert with AI: {str(e)}")

            success = True
            for platform, service in self.services.items():
                if service.is_enabled:
                    message = self._create_risk_alert_message(risk_dict, enhanced_alert, platform)
                    priority = 'urgent' if severity.lower() == 'high' else 'high'
                    if not self.delivery_queue.enqueue_message(message, priority):
                        success = False

            return success

        except Exception as e:
            self.logger.error(f"Error sending risk alert: {str(e)}")
            return False

    def send_market_update(
        self,
        market_event: str,
        market_data: Dict[str, Any],
        impact_level: str = 'medium'
    ) -> bool:

        if not self.config.enabled:
            return False

        try:
            market_dict = {
                'event': market_event,
                'impact': impact_level,
                'sectors': market_data.get('sectors', []),
                'metrics': market_data,
                'timestamp': datetime.now().isoformat()
            }

            enhanced_update = None
            if self.ai_enhancer:
                try:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        enhanced_update = loop.run_until_complete(
                            self.ai_enhancer.create_market_update(market_dict)
                        )
                    except RuntimeError:
                        enhanced_update = asyncio.run(
                            self.ai_enhancer.create_market_update(market_dict)
                        )

                    self.logger.info(f"Enhanced market update with AI: {market_event}")

                except Exception as e:
                    self.logger.warning(f"Failed to enhance market update with AI: {str(e)}")

            success = True
            for platform, service in self.services.items():
                if service.is_enabled:
                    message = self._create_market_update_message(market_dict, enhanced_update, platform)
                    priority = 'high' if impact_level.lower() == 'high' else 'normal'
                    if not self.delivery_queue.enqueue_message(message, priority):
                        success = False

            return success

        except Exception as e:
            self.logger.error(f"Error sending market update: {str(e)}")
            return False

    def _create_risk_alert_message(
        self,
        risk_data: Dict[str, Any],
        enhanced_alert: Optional[Dict[str, Any]],
        platform: str
    ) -> NotificationMessage:
        message_id = f"risk_{risk_data['type']}_{int(time.time())}_{platform}"

        if enhanced_alert and self.ai_enhancer:
            try:
                content = self.ai_enhancer.format_for_platform(enhanced_alert, platform)
            except Exception as e:
                self.logger.warning(f"Failed to format AI risk alert for {platform}: {str(e)}")
                content = f"Risk Alert: {risk_data['type']} - {risk_data['severity']} severity"
        else:
            content = f"Risk Alert: {risk_data['type']} - {risk_data['severity']} severity"

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
            priority='high',
            metadata={
                'type': 'risk_alert',
                'risk_type': risk_data['type'],
                'severity': risk_data['severity'],
                'ai_enhanced': bool(enhanced_alert)
            }
        )

    def _create_market_update_message(
        self,
        market_data: Dict[str, Any],
        enhanced_update: Optional[Dict[str, Any]],
        platform: str
    ) -> NotificationMessage:
        message_id = f"market_{int(time.time())}_{platform}"

        if enhanced_update and self.ai_enhancer:
            try:
                content = self.ai_enhancer.format_for_platform(enhanced_update, platform)
            except Exception as e:
                self.logger.warning(f"Failed to format AI market update for {platform}: {str(e)}")
                content = f"Market Update: {market_data['event']} - {market_data['impact']} impact"
        else:
            content = f"Market Update: {market_data['event']} - {market_data['impact']} impact"

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
                'type': 'market_update',
                'event': market_data['event'],
                'impact': market_data['impact'],
                'ai_enhanced': bool(enhanced_update)
            }
        )

    def shutdown(self):
        self.logger.info("Shutting down notification manager")

        if self.ai_enhancer:
            try:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(self.ai_enhancer.shutdown())
                except RuntimeError:
                    asyncio.run(self.ai_enhancer.shutdown())
            except Exception as e:
                self.logger.warning(f"Error shutting down AI enhancer: {str(e)}")

        self.delivery_queue.stop_processing()

        queue_status = self.delivery_queue.get_queue_status()
        self.logger.info(f"Final queue statistics: {queue_status['statistics']}")

        self.logger.info("Notification manager shutdown complete")