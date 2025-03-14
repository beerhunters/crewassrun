import os
from dotenv import load_dotenv

load_dotenv()


# Получение переменных конфигурации
try:
    API_TOKEN = os.getenv("API_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    ADMIN = os.getenv("ADMIN")
    FOR_LOGS = os.getenv("FOR_LOGS")
    # API_URL = os.getenv("API_URL")
    DATABASE_URL = os.getenv("DATABASE_URL")
except (TypeError, ValueError) as ex:
    print("Error while reading config:", ex)
