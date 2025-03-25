# Обновленная механика: "Круассановая лавина" (/avalanche)
# Концепция
# Игроки запускают "Круассановую лавину" — кооперативную игру, где первый участник "толкает" круассан с горы (вносит баллы),
# а другие могут присоединиться, усиливая "лавину". Чем больше участников, тем больше круассанов "скатывается" вниз,
# увеличивая общую награду. Есть шанс на "золотую лавину" с бонусом в 10 баллов.
# Это отличается от дуэли (PvP) и тира (одиночный шанс) своей командной динамикой и "нарастающим" эффектом.
#
# Как это работает
# Запуск лавины:
# Игрок отправляет /avalanche start.
# Требуется 5 баллов для старта.
# Лавина активна 60 секунд.
# Участие:
# Другие игроки присоединяются через /avalanche join, внося 3 балла.
# Каждый новый участник добавляет "круассан" в лавину, увеличивая общий пул.
# Результат:
# Через 60 секунд лавина "обрушивается":
# Базовая награда: каждый получает свои баллы обратно + 1 балл за каждого участника.
# Золотая лавина (шанс 5% + 5% за участника сверх первого, до 20%): +10 баллов каждому.
# Пул баллов делится поровну между участниками (остаток "теряется в снегу").
# Ограничения:
# Только в групповых чатах.
# Кулдаун 15 минут (900 секунд) для чата (через Redis).
# Максимум 5 участников.
# Визуальные эффекты:
# Эмодзи для старта, усиления и финала: снег, круассаны, золото.

