import asyncio
import os

import aiocron
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from dotenv import load_dotenv

from handlers.in_game import in_game_r
from handlers.new_member import new_member_r
from handlers.random_user import send_random_message
from handlers.start import start_r
from logger import logger


async def main():
    """Главная функция для запуска бота."""
    load_dotenv()
    bot = Bot(
        token=os.getenv("API_TOKEN"),
    )
    dp = Dispatcher()
    dp.include_routers(start_r, new_member_r, in_game_r)
    bot_commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/play", description="Играть"),
        BotCommand(command="/stats", description="Статистика"),
    ]
    await bot.set_my_commands(bot_commands)
    try:
        try:
            cron_task = aiocron.crontab(
                "0 9 * * *",
                func=lambda: asyncio.create_task(send_random_message(bot)),
            )
            cron_task.start()
            logger.info("Задача отправки случайного сообщения запущена...")
        except Exception as e:
            logger.error(f"Ошибка при запуске задачи: {e}")
        logger.info("Бот запущен...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
