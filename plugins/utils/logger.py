import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


# Initialize and configure the logger with both file and stream handlers.
class CustomLogger:
    _instance: Optional[logging.Logger] = None

    @staticmethod
    def setup_logger():
        # Get the root directory of the project
        ROOT_DIR = Path(__file__).parent.parent.absolute()
        LOG_FILE_PATH = os.path.join(ROOT_DIR, "logs.txt")

        # Create logs directory if it doesn't exist
        os.makedirs(ROOT_DIR, exist_ok=True)

        FORMAT = "[%(asctime)s - %(levelname)s] - %(name)s - %(message)s"
        DATE_FORMAT = "%d-%b-%y %H:%M:%S"

        base_logger = logging.getLogger("Bot")
        base_logger.setLevel(logging.INFO)

        if not base_logger.handlers:
            # File handler with rotation
            file_handler = RotatingFileHandler(
                LOG_FILE_PATH,
                maxBytes=10_000_000,  # 10MB
                backupCount=10,
                encoding="utf-8",
            )
            file_handler.setFormatter(logging.Formatter(FORMAT, DATE_FORMAT))
            base_logger.addHandler(file_handler)

            # Stream handler for console output
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(FORMAT, DATE_FORMAT))
            base_logger.addHandler(stream_handler)

        # Set Pyrogram logger to WARNING level
        logging.getLogger("pyrogram").setLevel(logging.WARNING)

        return base_logger

    @classmethod
    def get_logger(cls, name: str = None) -> logging.Logger:
        """
        Get or create a logger instance.

        Args:
            name: The name for the logger. Will be appended to base logger name.

        Returns:
            logging.Logger: Configured logger instance
        """
        if cls._instance is None:
            cls._instance = cls.setup_logger()

        if name:
            return cls._instance.getChild(name)
        return cls._instance


# Simple function interface for getting loggers
def get_logger(name: str = None) -> logging.Logger:
    """Get a configured logger instance."""
    return CustomLogger.get_logger(name)


# Convenience functions
log_info = lambda msg, name=None: get_logger(name).info(msg)
log_error = lambda msg, name=None: get_logger(name).error(msg)
log_warning = lambda msg, name=None: get_logger(name).warning(msg)
log_debug = lambda msg, name=None: get_logger(name).debug(msg)

# Export all needed functions and classes
__all__ = ["get_logger", "log_info", "log_error", "log_warning", "log_debug"]
