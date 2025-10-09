"""
Trading System Background Service

Runs the trading system as a background service on Windows/Linux.
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from trading_scheduler import TradingScheduler

class TradingService:
    """Background service for automated trading system."""
    
    def __init__(self):
        """Initialize the trading service."""
        self.scheduler = None
        self.is_running = False
        
        # Setup logging for service
        log_file = current_dir / 'trading_service.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        if hasattr(signal, 'SIGHUP'):  # Unix only
            signal.signal(signal.SIGHUP, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the trading service."""
        if self.is_running:
            self.logger.warning("Service is already running")
            return
        
        self.logger.info("🚀 Starting Trading System Background Service")
        self.logger.info(f"Working directory: {current_dir}")
        self.logger.info(f"Python path: {sys.executable}")
        
        try:
            # Initialize scheduler
            config_file = current_dir / 'config.json'
            self.scheduler = TradingScheduler(str(config_file))
            
            # Start scheduler
            self.is_running = True
            self.scheduler.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {str(e)}")
            self.is_running = False
            raise
    
    def stop(self):
        """Stop the trading service."""
        if not self.is_running:
            return
        
        self.logger.info("⏹️ Stopping Trading System Background Service")
        
        try:
            if self.scheduler:
                self.scheduler.stop()
            
            self.is_running = False
            self.logger.info("✅ Service stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping service: {str(e)}")
    
    def run(self):
        """Run the service (blocking)."""
        try:
            self.start()
            
            # Keep service running
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Service error: {str(e)}")
        finally:
            self.stop()

def main():
    """Main service entry point."""
    service = TradingService()
    service.run()

if __name__ == "__main__":
    main()