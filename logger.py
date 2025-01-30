import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Логи выводятся в консоль
    ],
)

# Создаем корневой логгер для всего приложения
logger = logging.getLogger()
