
import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime
from ml_models import MLModels
from ml_feature_engineer import MLFeatureEngineer
from notifications.notification_manager import NotificationManager
from notifications.base_service import SignalNotificationData
from google_sheets_logger import GoogleSheetsLogger

class EnhancedMLSignalGenerator:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file

        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.logger = logging.getLogger(__name__)

        self.ml_models = MLModels(config_file)
        self.feature_engineer = MLFeatureEngineer(config_file)

        try:
            self.notification_manager = NotificationManager(config_file)
            self.notifications_enabled = True
            self.logger.info("Notification manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize notification manager: {str(e)}")
            self.notification_manager = None
            self.notifications_enabled = False

        try:
            self.sheets_logger = GoogleSheetsLogger(config_file)
            self.sheets_logging_enabled = True
            self.logger.info("Google Sheets logger initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets logger: {str(e)}")
            self.sheets_logger = None
            self.sheets_logging_enabled = False

        self.notify_on_signals = self.config.get('notifications', {}).get('enabled', False)

    def generate_signals(self, indicators_data):
        signals = {}
        
        for symbol, data in indicators_data.items():
            if data is None or data.empty:
                continue
                
            try:
                symbol_signals = self._generate_symbol_signals(symbol, data)
                if symbol_signals:
                    signals[symbol] = symbol_signals
                    
            except Exception as e:
                self.logger.error(f"Error generating signals for {symbol}: {str(e)}")
                continue

        if self.notifications_enabled and self.notify_on_signals:
            self._send_signal_notifications(signals)
            
        if self.sheets_logging_enabled and signals:
            self._log_signals_to_sheets(signals)

        return signals

    def check_current_signals(self, current_indicators):
        current_signals = {}
        
        for symbol, data in current_indicators.items():
            if data is None:
                continue
                
            try:
                signals = self._generate_symbol_signals(symbol, data)
                if signals:
                    current_signals[symbol] = signals[-1]
                    
            except Exception as e:
                self.logger.error(f"Error checking current signals for {symbol}: {str(e)}")
                continue

        if self.notifications_enabled and self.notify_on_signals and current_signals:
            self._send_current_signal_notifications(current_signals)

        if self.sheets_logging_enabled and current_signals:
            self._log_current_signals_to_sheets(current_signals)

        return current_signals

    def _generate_symbol_signals(self, symbol, data):
        """
        Generate trading signals for a single symbol using ML models and technical indicators.
        
        Args:
            symbol (str): Stock symbol (e.g., "RELIANCE.NS")
            data (DataFrame or dict): Historical price and indicator data or current values
            
        Returns:
            list: List of signal dictionaries with standardized format
        """
        signals = []
        
        try:
            # Validate input data - handle both DataFrame and dict
            if data is None:
                self.logger.warning(f"No data available for {symbol}")
                return signals
            
            # Handle dictionary input (current indicators)
            if isinstance(data, dict):
                # This is current indicator data, create a signal from current values
                current_price = data.get('close', 0.0)
                current_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
                rsi = data.get('rsi', 50.0)
                sma_20 = data.get('sma_20', current_price)
                sma_50 = data.get('sma_50', current_price)
                
                # Generate signal based on current values only (no ML prediction for current data)
                signal_type = 'HOLD'
                confidence = 0.5
                reason = 'Current technical analysis only'
                
                # Simple technical analysis rules
                if rsi < 30 and current_price > sma_20:
                    signal_type = 'BUY'
                    confidence = 0.7
                    reason = 'Oversold RSI with price above SMA_20'
                elif rsi > 70 and current_price < sma_20:
                    signal_type = 'SELL'
                    confidence = 0.7
                    reason = 'Overbought RSI with price below SMA_20'
                elif current_price > sma_20 and sma_20 > sma_50:
                    signal_type = 'BUY'
                    confidence = 0.6
                    reason = 'Price above both moving averages'
                elif current_price < sma_20 and sma_20 < sma_50:
                    signal_type = 'SELL'
                    confidence = 0.6
                    reason = 'Price below both moving averages'
                else:
                    if rsi > 70:
                        reason = 'Overbought conditions (RSI > 70)'
                    elif rsi < 30:
                        reason = 'Oversold conditions (RSI < 30)'
                    else:
                        reason = 'Mixed signals, neutral stance'
                
                signal = {
                    'type': signal_type,
                    'price': round(current_price, 2),
                    'confidence': round(confidence, 3),
                    'ml_probability': 0.5,  # No ML prediction for current data
                    'reason': reason,
                    'date': current_date,
                    'rsi': round(rsi, 2),
                    'sma_20': round(sma_20, 2),
                    'sma_50': round(sma_50, 2),
                    'predictions': {}
                }
                
                signals.append(signal)
                self.logger.info(f"Generated {signal_type} signal for {symbol} at ₹{current_price:.2f} (confidence: {confidence:.2f})")
                return signals
            
            # Handle DataFrame input (historical data)
            if hasattr(data, 'empty') and data.empty:
                self.logger.warning(f"Empty data for {symbol}")
                return signals
                
            # Check if we have minimum required data
            if len(data) < 50:  # Need at least 50 days for meaningful analysis
                self.logger.warning(f"Insufficient data for {symbol}: {len(data)} records")
                return signals
            
            # Get the latest data point for signal generation
            latest_data = data.iloc[-1]
            current_price = latest_data.get('Close', 0.0)
            current_date = latest_data.name.strftime('%Y-%m-%d') if hasattr(latest_data.name, 'strftime') else datetime.now().strftime('%Y-%m-%d')
            
            # Extract technical indicators
            rsi = latest_data.get('RSI', 50.0)
            sma_20 = latest_data.get('SMA_20', current_price)
            sma_50 = latest_data.get('SMA_50', current_price)
            volume = latest_data.get('Volume', 0)
            
            # Initialize signal components
            ml_probability = 0.5  # Default neutral probability
            model_predictions = {}
            confidence = 0.5
            signal_type = 'HOLD'
            reason = 'Technical analysis only'
            
            # Try to get ML predictions (with error handling)
            try:
                # Prepare data for ML prediction
                engineered_data = self.feature_engineer.engineer_features(data)
                if engineered_data is not None and not engineered_data.empty:
                    prediction_data = self.feature_engineer.prepare_prediction_data(engineered_data, symbol)
                    
                    if prediction_data is not None:
                        # Try LSTM prediction
                        try:
                            lstm_pred = self.ml_models.predict(prediction_data, symbol, 'LSTM')
                            if lstm_pred is not None:
                                model_predictions['LSTM'] = float(lstm_pred)
                        except Exception as e:
                            self.logger.debug(f"LSTM prediction failed for {symbol}: {str(e)}")
                        
                        # Try GRU prediction
                        try:
                            gru_pred = self.ml_models.predict(prediction_data, symbol, 'GRU')
                            if gru_pred is not None:
                                model_predictions['GRU'] = float(gru_pred)
                        except Exception as e:
                            self.logger.debug(f"GRU prediction failed for {symbol}: {str(e)}")
                        
                        # Combine ML predictions if available
                        if model_predictions:
                            # Weighted average: LSTM (0.6) + GRU (0.4)
                            lstm_weight = 0.6
                            gru_weight = 0.4
                            
                            if 'LSTM' in model_predictions and 'GRU' in model_predictions:
                                ml_probability = (model_predictions['LSTM'] * lstm_weight + 
                                                model_predictions['GRU'] * gru_weight)
                                reason = 'ML models + technical analysis'
                            elif 'LSTM' in model_predictions:
                                ml_probability = model_predictions['LSTM']
                                reason = 'LSTM model + technical analysis'
                            elif 'GRU' in model_predictions:
                                ml_probability = model_predictions['GRU']
                                reason = 'GRU model + technical analysis'
                            
            except Exception as e:
                self.logger.debug(f"ML prediction pipeline failed for {symbol}: {str(e)}")
            
            # Apply technical analysis filters and determine signal
            # BUY conditions: ML probability > 0.65 AND RSI < 70 AND price > SMA_20
            if ml_probability > 0.65 and rsi < 70 and current_price > sma_20:
                signal_type = 'BUY'
                confidence = min(0.9, ml_probability + 0.1)
                if ml_probability > 0.8:
                    reason += ' - Strong bullish signals'
                else:
                    reason += ' - Moderate bullish signals'
            
            # SELL conditions: ML probability < 0.35 AND RSI > 30 AND price < SMA_20
            elif ml_probability < 0.35 and rsi > 30 and current_price < sma_20:
                signal_type = 'SELL'
                confidence = min(0.9, (1 - ml_probability) + 0.1)
                if ml_probability < 0.2:
                    reason += ' - Strong bearish signals'
                else:
                    reason += ' - Moderate bearish signals'
            
            # Additional technical analysis for HOLD refinement
            else:
                signal_type = 'HOLD'
                confidence = 0.5 + abs(ml_probability - 0.5) * 0.5
                
                # Provide more specific reasons for HOLD
                if rsi > 70:
                    reason += ' - Overbought conditions (RSI > 70)'
                elif rsi < 30:
                    reason += ' - Oversold conditions (RSI < 30)'
                elif abs(current_price - sma_20) / sma_20 < 0.02:  # Within 2% of SMA_20
                    reason += ' - Price near moving average'
                else:
                    reason += ' - Mixed signals, wait for clearer trend'
            
            # Create the signal dictionary
            signal = {
                'type': signal_type,
                'price': round(current_price, 2),
                'confidence': round(confidence, 3),
                'ml_probability': round(ml_probability, 3),
                'reason': reason,
                'date': current_date,
                'rsi': round(rsi, 2),
                'sma_20': round(sma_20, 2),
                'sma_50': round(sma_50, 2),
                'predictions': model_predictions
            }
            
            signals.append(signal)
            
            self.logger.info(f"Generated {signal_type} signal for {symbol} at ₹{current_price:.2f} (confidence: {confidence:.2f})")
            
        except Exception as e:
            self.logger.error(f"Error in _generate_symbol_signals for {symbol}: {str(e)}")
            # Return empty signals list on error
            
        return signals

    def _send_signal_notifications(self, all_signals):
        if not self.notification_manager:
            return

        notification_count = 0

        for symbol, signals in all_signals.items():
            for signal in signals:
                try:
                    signal_data = self._create_signal_notification_data(signal, symbol)

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
        if not self.notification_manager:
            return

        notification_count = 0

        for symbol, signal in current_signals.items():
            try:
                signal_data = self._create_signal_notification_data(signal, symbol)

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
        signal_type = signal.get('type', 'UNKNOWN')
        price = signal.get('price', 0.0)
        reason = signal.get('reason', 'No reason provided')

        confidence = signal.get('confidence', 0.5)
        ml_probability = signal.get('ml_probability', 0.5)

        model_predictions = signal.get('predictions', {})

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
        if self.notification_manager:
            try:
                self.notification_manager.shutdown()
                self.logger.info("Notification system shutdown complete")
            except Exception as e:
                self.logger.error(f"Error shutting down notifications: {str(e)}")

    def _log_signals_to_sheets(self, all_signals):
        if not self.sheets_logger:
            return

        try:
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

            if signals_for_sheets:
                self.sheets_logger.log_current_signals(signals_for_sheets)
                self.logger.info(f"Logged {len(signals_for_sheets)} signals to Google Sheets")

                if self.notifications_enabled and self.notification_manager:
                    total_signals = sum(len(signals) for signals in signals_for_sheets.values())
                    self.notification_manager.send_alert(
                        'info',
                        f"📊 Logged {total_signals} new trading signals to Google Sheets",
                        'low'
                    )

        except Exception as e:
            self.logger.error(f"Error logging signals to Google Sheets: {str(e)}")

            if self.notifications_enabled and self.notification_manager:
                self.notification_manager.send_alert(
                    'error',
                    f"Failed to log signals to Google Sheets: {str(e)}",
                    'normal'
                )

    def _log_current_signals_to_sheets(self, current_signals):
        if not self.sheets_logger:
            return

        try:
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

            if formatted_signals:
                self.sheets_logger.log_current_signals(formatted_signals)
                self.logger.info(f"Logged {len(formatted_signals)} current signals to Google Sheets")

                if self.notifications_enabled and self.notification_manager:
                    self.notification_manager.send_alert(
                        'info',
                        f"📊 Logged {len(formatted_signals)} current signals to Google Sheets",
                        'low'
                    )

        except Exception as e:
            self.logger.error(f"Error logging current signals to Google Sheets: {str(e)}")

            if self.notifications_enabled and self.notification_manager:
                self.notification_manager.send_alert(
                    'error',
                    f"Failed to log current signals to Google Sheets: {str(e)}",
                    'normal'
                )

def create_enhanced_signal_generator(config_file='config.json'):
    return EnhancedMLSignalGenerator(config_file)