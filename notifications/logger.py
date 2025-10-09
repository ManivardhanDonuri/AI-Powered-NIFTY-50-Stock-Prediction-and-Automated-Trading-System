"""
Notification logging configuration

Sets up specialized logging for the notification module with appropriate formatters and handlers.
"""

import logging
import sys
from datetime import datetime
from typing import Optional

class NotificationFormatter(logging.Formatter):
    """Custom formatter for notification logs."""
    
    def __init__(self):
        super().__init__()
        
    def format(self, record):
        """Format log record with notification-specific information."""
        # Create timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Color codes for different log levels
        colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green  
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m'  # Magenta
        }
        reset_color = '\033[0m'
        
        # Get color for log level
        color = colors.get(record.levelname, '')
        
        # Format the message
        formatted_message = (
            f"{color}[{timestamp}] "
            f"NOTIFICATIONS.{record.name.split('.')[-1].upper()} "
            f"{record.levelname}{reset_color}: {record.getMessage()}"
        )
        
        # Add exception info if present
        if record.exc_info:
            formatted_message += f"\n{self.formatException(record.exc_info)}"
            
        return formatted_message

def setup_notification_logging(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up logging configuration for the notification module.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console_output: Whether to output to console
        
    Returns:
        logging.Logger: Configured logger for notifications
    """
    # Create logger for notifications
    logger = logging.getLogger('notifications')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = NotificationFormatter()
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to create file handler for {log_file}: {str(e)}")
    
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False
    
    logger.info("Notification logging configured successfully")
    return logger

def get_notification_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific notification component.
    
    Args:
        name: Component name (e.g., 'telegram', 'whatsapp', 'manager')
        
    Returns:
        logging.Logger: Logger for the component
    """
    return logging.getLogger(f'notifications.{name}')

# Default logger setup
_default_logger = None

def get_default_logger() -> logging.Logger:
    """Get the default notification logger."""
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_notification_logging()
    return _default_logger