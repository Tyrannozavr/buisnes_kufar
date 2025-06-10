import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

log_directory = "logging"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)


# Настройка логирования
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)  # Изменено на DEBUG для захвата всех уровней сообщений

current_date = datetime.now().strftime("%Y-%m-%d")
log_file_name = f"app_{current_date}.log"


# Создаем обработчик для файла с ежедневной ротацией
file_handler = TimedRotatingFileHandler(
    filename=os.path.join(log_directory, log_file_name),  # Имя файла с датой
    when="midnight",  # Ротация каждый день в полночь
    interval=1,  # Каждый день
    backupCount=7  # Хранить последние 7 файлов
)
file_handler.setLevel(logging.INFO)

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # Устанавливаем уровень DEBUG для консоли

# Форматирование логов
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)