import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime
from signal_generator import SignalGenerator
from ml_models import MLModels
from ml_feature_engineer import MLFeatureEngineer

class MLSignalGenerator(SignalGenerator):
    def __init__(self, config_file='config.json'):
        """Initialize ML-enhanced signal generator."""
        super().__init__(config_file)
        
        self.ml_config = self.config['ml']
        self.signals_config = self.config['signals']
        
        # Initialize ML components
        self.ml_models = MLModels(config_file)
        self.feature_engineer = MLFeatureEngineer(config_file)
        
        self.logger.info("ML Signal Generator initialized")
    
    def generate_ml_signals(self, indicators_data):
        """Generate ML-based trading signals."""
        ml_signals = {}
        
        for symbol, data in indicators_data.items():
            if data is not None and not data.empty:
                signals = self._generate_ml_stock_signals(symbol, data)
                if signals:
                    ml_signals[symbol] = signals
        
        self.logger.info(f"Generated ML signals for {len(ml_signals)} stocks")
        return ml_signals
    
    def _generate_ml_stock_signals(self, symbol, data):
        """Generate ML signals for a single stock."""
        try:
            # Engineer features
            engineered_data = self.feature_engineer.engineer_features(data)
            if engineered_data is None or len(engineered_data) < self.ml_config['sequence_length']:
                self.logger.warning(f"Insufficient data for ML prediction for {symbol}")
                return []
            
            signals = []
            
            # Generate signals for each day (walk-forward approach)
            for i in range(self.ml_config['sequence_length'], len(engineered_data)):
                current_data = engineered_data.iloc[:i+1]
                current_row = engineered_data.iloc[i]
                
                # Prepare prediction data
                pred_data = self.feature_engineer.prepare_prediction_data(current_data, symbol)
                if pred_data is None:
                    continue
                
                # Get predictions from both models
                predictions = {}
                confidences = {}
                
                for model_type in self.ml_config['models']:
                    pred = self.ml_models.predict(pred_data, symbol, model_type)
                    if pred is not None:
                        predictions[model_type] = pred
                        confidences[model_type] = abs(pred - 0.5) * 2  # Convert to confidence (0-1)
                
                if not predictions:
                    continue
                
                # Ensemble prediction (average of available models)
                avg_prediction = np.mean(list(predictions.values()))
                avg_confidence = np.mean(list(confidences.values()))
                
                # Generate signal based on prediction and confidence
                if (avg_prediction > self.signals_config['ml_threshold'] and 
                    avg_confidence > self.signals_config['confidence_threshold']):
                    
                    signal = {
                        'type': 'BUY',
                        'date': current_row.name.strftime('%Y-%m-%d'),
                        'price': current_row['Close'],
                        'ml_probability': avg_prediction,
                        'confidence': avg_confidence,
                        'predictions': predictions,
                        'reason': f"ML prediction: {avg_prediction:.3f} (confidence: {avg_confidence:.3f})"
                    }
                    signals.append(signal)
                
                elif (avg_prediction < (1 - self.signals_config['ml_threshold']) and 
                      avg_confidence > self.signals_config['confidence_threshold']):
                    
                    signal = {
                        'type': 'SELL',
                        'date': current_row.name.strftime('%Y-%m-%d'),
                        'price': current_row['Close'],
                        'ml_probability': avg_prediction,
                        'confidence': avg_confidence,
                        'predictions': predictions,
                        'reason': f"ML prediction: {avg_prediction:.3f} (confidence: {avg_confidence:.3f})"
                    }
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generating ML signals for {symbol}: {str(e)}")
            return []
    
    def generate_hybrid_signals(self, indicators_data):
        """Generate hybrid signals combining rule-based and ML approaches."""
        # Get rule-based signals
        rule_signals = super().generate_signals(indicators_data)
        
        # Get ML signals
        ml_signals = self.generate_ml_signals(indicators_data)
        
        # Combine signals
        hybrid_signals = {}
        
        for symbol in indicators_data.keys():
            symbol_rule_signals = rule_signals.get(symbol, [])
            symbol_ml_signals = ml_signals.get(symbol, [])
            
            combined_signals = self._combine_signals(
                symbol, symbol_rule_signals, symbol_ml_signals
            )
            
            if combined_signals:
                hybrid_signals[symbol] = combined_signals
        
        self.logger.info(f"Generated hybrid signals for {len(hybrid_signals)} stocks")
        return hybrid_signals
    
    def _combine_signals(self, symbol, rule_signals, ml_signals):
        """Combine rule-based and ML signals using weighted approach."""
        combined_signals = []
        
        # Create date-indexed dictionaries for easier lookup
        rule_dict = {s['date']: s for s in rule_signals}
        ml_dict = {s['date']: s for s in ml_signals}
        
        # Get all unique dates
        all_dates = set(rule_dict.keys()) | set(ml_dict.keys())
        
        for date in sorted(all_dates):
            rule_signal = rule_dict.get(date)
            ml_signal = ml_dict.get(date)
            
            # Calculate weighted signal strength
            signal_strength = 0
            signal_type = None
            reasons = []
            
            # Rule-based contribution
            if rule_signal:
                if rule_signal['type'] == 'BUY':
                    signal_strength += self.signals_config['rule_weight']
                    reasons.append(f"Rule: {rule_signal['reason']}")
                elif rule_signal['type'] == 'SELL':
                    signal_strength -= self.signals_config['rule_weight']
                    reasons.append(f"Rule: {rule_signal['reason']}")
            
            # ML contribution
            if ml_signal:
                ml_contribution = (ml_signal['ml_probability'] - 0.5) * 2  # Convert to -1 to 1
                ml_contribution *= self.signals_config['ml_weight'] * ml_signal['confidence']
                signal_strength += ml_contribution
                reasons.append(f"ML: {ml_signal['reason']}")
            
            # Determine final signal
            threshold = 0.3  # Minimum strength for signal generation
            
            if signal_strength > threshold:
                signal_type = 'BUY'
                price = rule_signal['price'] if rule_signal else ml_signal['price']
            elif signal_strength < -threshold:
                signal_type = 'SELL'
                price = rule_signal['price'] if rule_signal else ml_signal['price']
            
            if signal_type:
                combined_signal = {
                    'type': signal_type,
                    'date': date,
                    'price': price,
                    'signal_strength': signal_strength,
                    'rule_signal': rule_signal,
                    'ml_signal': ml_signal,
                    'reason': f"Hybrid ({signal_type}): " + "; ".join(reasons)
                }
                combined_signals.append(combined_signal)
        
        return combined_signals
    
    def generate_signals(self, indicators_data):
        """Generate signals based on configured mode."""
        mode = self.signals_config['mode'].lower()
        
        if mode == 'rule':
            return super().generate_signals(indicators_data)
        elif mode == 'ml':
            return self.generate_ml_signals(indicators_data)
        elif mode == 'hybrid':
            return self.generate_hybrid_signals(indicators_data)
        else:
            self.logger.error(f"Unknown signal mode: {mode}")
            return {}
    
    def check_current_ml_signals(self, current_indicators):
        """Check for current ML-based signals."""
        current_ml_signals = {}
        
        for symbol, indicators in current_indicators.items():
            try:
                # Create a dummy dataframe with current indicators
                current_data = pd.DataFrame([{
                    'Close': indicators['close'],
                    'SMA_20': indicators['sma_20'],
                    'SMA_50': indicators['sma_50'],
                    'RSI': indicators['rsi'],
                    'Volume': 1000000,  # Placeholder volume
                }])
                
                # Get ML prediction
                pred_data = self.feature_engineer.prepare_prediction_data(current_data, symbol)
                if pred_data is None:
                    continue
                
                # Get predictions from available models
                predictions = {}
                for model_type in self.ml_config['models']:
                    pred = self.ml_models.predict(pred_data, symbol, model_type)
                    if pred is not None:
                        predictions[model_type] = pred
                
                if not predictions:
                    continue
                
                # Calculate ensemble prediction
                avg_prediction = np.mean(list(predictions.values()))
                confidence = np.std(list(predictions.values()))  # Use std as uncertainty measure
                confidence = max(0, 1 - confidence)  # Convert to confidence
                
                # Generate signal
                if (avg_prediction > self.signals_config['ml_threshold'] and 
                    confidence > self.signals_config['confidence_threshold']):
                    
                    current_ml_signals[symbol] = {
                        'type': 'BUY',
                        'date': indicators['date'],
                        'price': indicators['close'],
                        'ml_probability': avg_prediction,
                        'confidence': confidence,
                        'predictions': predictions,
                        'reason': f"ML prediction: {avg_prediction:.3f} (confidence: {confidence:.3f})"
                    }
                
                elif (avg_prediction < (1 - self.signals_config['ml_threshold']) and 
                      confidence > self.signals_config['confidence_threshold']):
                    
                    current_ml_signals[symbol] = {
                        'type': 'SELL',
                        'date': indicators['date'],
                        'price': indicators['close'],
                        'ml_probability': avg_prediction,
                        'confidence': confidence,
                        'predictions': predictions,
                        'reason': f"ML prediction: {avg_prediction:.3f} (confidence: {confidence:.3f})"
                    }
                    
            except Exception as e:
                self.logger.error(f"Error checking current ML signals for {symbol}: {str(e)}")
                continue
        
        return current_ml_signals
    
    def check_current_signals(self, current_indicators):
        """Check for current signals based on configured mode."""
        mode = self.signals_config['mode'].lower()
        
        if mode == 'rule':
            return super().check_current_signals(current_indicators)
        elif mode == 'ml':
            return self.check_current_ml_signals(current_indicators)
        elif mode == 'hybrid':
            # Get both types of signals
            rule_signals = super().check_current_signals(current_indicators)
            ml_signals = self.check_current_ml_signals(current_indicators)
            
            # Combine current signals
            hybrid_signals = {}
            all_symbols = set(rule_signals.keys()) | set(ml_signals.keys())
            
            for symbol in all_symbols:
                rule_signal = rule_signals.get(symbol)
                ml_signal = ml_signals.get(symbol)
                
                # Simple combination for current signals
                if rule_signal and ml_signal:
                    # Both agree
                    if rule_signal['type'] == ml_signal['type']:
                        hybrid_signals[symbol] = {
                            'type': rule_signal['type'],
                            'date': rule_signal['date'],
                            'price': rule_signal['price'],
                            'reason': f"Hybrid: Rule + ML agree on {rule_signal['type']}"
                        }
                elif rule_signal:
                    hybrid_signals[symbol] = rule_signal
                elif ml_signal:
                    hybrid_signals[symbol] = ml_signal
            
            return hybrid_signals
        else:
            return {}

if __name__ == "__main__":
    # Test the ML signal generator
    import yfinance as yf
    from datetime import datetime, timedelta
    from technical_indicators import TechnicalIndicators
    
    # Get sample data
    stock = yf.Ticker("RELIANCE.NS")
    data = stock.history(start=datetime.now() - timedelta(days=365), end=datetime.now())
    
    # Calculate indicators
    indicators = TechnicalIndicators()
    indicators_data = {"RELIANCE.NS": indicators.calculate_indicators(data)}
    
    # Generate ML signals
    ml_signal_gen = MLSignalGenerator()
    signals = ml_signal_gen.generate_signals(indicators_data)
    
    print(f"Generated {len(signals.get('RELIANCE.NS', []))} signals for RELIANCE.NS")
    for signal in signals.get('RELIANCE.NS', [])[:5]:  # Show first 5 signals
        print(f"{signal['type']} at {signal['date']}: ₹{signal['price']:.2f} - {signal['reason']}")