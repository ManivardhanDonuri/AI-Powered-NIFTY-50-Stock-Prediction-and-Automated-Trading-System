import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime

class Backtester:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run_backtest(self, indicators_data, all_signals):
        backtest_results = {}

        for symbol in indicators_data.keys():
            if symbol in all_signals and indicators_data[symbol] is not None:
                result = self._backtest_stock(symbol, indicators_data[symbol], all_signals[symbol])
                if result:
                    backtest_results[symbol] = result

        self.logger.info(f"Completed backtest for {len(backtest_results)} stocks")
        return backtest_results

    def _backtest_stock(self, symbol, data, signals):
        if not signals:
            return None

        trades = []
        position = None
        entry_price = 0
        entry_date = None

        for signal in signals:
            if signal['type'] == 'BUY' and position is None:
                position = 'LONG'
                entry_price = signal['price']
                entry_date = signal['date']

            elif signal['type'] == 'SELL' and position == 'LONG':
                exit_price = signal['price']
                exit_date = signal['date']

                pnl = exit_price - entry_price
                pnl_pct = (pnl / entry_price) * 100

                entry_dt = datetime.strptime(entry_date, '%Y-%m-%d')
                exit_dt = datetime.strptime(exit_date, '%Y-%m-%d')
                holding_days = (exit_dt - entry_dt).days

                trade = {
                    'entry_date': entry_date,
                    'exit_date': exit_date,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'holding_days': holding_days,
                    'result': 'WIN' if pnl > 0 else 'LOSS'
                }
                trades.append(trade)

                position = None
                entry_price = 0
                entry_date = None

        if not trades:
            return None

        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

        total_pnl = sum(t['pnl'] for t in trades)
        total_pnl_pct = sum(t['pnl_pct'] for t in trades)
        avg_pnl_per_trade = total_pnl / total_trades if total_trades > 0 else 0

        max_win = max(t['pnl'] for t in trades) if trades else 0
        max_loss = min(t['pnl'] for t in trades) if trades else 0

        avg_holding_days = np.mean([t['holding_days'] for t in trades]) if trades else 0

        returns = [t['pnl_pct'] for t in trades]
        sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0

        cumulative_returns = []
        cumulative = 0
        for trade in trades:
            cumulative += trade['pnl']
            cumulative_returns.append(cumulative)

        return {
            'symbol': symbol,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'avg_pnl_per_trade': avg_pnl_per_trade,
            'max_win': max_win,
            'max_loss': max_loss,
            'avg_holding_days': avg_holding_days,
            'sharpe_ratio': sharpe_ratio,
            'trades': trades,
            'cumulative_returns': cumulative_returns
        }

    def get_portfolio_summary(self, backtest_results):
        if not backtest_results:
            return None

        all_trades = []
        symbols_traded = list(backtest_results.keys())

        for result in backtest_results.values():
            all_trades.extend(result['trades'])

        if not all_trades:
            return None

        total_trades = len(all_trades)
        winning_trades = len([t for t in all_trades if t['pnl'] > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

        total_pnl = sum(t['pnl'] for t in all_trades)
        total_pnl_pct = sum(t['pnl_pct'] for t in all_trades)
        avg_pnl_per_trade = total_pnl / total_trades if total_trades > 0 else 0

        returns = [t['pnl_pct'] for t in all_trades]
        sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'avg_pnl_per_trade': avg_pnl_per_trade,
            'sharpe_ratio': sharpe_ratio,
            'symbols_traded': symbols_traded
        }

if __name__ == "__main__":
    import yfinance as yf
    from datetime import datetime, timedelta
    from technical_indicators import TechnicalIndicators
    from ml_signal_generator_enhanced import EnhancedMLSignalGenerator

    stock = yf.Ticker("RELIANCE.NS")
    data = stock.history(start=datetime.now() - timedelta(days=180), end=datetime.now())

    indicators = TechnicalIndicators()
    indicators_data = indicators.calculate_indicators(data)

    signal_gen = SignalGenerator()
    signals = signal_gen._generate_stock_signals("RELIANCE.NS", indicators_data)

    backtester = Backtester()
    result = backtester._backtest_stock("RELIANCE.NS", indicators_data, signals)

    if result:
        print(f"Backtest Results for {result['symbol']}:")
        print(f"Total Trades: {result['total_trades']}")
        print(f"Win Rate: {result['win_rate']:.2f}%")
        print(f"Total P&L: ₹{result['total_pnl']:.2f}")
        print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")