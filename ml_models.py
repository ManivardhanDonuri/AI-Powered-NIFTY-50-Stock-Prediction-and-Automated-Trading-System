import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging
import json
import os
import joblib
from datetime import datetime

class MLModels:
    def __init__(self, config_file='config.json'):
        """Initialize ML models with configuration."""
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.ml_config = self.config['ml']
        self.model_save_path = self.ml_config['model_save_path']
        
        # Create directories if they don't exist
        os.makedirs(self.model_save_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Set random seeds for reproducibility
        np.random.seed(42)
        tf.random.set_seed(42)
        
        self.models = {}
        self.model_history = {}
    
    def create_lstm_model(self, input_shape):
        """Create LSTM model architecture."""
        model = Sequential([
            LSTM(self.ml_config['lstm_units'], 
                 return_sequences=True, 
                 input_shape=input_shape),
            Dropout(self.ml_config['dropout_rate']),
            BatchNormalization(),
            
            LSTM(self.ml_config['lstm_units'] // 2, 
                 return_sequences=False),
            Dropout(self.ml_config['dropout_rate']),
            BatchNormalization(),
            
            Dense(25, activation='relu'),
            Dropout(self.ml_config['dropout_rate']),
            
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=self.ml_config['learning_rate']),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def create_gru_model(self, input_shape):
        """Create GRU model architecture."""
        model = Sequential([
            GRU(self.ml_config['gru_units'], 
                return_sequences=True, 
                input_shape=input_shape),
            Dropout(self.ml_config['dropout_rate']),
            BatchNormalization(),
            
            GRU(self.ml_config['gru_units'] // 2, 
                return_sequences=False),
            Dropout(self.ml_config['dropout_rate']),
            BatchNormalization(),
            
            Dense(25, activation='relu'),
            Dropout(self.ml_config['dropout_rate']),
            
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=self.ml_config['learning_rate']),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_model(self, X, y, symbol, model_type='LSTM'):
        """Train a model for a specific symbol."""
        try:
            self.logger.info(f"Training {model_type} model for {symbol}")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=1-self.ml_config['train_test_split'], 
                random_state=42,
                stratify=y
            )
            
            # Create model
            input_shape = (X.shape[1], X.shape[2])
            if model_type.upper() == 'LSTM':
                model = self.create_lstm_model(input_shape)
            elif model_type.upper() == 'GRU':
                model = self.create_gru_model(input_shape)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Callbacks
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-7
                )
            ]
            
            # Train model
            history = model.fit(
                X_train, y_train,
                epochs=self.ml_config['epochs'],
                batch_size=self.ml_config['batch_size'],
                validation_split=self.ml_config['validation_split'],
                callbacks=callbacks,
                verbose=1
            )
            
            # Evaluate model
            test_predictions = model.predict(X_test)
            test_predictions_binary = (test_predictions > 0.5).astype(int)
            
            accuracy = accuracy_score(y_test, test_predictions_binary)
            precision = precision_score(y_test, test_predictions_binary)
            recall = recall_score(y_test, test_predictions_binary)
            f1 = f1_score(y_test, test_predictions_binary)
            
            self.logger.info(f"{model_type} model for {symbol} - Accuracy: {accuracy:.4f}, "
                           f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
            
            # Save model
            model_filename = f"{symbol}_{model_type.lower()}_model.h5"
            model_path = os.path.join(self.model_save_path, model_filename)
            model.save(model_path)
            
            # Save model info
            model_info = {
                'symbol': symbol,
                'model_type': model_type,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'input_shape': input_shape,
                'trained_date': datetime.now().isoformat(),
                'model_path': model_path
            }
            
            info_filename = f"{symbol}_{model_type.lower()}_info.pkl"
            info_path = os.path.join(self.model_save_path, info_filename)
            joblib.dump(model_info, info_path)
            
            # Store in memory
            model_key = f"{symbol}_{model_type.upper()}"
            self.models[model_key] = model
            self.model_history[model_key] = history
            
            return model, model_info
            
        except Exception as e:
            self.logger.error(f"Error training {model_type} model for {symbol}: {str(e)}")
            return None, None
    
    def load_model(self, symbol, model_type='LSTM'):
        """Load a trained model."""
        try:
            model_filename = f"{symbol}_{model_type.lower()}_model.h5"
            model_path = os.path.join(self.model_save_path, model_filename)
            
            if os.path.exists(model_path):
                model = load_model(model_path)
                model_key = f"{symbol}_{model_type.upper()}"
                self.models[model_key] = model
                
                # Load model info
                info_filename = f"{symbol}_{model_type.lower()}_info.pkl"
                info_path = os.path.join(self.model_save_path, info_filename)
                if os.path.exists(info_path):
                    model_info = joblib.load(info_path)
                    return model, model_info
                
                return model, None
            else:
                self.logger.warning(f"Model not found: {model_path}")
                return None, None
                
        except Exception as e:
            self.logger.error(f"Error loading {model_type} model for {symbol}: {str(e)}")
            return None, None
    
    def predict(self, X, symbol, model_type='LSTM'):
        """Make predictions using trained model."""
        try:
            model_key = f"{symbol}_{model_type.upper()}"
            
            # Load model if not in memory
            if model_key not in self.models:
                model, _ = self.load_model(symbol, model_type)
                if model is None:
                    return None
            else:
                model = self.models[model_key]
            
            # Make prediction
            prediction = model.predict(X, verbose=0)
            return prediction[0][0]  # Return probability
            
        except Exception as e:
            self.logger.error(f"Error making prediction with {model_type} for {symbol}: {str(e)}")
            return None
    
    def train_all_models(self, feature_data):
        """Train both LSTM and GRU models for all symbols."""
        trained_models = {}
        
        for symbol, (X, y, features) in feature_data.items():
            if X is not None and y is not None:
                symbol_models = {}
                
                # Train LSTM
                if 'LSTM' in self.ml_config['models']:
                    lstm_model, lstm_info = self.train_model(X, y, symbol, 'LSTM')
                    if lstm_model is not None:
                        symbol_models['LSTM'] = {
                            'model': lstm_model,
                            'info': lstm_info
                        }
                
                # Train GRU
                if 'GRU' in self.ml_config['models']:
                    gru_model, gru_info = self.train_model(X, y, symbol, 'GRU')
                    if gru_model is not None:
                        symbol_models['GRU'] = {
                            'model': gru_model,
                            'info': gru_info
                        }
                
                if symbol_models:
                    trained_models[symbol] = symbol_models
        
        self.logger.info(f"Trained models for {len(trained_models)} symbols")
        return trained_models
    
    def get_model_summary(self):
        """Get summary of all trained models."""
        summary = {}
        
        for model_key, model in self.models.items():
            symbol, model_type = model_key.split('_', 1)
            
            # Load model info
            info_filename = f"{symbol}_{model_type.lower()}_info.pkl"
            info_path = os.path.join(self.model_save_path, info_filename)
            
            if os.path.exists(info_path):
                model_info = joblib.load(info_path)
                summary[model_key] = model_info
        
        return summary

if __name__ == "__main__":
    # Test the ML models
    from ml_feature_engineer import MLFeatureEngineer
    from technical_indicators import TechnicalIndicators
    import yfinance as yf
    from datetime import datetime, timedelta
    
    # Get sample data
    stock = yf.Ticker("RELIANCE.NS")
    data = stock.history(start=datetime.now() - timedelta(days=365), end=datetime.now())
    
    # Calculate indicators and engineer features
    indicators = TechnicalIndicators()
    indicators_data = indicators.calculate_indicators(data)
    
    feature_engineer = MLFeatureEngineer()
    engineered_data = feature_engineer.engineer_features(indicators_data)
    
    if engineered_data is not None:
        X, y, features = feature_engineer.prepare_sequences(engineered_data, "RELIANCE.NS")
        
        if X is not None and y is not None:
            # Train models
            ml_models = MLModels()
            
            # Train LSTM
            lstm_model, lstm_info = ml_models.train_model(X, y, "RELIANCE.NS", "LSTM")
            if lstm_model is not None:
                print(f"LSTM model trained successfully: {lstm_info}")
            
            # Train GRU
            gru_model, gru_info = ml_models.train_model(X, y, "RELIANCE.NS", "GRU")
            if gru_model is not None:
                print(f"GRU model trained successfully: {gru_info}")