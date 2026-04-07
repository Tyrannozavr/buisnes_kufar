import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

log_directory = "logging"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)


class _ExcludeErrorLevelsFilter(logging.Filter):
    """DEBUG, INFO, WARNING — в общий лог; ERROR и CRITICAL только в error-файл."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR


# Настройка логирования
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

# Базовые имена; после ротации к имени добавляется суффикс даты (когда=midnight)
general_log_path = os.path.join(log_directory, "app.log")
error_log_path = os.path.join(log_directory, "app_error.log")

# Общий лог: без ERROR/CRITICAL (ротация каждый день в полночь)
general_file_handler = TimedRotatingFileHandler(
    filename=general_log_path,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)
# Как раньше: в общий файл не пишем DEBUG (только консоль)
general_file_handler.setLevel(logging.INFO)
general_file_handler.addFilter(_ExcludeErrorLevelsFilter())

# Только ошибки: ERROR, CRITICAL (в т.ч. traceback из logger.exception)
error_file_handler = TimedRotatingFileHandler(
    filename=error_log_path,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)
error_file_handler.setLevel(logging.ERROR)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
general_file_handler.setFormatter(formatter)
error_file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(general_file_handler)
logger.addHandler(error_file_handler)
logger.addHandler(console_handler)
