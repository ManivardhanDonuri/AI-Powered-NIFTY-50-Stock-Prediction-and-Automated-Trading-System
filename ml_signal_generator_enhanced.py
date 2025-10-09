"""
Enhanced ML Signal Generator with Notification Integration

Extends the existing ML signal generator to send real-time notifications when signals are generated.
"""

import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime
from ml_signal_generator import MLSignalGenerator
from notifications.notification_manager import NotificationManager
from notifications.base_service import SignalNotificationData
from google_sheets_logger import GoogleSheetsLogger

class EnhancedMLSignalGenerator(MLSignalGenerator):
    """ML Signal Generator with notification capabilities."""
    
    def __init__(self, config_file='config.json'):
        """Initialize enhanced ML signal generator with notifications."""
        super().__init__(config_file)
        
        # Initialize notification manager
        try:
            self.notification_manager = NotificationManager(config_file)
            self.notifications_enabled = True
            self.logger.info("Notification manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize notification manager: {str(e)}")
            self.notification_manager = None
            self.notifications_enabled = False
        
        # Initialize Google Sheets logger
        try:
            self.sheets_logger = GoogleSheetsLogger(config_file)
            self.sheets_logging_enabled = True
            self.logger.info("Google Sheets logger initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets logger: {str(e)}")
            self.sheets_logger = None
            self.sheets_logging_enabled = False
        
        # Notification settings
        self.notify_on_signals = self.config.get('notifications', {}).get('enabled', False)
        
    def generate_signals(self, indicators_data):
        """Generate signals and send notifications."""
        # Generate signals using parent method
        signals = super().generate_signals(indicators_data)
        
        # Send notifications for new signals
        if self.notifications_enabled and self.notify_on_signals:
            self._send_signal_notifications(signals)
        
        # Log signals to Google Sheets
        if self.sheets_logging_enabled and signals:
            self._log_signals_to_sheets(signals)
        
        return signals
    
    def check_current_signals(self, current_indicators):
        """Check current signals and send notifications."""
        # Get current signals using parent method
        current_signals = super().check_current_signals(current_indicators)
        
        # Send notifications for current signals
        if self.notifications_enabled and self.notify_on_signals and current_signals:
            self._send_current_signal_notifications(current_signals)
        
        # Log current signals to Google Sheets
        if self.sheets_logging_enabled and current_signals:
            self._log_current_signals_to_sheets(current_signals)
        
        return current_signals
    
    def _send_signal_notifications(self, all_signals):
        """Send notifications for generated signals."""
        if not self.notification_manager:
            return
        
        notification_count = 0
        
        for symbol, signals in all_signals.items():
            for signal in signals:
                try:
                    # Create signal notification data
                    signal_data = self._create_signal_notification_data(signal, symbol)
                    
                    # Send notification
                    success = self.notification_manager.send_signal_notification(signal_data, symbol)
                    
                    if success:
                        notification_count += 1
                        self.logger.info(f"Notification sent for {symbol} {signal['type']} signal")
                    else:
                        self.logger.warning(f"Failed to send notification for {symbol} {signal['type']} signal")
                        
                except Exception as e:
                    self.logger.error(f"Error sending notification for {symbol}: {str(e)}")
        
        if notification_count > 0:
            self.logger.info(f"Sent {notification_count} signal notifications")
    
    def _send_current_signal_notifications(self, current_signals):
        """Send notifications for current signals."""
        if not self.notification_manager:
            return
        
        notification_count = 0
        
        for symbol, signal in current_signals.items():
            try:
                # Create signal notification data
                signal_data = self._create_signal_notification_data(signal, symbol)
                
                # Send notification with high priority for current signals
                success = self.notification_manager.send_signal_notification(signal_data, symbol)
                
                if success:
                    notification_count += 1
                    self.logger.info(f"Current signal notification sent for {symbol} {signal['type']}")
                else:
                    self.logger.warning(f"Failed to send current signal notification for {symbol}")
                    
            except Exception as e:
                self.logger.error(f"Error sending current signal notification for {symbol}: {str(e)}")
        
        if notification_count > 0:
            self.logger.info(f"Sent {notification_count} current signal notifications")
    
    def _create_signal_notification_data(self, signal, symbol):
        """Create SignalNotificationData from signal dictionary."""
        # Extract data from signal
        signal_type = signal.get('type', 'UNKNOWN')
        price = signal.get('price', 0.0)
        reason = signal.get('reason', 'No reason provided')
        
        # Get confidence and ML probability
        confidence = signal.get('confidence', 0.5)
        ml_probability = signal.get('ml_probability', 0.5)
        
        # Get model predictions if available
        model_predictions = signal.get('predictions', {})
        
        # Create timestamp
        signal_date = signal.get('date')
        if isinstance(signal_date, str):
            timestamp = datetime.strptime(signal_date, '%Y-%m-%d')
        else:
            timestamp = datetime.now()
        
        return SignalNotificationData(
            symbol=symbol,
            signal_type=signal_type,
            price=price,
            confidence=confidence,
            ml_probability=ml_probability,
            reason=reason,
            timestamp=timestamp,
            model_predictions=model_predictions
        )
    
    def send_portfolio_summary_notification(self, portfolio_data):
        """Send portfolio summary notification."""
        if not self.notification_manager or not self.notifications_enabled:
            return False
        
        try:
            success = self.notification_manager.send_portfolio_summary(portfolio_data)
            if success:
                self.logger.info("Portfolio summary notification sent")
            else:
                self.logger.warning("Failed to send portfolio summary notification")
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending portfolio summary notification: {str(e)}")
            return False
    
    def send_system_alert(self, alert_type, message, priority='normal'):
        """Send system alert notification."""
        if not self.notification_manager or not self.notifications_enabled:
            return False
        
        try:
            success = self.notification_manager.send_alert(alert_type, message, priority)
            if success:
                self.logger.info(f"System alert sent: {alert_type}")
            else:
                self.logger.warning(f"Failed to send system alert: {alert_type}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending system alert: {str(e)}")
            return False
    
    def test_notifications(self):
        """Test notification services."""
        if not self.notification_manager:
            self.logger.error("Notification manager not available")
            return {}
        
        try:
            results = self.notification_manager.test_notifications()
            self.logger.info(f"Notification test results: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error testing notifications: {str(e)}")
            return {}
    
    def get_notification_status(self):
        """Get notification system health status."""
        if not self.notification_manager:
            return {
                'enabled': False,
                'error': 'Notification manager not initialized'
            }
        
        try:
            return self.notification_manager.get_health_status()
        except Exception as e:
            self.logger.error(f"Error getting notification status: {str(e)}")
            return {
                'enabled': False,
                'error': str(e)
            }
    
    def update_notification_preferences(self, preferences):
        """Update notification preferences."""
        if not self.notification_manager:
            return False
        
        try:
            success = self.notification_manager.update_preferences(preferences)
            if success:
                self.logger.info("Notification preferences updated")
            else:
                self.logger.warning("Failed to update notification preferences")
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating notification preferences: {str(e)}")
            return False
    
    def shutdown_notifications(self):
        """Shutdown notification system."""
        if self.notification_manager:
            try:
                self.notification_manager.shutdown()
                self.logger.info("Notification system shutdown complete")
            except Exception as e:
                self.logger.error(f"Error shutting down notifications: {str(e)}")
    
    def _log_signals_to_sheets(self, all_signals):
        """Log generated signals to Google Sheets."""
        if not self.sheets_logger:
            return
        
        try:
            # Convert signals to format expected by sheets logger
            signals_for_sheets = {}
            
            for symbol, signals in all_signals.items():
                formatted_signals = []
                for signal in signals:
                    formatted_signal = {
                        'symbol': symbol,
                        'type': signal.get('type', 'UNKNOWN'),
                        'date': signal.get('date', datetime.now().strftime('%Y-%m-%d')),
                        'price': signal.get('price', 0.0),
                        'confidence': signal.get('confidence', 0.0),
                        'ml_probability': signal.get('ml_probability', 0.0),
                        'reason': signal.get('reason', 'No reason provided'),
                        'rsi': signal.get('rsi', 0.0),
                        'sma_20': signal.get('sma_20', 0.0),
                        'sma_50': signal.get('sma_50', 0.0),
                        'logged_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    formatted_signals.append(formatted_signal)
                
                if formatted_signals:
                    signals_for_sheets[symbol] = formatted_signals
            
            # Log to Google Sheets
            if signals_for_sheets:
                self.sheets_logger.log_current_signals(signals_for_sheets)
                self.logger.info(f"Logged {len(signals_for_sheets)} signals to Google Sheets")
                
                # Send notification about logging
                if self.notifications_enabled and self.notification_manager:
                    total_signals = sum(len(signals) for signals in signals_for_sheets.values())
                    self.notification_manager.send_alert(
                        'info',
                        f"📊 Logged {total_signals} new trading signals to Google Sheets",
                        'low'
                    )
                    
        except Exception as e:
            self.logger.error(f"Error logging signals to Google Sheets: {str(e)}")
            
            # Send error notification
            if self.notifications_enabled and self.notification_manager:
                self.notification_manager.send_alert(
                    'error',
                    f"Failed to log signals to Google Sheets: {str(e)}",
                    'normal'
                )
    
    def _log_current_signals_to_sheets(self, current_signals):
        """Log current signals to Google Sheets."""
        if not self.sheets_logger:
            return
        
        try:
            # Convert current signals to format expected by sheets logger
            formatted_signals = {}
            
            for symbol, signal in current_signals.items():
                formatted_signal = {
                    'symbol': symbol,
                    'type': signal.get('type', 'UNKNOWN'),
                    'date': signal.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'price': signal.get('price', 0.0),
                    'confidence': signal.get('confidence', 0.0),
                    'ml_probability': signal.get('ml_probability', 0.0),
                    'reason': signal.get('reason', 'No reason provided'),
                    'rsi': signal.get('rsi', 0.0),
                    'logged_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                formatted_signals[symbol] = formatted_signal
            
            # Log to Google Sheets
            if formatted_signals:
                self.sheets_logger.log_current_signals(formatted_signals)
                self.logger.info(f"Logged {len(formatted_signals)} current signals to Google Sheets")
                
                # Send notification about logging
                if self.notifications_enabled and self.notification_manager:
                    self.notification_manager.send_alert(
                        'info',
                        f"📊 Logged {len(formatted_signals)} current signals to Google Sheets",
                        'low'
                    )
                    
        except Exception as e:
            self.logger.error(f"Error logging current signals to Google Sheets: {str(e)}")
            
            # Send error notification
            if self.notifications_enabled and self.notification_manager:
                self.notification_manager.send_alert(
                    'error',
                    f"Failed to log current signals to Google Sheets: {str(e)}",
                    'normal'
                )

# Convenience function to create enhanced signal generator
def create_enhanced_signal_generator(config_file='config.json'):
    """Create an enhanced ML signal generator with notifications."""
    return EnhancedMLSignalGenerator(config_file)