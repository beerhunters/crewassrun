# import asyncio
# import random
# from aiogram import Bot
# from buns_data import (
#     BUNS,
#     MESSAGES,
#     SHURSHU_MESSAGES,
#     BUNS_POINTS,
# )
# from database.queries import get_random_user, add_or_update_user_bun
#
#
# async def send_random_message(bot: Bot, chat_id: int):
#     user = await get_random_user(chat_id=chat_id)
#     if not user:
#         return
#     pre_message = random.choice(SHURSHU_MESSAGES)
#     await bot.send_message(chat_id, pre_message, parse_mode="HTML")
#     await asyncio.sleep(2)
#     text = "Пу-пу-пу"
#     msg = await bot.send_message(chat_id, text, parse_mode="HTML")
#     emojis = ["⏳", "⌛", "⏳", "⌛", "⏳", "⌛", "⏳", "⌛"]
#     for emoji in emojis:
#         await msg.edit_text(f"Пу-пу-пу... {emoji}")
#         await asyncio.sleep(1)
#     bun = random.choice(BUNS)
#     message = random.choice(MESSAGES).format(
#         user=f"@{user.username}" if user.username else user.full_name, bun=bun
#     )
#     await bot.send_message(chat_id, message, parse_mode="HTML")
#     points_per_bun = BUNS_POINTS.get(bun, 0)
#     await add_or_update_user_bun(
#         user_id=user.id,
#         bun=bun,
#         chat_id=chat_id,
#     )
import asyncio
import random
from aiogram import Bot
from buns_data import SHURSHU_MESSAGES, MESSAGES, BUNS_POINTS
from database.queries import get_random_user, add_or_update_user_bun


async def send_random_message(bot: Bot, chat_id: int):
    user = await get_random_user(chat_id=chat_id)
    if not user:
        return
    pre_message = random.choice(SHURSHU_MESSAGES)
    await bot.send_message(chat_id, pre_message, parse_mode="HTML")
    await asyncio.sleep(2)
    text = "Пу-пу-пу"
    msg = await bot.send_message(chat_id, text, parse_mode="HTML")
    emojis = ["⏳", "⌛", "⏳", "⌛", "⏳", "⌛", "⏳", "⌛"]
    for emoji in emojis:
        await msg.edit_text(f"Пу-пу-пу... {emoji}")
        await asyncio.sleep(1)

    # Выбираем случайную булочку и её очки прямо из BUNS_POINTS
    bun, points_per_bun = random.choice(list(BUNS_POINTS.items()))

    message = random.choice(MESSAGES).format(
        user=f"{user.username}" if user.username else user.full_name, bun=bun
    )
    await bot.send_message(chat_id, message, parse_mode="HTML")

    await add_or_update_user_bun(
        user_id=user.id,
        bun=bun,
        chat_id=chat_id,
    )
