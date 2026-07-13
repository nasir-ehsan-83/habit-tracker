import logging
from logging.handlers import RotatingFileHandler
import os


LOG_DIR = "../../log"
os.makedirs(LOG_DIR, exist_ok = True)

LOG_FORMAT = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"

logger = logging.getLogger()
logger.setLevel(logging.WARNING) 


if logger.hasHandlers():
    logger.handlers.clear()

class ExactLevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(console_handler)


warning_file_handler = RotatingFileHandler(
    filename = os.path.join(LOG_DIR, "security_audit.log"),
    maxBytes = 5 * 1024 * 1024,  # 5 MB
    backupCount = 3,
    encoding = "utf-8"
)
warning_file_handler.setLevel(logging.WARNING)
warning_file_handler.addFilter(ExactLevelFilter(logging.WARNING))
warning_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(warning_file_handler)


error_file_handler = RotatingFileHandler(
    filename = os.path.join(LOG_DIR, "errors.log"),
    maxBytes = 5 * 1024 * 1024,  # 5 MB
    backupCount = 5,
    encoding = "utf-8"
)
error_file_handler.setLevel(logging.ERROR)
error_file_handler.addFilter(ExactLevelFilter(logging.ERROR))
error_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(error_file_handler)


critical_file_handler = RotatingFileHandler(
    filename = os.path.join(LOG_DIR, "critical.log"),
    maxBytes = 5 * 1024 * 1024,  # 5 MB
    backupCount = 5,
    encoding = "utf-8"
)
critical_file_handler.setLevel(logging.CRITICAL)
critical_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(critical_file_handler)
