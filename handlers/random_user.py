# import os
import random
from aiogram import Bot

# from dotenv import load_dotenv

from database.queries import get_random_user, add_or_update_user_bun

# load_dotenv()

# GROUP_ID = os.getenv("GROUP_ID")
BUNS = [
    "Круассан",
    "Шасон",
    "ПанШоколя",
    "Булочка Шу",
    "Даниш",
    "Сочень",
    "Улитка с изюмом",
    "Рулет лимонный",
    "Брауни",
    "Пирог вишневый",
]

MESSAGES = [
    "@{user}, ты сегодня самый хрустящий {bun}! 🥐",
    "@{user}, свежий, как только из печи {bun}! 🔥",
    "@{user}, сегодня ты — восхитительный {bun}! 😋",
    "@{user}, быть {bun} — это искусство, и ты его воплощение! 🎨",
    "@{user}, кто тут самый аппетитный {bun}? Конечно же ты! 🍰",
    "@{user}, день обещает быть сладким, ведь ты {bun}! 🍫",
    "@{user}, хрустишь, как настоящий {bun}! 🔥",
    "@{user}, идеальный день для идеального {bun}! 💯",
    "@{user}, теплее всех сегодня {bun}, потому что это ты! ☕",
    "@{user}, готов к приключениям? {bun} в деле! 🚀",
]


async def send_random_message(bot: Bot):
    user = await get_random_user()  # Получаем случайного пользователя
    chat_id = user.chat_id
    if not user:
        return  # Если пользователей нет в БД

    bun = random.choice(BUNS)  # Выбираем случайную булочку
    message = random.choice(MESSAGES).format(
        user=f"{user.username}" if user.username else user.full_name, bun=bun
    )
    await bot.send_message(chat_id, message, parse_mode="HTML")  # Отправляем сообщение

    # Сохраняем в БД
    # async with async_session() as session:
    await add_or_update_user_bun(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        bun=bun,
        chat_id=chat_id,
    )
