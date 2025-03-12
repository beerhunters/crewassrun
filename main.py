# import asyncio
# import os
#
# import aiocron
# from aiogram import Bot, Dispatcher
# from aiogram.types import BotCommand
#
# from dotenv import load_dotenv
#
# from handlers.exceptions import error_router
# from handlers.in_game import in_game_r
# from handlers.new_member import new_member_r
# from handlers.random_user import send_random_message
# from handlers.start import start_r
# from logger import logger
#
#
# async def main():
#     """Главная функция для запуска бота."""
#     load_dotenv()
#     bot = Bot(
#         token=os.getenv("API_TOKEN"),
#     )
#     dp = Dispatcher()
#     dp.include_routers(start_r, new_member_r, in_game_r, error_router)
#     bot_commands = [
#         BotCommand(command="/start", description="Запустить бота"),
#         BotCommand(command="/play", description="Играть"),
#         BotCommand(command="/stats", description="Статистика"),
#         BotCommand(command="/stats_me", description="Моя статистика"),
#     ]
#     await bot.set_my_commands(bot_commands)
#     try:
#         try:
#             cron_task = aiocron.crontab(
#                 "0 9 * * *",
#                 func=lambda: asyncio.create_task(
#                     send_random_message(bot, chat_id=int(os.getenv("CHAT_ID")))
#                 ),
#             )
#             cron_task.start()
#             logger.info("Задача отправки случайного сообщения запущена...")
#         except Exception as e:
#             logger.error(f"Ошибка при запуске задачи: {e}")
#         logger.info("Бот запущен...")
#         await dp.start_polling(bot)
#     except Exception as e:
#         logger.error(f"Ошибка при работе бота: {e}")
#     finally:
#         await bot.session.close()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
# main.py
import asyncio
import os

import aiocron
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from dotenv import load_dotenv

from handlers.admin_cntr import admin_cntr
from handlers.exceptions import error_router
from handlers.in_game import in_game_r
from handlers.new_member import new_member_r
from handlers.random_user import send_random_message
from handlers.start import start_r
from logger import logger
from database.queries import get_active_chat_ids


async def send_daily_messages(bot: Bot):
    """Отправка утренних сообщений во все активные чаты."""
    try:
        chat_ids = await get_active_chat_ids()
        if not chat_ids:
            logger.warning("Нет активных чатов для отправки сообщений.")
            return

        for chat_id in chat_ids:
            try:
                await send_random_message(bot, chat_id=chat_id)
                logger.info(f"Сообщение отправлено в чат {chat_id}")
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка при получении активных чатов: {e}")


async def main():
    """Главная функция для запуска бота."""
    load_dotenv()
    bot = Bot(token=os.getenv("API_TOKEN"))
    dp = Dispatcher()
    dp.include_routers(start_r, new_member_r, in_game_r, admin_cntr, error_router)
    bot_commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/play", description="Играть"),
        BotCommand(command="/stats", description="Статистика"),
        BotCommand(command="/stats_me", description="Моя статистика"),
    ]
    await bot.set_my_commands(bot_commands)
    try:
        try:
            # Запускаем задачу отправки сообщений каждое утро в 9:00
            cron_task = aiocron.crontab(
                "0 9 * * *",
                func=lambda: asyncio.create_task(send_daily_messages(bot)),
            )
            # cron_task = aiocron.crontab(
            #     "* * * * *",
            #     func=lambda: asyncio.create_task(send_daily_messages(bot)),
            # )
            # cron_task = aiocron.crontab(
            #     os.getenv("CRON_SCHEDULE", "0 9 * * *"),
            #     func=lambda: asyncio.create_task(send_daily_messages(bot)),
            # )
            cron_task.start()
            logger.info("Задача отправки утренних сообщений запущена...")
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
