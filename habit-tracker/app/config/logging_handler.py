import logging
from logging.handlers import RotatingFileHandler
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOG_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG) 

if logger.hasHandlers():
    logger.handlers.clear()

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(console_handler)

warning_file_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "security_audit.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)
warning_file_handler.setLevel(logging.WARNING)
warning_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(warning_file_handler)

error_file_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "errors.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(error_file_handler)

critical_file_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "critical.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)
critical_file_handler.setLevel(logging.CRITICAL)
critical_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(critical_file_handler)
