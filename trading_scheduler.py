"""
Automated Trading System Scheduler

Runs continuously to monitor markets and send notifications automatically.
"""

import time
import schedule
import threading
import logging
import json
from datetime import datetime, time as dt_time
from typing import Dict, Any
import sys
import traceback

from main import TradingSystem

class TradingScheduler:
    """Automated scheduler for trading system with notifications."""
    
    def __init__(self, config_file='config.json'):
        """Initialize the trading scheduler."""
        self.config_file = config_file
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_scheduler.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Initialize trading system
        self.trading_system = TradingSystem(config_file)
        
        # Scheduler settings
        self.is_running = False
        self.scheduler_thread = None
        
        # Market hours (Indian Stock Exchange)
        self.market_open = dt_time(9, 15)  # 9:15 AM
        self.market_close = dt_time(15, 30)  # 3:30 PM
        
        # Notification settings
        self.notifications_enabled = self.config.get('notifications', {}).get('enabled', False)
        
        self.logger.info("Trading scheduler initialized")
    
    def setup_schedule(self):
        """Setup the automated schedule."""
        self.logger.info("Setting up automated trading schedule...")
        
        # Market monitoring during trading hours (every 5 minutes)
        schedule.every(5).minutes.do(self._run_market_monitoring)
        
        # Daily analysis after market close (4:00 PM)
        schedule.every().day.at("16:00").do(self._run_daily_analysis)
        
        # Portfolio summary (6:00 PM daily)
        schedule.every().day.at("18:00").do(self._send_portfolio_summary)
        
        # Weekly model retraining (Sunday 2:00 AM)
        schedule.every().sunday.at("02:00").do(self._retrain_models)
        
        # System health check (every hour)
        schedule.every().hour.do(self._health_check)
        
        self.logger.info("Schedule configured:")
        self.logger.info("- Market monitoring: Every 5 minutes during market hours")
        self.logger.info("- Daily analysis: 4:00 PM")
        self.logger.info("- Portfolio summary: 6:00 PM")
        self.logger.info("- Model retraining: Sunday 2:00 AM")
        self.logger.info("- Health checks: Every hour")
    
    def start(self):
        """Start the automated scheduler."""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.setup_schedule()
        self.is_running = True
        
        # Send startup notification
        if self.notifications_enabled:
            self._send_startup_notification()
        
        # Start scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("🚀 Automated trading scheduler started!")
        self.logger.info("The system will now monitor markets and send notifications automatically.")
        
        # Keep main thread alive
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the automated scheduler."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping automated scheduler...")
        self.is_running = False
        
        # Send shutdown notification
        if self.notifications_enabled:
            self._send_shutdown_notification()
        
        # Wait for scheduler thread to finish
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Automated scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop."""
        self.logger.info("Scheduler thread started")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {str(e)}")
                self.logger.error(traceback.format_exc())
                time.sleep(60)  # Wait before retrying
        
        self.logger.info("Scheduler thread stopped")
    
    def _is_market_hours(self) -> bool:
        """Check if current time is within market hours."""
        now = datetime.now().time()
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if datetime.now().weekday() >= 5:  # Saturday or Sunday
            return False
        
        return self.market_open <= now <= self.market_close
    
    def _run_market_monitoring(self):
        """Run market monitoring during trading hours."""
        try:
            # Only run during market hours
            if not self._is_market_hours():
                return
            
            self.logger.info("🔍 Running automated market monitoring...")
            
            # Run daily monitoring (checks for current signals)
            success = self.trading_system.run_daily_monitoring()
            
            if success:
                self.logger.info("✅ Market monitoring completed successfully")
            else:
                self.logger.error("❌ Market monitoring failed")
                
                # Send error notification
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
        """Run complete daily analysis after market close."""
        try:
            self.logger.info("📊 Running automated daily analysis...")
            
            # Run complete analysis
            success = self.trading_system.run_complete_analysis()
            
            if success:
                self.logger.info("✅ Daily analysis completed successfully")
                
                # Send success notification
                if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                    self.trading_system.signal_generator.send_system_alert(
                        'success',
                        'Daily trading analysis completed successfully. Check logs for details.',
                        'normal'
                    )
            else:
                self.logger.error("❌ Daily analysis failed")
                
                # Send error notification
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
        """Send daily portfolio summary."""
        try:
            self.logger.info("📈 Sending automated portfolio summary...")
            
            if not self.notifications_enabled:
                self.logger.info("Notifications disabled, skipping portfolio summary")
                return
            
            # Get latest portfolio data by running a quick analysis
            stock_data = self.trading_system.data_fetcher.fetch_all_stocks_data()
            if not stock_data:
                self.logger.warning("No stock data available for portfolio summary")
                return
            
            indicators_data = self.trading_system.indicators.calculate_all_indicators(stock_data)
            if not indicators_data:
                self.logger.warning("No indicators data available for portfolio summary")
                return
            
            # Generate signals for portfolio calculation
            all_signals = self.trading_system.signal_generator.generate_signals(indicators_data)
            backtest_results = self.trading_system.backtester.run_backtest(indicators_data, all_signals)
            portfolio_summary = self.trading_system.backtester.get_portfolio_summary(backtest_results)
            
            # Send portfolio summary notification
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
        """Retrain ML models weekly."""
        try:
            self.logger.info("🧠 Starting automated model retraining...")
            
            # Send notification about retraining start
            if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                self.trading_system.signal_generator.send_system_alert(
                    'info',
                    'Starting weekly ML model retraining. This may take some time.',
                    'normal'
                )
            
            # Run model training
            success = self.trading_system.train_ml_models()
            
            if success:
                self.logger.info("✅ Model retraining completed successfully")
                
                # Send success notification
                if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'send_system_alert'):
                    self.trading_system.signal_generator.send_system_alert(
                        'success',
                        'Weekly ML model retraining completed successfully. Models updated with latest data.',
                        'normal'
                    )
            else:
                self.logger.error("❌ Model retraining failed")
                
                # Send error notification
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
        """Perform system health check."""
        try:
            self.logger.info("🏥 Running system health check...")
            
            health_issues = []
            
            # Check notification system health
            if self.notifications_enabled and hasattr(self.trading_system.signal_generator, 'get_notification_status'):
                status = self.trading_system.signal_generator.get_notification_status()
                
                if not status.get('enabled', False):
                    health_issues.append("Notification system is disabled")
                
                # Check individual services
                services = status.get('services', {})
                for service_name, service_status in services.items():
                    if service_status.get('enabled', False) and not service_status.get('connection_valid', False):
                        health_issues.append(f"{service_name.title()} service connection failed")
            
            # Check data availability
            try:
                stock_data = self.trading_system.data_fetcher.fetch_all_stocks_data()
                if not stock_data:
                    health_issues.append("No stock data available")
            except Exception as e:
                health_issues.append(f"Data fetching error: {str(e)}")
            
            # Report health status
            if health_issues:
                self.logger.warning(f"Health check found {len(health_issues)} issues:")
                for issue in health_issues:
                    self.logger.warning(f"  - {issue}")
                
                # Send warning notification for critical issues
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
        """Send notification when scheduler starts."""
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
        """Send notification when scheduler stops."""
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
    """Main function to run the automated scheduler."""
    print("🤖 AUTOMATED TRADING SYSTEM SCHEDULER")
    print("=" * 50)
    print("This will run continuously and monitor markets automatically.")
    print("Press Ctrl+C to stop the scheduler.\n")
    
    # Initialize and start scheduler
    scheduler = TradingScheduler()
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping scheduler...")
        scheduler.stop()
        print("✅ Scheduler stopped successfully!")

if __name__ == "__main__":
    main()