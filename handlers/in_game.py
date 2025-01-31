import random

from aiogram import types, Router
from aiogram.filters import Command

from buns_data import IN_GAME_TEXT
from database.queries import (
    get_user_by_id,
    add_user_to_game,
    add_user,
    get_top_users_by_repetitions,
)

in_game_r = Router()


@in_game_r.message(Command(commands="play"))
async def in_game_handler(message: types.Message):
    from_user = message.from_user
    chat_id = message.chat.id

    # Проверяем, не личные ли это сообщения
    if message.chat.type == "private":
        await message.reply("Эту команду можно использовать только в групповом чате!")
        return
    # Проверим, есть ли данные о пользователе
    if not message.from_user:
        await message.reply("Не удалось получить информацию о пользователе.")
        return

    user_id = from_user.id
    user = await get_user_by_id(
        user_id, chat_id
    )  # Функция для получения пользователя по ID

    if user:
        # Если пользователь существует в базе, проверим, в игре ли он
        if user.in_game:  # Предположим, что в User добавлен атрибут in_game
            await message.reply("Ты уже в игре! 🎮")
        else:
            # Если не в игре, добавим в игру
            await add_user_to_game(user_id)
            text = random.choice(IN_GAME_TEXT).format(
                user=(
                    f"{from_user.username}"
                    if from_user.username
                    else from_user.full_name
                )
            )
            await message.reply(text)
            # await message.reply(f"Ты успешно присоединился к игре, {user.username}! 🎉")
    else:
        # Если пользователя нет в базе данных
        await add_user(
            user_id=from_user.id,
            username=from_user.username,
            full_name=from_user.full_name,
            chat_id=chat_id,
        )
        text = random.choice(IN_GAME_TEXT).format(
            user=f"{from_user.username}" if from_user.username else from_user.full_name
        )
        await message.reply(text)
        # await message.reply(
        #     f"Ты успешно присоединился к игре, {from_user.username}! 🎉"
        # )


@in_game_r.message(Command(commands="stats"))
async def stats_handler(message: types.Message):
    chat_id = message.chat.id  # Учитываем ID чата для статистики

    # Проверяем, не личные ли это сообщения
    if message.chat.type == "private":
        await message.reply("Эту команду можно использовать только в групповом чате!")
        return

    top_users = await get_top_users_by_repetitions(chat_id=chat_id)

    if not top_users:
        await message.reply("Пока нет данных для статистики 📊")
        return

    # Формируем текст статистики
    stats_text = "**🏆 Топ-10 игроков:**\n\n"
    for i, (full_name, bun, max_repeats) in enumerate(top_users, start=1):
        stats_text += f"{i}. {full_name} — {bun} ({max_repeats} раз) 🔥\n"

    await message.reply(stats_text, parse_mode="Markdown")
