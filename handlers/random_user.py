# # # import asyncio
# # # import random
# # # from aiogram import Bot
# # # from buns_data import (
# # #     BUNS,
# # #     MESSAGES,
# # #     SHURSHU_MESSAGES,
# # #     BUNS_POINTS,
# # # )
# # # from database.queries import get_random_user, add_or_update_user_bun
# # #
# # #
# # # async def send_random_message(bot: Bot, chat_id: int):
# # #     user = await get_random_user(chat_id=chat_id)
# # #     if not user:
# # #         return
# # #     pre_message = random.choice(SHURSHU_MESSAGES)
# # #     await bot.send_message(chat_id, pre_message, parse_mode="HTML")
# # #     await asyncio.sleep(2)
# # #     text = "Пу-пу-пу"
# # #     msg = await bot.send_message(chat_id, text, parse_mode="HTML")
# # #     emojis = ["⏳", "⌛", "⏳", "⌛", "⏳", "⌛", "⏳", "⌛"]
# # #     for emoji in emojis:
# # #         await msg.edit_text(f"Пу-пу-пу... {emoji}")
# # #         await asyncio.sleep(1)
# # #     bun = random.choice(BUNS)
# # #     message = random.choice(MESSAGES).format(
# # #         user=f"@{user.username}" if user.username else user.full_name, bun=bun
# # #     )
# # #     await bot.send_message(chat_id, message, parse_mode="HTML")
# # #     points_per_bun = BUNS_POINTS.get(bun, 0)
# # #     await add_or_update_user_bun(
# # #         user_id=user.id,
# # #         bun=bun,
# # #         chat_id=chat_id,
# # #     )
# # import asyncio
# # import random
# # from aiogram import Bot
# # from buns_data import SHURSHU_MESSAGES, MESSAGES, BUNS_POINTS
# # from database.queries import get_random_user, add_or_update_user_bun
# #
# #
# # async def send_random_message(bot: Bot, chat_id: int):
# #     user = await get_random_user(chat_id=chat_id)
# #     if not user:
# #         return
# #     pre_message = random.choice(SHURSHU_MESSAGES)
# #     await bot.send_message(chat_id, pre_message, parse_mode="HTML")
# #     await asyncio.sleep(2)
# #     text = "Пу-пу-пу"
# #     msg = await bot.send_message(chat_id, text, parse_mode="HTML")
# #     emojis = ["⏳", "⌛", "⏳", "⌛", "⏳", "⌛", "⏳", "⌛"]
# #     for emoji in emojis:
# #         await msg.edit_text(f"Пу-пу-пу... {emoji}")
# #         await asyncio.sleep(1)
# #
# #     # Выбираем случайную булочку и её очки прямо из BUNS_POINTS
# #     bun, points_per_bun = random.choice(list(BUNS_POINTS.items()))
# #
# #     message = random.choice(MESSAGES).format(
# #         user=f"{user.username}" if user.username else user.full_name, bun=bun
# #     )
# #     await bot.send_message(chat_id, message, parse_mode="HTML")
# #
# #     await add_or_update_user_bun(
# #         user_id=user.id,
# #         bun=bun,
# #         chat_id=chat_id,
# #     )
# # handlers/random_user.py
# import asyncio
# import random
# from aiogram import Bot
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from buns_data import SHURSHU_MESSAGES, MESSAGES, BUNS_POINTS
# from database.queries import get_random_user, add_or_update_user_bun
# from logger import logger
#
#
# async def send_random_message(bot: Bot, chat_id: int):
#     """Отправка интерактивного сообщения с выбором случайной булочки."""
#     # Проверяем, есть ли активные пользователи
#     user = await get_random_user(chat_id=chat_id)
#     if not user:
#         await bot.send_message(chat_id, "В этом чате нет активных игроков! 😔")
#         logger.warning(f"Нет активных пользователей в чате {chat_id}")
#         return
#
#     display_name = f"{user.username}" if user.username else user.full_name
#
#     # 1. Вступительное сообщение
#     pre_message = random.choice(SHURSHU_MESSAGES)
#     await bot.send_message(
#         chat_id, pre_message.format(user=display_name), parse_mode="HTML"
#     )
#     await asyncio.sleep(1)
#
#     # 2. Анимация "рулетки" булочек
#     bun_names = list(BUNS_POINTS.keys())
#     text = "Крутим барабан булочек... 🎡"
#     msg = await bot.send_message(chat_id, text, parse_mode="HTML")
#
#     for _ in range(5):  # 5 итераций для эффекта
#         random_bun = random.choice(bun_names)
#         await msg.edit_text(f"Крутим барабан булочек... 🎡\nТекущая: {random_bun}")
#         await asyncio.sleep(0.8)  # Ускоряем для динамики
#
#     # 3. Финальный "барабанный бой"
#     effects = ["🥁 Шур-шур...", "🥁 Бум-бум...", "🥁 Тадам!"]
#     for effect in effects:
#         await msg.edit_text(effect)
#         await asyncio.sleep(1)
#
#     # 4. Раскрытие булочки
#     bun, points_per_bun = random.choice(list(BUNS_POINTS.items()))
#     final_message = random.choice(MESSAGES).format(user=display_name, bun=bun)
#     await msg.edit_text(
#         f"{final_message}\n\nОчков за булочку: <b>{points_per_bun}</b> 🍰",
#         parse_mode="HTML",
#     )
#
#     # 5. Сохранение результата в базе
#     try:
#         await add_or_update_user_bun(
#             user_id=user.id,
#             bun=bun,
#             chat_id=chat_id,
#         )
#         logger.info(f"Булочка {bun} добавлена для {display_name} в чате {chat_id}")
#     except Exception as e:
#         logger.error(
#             f"Ошибка при сохранении булочки для {user.id} в чате {chat_id}: {e}"
#         )
# handlers/random_user.py
import asyncio
import random
from aiogram import Bot
from buns_data import SHURSHU_MESSAGES, MESSAGES, BUNS_POINTS
from database.queries import get_random_user, add_or_update_user_bun
from logger import logger


