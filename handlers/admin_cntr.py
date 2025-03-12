from aiogram import Router, types
from aiogram.filters import Command

from database.queries import get_all_users, remove_user_from_game

admin_cntr = Router()

ALLOWED_ADMIN_ID = 267863612  # ID администратора


@admin_cntr.message(Command(commands="user_list"))
async def user_list_handler(message: types.Message):
    """Вывод списка всех пользователей (только для admin в ЛС)."""
    if message.chat.type != "private" or message.from_user.id != ALLOWED_ADMIN_ID:
        await message.reply(
            "Эта команда доступна только администратору в личных сообщениях!"
        )
        return

    users = await get_all_users()
    if not users:
        await message.reply("Пользователей в базе нет.")
        return

    response = "<b>Список пользователей:</b>\n\n"
    for i, user in enumerate(users, start=1):
        display_name = f"@{user['username']}" if user["username"] else user["full_name"]
        status = "в игре" if user["in_game"] else "не в игре"
        response += f"{i}. {display_name} (ID: {user['telegram_id']}, Чат: {user['chat_id']}) - {status}\n"
    await message.reply(response, parse_mode="HTML")


@admin_cntr.message(Command(commands="remove_from_game"))
async def remove_from_game_handler(message: types.Message):
    """Удаление пользователя из розыгрыша по порядковому номеру (только для admin в ЛС)."""
    if message.chat.type != "private" or message.from_user.id != ALLOWED_ADMIN_ID:
        await message.reply(
            "Эта команда доступна только администратору в личных сообщениях!"
        )
        return

    # Ожидаем один аргумент: порядковый номер из списка /user_list
    args = message.text.split()[1:]  # Пропускаем саму команду
    if len(args) != 1:
        await message.reply("Использование: /remove_from_game <порядковый_номер>")
        return

    try:
        user_index = (
            int(args[0]) - 1
        )  # Преобразуем в индекс (нумерация с 1, индексы с 0)
    except ValueError:
        await message.reply("Порядковый номер должен быть целым числом!")
        return

    # Получаем список всех пользователей
    users = await get_all_users()
    if not users:
        await message.reply("Список пользователей пуст.")
        return

    # Проверяем, что номер в допустимом диапазоне
    if user_index < 0 or user_index >= len(users):
        await message.reply(
            f"Пользователь с номером {user_index + 1} не найден в списке!"
        )
        return

    # Извлекаем данные пользователя по индексу
    user = users[user_index]
    telegram_id = user["telegram_id"]
    chat_id = user["chat_id"]
    display_name = f"@{user['username']}" if user["username"] else user["full_name"]

    # Удаляем пользователя из розыгрыша
    removed = await remove_user_from_game(telegram_id=telegram_id, chat_id=chat_id)
    if removed:
        await message.reply(
            f"Пользователь {display_name} (ID: {telegram_id}) удален из розыгрыша в чате {chat_id}."
        )
    else:
        await message.reply(
            f"Пользователь {display_name} (ID: {telegram_id}) уже не в игре в чате {chat_id}."
        )
