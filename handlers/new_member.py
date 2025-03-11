# # handlers/new_member.py
# import random
#
# from aiogram import Bot, Router
# from aiogram.types import ChatMemberUpdated
# from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER
# from database.queries import add_user
# from logger import logger
#
# # Список стикеров
# STICKER_IDS = [
#     "CAACAgIAAxkBAAENqQdnmgj2PreJnV9zPnYLeQr9oE_6ywACBmYAAl3N0Uj-7tbvioUa5TYE",
#     "CAACAgIAAxkBAAENp0FnmOucMj3bxD-d8KBzb7sqM1RTlQACu1wAAkI8yEgIHgv8-kFWxzYE",
# ]
#
# new_member_r = Router()
#
#
# @new_member_r.chat_member(
#     ChatMemberUpdatedFilter(IS_NOT_MEMBER >> MEMBER)  # Фильтр на вступление в чат
# )
# async def new_member_handler(event: ChatMemberUpdated, bot: Bot):
#     """Обработчик вступления нового участника в чат: отправляет стикер с упоминанием."""
#     new_member = event.new_chat_member.user
#     chat_id = event.chat.id
#
#     # Пропускаем ботов
#     if new_member.is_bot:
#         logger.debug(f"Пропущен бот: {new_member.full_name} (ID: {new_member.id})")
#         return
#
#     # Добавляем пользователя в базу
#     try:
#         user = await add_user(
#             telegram_id=new_member.id,
#             username=new_member.username,
#             full_name=new_member.full_name,
#             chat_id=chat_id,
#         )
#         if user:
#             logger.info(
#                 f"Добавлен новый участник: {new_member.full_name} (ID: {new_member.id}) в чат {chat_id}"
#             )
#         else:
#             logger.warning(
#                 f"Пользователь {new_member.id} уже существует в базе для чата {chat_id}"
#             )
#     except Exception as e:
#         logger.error(f"Ошибка при добавлении пользователя {new_member.id}: {e}")
#         return
#
#     # Отправляем стикер с упоминанием пользователя
#     try:
#         sticker_id = random.choice(STICKER_IDS)
#         await bot.send_sticker(
#             chat_id,
#             sticker=sticker_id,
#         )
#         logger.info(
#             f"Стикер отправлен новому участнику: {new_member.full_name} (ID: {new_member.id}) в чат {chat_id}"
#         )
#     except Exception as e:
#         logger.error(f"Ошибка при отправке стикера в чат {chat_id}: {e}")
# handlers/new_member.py
import random

from aiogram import Bot, Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER
from database.queries import add_user, get_user_by_id, add_user_to_game
from logger import logger

# Список стикеров
STICKER_IDS = [
    "CAACAgIAAxkBAAENqQdnmgj2PreJnV9zPnYLeQr9oE_6ywACBmYAAl3N0Uj-7tbvioUa5TYE",
    "CAACAgIAAxkBAAENp0FnmOucMj3bxD-d8KBzb7sqM1RTlQACu1wAAkI8yEgIHgv8-kFWxzYE",
]

new_member_r = Router()


@new_member_r.chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER >> MEMBER)  # Фильтр на вступление в чат
)
async def new_member_handler(event: ChatMemberUpdated, bot: Bot):
    """Обработчик вступления участника в чат: отправляет стикер при добавлении или возвращении в игру."""
    new_member = event.new_chat_member.user
    chat_id = event.chat.id

    # Пропускаем ботов
    if new_member.is_bot:
        logger.debug(f"Пропущен бот: {new_member.full_name} (ID: {new_member.id})")
        return

    telegram_id = new_member.id
    # Проверяем, существует ли пользователь в базе
    user = await get_user_by_id(telegram_id, chat_id)

    send_sticker = False
    if user:
        # Пользователь существует, проверяем статус in_game
        if not user.in_game:
            # Если пользователь не в игре, включаем его
            await add_user_to_game(telegram_id, chat_id)
            send_sticker = True
            logger.info(
                f"Пользователь {new_member.full_name} (ID: {telegram_id}) возвращён в игру в чате {chat_id}"
            )
        else:
            logger.debug(f"Пользователь {new_member.id} уже в игре в чате {chat_id}")
    else:
        # Новый пользователь, добавляем с in_game=True
        await add_user(
            telegram_id=telegram_id,
            username=new_member.username,
            full_name=new_member.full_name,
            chat_id=chat_id,
            in_game=True,  # Устанавливаем in_game=True для новых участников
        )
        send_sticker = True
        logger.info(
            f"Добавлен новый участник: {new_member.full_name} (ID: {telegram_id}) в чат {chat_id}"
        )

    # Отправляем стикер, если пользователь новый или вернулся в игру
    if send_sticker:
        try:
            sticker_id = random.choice(STICKER_IDS)
            await bot.send_sticker(chat_id, sticker=sticker_id)
            logger.info(
                f"Стикер отправлен участнику: {new_member.full_name} (ID: {telegram_id}) в чат {chat_id}"
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке стикера в чат {chat_id}: {e}")
