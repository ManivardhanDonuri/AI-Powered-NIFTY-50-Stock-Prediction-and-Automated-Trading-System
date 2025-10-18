import logging
import json
import sys
from datetime import datetime
import traceback

from data_fetcher import DataFetcher
from technical_indicators import TechnicalIndicators
from ml_signal_generator_enhanced import EnhancedMLSignalGenerator
from backtester import Backtester
from google_sheets_logger import GoogleSheetsLogger
from ml_trainer import MLTrainer

class TradingSystem:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_system.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.data_fetcher = DataFetcher(config_file)
        self.indicators = TechnicalIndicators(config_file)

        self.signal_generator = EnhancedMLSignalGenerator(config_file)
        self.logger.info("Using Enhanced ML Signal Generator")

        self.backtester = Backtester(config_file)
        self.sheets_logger = GoogleSheetsLogger(config_file)
        self.ml_trainer = MLTrainer(config_file)

        self.logger.info("Trading system initialized successfully")

    def run_complete_analysis(self):
        try:
            self.logger.info("Starting complete trading analysis...")

            self.logger.info("Step 1: Fetching historical data...")
            stock_data = self.data_fetcher.fetch_all_stocks_data()

            if not stock_data:
                self.logger.error("No stock data fetched. Exiting.")
                return False

            self.logger.info("Step 2: Calculating technical indicators...")
            indicators_data = self.indicators.calculate_all_indicators(stock_data)

            if not indicators_data:
                self.logger.error("No indicators calculated. Exiting.")
                return False

            self.logger.info("Step 3: Generating trading signals...")
            all_signals = self.signal_generator.generate_signals(indicators_data)

            self.logger.info("Step 4: Running backtest...")
            backtest_results = self.backtester.run_backtest(indicators_data, all_signals)

            self.logger.info("Step 5: Checking current signals...")
            current_indicators = self.indicators.get_current_indicators(indicators_data)
            current_signals = self.signal_generator.check_current_signals(current_indicators)

            portfolio_summary = self.backtester.get_portfolio_summary(backtest_results)

            if hasattr(self.signal_generator, 'send_portfolio_summary_notification') and portfolio_summary:
                self.logger.info("Step 6.5: Sending portfolio summary notification...")
                self.signal_generator.send_portfolio_summary_notification(portfolio_summary)

            self.logger.info("Step 7: Logging to Google Sheets...")
            self._log_to_sheets(backtest_results, current_signals, portfolio_summary)

            # Skip visualization generation
            self.logger.info("Step 8: Skipping visualization generation (disabled)")

            self._print_summary(backtest_results, current_signals, portfolio_summary)

            self.logger.info("Complete trading analysis finished successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Error in complete analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def _log_to_sheets(self, backtest_results, current_signals, portfolio_summary):
        try:
            if backtest_results:
                self.sheets_logger.log_trades(backtest_results)
                self.sheets_logger.log_pnl_summary(backtest_results)

            if portfolio_summary:
                self.sheets_logger.log_portfolio_summary(portfolio_summary)

            if current_signals:
                self.sheets_logger.log_current_signals(current_signals)

        except Exception as e:
            self.logger.error(f"Error logging to sheets: {str(e)}")

    def _generate_visualizations(self, backtest_results, indicators_data, all_signals):
        # Visualization generation disabled
        self.logger.info("Visualization generation is disabled")
        pass

    def _print_summary(self, backtest_results, current_signals, portfolio_summary):
        print("\n" + "="*60)
        print("TRADING SYSTEM ANALYSIS SUMMARY")
        print("="*60)

        if current_signals:
            print(f"\n🔔 CURRENT SIGNALS ({len(current_signals)}):")
            for symbol, signal in current_signals.items():
                print(f"  {symbol}: {signal['type']} at ₹{signal['price']:.2f} - {signal['reason']}")
        else:
            print("\n🔔 CURRENT SIGNALS: None")

        if backtest_results:
            print(f"\n📊 BACKTEST RESULTS ({len(backtest_results)} symbols):")
            for symbol, result in backtest_results.items():
                print(f"  {symbol}: {result['total_trades']} trades, "
                      f"Win Rate: {result['win_rate']:.1f}%, "
                      f"P&L: ₹{result['total_pnl']:.2f}")

        if portfolio_summary:
            print(f"\n💰 PORTFOLIO SUMMARY:")
            print(f"  Total Trades: {portfolio_summary['total_trades']}")
            print(f"  Win Rate: {portfolio_summary['win_rate']:.2f}%")
            print(f"  Total P&L: ₹{portfolio_summary['total_pnl']:.2f}")
            print(f"  Sharpe Ratio: {portfolio_summary['sharpe_ratio']:.2f}")

        print("\n" + "="*60)

    def run_daily_monitoring(self):
        try:
            self.logger.info("Running daily monitoring...")

            stock_data = self.data_fetcher.fetch_all_stocks_data()
            indicators_data = self.indicators.calculate_all_indicators(stock_data)

            current_indicators = self.indicators.get_current_indicators(indicators_data)
            current_signals = self.signal_generator.check_current_signals(current_indicators)

            self.logger.info(f"Daily monitoring completed. Found {len(current_signals)} signals.")
            return True

        except Exception as e:
            self.logger.error(f"Error in daily monitoring: {str(e)}")
            return False

    def train_ml_models(self):
        try:
            self.logger.info("Starting ML model training...")

            trained_models = self.ml_trainer.train_all_models()

            if trained_models:
                self.logger.info("ML model training completed successfully!")
                return True
            else:
                self.logger.error("ML model training failed!")
                return False

        except Exception as e:
            self.logger.error(f"Error in ML training: {str(e)}")
            return False

    def run_dashboard(self):
        try:
            self.logger.info("Web dashboard functionality has been moved to the Next.js frontend.")
            self.logger.info("Please run the frontend application instead:")
            self.logger.info("cd trading-frontend && npm run dev")
            self.logger.info("Then visit http://localhost:3000")
            return True

        except Exception as e:
            self.logger.error(f"Error launching dashboard: {str(e)}")
            return False

    def test_notifications(self):
        try:
            self.logger.info("Testing notification services...")

            if hasattr(self.signal_generator, 'test_notifications'):
                results = self.signal_generator.test_notifications()

                print("\n📱 NOTIFICATION TEST RESULTS")
                print("="*40)

                for service, success in results.items():
                    status = "✅ SUCCESS" if success else "❌ FAILED"
                    print(f"{service.upper()}: {status}")

                if hasattr(self.signal_generator, 'get_notification_status'):
                    status = self.signal_generator.get_notification_status()
                    print(f"\nNotification System Enabled: {status.get('enabled', False)}")

                return all(results.values()) if results else False
            else:
                print("❌ Notification system not available")
                return False

        except Exception as e:
            self.logger.error(f"Error testing notifications: {str(e)}")
            return False