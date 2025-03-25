# Новая механика: "Сосисочный тир" (/shooting_range)
# Концепция
# Игроки могут участвовать в "Сосисочном тире" — мини-игре, где они "стреляют" сосисками по мишеням.
# Это одиночная игра с элементами удачи и риска: чем дальше мишень, тем сложнее попасть, но выше награда.
# Успешные попадания приносят баллы, а редкое "идеальное попадание" дает "сосиску с 10 баллами".
# Добавим визуальные эффекты и возможность "перестрелки" для повышения интерактивности.
#
# Как это работает
# Запуск тира:
# Игрок отправляет /shooting_range.
# Требуется минимум 3 балла для участия (стоимость "патрона").
# Выбор мишени:
# Бот предлагает 3 мишени с разным расстоянием и шансом попадания:
# Близкая (70% успеха, +3 балла).
# Средняя (50% успеха, +5 баллов).
# Дальняя (30% успеха, +8 баллов).
# Игрок отвечает числом (1, 2 или 3) в течение 15 секунд.
# Стрельба:
# Бот имитирует бросок сосиски с визуальными эффектами.
# Шанс "идеального попадания" (5% для любой мишени): +10 баллов ("сосиска").
# Награды и штрафы:
# Попадание: игрок получает баллы в зависимости от мишени.
# Промах: теряет 3 балла (стоимость "патрона").
# Идеальное попадание: +10 баллов дополнительно.
# Ограничения:
# Только в групповых чатах.
# Кулдаун 5 минут (300 секунд) для каждого игрока (через Redis).
# Перестрелка (опционально):
# Если в течение 10 секунд после попадания другой игрок пишет /shoot, он "перехватывает" часть награды (2 балла), если попадет в ту же мишень.