# from aiogram import Bot, Router
# from aiogram.types import Message
# from aiogram.filters import Command
# from database.queries import (
#     get_user_by_id,
#     get_user_points,
#     update_user_points,
#     reset_user_on_zero_points,
# )
# from logger import logger
# import random
# import asyncio
# import time
# import redis
# import os
#
# croissant_avalanche_r = Router()
#
# # Подключение к Redis
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# redis_client = redis.Redis(
#     host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
# )
#
# # Константы
# AVALANCHE_START_COST = 5  # Стоимость запуска
# AVALANCHE_JOIN_COST = 3  # Стоимость присоединения
# AVALANCHE_COOLDOWN = 900  # 15 минут в секундах
# AVALANCHE_DURATION = 60  # 60 секунд на сбор участников
# MAX_PARTICIPANTS = 5  # Максимум участников
# BASE_GOLD_CHANCE = 5  # Базовый шанс золотой лавины
# GOLD_CHANCE_PER_PLAYER = 5  # Дополнительный шанс за игрока
# GOLD_BONUS = 10  # Бонус за золотую лавину
#
# # Эмодзи
# SNOW_EMOJI = "❄️"  # Старт лавины
# MOUNTAIN_EMOJI = "🏔️"  # Усиление лавины
# CROISSANT_EMOJI = "🥐"  # Обычный круассан
# GOLD_CROISSANT_EMOJI = "🥐✨"  # Золотая лавина
#
# # Сообщения
# AVALANCHE_START_MESSAGES = [
#     "{snow_emoji} @{player} толкнул Круассановую лавину! Внес {cost} баллов. Присоединяйтесь (/avalanche join) в течение 60 секунд! {croissant_emoji}",
# ]
#
# AVALANCHE_JOIN_MESSAGES = [
#     "{mountain_emoji} @{player} усилил лавину! Внес {cost} балла. Круассанов: {count}.",
# ]
#
# AVALANCHE_RESULT_MESSAGES = [
#     "{croissant_emoji} Лавина обрушилась! Награды: {rewards}",
#     "{croissant_emoji} Круассаны скатились вниз! Участники получают: {rewards}",
# ]
#
# AVALANCHE_GOLD_RESULT_MESSAGES = [
#     "{gold_croissant_emoji} ЗОЛОТАЯ ЛАВИНА! Участники в восторге: {rewards}",
#     "{gold_croissant_emoji} Золотой обвал! Награды: {rewards}",
# ]
#
# AVALANCHE_COOLDOWN_MESSAGES = [
#     "Лавина еще не готова, @{player}! Подожди немного. ⏳",
#     "@{player}, круассаны застыли в снегу! Вернись позже. ⏳",
# ]
#
# AVALANCHE_FULL_MESSAGES = [
#     "Лавина слишком большая! Больше участников не добавить. {croissant_emoji}",
# ]
#
# # Словарь активных лавин (chat_id: {starter_id: {"participants": {user_id: cost}, "timestamp": float}})
# active_avalanches = {}
#
#
# @croissant_avalanche_r.message(
#     Command(commands=["avalanche"], prefixes=["/"], suffix="start")
# )
# async def avalanche_start_handler(message: Message, bot: Bot):
#     """Обработчик команды /avalanche start: запуск лавины."""
#     if message.chat.type == "private":
#         await message.reply("Лавина работает только в групповых чатах! 🥐")
#         return
#
#     chat_id = message.chat.id
#     player = message.from_user
#
#     player_data = await get_user_by_id(player.id, chat_id)
#     if not player_data or not player_data.in_game:
#         await message.reply("Ты не в игре! Сначала вступи в игру.")
#         return
#
#     # Проверка кулдауна
#     cooldown_key = f"avalanche:cooldown:{chat_id}"
#     last_avalanche_time = redis_client.get(cooldown_key)
#     if last_avalanche_time and (
#         time.time() - float(last_avalanche_time) < AVALANCHE_COOLDOWN
#     ):
#         await message.reply(
#             random.choice(AVALANCHE_COOLDOWN_MESSAGES).format(player=player.username)
#         )
#         return
#
#     # Проверка баллов
#     player_points = await get_user_points(player.id, chat_id)
#     if player_points < AVALANCHE_START_COST:
#         await message.reply(
#             f"Для запуска лавины нужно минимум {AVALANCHE_START_COST} баллов!"
#         )
#         return
#
#     # Запускаем лавину
#     if chat_id not in active_avalanches:
#         active_avalanches[chat_id] = {}
#     active_avalanches[chat_id][player.id] = {
#         "participants": {player.id: AVALANCHE_START_COST},
#         "timestamp": time.time(),
#     }
#
#     await update_user_points(player.id, chat_id, -AVALANCHE_START_COST)
#     await message.reply(
#         random.choice(AVALANCHE_START_MESSAGES).format(
#             snow_emoji=SNOW_EMOJI,
#             player=player.username,
#             cost=AVALANCHE_START_COST,
#             croissant_emoji=CROISSANT_EMOJI,
#         )
#     )
#
#     # Ждем участников 60 секунд
#     await asyncio.sleep(AVALANCHE_DURATION)
#     if chat_id in active_avalanches and player.id in active_avalanches[chat_id]:
#         await process_avalanche_result(bot, chat_id, player.id)
#
#
# @croissant_avalanche_r.message(
#     Command(commands=["avalanche"], prefixes=["/"], suffix="join")
# )
# async def avalanche_join_handler(message: Message, bot: Bot):
#     """Обработчик команды /avalanche join: присоединение к лавине."""
#     chat_id = message.chat.id
#     player = message.from_user
#
#     if chat_id not in active_avalanches or not active_avalanches[chat_id]:
#         await message.reply(
#             "В чате нет активной лавины! Запусти ее командой /avalanche start 🥐"
#         )
#         return
#
#     player_data = await get_user_by_id(player.id, chat_id)
#     if not player_data or not player_data.in_game:
#         await message.reply("Ты не в игре! Сначала вступи в игру.")
#         return
#
#     # Находим активную лавину
#     starter_id = next(iter(active_avalanches[chat_id]))
#     avalanche = active_avalanches[chat_id][starter_id]
#
#     if player.id in avalanche["participants"]:
#         await message.reply("Ты уже в лавине! Жди обвала. 🥐")
#         return
#
#     if len(avalanche["participants"]) >= MAX_PARTICIPANTS:
#         await message.reply(
#             random.choice(AVALANCHE_FULL_MESSAGES).format(
#                 croissant_emoji=CROISSANT_EMOJI
#             )
#         )
#         return
#
#     # Проверка баллов
#     player_points = await get_user_points(player.id, chat_id)
#     if player_points < AVALANCHE_JOIN_COST:
#         await message.reply(f"Для участия нужно минимум {AVALANCHE_JOIN_COST} балла!")
#         return
#
#     # Добавляем участника
#     await update_user_points(player.id, chat_id, -AVALANCHE_JOIN_COST)
#     avalanche["participants"][player.id] = AVALANCHE_JOIN_COST
#     await message.reply(
#         random.choice(AVALANCHE_JOIN_MESSAGES).format(
#             mountain_emoji=MOUNTAIN_EMOJI,
#             player=player.username,
#             cost=AVALANCHE_JOIN_COST,
#             count=len(avalanche["participants"]),
#         )
#     )
#
#
# async def process_avalanche_result(bot: Bot, chat_id: int, starter_id: int):
#     """Обработка результата лавины."""
#     if chat_id not in active_avalanches or starter_id not in active_avalanches[chat_id]:
#         return
#
#     avalanche = active_avalanches[chat_id][starter_id]
#     participants = avalanche["participants"]
#     participant_count = len(participants)
#
#     # Определяем шанс золотой лавины
#     gold_chance = min(
#         BASE_GOLD_CHANCE + GOLD_CHANCE_PER_PLAYER * (participant_count - 1), 20
#     )
#     is_gold = random.randint(1, 100) <= gold_chance
#
#     # Формируем награды
#     total_pool = sum(participants.values())  # Все внесенные баллы
#     base_reward = total_pool + participant_count  # Добавляем по 1 баллу за участника
#     gold_bonus = GOLD_BONUS if is_gold else 0
#     reward_per_player = (base_reward + gold_bonus) // participant_count
#
#     rewards = []
#     for pid, cost in participants.items():
#         user_data = await get_user_by_id(pid, chat_id)
#         total_reward = cost + reward_per_player
#         await update_user_points(pid, chat_id, total_reward)
#         rewards.append(f"@{user_data.username}: +{total_reward} баллов")
#
#     # Отправляем результат
#     if is_gold:
#         message_text = random.choice(AVALANCHE_GOLD_RESULT_MESSAGES).format(
#             gold_croissant_emoji=GOLD_CROISSANT_EMOJI, rewards=", ".join(rewards)
#         )
#     else:
#         message_text = random.choice(AVALANCHE_RESULT_MESSAGES).format(
#             croissant_emoji=CROISSANT_EMOJI, rewards=", ".join(rewards)
#         )
#     await bot.send_message(chat_id, message_text)
#
#     # Устанавливаем кулдаун
#     redis_client.setex(f"avalanche:cooldown:{chat_id}", AVALANCHE_COOLDOWN, time.time())
#
#     # Удаляем лавину
#     del active_avalanches[chat_id][starter_id]
#     if not active_avalanches[chat_id]:
#         del active_avalanches[chat_id]
#
#     # Проверка обнуления (маловероятно, но на всякий случай)
#     for pid in participants:
#         points = await get_user_points(pid, chat_id)
#         if points <= 0:
#             await reset_user_on_zero_points(pid, chat_id)
#             user_data = await get_user_by_id(pid, chat_id)
#             await bot.send_message(
#                 chat_id, f"@{user_data.username} обнулился после лавины!"
#             )
