import logging
from logging.handlers import RotatingFileHandler
import os
from typing import TextIO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""Base directory of the project."""

LOG_DIR: str = os.path.join(BASE_DIR, "logs")
"""Directory where log files will be stored."""

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT: str = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
"""Log message format: timestamp - logger name - level - message."""

logger: logging.Logger = logging.getLogger()
"""Global logger instance for the application."""

logger.setLevel(logging.DEBUG) 

if logger.hasHandlers():
    logger.handlers.clear()

console_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
"""Console handler that logs INFO level and above to standard output."""

console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(console_handler)

warning_file_handler: RotatingFileHandler = RotatingFileHandler(
    filename = os.path.join(LOG_DIR, "security_audit.log"),
    maxBytes = 5 * 1024 * 1024,
    backupCount = 3,
    encoding = "utf-8"
)

"""File handler that logs WARNING level to security_audit.log with rotation.

Logs are rotated when file reaches 5MB, keeping 3 backup files.
"""

warning_file_handler.setLevel(logging.WARNING)
warning_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(warning_file_handler)

error_file_handler: RotatingFileHandler = RotatingFileHandler(
    filename = os.path.join(LOG_DIR, "errors.log"),
    maxBytes = 5 * 1024 * 1024,
    backupCount = 5,
    encoding = "utf-8"
)

"""File handler that logs ERROR level to errors.log with rotation.

Logs are rotated when file reaches 5MB, keeping 5 backup files.
"""

error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(error_file_handler)

critical_file_handler: RotatingFileHandler = RotatingFileHandler(
    filename = os.path.join(LOG_DIR, "critical.log"),
    maxBytes = 5 * 1024 * 1024,
    backupCount = 5,
    encoding = "utf-8"
)

"""File handler that logs CRITICAL level to critical.log with rotation.

Logs are rotated when file reaches 5MB, keeping 5 backup files.
"""

critical_file_handler.setLevel(logging.CRITICAL)
critical_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(critical_file_handler)