# from aiogram import Bot, Router, F
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
# shooting_range_r = Router()
#
# # Подключение к Redis
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# redis_client = redis.Redis(
#     host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
# )
#
# # Константы
# SHOOTING_COST = 3  # Стоимость выстрела
# SHOOTING_COOLDOWN = 300  # 5 минут в секундах
# TARGETS = [
#     {"name": "Близкая", "chance": 70, "reward": 3},
#     {"name": "Средняя", "chance": 50, "reward": 5},
#     {"name": "Дальняя", "chance": 30, "reward": 8},
# ]
# CRIT_CHANCE = 5  # Шанс идеального попадания (5%)
# CRIT_BONUS = 10  # Бонус за идеальное попадание
#
# # Эмодзи
# THROW_EMOJI = "🌭💨"  # Бросок
# CRIT_EMOJI = "🌭✨"  # Идеальное попадание
# HIT_EMOJI = "🎯"  # Попадание
# MISS_EMOJI = "💨"  # Промах
#
# # Сообщения
# SHOOTING_START_MESSAGES = [
#     "Добро пожаловать в Сосисочный тир! 🎯 Выбери мишень (ответь числом 1-3 в течение 15 сек):\n"
#     "1. Близкая (70%, +3 балла)\n2. Средняя (50%, +5 баллов)\n3. Дальняя (30%, +8 баллов)",
# ]
#
# SHOOTING_THROW_MESSAGES = [
#     "{throw_emoji} @{player} стреляет по {target} мишени... ",
# ]
#
# SHOOTING_HIT_MESSAGES = [
#     "{hit_emoji} Попадание! +{reward} баллов! Перехватить 2 балла: /shoot (10 сек)!",
#     "{hit_emoji} Точно в цель! @{player} получает +{reward} баллов! /shoot для перехвата (10 сек)!",
# ]
#
# SHOOTING_CRIT_MESSAGES = [
#     "{crit_emoji} ИДЕАЛЬНОЕ ПОПАДАНИЕ! @{player} получает сосиску с 10 баллами + {reward}! Перехват невозможен!",
#     "{crit_emoji} В яблочко! +{reward} баллов и сосиска с 10 баллами для @{player}!",
# ]
#
# SHOOTING_MISS_MESSAGES = [
#     "{miss_emoji} Промах! @{player} теряет {cost} балла.",
#     "{miss_emoji} Сосиска улетела мимо! -{cost} балла для @{player}.",
# ]
#
# SHOOTING_INTERCEPT_MESSAGES = [
#     "{hit_emoji} @{interceptor} перехватил! Забирает 2 балла у @{player}!",
#     "{hit_emoji} Точный выстрел @{interceptor}! 2 балла переходят от @{player}!",
# ]
#
# SHOOTING_INTERCEPT_MISS_MESSAGES = [
#     "{miss_emoji} @{interceptor} промахнулся при перехвате! Ничего не получает.",
# ]
#
# SHOOTING_COOLDOWN_MESSAGES = [
#     "@{player}, тир еще перезаряжается! Подожди немного. ⏳",
#     "Сосиски в тире закончились, @{player}! Вернись позже. ⏳",
# ]
#
# # Словарь активных тиров (chat_id: {player_id: {"target": int, "timestamp": float}})
# active_ranges = {}
#
#
# @shooting_range_r.message(Command("shooting_range"))
# async def shooting_range_handler(message: Message, bot: Bot):
#     """Обработчик команды /shooting_range: запуск сосисочного тира."""
#     if message.chat.type == "private":
#         await message.reply("Тир работает только в групповых чатах! 🌭")
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
#     cooldown_key = f"shooting:cooldown:{chat_id}:{player.id}"
#     last_shot_time = redis_client.get(cooldown_key)
#     if last_shot_time and (time.time() - float(last_shot_time) < SHOOTING_COOLDOWN):
#         await message.reply(
#             random.choice(SHOOTING_COOLDOWN_MESSAGES).format(player=player.username)
#         )
#         return
#
#     # Проверка баллов
#     player_points = await get_user_points(player.id, chat_id)
#     if player_points < SHOOTING_COST:
#         await message.reply(f"Для выстрела нужно минимум {SHOOTING_COST} балла!")
#         return
#
#     # Регистрируем тир
#     if chat_id not in active_ranges:
#         active_ranges[chat_id] = {}
#     active_ranges[chat_id][player.id] = {"target": None, "timestamp": time.time()}
#
#     # Предлагаем выбрать мишень
#     await message.reply(random.choice(SHOOTING_START_MESSAGES))
#
#     # Ждем выбора 15 секунд
#     await asyncio.sleep(15)
#     if (
#         chat_id in active_ranges
#         and player.id in active_ranges[chat_id]
#         and active_ranges[chat_id][player.id]["target"] is None
#     ):
#         await bot.send_message(
#             chat_id, f"@{player.username} не выбрал мишень! Тир закрыт."
#         )
#         del active_ranges[chat_id][player.id]
#         if not active_ranges[chat_id]:
#             del active_ranges[chat_id]
#
#
# @shooting_range_r.message(F.text(text=["1", "2", "3"]))
# async def shooting_target_handler(message: Message, bot: Bot):
#     """Обработчик выбора мишени."""
#     chat_id = message.chat.id
#     player = message.from_user
#
#     if chat_id not in active_ranges or player.id not in active_ranges[chat_id]:
#         return
#
#     target_idx = int(message.text) - 1
#     if target_idx not in range(len(TARGETS)):
#         return
#
#     target = TARGETS[target_idx]
#     active_ranges[chat_id][player.id]["target"] = target_idx
#
#     # Снимаем стоимость выстрела
#     await update_user_points(player.id, chat_id, -SHOOTING_COST)
#
#     # Стрельба
#     await bot.send_message(
#         chat_id,
#         random.choice(SHOOTING_THROW_MESSAGES).format(
#             throw_emoji=THROW_EMOJI,
#             player=player.username,
#             target=target["name"].lower(),
#         ),
#     )
#     await asyncio.sleep(1)
#
#     # Определяем результат
#     hit = random.randint(1, 100) <= target["chance"]
#     crit = random.randint(1, 100) <= CRIT_CHANCE if hit else False
#     reward = target["reward"] + CRIT_BONUS if crit else target["reward"] if hit else 0
#
#     if crit:
#         message_text = random.choice(SHOOTING_CRIT_MESSAGES).format(
#             crit_emoji=CRIT_EMOJI, player=player.username, reward=target["reward"]
#         )
#         await update_user_points(player.id, chat_id, reward)
#         await bot.send_message(chat_id, message_text)
#     elif hit:
#         message_text = random.choice(SHOOTING_HIT_MESSAGES).format(
#             hit_emoji=HIT_EMOJI, player=player.username, reward=reward
#         )
#         await update_user_points(player.id, chat_id, reward)
#         await bot.send_message(chat_id, message_text)
#
#         # Ждем перехват
#         await asyncio.sleep(10)
#         if chat_id in active_ranges and player.id in active_ranges[chat_id]:
#             del active_ranges[chat_id][player.id]
#             if not active_ranges[chat_id]:
#                 del active_ranges[chat_id]
#     else:
#         message_text = random.choice(SHOOTING_MISS_MESSAGES).format(
#             miss_emoji=MISS_EMOJI, player=player.username, cost=SHOOTING_COST
#         )
#         await bot.send_message(chat_id, message_text)
#         del active_ranges[chat_id][player.id]
#         if not active_ranges[chat_id]:
#             del active_ranges[chat_id]
#
#     # Устанавливаем кулдаун
#     redis_client.setex(
#         f"shooting:cooldown:{chat_id}:{player.id}", SHOOTING_COOLDOWN, time.time()
#     )
#
#     # Проверка обнуления
#     new_points = await get_user_points(player.id, chat_id)
#     if new_points <= 0:
#         await reset_user_on_zero_points(player.id, chat_id)
#         await bot.send_message(
#             chat_id, f"@{player.username} обнулился после тира! {MISS_EMOJI}"
#         )
#
#
# @shooting_range_r.message(Command("shoot"))
# async def shooting_intercept_handler(message: Message, bot: Bot):
#     """Обработчик перехвата."""
#     chat_id = message.chat.id
#     interceptor = message.from_user
#
#     if chat_id not in active_ranges or not any(
#         active_ranges[chat_id][pid]["target"] is not None
#         for pid in active_ranges[chat_id]
#     ):
#         await message.reply("Нет активных мишеней для перехвата! 🎯")
#         return
#
#     # Находим последнего стрелявшего
#     shooter_id = max(
#         active_ranges[chat_id], key=lambda pid: active_ranges[chat_id][pid]["timestamp"]
#     )
#     shooter_data = await get_user_by_id(shooter_id, chat_id)
#     target_idx = active_ranges[chat_id][shooter_id]["target"]
#     target = TARGETS[target_idx]
#
#     # Стрельба для перехвата
#     await bot.send_message(
#         chat_id,
#         random.choice(SHOOTING_THROW_MESSAGES).format(
#             throw_emoji=THROW_EMOJI,
#             player=interceptor.username,
#             target=target["name"].lower(),
#         ),
#     )
#     await asyncio.sleep(1)
#
#     hit = random.randint(1, 100) <= target["chance"]
#     if hit:
#         message_text = random.choice(SHOOTING_INTERCEPT_MESSAGES).format(
#             hit_emoji=HIT_EMOJI,
#             interceptor=interceptor.username,
#             player=shooter_data.username,
#         )
#         await update_user_points(interceptor.id, chat_id, 2)
#         await update_user_points(shooter_id, chat_id, -2)
#         await bot.send_message(chat_id, message_text)
#     else:
#         message_text = random.choice(SHOOTING_INTERCEPT_MISS_MESSAGES).format(
#             miss_emoji=MISS_EMOJI, interceptor=interceptor.username
#         )
#         await bot.send_message(chat_id, message_text)
#
#     # Удаляем тир после перехвата
#     del active_ranges[chat_id][shooter_id]
#     if not active_ranges[chat_id]:
#         del active_ranges[chat_id]
