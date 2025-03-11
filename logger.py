# logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

# Убедимся, что папка logs существует
if not os.path.exists("logs"):
    os.makedirs("logs")

# Создаём форматтер для логов
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)

# Настройка обработчика для файла (ошибки и выше)
file_handler = RotatingFileHandler(
    "logs/bot.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,  # Храним до 5 файлов логов
    encoding="utf-8",
)
file_handler.setLevel(logging.ERROR)  # Логируем INFO и выше в файл
file_handler.setFormatter(formatter)

# Настройка обработчика для консоли (DEBUG и выше)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Выводим всё в консоль для отладки
console_handler.setFormatter(formatter)

# Настройка корневого логгера
logging.basicConfig(
    level=logging.INFO,  # Устанавливаем минимальный уровень для приложения
    handlers=[file_handler, console_handler],  # Оба обработчика
)

# Создаём логгер для использования в приложении
logger = logging.getLogger("bot")

# Тестовое сообщение для проверки
logger.debug("Логирование настроено и работает")
