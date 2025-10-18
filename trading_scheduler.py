
import time
import schedule
import threading
import logging
import json
from datetime import datetime, time as dt_time
from typing import Dict, Any
import sys
import traceback

from trading_system import TradingSystem

class TradingScheduler:

    def __init__(self, config_file='config.json'):
        self.config_file = config_file

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_scheduler.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.trading_system = TradingSystem(config_file)

        self.is_running = False
        self.scheduler_thread = None

        self.market_open = dt_time(9, 15)
        self.market_close = dt_time(15, 30)

        self.notifications_enabled = self.config.get('notifications', {}).get('enabled', False)

        self.logger.info("Trading scheduler initialized")

    def setup_schedule(self):
        self.logger.info("Setting up automated trading schedule...")

        schedule.every(5).minutes.do(self._run_market_monitoring)

        schedule.every().day.at("16:00").do(self._run_daily_analysis)

        schedule.every().day.at("18:00").do(self._send_portfolio_summary)

        schedule.every().sunday.at("02:00").do(self._retrain_models)

        schedule.every().hour.do(self._health_check)

        self.logger.info("Schedule configured:")
        self.logger.info("- Market monitoring: Every 5 minutes during market hours")
        self.logger.info("- Daily analysis: 4:00 PM")
        self.logger.info("- Portfolio summary: 6:00 PM")
        self.logger.info("- Model retraining: Sunday 2:00 AM")
        self.logger.info("- Health checks: Every hour")

    def start(self):
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return

        self.setup_schedule()
        self.is_running = True

        if self.notifications_enabled:
            self._send_startup_notification()

        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

        self.logger.info("🚀 Automated trading scheduler started!")
        self.logger.info("The system will now monitor markets and send notifications automatically.")

        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        if not self.is_running:
            return

        self.logger.info("Stopping automated scheduler...")
        self.is_running = False

        if self.notifications_enabled:
            self._send_shutdown_notification()

        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)

        self.logger.info("Automated scheduler stopped")

    def _run_scheduler(self):
        self.logger.info("Scheduler thread started")

        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(30)
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {str(e)}")
                self.logger.error(traceback.format_exc())
                time.sleep(60)

        self.logger.info("Scheduler thread stopped")

    def _is_market_hours(self) -> bool:
        now = datetime.now().time()

        if datetime.now().weekday() >= 5:
            return False

        return self.market_open <= now <= self.market_close

    def _run_market_monitoring(self):
        try:
            if not self._is_market_hours():
                return

            self.logger.info("🔍 Running automated market monitoring...")

            success = self.trading_system.run_daily_monitoring()

            if success:
                self.logger.info("✅ Market monitoring completed successfully")
            else:
                self.logger.error("❌ Market monitoring failed")

                if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                    self.trading_system.signal_generator.send_system_alert(
                        'error',
                        'Market monitoring failed. Check system logs.',
                        'urgent'
                    )

        except Exception as e:
            self.logger.error(f"Error in market monitoring: {str(e)}")
            self.logger.error(traceback.format_exc())

    def _run_daily_analysis(self):
        try:
            self.logger.info("📊 Running automated daily analysis...")

            success = self.trading_system.run_complete_analysis()

            if success:
                self.logger.info("✅ Daily analysis completed successfully")

                if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                    self.trading_system.signal_generator.send_system_alert(
                        'success',
                        'Daily trading analysis completed successfully. Check logs for details.',
                        'normal'
                    )
            else:
                self.logger.error("❌ Daily analysis failed")

                if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                    self.trading_system.signal_generator.send_system_alert(
                        'error',
                        'Daily analysis failed. Check system logs for details.',
                        'urgent'
                    )

        except Exception as e:
            self.logger.error(f"Error in daily analysis: {str(e)}")
            self.logger.error(traceback.format_exc())

    def _send_portfolio_summary(self):
        try:
            self.logger.info("📈 Sending automated portfolio summary...")

            if not self.notifications_enabled:
                self.logger.info("Notifications disabled, skipping portfolio summary")
                return

            stock_data = self.trading_system.data_fetcher.fetch_all_stocks_data()
            if not stock_data:
                self.logger.warning("No stock data available for portfolio summary")
                return

            indicators_data = self.trading_system.indicators.calculate_all_indicators(stock_data)
            if not indicators_data:
                self.logger.warning("No indicators data available for portfolio summary")
                return

            all_signals = self.trading_system.signal_generator.generate_signals(indicators_data)
            backtest_results = self.trading_system.backtester.run_backtest(indicators_data, all_signals)
            portfolio_summary = self.trading_system.backtester.get_portfolio_summary(backtest_results)

            if portfolio_summary and hasattr(self.trading_system.signal_generator, 'send_portfolio_summary_notification'):
                success = self.trading_system.signal_generator.send_portfolio_summary_notification(portfolio_summary)

                if success:
                    self.logger.info("✅ Portfolio summary sent successfully")
                else:
                    self.logger.error("❌ Failed to send portfolio summary")

        except Exception as e:
            self.logger.error(f"Error sending portfolio summary: {str(e)}")
            self.logger.error(traceback.format_exc())

    def _retrain_models(self):
        try:
            self.logger.info("🧠 Starting automated model retraining...")

            if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                self.trading_system.signal_generator.send_system_alert(
                    'info',
                    'Starting weekly ML model retraining. This may take some time.',
                    'normal'
                )

            success = self.trading_system.train_ml_models()

            if success:
                self.logger.info("✅ Model retraining completed successfully")

                if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                    self.trading_system.signal_generator.send_system_alert(
                        'success',
                        'Weekly ML model retraining completed successfully. Models updated with latest data.',
                        'normal'
                    )
            else:
                self.logger.error("❌ Model retraining failed")

                if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                    self.trading_system.signal_generator.send_system_alert(
                        'error',
                        'Weekly ML model retraining failed. Check system logs.',
                        'high'
                    )

        except Exception as e:
            self.logger.error(f"Error in model retraining: {str(e)}")
            self.logger.error(traceback.format_exc())

    def _health_check(self):
        try:
            self.logger.info("🏥 Running system health check...")

            health_issues = []

            if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'get_notification_status'):
                status = self.trading_system.signal_generator.get_notification_status()

                if not status.get('enabled', False):
                    health_issues.append("Notification system is disabled")

                services = status.get('services', {})
                for service_name, service_status in services.items():
                    if service_status.get('enabled', False) and not service_status.get('connection_valid', False):
                        health_issues.append(f"{service_name.title()} service connection failed")

            try:
                stock_data = self.trading_system.data_fetcher.fetch_all_stocks_data()
                if not stock_data:
                    health_issues.append("No stock data available")
            except Exception as e:
                health_issues.append(f"Data fetching error: {str(e)}")

            if health_issues:
                self.logger.warning(f"Health check found {len(health_issues)} issues:")
                for issue in health_issues:
                    self.logger.warning(f"  - {issue}")

                if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                    self.trading_system.signal_generator.send_system_alert(
                        'warning',
                        f"System health check found {len(health_issues)} issues: " + "; ".join(health_issues[:3]),
                        'normal'
                    )
            else:
                self.logger.info("✅ System health check passed")

        except Exception as e:
            self.logger.error(f"Error in health check: {str(e)}")
            self.logger.error(traceback.format_exc())

    def _send_startup_notification(self):
        try:
            if hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                self.trading_system.signal_generator.send_system_alert(
                    'success',
                    '🚀 Automated trading system started! Market monitoring and notifications are now active.',
                    'normal'
                )
        except Exception as e:
            self.logger.error(f"Error sending startup notification: {str(e)}")

    def _send_shutdown_notification(self):
        try:
            if hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                self.trading_system.signal_generator.send_system_alert(
                    'warning',
                    '⏹️ Automated trading system stopped. Market monitoring is no longer active.',
                    'high'
                )
        except Exception as e:
            self.logger.error(f"Error sending shutdown notification: {str(e)}")

def main():
    print("🤖 AUTOMATED TRADING SYSTEM SCHEDULER")
    print("=" * 50)
    print("This will run continuously and monitor markets automatically.")
    print("Press Ctrl+C to stop the scheduler.\n")

    scheduler = TradingScheduler()

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping scheduler...")
        scheduler.stop()
        print("✅ Scheduler stopped successfully!")

if __name__ == "__main__":
    main()