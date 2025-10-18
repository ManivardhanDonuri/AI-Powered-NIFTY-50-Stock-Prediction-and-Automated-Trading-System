
import json
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from trading_system import TradingSystem
    TRADING_SYSTEM_AVAILABLE = True
except ImportError as e:
    TRADING_SYSTEM_AVAILABLE = False
    logging.warning(f"Trading system not available: {e}")

try:
    from backtester import Backtester
    BACKTESTER_AVAILABLE = True
except ImportError as e:
    BACKTESTER_AVAILABLE = False
    logging.warning(f"Backtester not available: {e}")

try:
    from data_fetcher import DataFetcher
    DATA_FETCHER_AVAILABLE = True
except ImportError as e:
    DATA_FETCHER_AVAILABLE = False
    logging.warning(f"Data fetcher not available: {e}")

try:
    from technical_indicators import TechnicalIndicators
    INDICATORS_AVAILABLE = True
except ImportError as e:
    INDICATORS_AVAILABLE = False
    logging.warning(f"Technical indicators not available: {e}")

class TradingContextProvider:

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)

        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            self.config = {}

        self._initialize_components()

        self._context_cache = {}
        self._cache_ttl = 900

    def _initialize_components(self):
        try:
            if DATA_FETCHER_AVAILABLE:
                self.data_fetcher = DataFetcher(self.config_path)
            else:
                self.data_fetcher = None

            if INDICATORS_AVAILABLE:
                self.indicators = TechnicalIndicators(self.config_path)
            else:
                self.indicators = None

            if BACKTESTER_AVAILABLE:
                self.backtester = Backtester(self.config_path)
            else:
                self.backtester = None

            self.logger.info("Trading system components initialized (available components only)")
        except Exception as e:
            self.logger.error(f"Failed to initialize trading components: {str(e)}")
            self.data_fetcher = None
            self.indicators = None
            self.backtester = None

    def get_portfolio_context(self) -> Dict[str, Any]:
        cache_key = "portfolio_context"

        if self._is_cache_valid(cache_key):
            return self._context_cache[cache_key]['data']

        try:
            portfolio_context = {}

            if self.backtester:
                try:
                    portfolio_context['summary'] = {
                        'status': 'No recent portfolio data available',
                        'last_updated': datetime.now().isoformat(),
                        'note': 'Run trading analysis to get current portfolio data'
                    }
                except Exception as e:
                    self.logger.warning(f"Could not get portfolio summary: {str(e)}")

            symbols = self.config.get('stocks', {}).get('symbols', [])
            portfolio_context['tracked_symbols'] = symbols
            portfolio_context['symbol_count'] = len(symbols)

            self._cache_data(cache_key, portfolio_context)
            return portfolio_context

        except Exception as e:
            self.logger.error(f"Error getting portfolio context: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def get_market_context(self) -> Dict[str, Any]:
        cache_key = "market_context"

        if self._is_cache_valid(cache_key):
            return self._context_cache[cache_key]['data']

        try:
            market_context = {}

            market_config = self.config.get('market', {})
            market_context['market'] = market_config.get('name', 'NIFTY 50')
            market_context['currency'] = market_config.get('currency', 'INR')
            market_context['timezone'] = market_config.get('timezone', 'Asia/Kolkata')

            trading_hours = market_config.get('trading_hours', {})
            market_context['trading_hours'] = trading_hours

            now = datetime.now()
            market_context['current_time'] = now.isoformat()
            market_context['is_trading_day'] = now.weekday() < 5

            data_source = self.config.get('data_source', {})
            market_context['data_source'] = data_source.get('provider', 'yfinance')

            self._cache_data(cache_key, market_context)
            return market_context

        except Exception as e:
            self.logger.error(f"Error getting market context: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def get_signal_context(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        cache_key = f"signal_context_{symbol or 'all'}"

        if self._is_cache_valid(cache_key):
            return self._context_cache[cache_key]['data']

        try:
            signals_context = []

            ml_config = self.config.get('ml', {})
            if ml_config.get('enabled', False):
                signals_context.append({
                    'type': 'ML_ENABLED',
                    'model_type': ml_config.get('model_type', 'ensemble'),
                    'confidence_threshold': ml_config.get('confidence_threshold', 0.6),
                    'timestamp': datetime.now().isoformat(),
                    'note': 'ML signal generation is enabled'
                })

            signal_config = self.config.get('signals', {})
            enabled_signals = []

            for signal_type, config in signal_config.items():
                if isinstance(config, dict) and config.get('enabled', False):
                    enabled_signals.append({
                        'type': signal_type.upper(),
                        'parameters': config,
                        'enabled': True
                    })

            if enabled_signals:
                signals_context.extend(enabled_signals)

            signals_context.append({
                'type': 'INFO',
                'message': 'Recent signals would be available after running trading analysis',
                'timestamp': datetime.now().isoformat()
            })

            self._cache_data(cache_key, signals_context)
            return signals_context

        except Exception as e:
            self.logger.error(f"Error getting signal context: {str(e)}")
            return [{'error': str(e), 'timestamp': datetime.now().isoformat()}]

    def get_performance_context(self) -> Dict[str, Any]:
        cache_key = "performance_context"

        if self._is_cache_valid(cache_key):
            return self._context_cache[cache_key]['data']

        try:
            performance_context = {}

            backtest_config = self.config.get('backtesting', {})
            performance_context['backtest_period'] = backtest_config.get('period', '1y')
            performance_context['initial_capital'] = backtest_config.get('initial_capital', 100000)
            performance_context['transaction_cost'] = backtest_config.get('transaction_cost', 0.001)

            performance_context['metrics'] = {
                'note': 'Performance metrics available after running analysis',
                'available_metrics': [
                    'total_return',
                    'sharpe_ratio',
                    'max_drawdown',
                    'win_rate',
                    'profit_factor',
                    'total_trades'
                ]
            }

            performance_context['last_updated'] = datetime.now().isoformat()

            self._cache_data(cache_key, performance_context)
            return performance_context

        except Exception as e:
            self.logger.error(f"Error getting performance context: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def get_technical_indicators_context(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        cache_key = f"indicators_context_{symbol or 'all'}"

        if self._is_cache_valid(cache_key):
            return self._context_cache[cache_key]['data']

        try:
            indicators_context = {}

            indicators_config = self.config.get('indicators', {})

            rsi_config = indicators_config.get('rsi', {})
            if rsi_config.get('enabled', False):
                indicators_context['rsi'] = {
                    'enabled': True,
                    'period': rsi_config.get('period', 14),
                    'overbought': rsi_config.get('overbought', 70),
                    'oversold': rsi_config.get('oversold', 30)
                }

            macd_config = indicators_config.get('macd', {})
            if macd_config.get('enabled', False):
                indicators_context['macd'] = {
                    'enabled': True,
                    'fast_period': macd_config.get('fast_period', 12),
                    'slow_period': macd_config.get('slow_period', 26),
                    'signal_period': macd_config.get('signal_period', 9)
                }

            bb_config = indicators_config.get('bollinger_bands', {})
            if bb_config.get('enabled', False):
                indicators_context['bollinger_bands'] = {
                    'enabled': True,
                    'period': bb_config.get('period', 20),
                    'std_dev': bb_config.get('std_dev', 2)
                }

            ma_config = indicators_config.get('moving_averages', {})
            if ma_config.get('enabled', False):
                indicators_context['moving_averages'] = {
                    'enabled': True,
                    'short_period': ma_config.get('short_period', 10),
                    'long_period': ma_config.get('long_period', 50)
                }

            indicators_context['note'] = 'Current indicator values available after fetching latest data'
            indicators_context['timestamp'] = datetime.now().isoformat()

            self._cache_data(cache_key, indicators_context)
            return indicators_context

        except Exception as e:
            self.logger.error(f"Error getting indicators context: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def aggregate_context(self, query_type: str = 'general') -> Dict[str, Any]:
        try:
            context = {
                'query_type': query_type,
                'timestamp': datetime.now().isoformat(),
                'portfolio': self.get_portfolio_context(),
                'market': self.get_market_context(),
                'signals': self.get_signal_context(),
                'performance': self.get_performance_context(),
                'indicators': self.get_technical_indicators_context()
            }

            if query_type == 'portfolio':
                context['focus'] = 'portfolio_analysis'
            elif query_type == 'signals':
                context['focus'] = 'signal_analysis'
            elif query_type == 'market':
                context['focus'] = 'market_analysis'
            else:
                context['focus'] = 'general_trading'

            return context

        except Exception as e:
            self.logger.error(f"Error aggregating context: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'query_type': query_type
            }

    def update_context_from_trading_system(self, trading_results: Dict[str, Any]):
        try:
            if 'portfolio_summary' in trading_results:
                self._cache_data('portfolio_context', {
                    'summary': trading_results['portfolio_summary'],
                    'last_updated': datetime.now().isoformat(),
                    'source': 'trading_system_update'
                })

            if 'current_signals' in trading_results:
                self._cache_data('signal_context_all', trading_results['current_signals'])

            if 'backtest_results' in trading_results:
                performance_data = {
                    'backtest_results': trading_results['backtest_results'],
                    'last_updated': datetime.now().isoformat(),
                    'source': 'trading_system_update'
                }
                self._cache_data('performance_context', performance_data)

            self.logger.info("Context updated with fresh trading system results")

        except Exception as e:
            self.logger.error(f"Error updating context from trading system: {str(e)}")

    def _is_cache_valid(self, cache_key: str) -> bool:
        if cache_key not in self._context_cache:
            return False

        cache_entry = self._context_cache[cache_key]
        cache_age = datetime.now() - cache_entry['timestamp']

        return cache_age.total_seconds() < self._cache_ttl

    def _cache_data(self, cache_key: str, data: Any):
        self._context_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }

    def clear_cache(self):
        self._context_cache.clear()
        self.logger.info("Context cache cleared")

    def get_health_status(self) -> Dict[str, Any]:
        return {
            'status': 'healthy',
            'cache_entries': len(self._context_cache),
            'cache_ttl_seconds': self._cache_ttl,
            'components': {
                'data_fetcher': 'initialized' if self.data_fetcher else 'failed',
                'indicators': 'initialized' if self.indicators else 'failed',
                'backtester': 'initialized' if self.backtester else 'failed'
            },
            'config_loaded': bool(self.config),
            'timestamp': datetime.now().isoformat()
        }