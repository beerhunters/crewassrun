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

# # Тестовое сообщение для проверки
# logger.debug("Логирование настроено и работает")

# import logging
# from aiogram.dispatcher.middlewares.base import BaseMiddleware
# from aiogram.types import Update
#
#
# # ---- Кастомный форматтер ----
#
#
# class CustomFormatter(logging.Formatter):
#     grey = "\x1b[38;21m"
#     green = "\x1b[32;1m"
#     yellow = "\x1b[33;1m"
#     red = "\x1b[31;1m"
#     bold_red = "\x1b[41m"
#     reset = "\x1b[0m"
#     format = "%(asctime)s | %(levelname)s | - %(message)s"  # Убрали filename и lineno
#
#     FORMATS = {
#         logging.DEBUG: grey + format + reset,
#         logging.INFO: green + format + reset,
#         logging.WARNING: yellow + format + reset,
#         logging.ERROR: red + format + reset,
#         logging.CRITICAL: bold_red + format + reset,
#     }
#
#     def format(self, record):
#         log_fmt = self.FORMATS.get(record.levelno, self.format)
#         formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
#         record.levelname = record.levelname.ljust(8)
#         return formatter.format(record)
#
#
# # ---- Настройка логгера ----
#
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# handler.setFormatter(CustomFormatter())
#
# logger = logging.getLogger("bot_logger")
#
# if not logger.handlers:
#     logger.addHandler(handler)
#
# logger.setLevel(logging.DEBUG)
# logger.propagate = False
#
# # Убираем логи aiogram про Update id=...
# logging.getLogger("aiogram.event").setLevel(logging.WARNING)
#
#
# # ---- Middleware с улучшенным логированием ----
#
#
# class LoggingMiddleware(BaseMiddleware):
#     async def __call__(self, handler, event: Update, data):
#         try:
#             # Тип события
#             event_type = event.event_type if hasattr(event, "event_type") else "unknown"
#
#             # Формируем лог-сообщение с подробной информацией
#             log_message = f"📌 EVENT | {event_type.upper()}"
#
#             if event.message:
#                 msg = event.message
#                 log_message += (
#                     f" | User ID: {msg.from_user.id}"
#                     f" | Username: @{msg.from_user.username if msg.from_user.username else 'N/A'}"
#                     f" | Chat ID: {msg.chat.id}"
#                     f" | Chat Type: {msg.chat.type}"
#                     f" | Message ID: {msg.message_id}"
#                 )
#                 if msg.text:
#                     log_message += f" | Text: {msg.text}"
#                 elif msg.content_type != "text":
#                     log_message += f" | Content: {msg.content_type}"
#
#             elif event.callback_query:
#                 cb = event.callback_query
#                 log_message += (
#                     f" | User ID: {cb.from_user.id}"
#                     f" | Username: @{cb.from_user.username if cb.from_user.username else 'N/A'}"
#                     f" | Chat ID: {cb.message.chat.id if cb.message else 'N/A'}"
#                     f" | Chat Type: {cb.message.chat.type if cb.message else 'N/A'}"
#                     f" | Callback: {cb.data}"
#                 )
#
#             logger.info(log_message)
#
#             return await handler(event, data)
#
#         except Exception as e:
#             logger.error(f"Logging error: {e}", exc_info=True)
#             return await handler(event, data)
#
#
# # Экспортируем логгер и middleware
# __all__ = ["logger", "LoggingMiddleware"]
