import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import json

class MLFeatureEngineer:
    def __init__(self, config_file='config.json'):
        """Initialize ML feature engineer with configuration."""
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.ml_config = self.config['ml']
        self.sequence_length = self.ml_config['sequence_length']
        self.features = self.ml_config['features']
        self.scaler_save_path = self.ml_config['scaler_save_path']
        
        # Create directories if they don't exist
        os.makedirs(self.scaler_save_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.scalers = {}
    
    def engineer_features(self, data):
        """Engineer features for ML models."""
        try:
            if data is None or data.empty:
                return None
            
            # Create a copy to avoid modifying original data
            df = data.copy()
            
            # Calculate returns
            df['Returns'] = df['Close'].pct_change()
            
            # Calculate additional technical indicators
            df['Price_MA_Ratio'] = df['Close'] / df['SMA_20']
            df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
            
            # Price momentum features
            df['Price_Change_1d'] = df['Close'].pct_change(1)
            df['Price_Change_5d'] = df['Close'].pct_change(5)
            df['Price_Change_10d'] = df['Close'].pct_change(10)
            
            # Volatility features
            df['Volatility_10d'] = df['Returns'].rolling(window=10).std()
            df['Volatility_20d'] = df['Returns'].rolling(window=20).std()
            
            # RSI momentum
            df['RSI_Change'] = df['RSI'].diff()
            df['RSI_MA'] = df['RSI'].rolling(window=14).mean()
            
            # SMA features
            df['SMA_Spread'] = (df['SMA_20'] - df['SMA_50']) / df['SMA_50']
            df['Price_Above_SMA20'] = (df['Close'] > df['SMA_20']).astype(int)
            df['Price_Above_SMA50'] = (df['Close'] > df['SMA_50']).astype(int)
            
            # Target variable (next day return direction)
            df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
            
            # Drop NaN values
            df = df.dropna()
            
            self.logger.info(f"Engineered features for {len(df)} records")
            return df
            
        except Exception as e:
            self.logger.error(f"Error engineering features: {str(e)}")
            return None
    
    def prepare_sequences(self, data, symbol):
        """Prepare sequences for LSTM/GRU models."""
        try:
            if data is None or data.empty:
                return None, None, None
            
            # Select features for ML
            feature_columns = []
            for feature in self.features:
                if feature in data.columns:
                    feature_columns.append(feature)
                else:
                    self.logger.warning(f"Feature {feature} not found in data")
            
            if not feature_columns:
                self.logger.error("No valid features found")
                return None, None, None
            
            # Prepare feature matrix
            feature_data = data[feature_columns].values
            target_data = data['Target'].values
            
            # Scale features
            scaler = MinMaxScaler()
            scaled_features = scaler.fit_transform(feature_data)
            
            # Save scaler
            scaler_path = os.path.join(self.scaler_save_path, f'{symbol}_scaler.pkl')
            joblib.dump(scaler, scaler_path)
            self.scalers[symbol] = scaler
            
            # Create sequences
            X, y = [], []
            for i in range(self.sequence_length, len(scaled_features)):
                X.append(scaled_features[i-self.sequence_length:i])
                y.append(target_data[i])
            
            X = np.array(X)
            y = np.array(y)
            
            self.logger.info(f"Created {len(X)} sequences for {symbol}")
            return X, y, feature_columns
            
        except Exception as e:
            self.logger.error(f"Error preparing sequences for {symbol}: {str(e)}")
            return None, None, None
    
    def load_scaler(self, symbol):
        """Load saved scaler for a symbol."""
        try:
            scaler_path = os.path.join(self.scaler_save_path, f'{symbol}_scaler.pkl')
            if os.path.exists(scaler_path):
                scaler = joblib.load(scaler_path)
                self.scalers[symbol] = scaler
                return scaler
            else:
                self.logger.warning(f"Scaler not found for {symbol}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading scaler for {symbol}: {str(e)}")
            return None
    
    def prepare_prediction_data(self, data, symbol):
        """Prepare data for prediction."""
        try:
            if symbol not in self.scalers:
                scaler = self.load_scaler(symbol)
                if scaler is None:
                    return None
            else:
                scaler = self.scalers[symbol]
            
            # Select features
            feature_columns = []
            for feature in self.features:
                if feature in data.columns:
                    feature_columns.append(feature)
            
            if not feature_columns:
                return None
            
            # Get last sequence_length records
            if len(data) < self.sequence_length:
                self.logger.warning(f"Not enough data for prediction. Need {self.sequence_length}, got {len(data)}")
                return None
            
            feature_data = data[feature_columns].tail(self.sequence_length).values
            scaled_features = scaler.transform(feature_data)
            
            # Reshape for model input
            X = scaled_features.reshape(1, self.sequence_length, len(feature_columns))
            
            return X
            
        except Exception as e:
            self.logger.error(f"Error preparing prediction data for {symbol}: {str(e)}")
            return None

if __name__ == "__main__":
    # Test the feature engineer
    import yfinance as yf
    from datetime import datetime, timedelta
    from technical_indicators import TechnicalIndicators
    
    # Get sample data
    stock = yf.Ticker("RELIANCE.NS")
    data = stock.history(start=datetime.now() - timedelta(days=365), end=datetime.now())
    
    # Calculate indicators
    indicators = TechnicalIndicators()
    indicators_data = indicators.calculate_indicators(data)
    
    # Engineer features
    feature_engineer = MLFeatureEngineer()
    engineered_data = feature_engineer.engineer_features(indicators_data)
    
    if engineered_data is not None:
        print(f"Engineered features for {len(engineered_data)} records")
        print(f"Features: {engineered_data.columns.tolist()}")
        
        # Prepare sequences
        X, y, features = feature_engineer.prepare_sequences(engineered_data, "RELIANCE.NS")
        if X is not None:
            print(f"Created sequences: X shape {X.shape}, y shape {y.shape}")