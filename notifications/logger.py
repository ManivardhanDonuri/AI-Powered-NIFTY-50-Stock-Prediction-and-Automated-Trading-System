
import logging
import sys
from datetime import datetime
from typing import Optional

class NotificationFormatter(logging.Formatter):

    def __init__(self):
        super().__init__()

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

        colors = {
            'DEBUG': '\033[36m',
            'INFO': '\033[32m',
            'WARNING': '\033[33m',
            'ERROR': '\033[31m',
            'CRITICAL': '\033[35m'
        }
        reset_color = '\033[0m'

        color = colors.get(record.levelname, '')

        formatted_message = (
            f"{color}[{timestamp}] "
            f"NOTIFICATIONS.{record.name.split('.')[-1].upper()} "
            f"{record.levelname}{reset_color}: {record.getMessage()}"
        )

        if record.exc_info:
            formatted_message += f"\n{self.formatException(record.exc_info)}"

        return formatted_message

def setup_notification_logging(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:

    logger = logging.getLogger('notifications')
    logger.setLevel(getattr(logging, log_level.upper()))

    logger.handlers.clear()

    formatter = NotificationFormatter()

    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to create file handler for {log_file}: {str(e)}")

    logger.propagate = False

    logger.info("Notification logging configured successfully")
    return logger

def get_notification_logger(name: str) -> logging.Logger:

    return logging.getLogger(f'notifications.{name}')

_default_logger = None

def get_default_logger() -> logging.Logger:
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_notification_logging()
    return _default_logger