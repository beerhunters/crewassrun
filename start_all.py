import subprocess
import time
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к проекту
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Уникальные имена для процессов
COMMANDS = [
    {
        "name": "c_bot_telegram",
        "script": "main.py",
        "interpreter": "python3",
        "cwd": BASE_DIR,
        "log": os.path.join(BASE_DIR, "logs/telegram-bot.log"),
    },
    {
        "name": "c_bot_api",
        "script": "api/main.py",
        "interpreter": "python3",
        "cwd": BASE_DIR,
        "log": os.path.join(BASE_DIR, "logs/api.log"),
        "args": "--port 8000",
    },
    {
        "name": "c_bot_admin",
        "script": "admin/app.py",
        "interpreter": "python3",
        "cwd": BASE_DIR,
        "log": os.path.join(BASE_DIR, "logs/admin.log"),
        "args": "--port 5000",
    },
]


def start_process(process):
    """Запускает процесс через pm2, если он ещё не запущен"""
    # Проверяем, существует ли процесс с таким именем
    check_cmd = ["pm2", "list"]
    result = subprocess.run(check_cmd, capture_output=True, text=True)
    if process["name"] in result.stdout:
        logger.info(f"Процесс {process['name']} уже запущен, пропускаем...")
        return 0

    cmd = [
        "pm2",
        "start",
        process["script"],
        "--name",
        process["name"],
        "--interpreter",
        process["interpreter"],
        "--output",
        process["log"],
        "--error",
        process["log"],
        "--restart-delay",
        "5000",  # Задержка перезапуска 5 секунд
    ]
    if "args" in process:
        cmd.append(process["args"])
    if "cwd" in process:
        cmd.extend(["--cwd", process["cwd"]])

    logger.info(f"Запуск {process['name']}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        logger.info(f"{process['name']} успешно запущен")
    else:
        logger.error(f"Ошибка запуска {process['name']}: {result.stderr}")
    return result.returncode


def main():
    # Создаём папку для логов, если её нет
    os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

    # Последовательный запуск
    for process in COMMANDS:
        start_process(process)
        time.sleep(5)  # Задержка 5 секунд между запусками для снижения нагрузки

    # Сохранение конфигурации pm2
    subprocess.run(["pm2", "save"], capture_output=True)
    logger.info("Все процессы проверены/запущены. Проверка статуса:")
    subprocess.run(["pm2", "list"])


if __name__ == "__main__":
    main()
