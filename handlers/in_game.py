import random
import re

from aiogram import types, Router
from aiogram.filters import Command

from buns_data import IN_GAME_TEXT
from database.queries import (
    get_user_by_id,
    add_user_to_game,
    add_user,
    # get_top_users_by_repetitions,
    get_top_buns_with_users,
    get_user_buns_stats,
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


# @in_game_r.message(Command(commands="stats"))
# async def stats_handler(message: types.Message):
#     chat_id = message.chat.id  # Учитываем ID чата для статистики
#
#     # Проверяем, не личные ли это сообщения
#     if message.chat.type == "private":
#         await message.reply("Эту команду можно использовать только в групповом чате!")
#         return
#
#     top_buns = await get_top_buns_with_users(chat_id=chat_id)
#
#     if not top_buns:
#         await message.reply("Пока нет данных для статистики 📊")
#         return
#
#     # Формируем текст статистики
#     stats_text = "**🏆 Топ-10 булочек и их владельцев:**\n\n"
#     for i, item in enumerate(top_buns, start=1):
#         bun = item["bun"]
#         users = item["users"]
#         stats_text += f"{i}. {bun} - {', '.join(users)} 🔥\n"
#
#     await message.reply(stats_text, parse_mode="Markdown")
async def escape_markdown(text: str) -> str:
    """Экранирует специальные символы Markdown v2, включая дефис."""
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"  # Добавляем \ в список экранируемых символов
    return re.sub(r"([" + re.escape(escape_chars) + r"])", r"\\\1", text)


# @in_game_r.message(Command(commands="stats"))
# async def stats_handler(message: types.Message):
#     chat_id = message.chat.id
#
#     if message.chat.type == "private":
#         await message.reply("Эту команду можно использовать только в групповом чате!")
#         return
#
#     top_buns = await get_top_buns_with_users(chat_id=chat_id)
#
#     if not top_buns:
#         await message.reply("Пока нет данных для статистики 📊")
#         return
#
#     # Экранируем спецсимволы перед отправкой
#     stats_text = "**🏆 Топ-10 булочек и их владельцев:**\n\n"
#     for i, item in enumerate(top_buns, start=1):
#         bun = await escape_markdown(item["bun"])  # Экранируем булочку
#         users = [
#             await escape_markdown(user) for user in item["users"]
#         ]  # Экранируем юзернеймы
#         stats_text += f"{i}. {bun} - {', '.join(users)} 🔥\n"
#
#     await message.reply(stats_text, parse_mode="MarkdownV2")  # Используем MarkdownV2
@in_game_r.message(Command(commands="stats"))
async def stats_handler(message: types.Message):
    chat_id = message.chat.id

    if message.chat.type == "private":
        await message.reply("Эту команду можно использовать только в групповом чате!")
        return

    top_buns = await get_top_buns_with_users(chat_id=chat_id)

    if not top_buns:
        await message.reply("Пока нет данных для статистики 📊")
        return

    # Экранируем символы перед отправкой
    stats_text = "*🏆 Топ\\-10 булочек и их владельцев\\:*\n\n"
    for i, item in enumerate(top_buns, start=1):
        bun = await escape_markdown(item["bun"])  # Экранируем булочку
        users = [
            await escape_markdown(user) for user in item["users"]
        ]  # Экранируем юзернеймы
        stats_text += f"{i}\\ {bun} \\- {'\\, '.join(users)} 🔥\n"
        print(stats_text)
    await message.reply(stats_text, parse_mode="MarkdownV2")


@in_game_r.message(Command(commands="stats_me"))
async def stats_me_handler(message: types.Message):
    user_id = message.from_user.id  # Получаем ID пользователя, который вызвал команду
    chat_id = message.chat.id  # Получаем chat_id

    # Проверяем, не личные ли это сообщения
    if message.chat.type == "private":
        await message.reply("Эту команду можно использовать только в групповом чате!")
        return

    # Получаем статистику по булочкам для конкретного пользователя
    user_buns = await get_user_buns_stats(user_id=user_id, chat_id=chat_id)

    if not user_buns:
        await message.reply("Вы еще не выбрали булочек или не играете в этой игре 📊")
        return

    # Формируем текст статистики для пользователя
    stats_text = f"**🧁 Ваша статистика\\:**\n\n"
    for i, item in enumerate(user_buns, start=1):
        bun = item["bun"]
        count = item["count"]
        stats_text += f"{i}\\ {bun} \\- {count} раз\\(а\\) 🔥\n"

    await message.reply(stats_text, parse_mode="Markdown")
