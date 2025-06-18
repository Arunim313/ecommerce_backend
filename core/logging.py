import logging
import os
from pathlib import Path
from datetime import datetime
from core.config import settings

def setup_logging():
    """Initialize logging with console and file handlers"""
    log_level = "DEBUG" if settings.DEBUG else os.getenv("LOG_LEVEL", "INFO").upper()
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    log_level = log_level if log_level in valid_levels else "INFO"

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Log file with timestamp
    log_filename = logs_dir / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_filename, mode="w", encoding="utf-8")
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at level: {log_level}")
    logger.info(f"Logs written to: {log_filename}")

def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name"""
    return logging.getLogger(name)
