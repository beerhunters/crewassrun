# 🥐 Булочка Дня — Telegram-бот для гурманов и веселья!

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-supported-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Булочка Дня** — это Telegram-бот, который каждый день выбирает самую аппетитную булочку среди участников чата, приветствует новичков стикерами и предлагает интерактивные игры с сосисками и булочками! 🍩✨

## 🚀 Функционал

- **Булочка Дня** — ежедневный выбор случайного участника с вручением виртуальной булочки.
- **Приветствие новичков** — бот отправляет стикеры и юмористические сообщения новым участникам.
- **Статистика** — узнайте, кто чаще всех становился булочкой!
- **Игра с сосисками** — кидайте сосиски в других участников, зарабатывайте бонусы или получайте штрафы.
- **Админка** — веб-интерфейс для управления ботом (доступен по `https://<your-ip>/crewassrun/`).
- **API** — программный интерфейс для интеграции (доступен по `https://<your-ip>/crewassrun/api/`).

## 🔧 Команды

- `/start` — запуск бота и активация в чате.
- `/play` — вступление в игру.
- `/stats` — статистика по булочкам в чате.
- `/stats_me` — ваша личная статистика.
- `/sausage @username` — бросить сосиску в участника.
- `/random_sausage` — бросить сосиску в случайного участника.

## 📦 Установка и запуск

### Требования
- Docker и Docker Compose.
- Переменные окружения в файле `.env` (см. пример выше).

### Шаги
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/beerhunters/crewassrun.git
   cd crewassrun
   ```
2. Создайте файл .env в корне проекта с вашими настройками (см. пример выше). Укажите DOMAIN_OR_IP как ваш IP или домен.
3. Соберите и запустите контейнеры:
   ```bash
   docker-compose up --build
   ```
4. Бот начнет работу, админка будет доступна по https://<your-ip>/crewassrun/, API — по https://<your-ip>/crewassrun/api/. При первом подключении браузер предупредит о самоподписном сертификате — примите его. 
### Остановка
   ```bash
   docker-compose down
   ```
## 🛠 Конфигурация
- Бот: Работает в Telegram, требует токен API.
- Админка: Flask-приложение на порту 5000 внутри контейнера.
- API: FastAPI на порту 8000 внутри контейнера.
- Nginx: Кастомный образ с самоподписными сертификатами, проксирует запросы на админку и API через /crewassrun/ с поддержкой HTTPS.
- База данных: SQLite3, файл db.sqlite3 хранится в томе database.
### Ограничения ресурсов
- Бот, API, админка: 0.5 CPU, 256 МБ памяти.
- Nginx: 0.25 CPU, 128 МБ памяти.
## 🤝 Контрибьютинг
Приветствуем любые идеи и улучшения! Открывайте Issues или отправляйте Pull Requests. Все булочки будут вам благодарны! 🥐

## 📜 Лицензия
MIT License. Используйте, улучшайте и наслаждайтесь булочками!

Made by [Beerhunters](https://t.me/beerhunters) | [GitHub Profile](https://github.com/beerhunters/) | 2025