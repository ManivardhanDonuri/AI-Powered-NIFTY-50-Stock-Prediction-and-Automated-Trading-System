"""
Learning Scheduler Service for AI Trading Assistant.

This service runs scheduled learning and adaptation tasks including accuracy tracking,
retraining evaluation, and performance pattern analysis.
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading

from ..engines.learning_adaptation_engine import LearningAdaptationEngine
from ..logging.audit_logger import get_audit_logger
from data_fetcher import DataFetcher


class LearningScheduler:
    """
    Scheduler for automated learning and adaptation tasks.
    
    Runs background tasks to continuously monitor and improve model performance.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.learning_engine = LearningAdaptationEngine()
        self.audit_logger = get_audit_logger()
        self.data_fetcher = DataFetcher()
        
        self.is_running = False
        self.scheduler_thread = None
        
        # Configuration
        self.tracked_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]  # Default symbols to track
        self.accuracy_check_interval_hours = 6  # Check accuracy every 6 hours
        self.retraining_evaluation_interval_hours = 24  # Evaluate retraining daily
        self.pattern_analysis_interval_hours = 168  # Analyze patterns weekly
        
        self.logger.info("Learning Scheduler initialized")

    def start(self):
        """Start the learning scheduler."""
        if self.is_running:
            self.logger.warning("Learning scheduler is already running")
            return
        
        self.logger.info("Starting learning scheduler")
        
        # Schedule tasks
        self._schedule_tasks()
        
        # Start scheduler in background thread
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Learning scheduler started successfully")

    def stop(self):
        """Stop the learning scheduler."""
        if not self.is_running:
            self.logger.warning("Learning scheduler is not running")
            return
        
        self.logger.info("Stopping learning scheduler")
        self.is_running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        self.logger.info("Learning scheduler stopped")

    def _schedule_tasks(self):
        """Schedule all learning and adaptation tasks."""
        # Schedule accuracy tracking every 6 hours
        schedule.every(self.accuracy_check_interval_hours).hours.do(self._run_accuracy_tracking)
        
        # Schedule retraining evaluation daily at 2 AM
        schedule.every().day.at("02:00").do(self._run_retraining_evaluation)
        
        # Schedule performance pattern analysis weekly on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(self._run_pattern_analysis)
        
        # Schedule cleanup of old data monthly
        schedule.every().month.do(self._run_data_cleanup)
        
        self.logger.info("Learning tasks scheduled:")
        self.logger.info(f"- Accuracy tracking: Every {self.accuracy_check_interval_hours} hours")
        self.logger.info("- Retraining evaluation: Daily at 2:00 AM")
        self.logger.info("- Pattern analysis: Weekly on Sunday at 3:00 AM")
        self.logger.info("- Data cleanup: Monthly")

    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)

    def _run_accuracy_tracking(self):
        """Run accuracy tracking for all monitored symbols."""
        try:
            self.logger.info("🎯 Starting scheduled accuracy tracking")
            
            # Run accuracy tracking asynchronously
            asyncio.create_task(self._async_accuracy_tracking())
            
        except Exception as e:
            self.logger.error(f"Error in scheduled accuracy tracking: {str(e)}")

    def _run_retraining_evaluation(self):
        """Run retraining evaluation for all symbols."""
        try:
            self.logger.info("🧠 Starting scheduled retraining evaluation")
            
            # Run retraining evaluation asynchronously
            asyncio.create_task(self._async_retraining_evaluation())
            
        except Exception as e:
            self.logger.error(f"Error in scheduled retraining evaluation: {str(e)}")

    def _run_pattern_analysis(self):
        """Run performance pattern analysis."""
        try:
            self.logger.info("📊 Starting scheduled pattern analysis")
            
            # Run pattern analysis asynchronously
            asyncio.create_task(self._async_pattern_analysis())
            
        except Exception as e:
            self.logger.error(f"Error in scheduled pattern analysis: {str(e)}")

    def _run_data_cleanup(self):
        """Run data cleanup to remove old records."""
        try:
            self.logger.info("🧹 Starting scheduled data cleanup")
            
            # Run data cleanup asynchronously
            asyncio.create_task(self._async_data_cleanup())
            
        except Exception as e:
            self.logger.error(f"Error in scheduled data cleanup: {str(e)}")

    async def _async_accuracy_tracking(self):
        """Asynchronously track accuracy for all symbols."""
        try:
            timeframes = ["1d", "3d", "7d", "30d"]
            
            for symbol in self.tracked_symbols:
                for timeframe in timeframes:
                    try:
                        result = await self.learning_engine.track_prediction_accuracy(symbol, timeframe)
                        
                        if 'error' not in result:
                            self.logger.info(f"✅ Accuracy tracked for {symbol} {timeframe}")
                        else:
                            self.logger.warning(f"⚠️ Accuracy tracking failed for {symbol} {timeframe}: {result['error']}")
                            
                    except Exception as e:
                        self.logger.error(f"Error tracking accuracy for {symbol} {timeframe}: {str(e)}")
                    
                    # Small delay to avoid overwhelming the system
                    await asyncio.sleep(1)
            
            self.logger.info("Scheduled accuracy tracking completed")
            
        except Exception as e:
            self.logger.error(f"Error in async accuracy tracking: {str(e)}")

    async def _async_retraining_evaluation(self):
        """Asynchronously evaluate retraining needs."""
        try:
            # Evaluate retraining need for all symbols
            evaluation_result = await self.learning_engine.evaluate_retraining_need()
            
            if 'error' not in evaluation_result:
                symbols_needing_retraining = evaluation_result.get('symbols_needing_retraining', 0)
                
                if symbols_needing_retraining > 0:
                    self.logger.info(f"🔄 {symbols_needing_retraining} symbols need retraining")
                    
                    # Trigger retraining for symbols that need it
                    for recommendation in evaluation_result.get('retraining_recommendations', []):
                        if recommendation.get('recommended_action') == 'retrain':
                            symbol = recommendation['symbol']
                            
                            try:
                                retraining_result = await self.learning_engine.trigger_model_retraining(symbol)
                                
                                if 'error' not in retraining_result:
                                    success_rate = retraining_result.get('success_rate', 0)
                                    self.logger.info(f"🎯 Retraining completed for {symbol}: {success_rate:.1%} success rate")
                                else:
                                    self.logger.error(f"❌ Retraining failed for {symbol}: {retraining_result['error']}")
                                    
                            except Exception as e:
                                self.logger.error(f"Error retraining {symbol}: {str(e)}")
                            
                            # Delay between retraining to avoid system overload
                            await asyncio.sleep(30)
                else:
                    self.logger.info("✅ No symbols need retraining at this time")
            else:
                self.logger.error(f"Retraining evaluation failed: {evaluation_result['error']}")
            
            self.logger.info("Scheduled retraining evaluation completed")
            
        except Exception as e:
            self.logger.error(f"Error in async retraining evaluation: {str(e)}")

    async def _async_pattern_analysis(self):
        """Asynchronously analyze performance patterns."""
        try:
            # Analyze patterns for all symbols
            pattern_result = await self.learning_engine.identify_performance_patterns()
            
            if 'error' not in pattern_result:
                symbols_analyzed = pattern_result.get('total_symbols_analyzed', 0)
                self.logger.info(f"📈 Performance patterns analyzed for {symbols_analyzed} symbols")
                
                # Log key findings
                individual_patterns = pattern_result.get('individual_patterns', [])
                for pattern in individual_patterns:
                    symbol = pattern['symbol']
                    recommendations = pattern.get('recommendations', [])
                    
                    if recommendations:
                        self.logger.info(f"💡 Recommendations for {symbol}: {', '.join(recommendations)}")
                
                # Log cross-symbol patterns
                cross_patterns = pattern_result.get('cross_symbol_patterns', {})
                overall_trend = cross_patterns.get('overall_trend', 'unknown')
                self.logger.info(f"🌐 Overall market trend: {overall_trend}")
                
            else:
                self.logger.error(f"Pattern analysis failed: {pattern_result['error']}")
            
            self.logger.info("Scheduled pattern analysis completed")
            
        except Exception as e:
            self.logger.error(f"Error in async pattern analysis: {str(e)}")

    async def _async_data_cleanup(self):
        """Asynchronously clean up old data."""
        try:
            # Clean up data older than 90 days
            cleanup_result = await self.audit_logger.cleanup_old_data(days_to_keep=90)
            
            records_deleted = cleanup_result.get('records_deleted', 0)
            self.logger.info(f"🗑️ Data cleanup completed: {records_deleted} old records removed")
            
        except Exception as e:
            self.logger.error(f"Error in async data cleanup: {str(e)}")

    def add_symbol_to_tracking(self, symbol: str):
        """Add a symbol to the tracking list."""
        if symbol not in self.tracked_symbols:
            self.tracked_symbols.append(symbol)
            self.logger.info(f"Added {symbol} to learning tracking")

    def remove_symbol_from_tracking(self, symbol: str):
        """Remove a symbol from the tracking list."""
        if symbol in self.tracked_symbols:
            self.tracked_symbols.remove(symbol)
            self.logger.info(f"Removed {symbol} from learning tracking")

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the learning scheduler."""
        return {
            'is_running': self.is_running,
            'tracked_symbols': self.tracked_symbols,
            'configuration': {
                'accuracy_check_interval_hours': self.accuracy_check_interval_hours,
                'retraining_evaluation_interval_hours': self.retraining_evaluation_interval_hours,
                'pattern_analysis_interval_hours': self.pattern_analysis_interval_hours
            },
            'next_scheduled_tasks': [str(job) for job in schedule.jobs],
            'timestamp': datetime.now().isoformat()
        }


# Global scheduler instance
_learning_scheduler = None


def get_learning_scheduler() -> LearningScheduler:
    """Get the global learning scheduler instance."""
    global _learning_scheduler
    if _learning_scheduler is None:
        _learning_scheduler = LearningScheduler()
    return _learning_scheduler