import random

from aiogram import Bot, Router
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus
from database.queries import add_user
from logger import logger


STICKER_IDS = [
    "CAACAgIAAxkBAAENqQdnmgj2PreJnV9zPnYLeQr9oE_6ywACBmYAAl3N0Uj-7tbvioUa5TYE",
    "CAACAgIAAxkBAAENp0FnmOucMj3bxD-d8KBzb7sqM1RTlQACu1wAAkI8yEgIHgv8-kFWxzYE",
]

new_member_r = Router()


@new_member_r.chat_member()
async def new_member_handler(event: ChatMemberUpdated, bot: Bot):
    if (
        event.old_chat_member.status == ChatMemberStatus.LEFT
        and event.new_chat_member.status == ChatMemberStatus.MEMBER
    ):
        new_member = event.new_chat_member.user
        chat_id = event.chat.id
        if not new_member.is_bot:
            await add_user(
                user_id=new_member.id,
                username=new_member.username,
                full_name=new_member.full_name,
                chat_id=chat_id,
            )
            logger.info(
                f"Добавлен новый участник: {new_member.full_name} (ID: {new_member.id})"
            )
            try:
                sticker_id = random.choice(STICKER_IDS)
                await bot.send_sticker(chat_id, sticker=sticker_id)
                logger.info(
                    f"Стикер отправлен новому участнику: {new_member.full_name} (ID: {new_member.id})"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке стикера: {e}")
