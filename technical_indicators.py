import pandas as pd
import numpy as np
import logging
import json

class TechnicalIndicators:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.rsi_period = self.config['trading']['rsi_period']
        self.sma_short = self.config['trading']['sma_short']
        self.sma_long = self.config['trading']['sma_long']

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_sma(self, prices, period):
        return prices.rolling(window=period).mean()

    def calculate_indicators(self, data):
        try:
            if data is None or data.empty:
                return None

            data = data.copy()

            data['RSI'] = self.calculate_rsi(data['Close'], self.rsi_period)

            data['SMA_20'] = self.calculate_sma(data['Close'], self.sma_short)
            data['SMA_50'] = self.calculate_sma(data['Close'], self.sma_long)

            data['SMA_Crossover'] = np.where(
                (data['SMA_20'] > data['SMA_50']) &
                (data['SMA_20'].shift(1) <= data['SMA_50'].shift(1)),
                1,
                np.where(
                    (data['SMA_20'] < data['SMA_50']) &
                    (data['SMA_20'].shift(1) >= data['SMA_50'].shift(1)),
                    -1,
                    0
                )
            )

            data = data.dropna()

            self.logger.info(f"Calculated indicators for {len(data)} records")
            return data

        except Exception as e:
            self.logger.error(f"Error calculating indicators: {str(e)}")
            return None

    def calculate_all_indicators(self, stock_data):
        indicators_data = {}

        for symbol, data in stock_data.items():
            indicators = self.calculate_indicators(data)
            if indicators is not None:
                indicators_data[symbol] = indicators

        self.logger.info(f"Calculated indicators for {len(indicators_data)} stocks")
        return indicators_data

    def get_current_indicators(self, indicators_data):
        current_indicators = {}

        for symbol, data in indicators_data.items():
            if data is not None and not data.empty:
                latest = data.iloc[-1]
                current_indicators[symbol] = {
                    'rsi': latest['RSI'],
                    'sma_20': latest['SMA_20'],
                    'sma_50': latest['SMA_50'],
                    'close': latest['Close'],
                    'date': latest.name.strftime('%Y-%m-%d')
                }

        return current_indicators

if __name__ == "__main__":
    import yfinance as yf
    from datetime import datetime, timedelta

    stock = yf.Ticker("RELIANCE.NS")
    data = stock.history(start=datetime.now() - timedelta(days=180), end=datetime.now())

    indicators = TechnicalIndicators()
    result = indicators.calculate_indicators(data)

    if result is not None:
        print(f"Calculated indicators for {len(result)} records")
        print(f"Latest RSI: {result.iloc[-1]['RSI']:.2f}")
        print(f"Latest SMA_20: {result.iloc[-1]['SMA_20']:.2f}")
        print(f"Latest SMA_50: {result.iloc[-1]['SMA_50']:.2f}")