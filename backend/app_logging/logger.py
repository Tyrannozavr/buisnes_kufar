import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

log_directory = "logging"
if not os.path.exists(log_directory):
    try:
        os.makedirs(log_directory)
    except OSError:
        pass


class _ExcludeErrorLevelsFilter(logging.Filter):
    """DEBUG, INFO, WARNING — в общий лог; ERROR и CRITICAL только в error-файл."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR


logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

general_log_path = os.path.join(log_directory, "app.log")
error_log_path = os.path.join(log_directory, "app_error.log")

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

try:
    general_file_handler = TimedRotatingFileHandler(
        filename=general_log_path,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    general_file_handler.setLevel(logging.INFO)
    general_file_handler.addFilter(_ExcludeErrorLevelsFilter())
    general_file_handler.setFormatter(formatter)
    logger.addHandler(general_file_handler)

    error_file_handler = TimedRotatingFileHandler(
        filename=error_log_path,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)
except OSError as e:
    print(f"logging: cannot open {log_directory}/*.log: {e}; console only", file=sys.stderr)
