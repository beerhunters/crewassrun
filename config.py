import os
from dotenv import load_dotenv

load_dotenv()

# Получение переменных конфигурации
try:
    API_TOKEN = os.getenv("API_TOKEN")
except (TypeError, ValueError) as ex:
    print("Error while reading config:", ex)

ADMIN = 267863612
FOR_LOGS = -1002327384497

DOMAIN_OR_IP = "93.183.81.123"
# DOMAIN_OR_IP="85.193.91.223"