async def send_random_message(bot: Bot, chat_id: int):
    """Отправка интерактивного сообщения с выбором случайной булочки."""
    # Проверяем, есть ли активные пользователи
    user = await get_random_user(chat_id=chat_id)
    if not user:
        await bot.send_message(chat_id, "В этом чате нет активных игроков! 😔")
        logger.warning(f"Нет активных пользователей в чате {chat_id}")
        return

    display_name = f"{user.username}" if user.username else user.full_name

    # 1. Вступительное сообщение
    pre_message = random.choice(SHURSHU_MESSAGES)
    await bot.send_message(
        chat_id, pre_message.format(user=display_name), parse_mode="HTML"
    )
    await asyncio.sleep(1)

    # 2. Анимация "рулетки" булочек
    bun_names = list(BUNS_POINTS.keys())
    text = "Крутим барабан булочек... 🎡"
    msg = await bot.send_message(chat_id, text, parse_mode="HTML")

    # Выбираем 5 уникальных булочек для анимации
    animation_buns = random.sample(
        bun_names, min(5, len(bun_names))
    )  # Уникальные значения
    for random_bun in animation_buns:
        await msg.edit_text(f"Крутим барабан булочек... 🎡\nТекущая: {random_bun}")
        await asyncio.sleep(0.8)  # Ускоряем для динамики

    # 3. Финальный "барабанный бой"
    effects = ["🥁 Шур-шур...", "🥁 Бум-бум...", "🥁 Тадам!"]
    for effect in effects:
        await msg.edit_text(effect)
        await asyncio.sleep(1)

    # 4. Раскрытие булочки
    bun, points_per_bun = random.choice(list(BUNS_POINTS.items()))
    final_message = random.choice(MESSAGES).format(user=display_name, bun=bun)
    await msg.edit_text(
        f"{final_message}\n\nОчков за булочку: <b>{points_per_bun}</b> 🍰",
        parse_mode="HTML",
    )

    # 5. Сохранение результата в базе
    try:
        await add_or_update_user_bun(
            user_id=user.id,
            bun=bun,
            chat_id=chat_id,
        )
        logger.info(f"Булочка {bun} добавлена для {display_name} в чате {chat_id}")
    except Exception as e:
        logger.error(
            f"Ошибка при сохранении булочки для {user.id} в чате {chat_id}: {e}"
        )
