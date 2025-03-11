import random
from aiogram import types, Router
from aiogram.filters import Command, ChatMemberUpdatedFilter, LEFT
from buns_data import IN_GAME_TEXT
from database.queries import (
    get_user_by_id,
    add_user_to_game,
    add_user,
    get_user_buns_stats,
    get_top_users_by_points,
    set_user_out_of_game,
    remove_user_from_game,
    get_all_users,
)

in_game_r = Router()


ALLOWED_ADMIN_ID = 267863612  # ID пользователя, которому разрешены команды


def pluralize_times(count: int) -> str:
    """Возвращает правильную форму слова 'раз' в зависимости от числа."""
    if count % 10 == 1 and count % 100 != 11:
        return f"{count} раз"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return f"{count} раза"
    else:
        return f"{count} раз"


def pluralize_points(points: int) -> str:
    """Возвращает правильную форму слова 'очко' в зависимости от числа."""
    if points % 10 == 1 and points % 100 != 11:
        return f"{points} очко"
    elif points % 10 in [2, 3, 4] and points % 100 not in [12, 13, 14]:
        return f"{points} очка"
    else:
        return f"{points} очков"


@in_game_r.message(Command(commands="play"))
async def in_game_handler(message: types.Message):
    from_user = message.from_user
    chat_id = message.chat.id
    if message.chat.type == "private":
        await message.reply("Эту команду можно использовать только в групповом чате!")
        return
    if not from_user:
        await message.reply("Не удалось получить информацию о пользователе.")
        return
    user_id = from_user.id
    user = await get_user_by_id(user_id, chat_id)
    if user:
        if user.in_game:
            await message.reply("Ты уже в игре! 🎮")
        else:
            await add_user_to_game(user_id)
            text = random.choice(IN_GAME_TEXT).format(
                user=(
                    f"@{from_user.username}"
                    if from_user.username
                    else from_user.full_name
                )
            )
            await message.reply(text)
    else:
        await add_user(
            telegram_id=user_id,
            username=from_user.username,
            full_name=from_user.full_name,
            chat_id=chat_id,
        )
        text = random.choice(IN_GAME_TEXT).format(
            user=f"@{from_user.username}" if from_user.username else from_user.full_name
        )
        await message.reply(text)


@in_game_r.message(Command(commands="stats_me"))
async def stats_me_handler(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if message.chat.type == "private":
        await message.reply("Эту команду можно использовать только в групповом чате!")
        return
    user_buns = await get_user_buns_stats(telegram_id=user_id, chat_id=chat_id)
    if not user_buns:
        await message.reply("Вы еще не выбрали булочек или не играете в этой игре 📊")
        return
    username = message.from_user.username or message.from_user.full_name
    stats_text = f"<b>🧁 Статистика @{username}:</b>\n\n"
    total_points = 0
    for i, item in enumerate(user_buns, start=1):
        bun = item["bun"]
        count = item["count"]
        points = item["points"]
        times_text = pluralize_times(count)
        points_text = pluralize_points(points)
        stats_text += f"{i}. {bun} - {times_text} ({points_text}) 🔥\n"
        total_points += points
    total_points_text = pluralize_points(total_points)
    stats_text += f"\n<b>Всего:</b> {total_points_text}"
    await message.reply(stats_text, parse_mode="HTML")


@in_game_r.message(Command(commands="stats"))
async def statistic_handler(message: types.Message):
    chat_id = message.chat.id
    if message.chat.type == "private":
        await message.reply("Эту команду можно использовать только в групповом чате!")
        return

    top_users = await get_top_users_by_points(chat_id=chat_id)
    if not top_users:
        await message.reply("В этом чате пока нет активных игроков с булочками!")
        return

    stats_text = "<b>🏆 Топ-10 игроков по очкам:</b>\n\n"
    for i, user in enumerate(top_users, start=1):
        display_name = f"@{user['username']}" if user["username"] else user["full_name"]
        times_text = pluralize_times(user["count"])
        stats_text += f"{i}. {display_name} - {user['bun']} ({times_text})\n"
    await message.reply(stats_text, parse_mode="HTML")


@in_game_r.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEFT))
async def on_user_left_chat(update: types.ChatMemberUpdated):
    """Обработка события выхода пользователя из чата."""
    user_id = update.from_user.id
    chat_id = update.chat.id
    if update.chat.type == "private":
        return  # Игнорируем приватные чаты

    # Устанавливаем статус in_game=False
    changed = await set_user_out_of_game(telegram_id=user_id, chat_id=chat_id)
    if changed:
        display_name = (
            f"@{update.from_user.username}"
            if update.from_user.username
            else update.from_user.full_name
        )
        await update.bot.send_message(
            chat_id,
            f"{display_name} покинул чат и больше не участвует в розыгрыше булочек!",
            parse_mode="HTML",
        )


@in_game_r.message(Command(commands="user_list"))
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


@in_game_r.message(Command(commands="remove_from_game"))
async def remove_from_game_handler(message: types.Message):
    """Удаление пользователя из розыгрыша (только для admin в ЛС)."""
    if message.chat.type != "private" or message.from_user.id != ALLOWED_ADMIN_ID:
        await message.reply(
            "Эта команда доступна только администратору в личных сообщениях!"
        )
        return

    # Ожидаем аргументы: telegram_id и chat_id
    args = message.text.split()[1:]  # Пропускаем саму команду
    if len(args) != 2:
        await message.reply("Использование: /remove_from_game <telegram_id> <chat_id>")
        return

    try:
        telegram_id = int(args[0])
        chat_id = int(args[1])
    except ValueError:
        await message.reply("telegram_id и chat_id должны быть числами!")
        return

    removed = await remove_user_from_game(telegram_id=telegram_id, chat_id=chat_id)
    if removed:
        await message.reply(
            f"Пользователь {telegram_id} удален из розыгрыша в чате {chat_id}."
        )
    else:
        await message.reply(
            f"Пользователь {telegram_id} не найден или уже не в игре в чате {chat_id}."
        )
