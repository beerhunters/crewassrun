# # Новая механика: "Сосисочная дуэль" (/duel @username)
# # Концепция
# # Игроки могут вызывать друг друга на "сосисочную дуэль" — мини-игру, где два участника соревнуются в меткости или удаче.
# # Победитель получает баллы, а в редких случаях — "сосиску с 10 баллами" (специальный бонус).
# # Это добавит соревновательный элемент и повысит вовлеченность в чате.
# #
# # Как это работает
# # Вызов на дуэль:
# # Игрок отправляет команду /duel @username, указывая соперника.
# # Бот проверяет, что оба участника в игре и имеют минимум 5 баллов (ставка на дуэль).
# # Подтверждение:
# # Жертва должна ответить "Да" (или /accept) в течение 30 секунд, иначе дуэль отменяется.
# # Механика дуэли:
# # Каждый участник "бросает сосиску" (имитация случайного броска).
# # Бот генерирует случайное число от 1 до 10 для каждого:
# # Если у одного результат выше, он побеждает.
# # Если числа равны — ничья, и оба теряют по 2 балла за "неловкость".
# # Шанс "критического попадания" (10): если кто-то выкидывает 10, он получает "сосиску с 10 баллами" как бонус.
# # Награды и штрафы:
# # Победитель забирает 5 баллов от проигравшего + случайный бонус (1-5 баллов).
# # Проигравший теряет 5 баллов.
# # Критическое попадание (10): +10 баллов (специальная "сосиска").
# # Ничья: оба теряют 2 балла.
# # Ограничения:
# # Работает только в групповых чатах.
# # Один игрок может участвовать только в одной дуэли одновременно.
# # Между дуэлями с одним и тем же соперником — кулдаун 10 минут.
#
# from aiogram import Bot, Router, F
# from aiogram.types import Message
# from aiogram.filters import Command
# from database.queries import (
#     get_user_by_id,
#     get_user_points,
#     update_user_points,
#     get_user_by_username,
#     reset_user_on_zero_points,
# )
# import random
# import asyncio
# import time
#
# from logger import logger
#
# duel_game_r = Router()
#
# # Словарь для отслеживания активных дуэлей (chat_id: {challenger_id: {"opponent_id": int, "message_id": int}})
# active_duels = {}
#
# # Словарь для отслеживания кулдаунов (chat_id: {(challenger_id, opponent_id): timestamp})
# duel_cooldowns = {}
#
# # Константы
# DUEL_COOLDOWN = 600  # 10 минут в секундах
#
# # Эмодзи для эффектов
# THROW_EMOJI = "🌭💨"  # Бросок сосиски
# CRIT_EMOJI = "🌭✨"  # Критическое попадание
# HIT_EMOJI = "💥"  # Обычное попадание
# MISS_EMOJI = "😅"  # Ничья или промах
#
# # Сообщения для дуэли
# DUEL_CHALLENGE_MESSAGES = [
#     "@{challenger} вызывает @{opponent} на сосисочную дуэль! Ответь 'Да' или '/accept' в течение 30 секунд! 🌭",
#     "@{opponent}, @{challenger} бросил тебе сосисочный вызов! Примешь? ('Да' или '/accept', 30 сек) 🌭",
#     "Сосисочная дуэль! @{challenger} против @{opponent}! Соглашайся ('Да' или '/accept') в течение 30 секунд! 🌭",
# ]
#
# DUEL_ACCEPTED_MESSAGES = [
#     "Дуэль начинается! @{challenger} против @{opponent}! Кто метче бросит сосиску? 🎯",
#     "@{challenger} и @{opponent} вступают в сосисочную схватку! Готовьте сосиски! 🎯",
#     "Битва сосисок! @{challenger} vs @{opponent}! Пусть победит лучший! 🎯",
# ]
#
# DUEL_THROW_MESSAGES = [
#     "{throw_emoji} @{player} бросает сосиску... Результат: {score}!",
#     "{throw_emoji} @{player} швыряет сосиску с размахом... {score}!",
#     "{throw_emoji} Сосиска от @{player} летит в цель... {score}!",
# ]
#
# DUEL_RESULT_MESSAGES = [
#     "{hit_emoji} @{winner} ({winner_score}) уделал @{loser} ({loser_score})! Победа @{winner}! +{bonus} баллов и 5 от проигравшего!",
#     "{hit_emoji} @{winner} ({winner_score}) метче @{loser} ({loser_score})! @{winner} получает 5 баллов от соперника и бонус {bonus}!",
#     "{hit_emoji} Сосиска @{winner} ({winner_score}) размазала @{loser} ({loser_score})! +5 баллов и {bonus} бонуса!",
# ]
#
# DUEL_CRIT_MESSAGES = [
#     "{crit_emoji} @{winner} выкинул 10 — КРИТИЧЕСКОЕ ПОПАДАНИЕ! Сосиска с 10 баллами и 5 от @{loser} ({loser_score}) в кармане @{winner}!",
#     "{crit_emoji} Критический удар! @{winner} (10) уничтожил @{loser} ({loser_score}) и получает сосиску с 10 баллами + 5 от проигравшего!",
# ]
#
# DUEL_TIE_MESSAGES = [
#     "{miss_emoji} @{challenger} ({challenger_score}) и @{opponent} ({opponent_score}) оба промахнулись! Ничья, оба теряют по 2 балла за неловкость!",
#     "{miss_emoji} Ничья! @{challenger} и @{opponent} показали одинаковый результат ({challenger_score}) — минус 2 балла каждому!",
# ]
#
# DUEL_TIMEOUT_MESSAGES = [
#     "@{opponent} струсил или заснул! Дуэль с @{challenger} отменяется. 🌭",
#     "Время вышло! @{opponent} не принял вызов @{challenger}. Дуэль сорвалась! 🌭",
# ]
#
# DUEL_COOLDOWN_MESSAGES = [
#     "@{challenger}, ты уже дрался с @{opponent}! Подожди немного, сосиски остывают! ⏳",
#     "Между дуэлями с @{opponent} нужно передохнуть, @{challenger}! ⏳",
#     "@{challenger}, дай @{opponent} отдышаться после прошлой сосисочной битвы! ⏳",
# ]
#
#
# @duel_game_r.message(Command("duel"))
# async def duel_challenge_handler(message: Message, bot: Bot):
#     chat_id = message.chat.id
#     challenger = message.from_user
#     logger.debug(f"Вызов дуэли от {challenger.username} в чате {chat_id}")
#
#     if message.chat.type == "private":
#         await message.reply("Дуэли доступны только в групповых чатах! 🌭")
#         return
#
#     if not message.text.split(maxsplit=1)[1:]:
#         await message.reply("Укажи соперника! Пример: /duel @username")
#         return
#
#     opponent_username = message.text.split(maxsplit=1)[1].strip()
#     if not opponent_username.startswith("@"):
#         await message.reply("Юзернейм должен начинаться с @! Пример: /duel @username")
#         return
#     opponent_username = opponent_username[1:]
#
#     challenger_data = await get_user_by_id(challenger.id, chat_id)
#     if not challenger_data or not challenger_data.in_game:
#         await message.reply("Ты не в игре! Сначала вступи в игру.")
#         return
#
#     opponent_data = await get_user_by_username(chat_id, opponent_username)
#     if not opponent_data or not opponent_data.in_game:
#         await message.reply(f"@{opponent_username} не в игре или не найден!")
#         return
#
#     if opponent_data.telegram_id == challenger.id:
#         await message.reply("Нельзя вызвать себя на дуэль, это слишком странно! 🌭")
#         return
#
#     if chat_id in active_duels and (
#         challenger.id in active_duels[chat_id]
#         or opponent_data.telegram_id
#         in [d["opponent_id"] for d in active_duels[chat_id].values()]
#     ):
#         await message.reply("Один из вас уже в дуэли! Дождитесь окончания.")
#         return
#
#     duel_pair = tuple(sorted([challenger.id, opponent_data.telegram_id]))
#     if chat_id in duel_cooldowns and duel_pair in duel_cooldowns[chat_id]:
#         last_duel_time = duel_cooldowns[chat_id][duel_pair]
#         if time.time() - last_duel_time < DUEL_COOLDOWN:
#             await message.reply(
#                 random.choice(DUEL_COOLDOWN_MESSAGES).format(
#                     challenger=challenger.username, opponent=opponent_username
#                 )
#             )
#             return
#
#     challenger_points = await get_user_points(challenger.id, chat_id)
#     opponent_points = await get_user_points(opponent_data.telegram_id, chat_id)
#     if challenger_points < 5 or opponent_points < 5:
#         await message.reply("Для дуэли нужно минимум 5 баллов у каждого!")
#         return
#
#     if chat_id not in active_duels:
#         active_duels[chat_id] = {}
#     challenge_message = await message.reply(
#         random.choice(DUEL_CHALLENGE_MESSAGES).format(
#             challenger=challenger.username, opponent=opponent_username
#         )
#     )
#     active_duels[chat_id][challenger.id] = {
#         "opponent_id": opponent_data.telegram_id,
#         "message_id": challenge_message.message_id,
#     }
#     logger.debug(f"Зарегистрирован вызов: {active_duels[chat_id][challenger.id]}")
#
#     await asyncio.sleep(30)
#     if chat_id in active_duels and challenger.id in active_duels[chat_id]:
#         await bot.send_message(
#             chat_id,
#             random.choice(DUEL_TIMEOUT_MESSAGES).format(
#                 challenger=challenger.username, opponent=opponent_username
#             ),
#         )
#         del active_duels[chat_id][challenger.id]
#         if not active_duels[chat_id]:
#             del active_duels[chat_id]
#
#
# @duel_game_r.message(F.text.in_(["Да", "/accept"]))
# async def duel_accept_handler(message: Message, bot: Bot):
#     chat_id = message.chat.id
#     opponent = message.from_user
#     logger.debug(f"Получено: '{message.text}' от {opponent.username}")
#
#     if not message.reply_to_message:
#         logger.debug("Не реплай")
#         return
#
#     if chat_id not in active_duels:
#         logger.debug("Нет активных дуэлей")
#         return
#
#     challenger_id = next(
#         (
#             cid
#             for cid, data in active_duels[chat_id].items()
#             if data["opponent_id"] == opponent.id
#         ),
#         None,
#     )
#     if not challenger_id:
#         logger.debug(f"Нет вызова для {opponent.username}")
#         return
#
#     expected_message_id = active_duels[chat_id][challenger_id]["message_id"]
#     if message.reply_to_message.message_id != expected_message_id:
#         logger.debug(
#             f"Реплай на {message.reply_to_message.message_id}, ожидался {expected_message_id}"
#         )
#         return
#
#     logger.debug(f"Дуэль принята: {opponent.username} vs {challenger_id}")
#     challenger_data = await get_user_by_id(challenger_id, chat_id)
#     opponent_data = await get_user_by_id(opponent.id, chat_id)
#     if not challenger_data or not opponent_data:
#         await message.reply("Ошибка: один из участников не найден!")
#         return
#
#     await message.reply(
#         random.choice(DUEL_ACCEPTED_MESSAGES).format(
#             challenger=challenger_data.username, opponent=opponent_data.username
#         )
#     )
#
#     del active_duels[chat_id][challenger_id]
#     if not active_duels[chat_id]:
#         del active_duels[chat_id]
#
#     challenger_score = random.randint(1, 10)
#     await bot.send_message(
#         chat_id,
#         random.choice(DUEL_THROW_MESSAGES).format(
#             throw_emoji=THROW_EMOJI,
#             player=challenger_data.username,
#             score=challenger_score,
#         ),
#     )
#     await asyncio.sleep(1)
#
#     opponent_score = random.randint(1, 10)
#     await bot.send_message(
#         chat_id,
#         random.choice(DUEL_THROW_MESSAGES).format(
#             throw_emoji=THROW_EMOJI, player=opponent_data.username, score=opponent_score
#         ),
#     )
#     await asyncio.sleep(1)
#
#     duel_pair = tuple(sorted([challenger_id, opponent.id]))
#     if chat_id not in duel_cooldowns:
#         duel_cooldowns[chat_id] = {}
#     duel_cooldowns[chat_id][duel_pair] = time.time()
#
#     if challenger_score > opponent_score:
#         winner = challenger_data
#         loser = opponent_data
#         winner_score = challenger_score
#         loser_score = opponent_score
#         bonus = random.randint(1, 5)
#         if winner_score == 10:
#             bonus += 10
#             message_text = random.choice(DUEL_CRIT_MESSAGES).format(
#                 crit_emoji=CRIT_EMOJI,
#                 winner=winner.username,
#                 loser=loser.username,
#                 loser_score=loser_score,
#             )
#         else:
#             message_text = random.choice(DUEL_RESULT_MESSAGES).format(
#                 hit_emoji=HIT_EMOJI,
#                 winner=winner.username,
#                 loser=loser.username,
#                 winner_score=winner_score,
#                 loser_score=loser_score,
#                 bonus=bonus,
#             )
#         await update_user_points(winner.telegram_id, chat_id, 5 + bonus)
#         await update_user_points(loser.telegram_id, chat_id, -5)
#
#     elif opponent_score > challenger_score:
#         winner = opponent_data
#         loser = challenger_data
#         winner_score = opponent_score
#         loser_score = challenger_score
#         bonus = random.randint(1, 5)
#         if winner_score == 10:
#             bonus += 10
#             message_text = random.choice(DUEL_CRIT_MESSAGES).format(
#                 crit_emoji=CRIT_EMOJI,
#                 winner=winner.username,
#                 loser=loser.username,
#                 loser_score=loser_score,
#             )
#         else:
#             message_text = random.choice(DUEL_RESULT_MESSAGES).format(
#                 hit_emoji=HIT_EMOJI,
#                 winner=winner.username,
#                 loser=loser.username,
#                 winner_score=winner_score,
#                 loser_score=loser_score,
#                 bonus=bonus,
#             )
#         await update_user_points(winner.telegram_id, chat_id, 5 + bonus)
#         await update_user_points(loser.telegram_id, chat_id, -5)
#
#     else:
#         message_text = random.choice(DUEL_TIE_MESSAGES).format(
#             miss_emoji=MISS_EMOJI,
#             challenger=challenger_data.username,
#             opponent=opponent_data.username,
#             challenger_score=challenger_score,
#             opponent_score=opponent_score,
#         )
#         await update_user_points(challenger_id, chat_id, -2)
#         await update_user_points(opponent.id, chat_id, -2)
#
#     await bot.send_message(chat_id, message_text)
#
#     new_challenger_points = await get_user_points(challenger_id, chat_id)
#     new_opponent_points = await get_user_points(opponent.id, chat_id)
#     if new_challenger_points <= 0:
#         await reset_user_on_zero_points(challenger_id, chat_id)
#         await bot.send_message(
#             chat_id, f"@{challenger_data.username} обнулился после дуэли! {MISS_EMOJI}"
#         )
#     if new_opponent_points <= 0:
#         await reset_user_on_zero_points(opponent.id, chat_id)
#         await bot.send_message(
#             chat_id, f"@{opponent_data.username} обнулился после дуэли! {MISS_EMOJI}"
#         )
#
#
# # from aiogram import Bot, Router
# # from aiogram.types import Message, ChatType
# # from aiogram.filters import Command, Text
# # from database.queries import (
# #     get_user_by_id,
# #     get_user_points,
# #     update_user_points,
# #     get_user_by_username,
# #     reset_user_on_zero_points,
# # )
# # from logger import logger
# # import random
# # import asyncio
# # import time
# # import redis
# # import os
# # import json
# #
# # duel_game_r = Router()
# #
# # # Подключение к Redis
# # REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# # REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# # redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
# #
# # # Словарь для отслеживания активных дуэлей (chat_id: {challenger_id: opponent_id})
# # active_duels = {}
# #
# # # Константы
# # DUEL_COOLDOWN = 600  # 10 минут в секундах
# #
# # # Эмодзи для эффектов
# # THROW_EMOJI = "🌭💨"  # Бросок сосиски
# # CRIT_EMOJI = "🌭✨"   # Критическое попадание
# # HIT_EMOJI = "💥"      # Обычное попадание
# # MISS_EMOJI = "😅"     # Ничья или промах
# #
# # # Сообщения для дуэли
# # DUEL_CHALLENGE_MESSAGES = [
# #     "@{challenger} вызывает @{opponent} на сосисочную дуэль! Ответь 'Да' или '/accept' в течение 30 секунд! 🌭",
# #     "@{opponent}, @{challenger} бросил тебе сосисочный вызов! Примешь? ('Да' или '/accept', 30 сек) 🌭",
# #     "Сосисочная дуэль! @{challenger} против @{opponent}! Соглашайся ('Да' или '/accept') в течение 30 секунд! 🌭",
# # ]
# #
# # DUEL_ACCEPTED_MESSAGES = [
# #     "Дуэль начинается! @{challenger} против @{opponent}! Кто метче бросит сосиску? 🎯",
# #     "@{challenger} и @{opponent} вступают в сосисочную схватку! Готовьте сосиски! 🎯",
# #     "Битва сосисок! @{challenger} vs @{opponent}! Пусть победит лучший! 🎯",
# # ]
# #
# # DUEL_THROW_MESSAGES = [
# #     "{throw_emoji} @{player} бросает сосиску... Результат: {score}!",
# #     "{throw_emoji} @{player} швыряет сосиску с размахом... {score}!",
# #     "{throw_emoji} Сосиска от @{player} летит в цель... {score}!",
# # ]
# #
# # DUEL_RESULT_MESSAGES = [
# #     "{hit_emoji} @{winner} ({winner_score}) уделал @{loser} ({loser_score})! Победа @{winner}! +{bonus} баллов и 5 от проигравшего!",
# #     "{hit_emoji} @{winner} ({winner_score}) метче @{loser} ({loser_score})! @{winner} получает 5 баллов от соперника и бонус {bonus}!",
# #     "{hit_emoji} Сосиска @{winner} ({winner_score}) размазала @{loser} ({loser_score})! +5 баллов и {bonus} бонуса!",
# # ]
# #
# # DUEL_CRIT_MESSAGES = [
# #     "{crit_emoji} @{winner} выкинул 10 — КРИТИЧЕСКОЕ ПОПАДАНИЕ! Сосиска с 10 баллами и 5 от @{loser} ({loser_score}) в кармане @{winner}!",
# #     "{crit_emoji} Критический удар! @{winner} (10) уничтожил @{loser} ({loser_score}) и получает сосиску с 10 баллами + 5 от проигравшего!",
# # ]
# #
# # DUEL_TIE_MESSAGES = [
# #     "{miss_emoji} @{challenger} ({challenger_score}) и @{opponent} ({opponent_score}) оба промахнулись! Ничья, оба теряют по 2 балла за неловкость!",
# #     "{miss_emoji} Ничья! @{challenger} и @{opponent} показали одинаковый результат ({challenger_score}) — минус 2 балла каждому!",
# # ]
# #
# # DUEL_TIMEOUT_MESSAGES = [
# #     "@{opponent} струсил или заснул! Дуэль с @{challenger} отменяется. 🌭",
# #     "Время вышло! @{opponent} не принял вызов @{challenger}. Дуэль сорвалась! 🌭",
# # ]
# #
# # DUEL_COOLDOWN_MESSAGES = [
# #     "@{challenger}, ты уже дрался с @{opponent}! Подожди немного, сосиски остывают! ⏳",
# #     "Между дуэлями с @{opponent} нужно передохнуть, @{challenger}! ⏳",
# #     "@{challenger}, дай @{opponent} отдышаться после прошлой сосисочной битвы! ⏳",
# # ]
# #
# #
# # @duel_game_r.message(Command("duel"))
# # async def duel_challenge_handler(message: Message, bot: Bot):
# #     """Обработчик команды /duel @username: вызов на сосисочную дуэль."""
# #     if message.chat.type in [ChatType.PRIVATE]:
# #         await message.reply("Дуэли доступны только в групповых чатах! 🌭")
# #         return
# #
# #     chat_id = message.chat.id
# #     challenger = message.from_user
# #
# #     if not message.text.split(maxsplit=1)[1:]:
# #         await message.reply("Укажи соперника! Пример: /duel @username")
# #         return
# #
# #     opponent_username = message.text.split(maxsplit=1)[1].strip()
# #     if not opponent_username.startswith("@"):
# #         await message.reply("Юзернейм должен начинаться с @! Пример: /duel @username")
# #         return
# #     opponent_username = opponent_username[1:]
# #
# #     # Проверка участников
# #     challenger_data = await get_user_by_id(challenger.id, chat_id)
# #     if not challenger_data or not challenger_data.in_game:
# #         await message.reply("Ты не в игре! Сначала вступи в игру.")
# #         return
# #
# #     opponent_data = await get_user_by_username(chat_id, opponent_username)
# #     if not opponent_data or not opponent_data.in_game:
# #         await message.reply(f"@{opponent_username} не в игре или не найден!")
# #         return
# #
# #     if opponent_data.telegram_id == challenger.id:
# #         await message.reply("Нельзя вызвать себя на дуэль, это слишком странно! 🌭")
# #         return
# #
# #     # Проверка активных дуэлей
# #     if chat_id in active_duels and (challenger.id in active_duels[chat_id] or opponent_data.telegram_id in active_duels[chat_id]):
# #         await message.reply("Один из вас уже в дуэли! Дождитесь окончания.")
# #         return
# #
# #     # Проверка кулдауна в Redis
# #     duel_key = f"duel:cooldown:{chat_id}:{sorted([challenger.id, opponent_data.telegram_id])}"
# #     last_duel_time = redis_client.get(duel_key)
# #     if last_duel_time and (time.time() - float(last_duel_time) < DUEL_COOLDOWN):
# #         await message.reply(
# #             random.choice(DUEL_COOLDOWN_MESSAGES).format(
# #                 challenger=challenger.username,
# #                 opponent=opponent_username
# #             )
# #         )
# #         return
# #
# #     # Проверка баллов
# #     challenger_points = await get_user_points(challenger.id, chat_id)
# #     opponent_points = await get_user_points(opponent_data.telegram_id, chat_id)
# #     if challenger_points < 5 or opponent_points < 5:
# #         await message.reply("Для дуэли нужно минимум 5 баллов у каждого!")
# #         return
# #
# #     # Регистрируем дуэль
# #     if chat_id not in active_duels:
# #         active_duels[chat_id] = {}
# #     active_duels[chat_id][challenger.id] = opponent_data.telegram_id
# #
# #     # Отправляем вызов
# #     await message.reply(
# #         random.choice(DUEL_CHALLENGE_MESSAGES).format(
# #             challenger=challenger.username,
# #             opponent=opponent_username
# #         )
# #     )
# #
# #     # Ждем ответа 30 секунд
# #     await asyncio.sleep(30)
# #     if chat_id in active_duels and challenger.id in active_duels[chat_id]:
# #         await bot.send_message(
# #             chat_id,
# #             random.choice(DUEL_TIMEOUT_MESSAGES).format(
# #                 challenger=challenger.username,
# #                 opponent=opponent_username
# #             )
# #         )
# #         del active_duels[chat_id][challenger.id]
# #         if not active_duels[chat_id]:
# #             del active_duels[chat_id]
# #
# #
# # @duel_game_r.message(Text(text=["Да", "/accept"], ignore_case=True))
# # async def duel_accept_handler(message: Message, bot: Bot):
# #     """Обработчик принятия дуэли."""
# #     chat_id = message.chat.id
# #     opponent = message.from_user
# #
# #     # Проверяем, есть ли активный вызов для этого пользователя
# #     if chat_id not in active_duels or not any(opponent.id == opp_id for opp_id in active_duels[chat_id].values()):
# #         await message.reply("Тебя никто не вызывал на дуэль! 🌭")
# #         return
# #
# #     # Находим вызывающего
# #     challenger_id = next(
# #         cid for cid, oid in active_duels[chat_id].items() if oid == opponent.id
# #     )
# #     challenger_data = await get_user_by_id(challenger_id, chat_id)
# #     opponent_data = await get_user_by_id(opponent.id, chat_id)
# #
# #     # Начинаем дуэль
# #     await message.reply(
# #         random.choice(DUEL_ACCEPTED_MESSAGES).format(
# #             challenger=challenger_data.username,
# #             opponent=opponent_data.username
# #         )
# #     )
# #
# #     # Удаляем дуэль из активных перед началом
# #     del active_duels[chat_id][challenger_id]
# #     if not active_duels[chat_id]:
# #         del active_duels[chat_id]
# #
# #     # Броски сосисок с эффектами
# #     challenger_score = random.randint(1, 10)
# #     await bot.send_message(
# #         chat_id,
# #         random.choice(DUEL_THROW_MESSAGES).format(
# #             throw_emoji=THROW_EMOJI,
# #             player=challenger_data.username,
# #             score=challenger_score
# #         )
# #     )
# #     await asyncio.sleep(1)  # Пауза для эффекта
# #
# #     opponent_score = random.randint(1, 10)
# #     await bot.send_message(
# #         chat_id,
# #         random.choice(DUEL_THROW_MESSAGES).format(
# #             throw_emoji=THROW_EMOJI,
# #             player=opponent_data.username,
# #             score=opponent_score
# #         )
# #     )
# #     await asyncio.sleep(1)  # Пауза для эффекта
# #
# #     # Результат дуэли
# #     duel_key = f"duel:cooldown:{chat_id}:{sorted([challenger_id, opponent.id])}"
# #     redis_client.setex(duel_key, DUEL_COOLDOWN, time.time())  # Устанавливаем кулдаун в Redis
# #
# #     if challenger_score > opponent_score:
# #         winner = challenger_data
# #         loser = opponent_data
# #         winner_score = challenger_score
# #         loser_score = opponent_score
# #         bonus = random.randint(1, 5)
# #         if winner_score == 10:
# #             bonus += 10  # Сосиска с 10 баллами
# #             message_text = random.choice(DUEL_CRIT_MESSAGES).format(
# #                 crit_emoji=CRIT_EMOJI,
# #                 winner=winner.username,
# #                 loser=loser.username,
# #                 loser_score=loser_score
# #             )
# #         else:
# #             message_text = random.choice(DUEL_RESULT_MESSAGES).format(
# #                 hit_emoji=HIT_EMOJI,
# #                 winner=winner.username,
# #                 loser=loser.username,
# #                 winner_score=winner_score,
# #                 loser_score=loser_score,
# #                 bonus=bonus
# #             )
# #         await update_user_points(winner.telegram_id, chat_id, 5 + bonus)
# #         await update_user_points(loser.telegram_id, chat_id, -5)
# #
# #     elif opponent_score > challenger_score:
# #         winner = opponent_data
# #         loser = challenger_data
# #         winner_score = opponent_score
# #         loser_score = challenger_score
# #         bonus = random.randint(1, 5)
# #         if winner_score == 10:
# #             bonus += 10  # Сосиска с 10 баллами
# #             message_text = random.choice(DUEL_CRIT_MESSAGES).format(
# #                 crit_emoji=CRIT_EMOJI,
# #                 winner=winner.username,
# #                 loser=loser.username,
# #                 loser_score=loser_score
# #             )
# #         else:
# #             message_text = random.choice(DUEL_RESULT_MESSAGES).format(
# #                 hit_emoji=HIT_EMOJI,
# #                 winner=winner.username,
# #                 loser=loser.username,
# #                 winner_score=winner_score,
# #                 loser_score=loser_score,
# #                 bonus=bonus
# #             )
# #         await update_user_points(winner.telegram_id, chat_id, 5 + bonus)
# #         await update_user_points(loser.telegram_id, chat_id, -5)
# #
# #     else:  # Ничья
# #         message_text = random.choice(DUEL_TIE_MESSAGES).format(
# #             miss_emoji=MISS_EMOJI,
# #             challenger=challenger_data.username,
# #             opponent=opponent_data.username,
# #             challenger_score=challenger_score,
# #             opponent_score=opponent_score
# #         )
# #         await update_user_points(challenger_id, chat_id, -2)
# #         await update_user_points(opponent.id, chat_id, -2)
# #
# #     await bot.send_message(chat_id, message_text)
# #
# #     # Проверка обнуления баллов
# #     new_challenger_points = await get_user_points(challenger_id, chat_id)
# #     new_opponent_points = await get_user_points(opponent.id, chat_id)
# #     if new_challenger_points <= 0:
# #         await reset_user_on_zero_points(challenger_id, chat_id)
# #         await bot.send_message(chat_id, f"@{challenger_data.username} обнулился после дуэли! {MISS_EMOJI}")
# #     if new_opponent_points <= 0:
# #         await reset_user_on_zero_points(opponent.id, chat_id)
# #         await bot.send_message(chat_id, f"@{opponent_data.username} обнулился после дуэли! {MISS_EMOJI}")
