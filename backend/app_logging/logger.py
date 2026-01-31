import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# Для тестов можно задать LOG_DIR=/tmp, иначе пишем в logging/
log_directory = os.environ.get("LOG_DIR", "logging")
if not os.path.exists(log_directory):
    os.makedirs(log_directory, exist_ok=True)

# Настройка логирования
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)  # Изменено на DEBUG для захвата всех уровней сообщений

current_date = datetime.now().strftime("%Y-%m-%d")
log_file_name = f"app_{current_date}.log"

# Создаем обработчик для файла (при ошибке доступа — только консоль, чтобы тесты не падали)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
try:
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_directory, log_file_name),
        when="midnight",
        interval=1,
        backupCount=7,
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except (OSError, PermissionError):
    pass  # только консоль

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)