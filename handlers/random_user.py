import asyncio
import random
from aiogram import Bot

from buns_data import BUNS, MESSAGES, SHURSHU_MESSAGES

from database.queries import get_random_user, add_or_update_user_bun


async def send_random_message(bot: Bot):
    user = await get_random_user()  # Получаем случайного пользователя
    chat_id = user.chat_id
    if not user:
        return  # Если пользователей нет в БД

    # Сначала отправляем предшествующее сообщение (выбираем случайную фразу)
    pre_message = random.choice(SHURSHU_MESSAGES)
    await bot.send_message(chat_id, pre_message, parse_mode="HTML")

    # Делаем небольшую задержку (например, 2 секунды), чтобы создать эффект интриги
    await asyncio.sleep(2)

    # Отправляем начальное сообщение "Пу-пу-пу"
    text = "Пу-пу-пу"
    msg = await bot.send_message(chat_id, text, parse_mode="HTML")
    emojis = ["⏳", "⌛", "⏳", "⌛", "⏳", "⌛", "⏳", "⌛"]
    for emoji in emojis:
        await msg.edit_text(f"Пу-пу-пу... {emoji}")
        await asyncio.sleep(1)

    bun = random.choice(BUNS)  # Выбираем случайную булочку
    message = random.choice(MESSAGES).format(
        user=f"{user.username}" if user.username else user.full_name, bun=bun
    )
    await bot.send_message(chat_id, message, parse_mode="HTML")  # Отправляем сообщение

    # Сохраняем в БД
    await add_or_update_user_bun(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        bun=bun,
        chat_id=chat_id,
    )
