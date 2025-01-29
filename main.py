import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatMemberUpdated
import asyncio
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
STICKER_ID = os.getenv("STICKER_ID")
# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем экземпляры бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Обработка события: новый участник
@dp.chat_member()
async def new_member_handler(event: ChatMemberUpdated):
    # Проверяем, что статус участника изменился с "left" на "member"
    if (
        event.old_chat_member.status == ChatMemberStatus.LEFT
        and event.new_chat_member.status == ChatMemberStatus.MEMBER
    ):
        new_member = event.new_chat_member.user
        chat_id = event.chat.id

        # Проверяем, что это не бот
        if not new_member.is_bot:
            try:
                # Отправляем стикер
                await bot.send_sticker(chat_id, sticker=STICKER_ID)

                # Логирование
                logger.info(
                    f"Стикер отправлен новому участнику: {new_member.full_name} (ID: {new_member.id})"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке стикера: {e}")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
