# # from aiogram import Bot, Router
# # from aiogram.types import Message
# # from aiogram.filters import Command
# # from database.queries import (
# #     get_user_by_id,
# #     get_user_points,
# #     update_user_points,
# #     get_user_by_username,
# #     get_user_buns_stats,
# #     get_random_user,
# #     get_game_setting,
# #     reset_user_on_zero_points,
# # )
# # from logger import logger
# # import random
# # import asyncio
# #
# # sausage_game_r = Router()
# #
# # # Эмодзи для разных случаев
# # HOTDOG_EMOJI = "🌭"  # Бонус за сосиску
# # HIT_EMOJI = "💥"  # Успешное попадание
# # PENALTY_EMOJI = "😢"  # Штраф за атаку безоружного
# #
# # # Счетчик попыток броска без очков: {chat_id: {user_id: int}}
# # attempts_counter = {}
# #
# # # Юмористические фразы
# # NO_POINTS_MESSAGES = [
# #     "У тебя не хватает сосисочных баллов ({points}/{cost})! Иди испеки булочку!",
# #     "Сосиски не бесплатные, @{username}! У тебя только {points}/{cost} баллов.",
# #     "Твои карманы пусты, @{username}! {points}/{cost} — это не сосисочный уровень.",
# #     "Без баллов сосиску не кинешь, @{username}! ({points}/{cost})",
# # ]
# #
# # NO_POINTS_RANDOM_MESSAGES = [
# #     "@{username} попытался швырнуть случайную сосиску, но баллов нет ({points}/{cost})!",
# #     "Сосиска осталась в кармане у @{username} — не хватает баллов ({points}/{cost})!",
# #     "@{username} хотел кинуть сосиску наугад, но пустые карманы сказали 'нет' ({points}/{cost})!",
# #     "Рандомная сосиска? Не сегодня, @{username}! Баллов мало ({points}/{cost}).",
# # ]
# #
# # NO_POINTS_THIRD_ATTEMPT_MESSAGE = (
# #     "Эй, @{username}, хватит пытаться! У тебя {points} баллов, а нужно {cost}, чтобы кинуть сосиску. "
# #     "Пока не наберешь баллы, ничего не выйдет! Иди за булочками! 🌭"
# # )
# #
# # THROW_MESSAGES = [
# #     "🌭💨 @{attacker} швыряет сосиску в @{target}! Летит...",
# #     "🌭💨 @{attacker} метнул сосиску в @{target}! Смотрим...",
# #     "🌭💨 Сосиска от @{attacker} устремилась к @{target}! Что будет?",
# #     "🌭💨 @{attacker} зарядил сосиску в сторону @{target}! Ждем...",
# #     "🌭💨 @{attacker} бросил сосиску в @{target}! В полете...",
# # ]
# #
# # HIT_MESSAGES = [
# #     "@{attacker} метко попал сосиской в @{target}! У @{target} было {old_points}, стало {new_points}.",
# #     "@{attacker} зарядил сосиской прямо в @{target}! Теперь у жертвы {new_points} вместо {old_points}.",
# #     "Бам! @{attacker} угодил сосиской в @{target}! Баллы упали с {old_points} до {new_points}.",
# #     "@{attacker} устроил сосисочный сюрприз для @{target}! Осталось {new_points} баллов вместо {old_points}.",
# #     "Сосиска от @{attacker} прилетела в @{target}! Баллы тают: {old_points} → {new_points}.",
# # ]
# #
# # PENALTY_MESSAGES = [
# #     "@{attacker} кинул сосиску в @{target}, но тот был безоружен! Расплата: минус {penalty} баллов, осталось {new_points}.",
# #     "@{attacker} зря швырнул сосиску в пустые карманы @{target}! Штраф {penalty}, теперь у тебя {new_points} баллов.",
# #     "Ой-ой, @{attacker}! @{target} оказался без баллов, и сосиска вернулась бумерангом: -{penalty}, осталось {new_points}.",
# #     "@{attacker} попал сосиской в @{target}, но без толку! Штраф за подлость: -{penalty}, итого {new_points}.",
# #     "Сосиска от @{attacker} угодила в @{target}, но без толку! @{attacker} теряет {penalty}, теперь {new_points} баллов.",
# # ]
# #
# # NOT_IN_CHAT_MESSAGES = [
# #     "Сосиска улетела в пустоту, @{target} давно сбежал!",
# #     "@{target} где-то спрятался, и твоя сосиска пропала зря, @{attacker}!",
# #     "Куда кинул, @{attacker}? @{target} уже не в чате, сосиска потерялась!",
# #     "@{attacker} швырнул сосиску, но @{target} испарился из чата!",
# #     "Сосиска не долетела — @{target} сбежал от булочной битвы!",
# # ]
# #
# # SAUSAGE_BONUS_MESSAGES = [
# #     "@{attacker} кинул сосиску в @{target}, но у того уже была сосиска в тесте! Преимущество: +{bonus} баллов, теперь {new_points}!",
# #     "Сосиска от @{attacker} попала в @{target}, и тот обрадовался — он сосисочный мастер! +{bonus}, итого {new_points}.",
# #     "@{target} поймал сосиску от @{attacker} и вспомнил свои сосисочные корни! Бонус: +{bonus}, стало {new_points}.",
# #     "@{attacker}, твоя сосиска сделала @{target} счастливее! Он получает +{bonus} баллов, теперь {new_points}.",
# #     "Бум! @{attacker} попал в @{target}, но сосиска оказалась на его стороне! +{bonus}, итого {new_points}.",
# # ]
# #
# # RANDOM_Sausage_MESSAGES = [
# #     "@{attacker} швырнул сосиску наугад и целится в @{target}!",
# #     "Сосиска от @{attacker} улетела в случайного прохожего — @{target}!",
# #     "@{attacker} решил сыграть в сосисочную рулетку — @{target} под прицелом!",
# #     "Случайный бросок от @{attacker}, и @{target} стал мишенью!",
# #     "@{attacker} кинул сосиску в толпу, а попал в @{target}!",
# # ]
# #
# # MISS_MESSAGES = [
# #     "@{attacker} промахнулся! Сосиска улетела в закат.",
# #     "Ой! @{attacker} не попал в @{target}, она пролетела мимо!",
# #     "@{attacker} метил в @{target}, но сосиска решила уйти в свободный полёт!",
# #     "Промах! @{attacker} не угодил в @{target}, сосиска пропала зря.",
# #     "Сосиска от @{attacker} не долетела до @{target} — точность подкачала!",
# # ]
# #
# # SELF_HIT_MESSAGES = [
# #     "Сосиска чуть не попала в тебя самого, @{username}, но ты увернулся!",
# #     "@{username} швырнул сосиску и чуть не стал жертвой сам — ловкость спасла!",
# #     "Ой-ой, @{username}! Сосиска сделала круг и чуть не вернулась к тебе!",
# #     "@{username} метнул сосиску в воздух, но она решила поиграть с тобой в догонялки!",
# #     "Сосиска от @{username} чуть не устроила автогол, но ты вовремя отпрыгнул!",
# #     "@{username}, ты чуть не угостил себя сосиской — аккуратнее с рандомом!",
# # ]
# #
# # ZERO_POINTS_MESSAGES = [
# #     "@{username} остался без баллов и вылетел из гонки! Все булки растаяли.",
# #     "Баллы @{username} обнулились — прощай, сосисочная слава и булки!",
# #     "@{username} достиг дна: 0 баллов, 0 булок, 0 шансов!",
# #     "Сосисочная карьера @{username} рухнула — 0 баллов, булки конфискованы!",
# #     "@{username} теперь официально банкрот булочной войны — ни баллов, ни булок!",
# # ]
# #
# # NO_USERNAME_MESSAGES = [
# #     "У @{old_target} нет юзернейма, кидаем в @{new_target}!",
# #     "@{old_target} скрыл свой юзернейм, попал под раздачу @{new_target}!",
# #     "Без юзернейма у @{old_target}? Лови, @{new_target}!",
# #     "@{old_target} оказался безымянным, сосиска улетела к @{new_target}!",
# # ]
# #
# #
# # @sausage_game_r.message(Command("sausage", "сосиска"))
# # async def sausage_throw_handler(message: Message, bot: Bot):
# #     """Обработчик команды /sausage или /сосиска @username: кидаем сосиску в другого участника с юмором."""
# #     if message.chat.type == "private":
# #         await message.reply(
# #             "Эту команду можно использовать только в групповых чатах! 🌭"
# #         )
# #         return
# #
# #     chat_id = message.chat.id
# #     attacker = message.from_user
# #
# #     if not message.text.split(maxsplit=1)[1:]:
# #         await message.reply(
# #             "Укажи, в кого кинуть сосиску! Пример: /sausage @username или /сосиска @username"
# #         )
# #         return
# #
# #     target_username = message.text.split(maxsplit=1)[1].strip()
# #     if not target_username.startswith("@"):
# #         await message.reply(
# #             "Юзернейм должен начинаться с @! Пример: /sausage @username или /сосиска @username"
# #         )
# #         return
# #     target_username = target_username[1:]
# #
# #     # Проверка очков перед броском
# #     SAUSAGE_THROW_COST = (
# #         await get_game_setting("sausage_throw_cost") or 2
# #     )  # Установлено 2
# #     attacker_points = await get_user_points(attacker.id, chat_id)
# #     if attacker_points < SAUSAGE_THROW_COST:
# #         await handle_no_points(
# #             bot, chat_id, attacker, attacker_points, SAUSAGE_THROW_COST
# #         )
# #         return
# #
# #     target_data = await get_user_by_username(chat_id, target_username)
# #     if not target_data or not target_data.username:
# #         old_target = target_username
# #         target_data = await get_random_user(chat_id)
# #         if not target_data or not target_data.username:
# #             await message.reply("В чате нет участников с юзернеймами для атаки! 🌭")
# #             return
# #         if target_data.telegram_id == attacker.id:
# #             target_data = await get_random_user(chat_id)
# #             if (
# #                 not target_data
# #                 or not target_data.username
# #                 or target_data.telegram_id == attacker.id
# #             ):
# #                 await message.reply(
# #                     "Не удалось найти подходящую жертву с юзернеймом! 🌭"
# #                 )
# #                 return
# #         message_text = random.choice(NO_USERNAME_MESSAGES).format(
# #             old_target=old_target, new_target=target_data.username
# #         )
# #         await message.reply(message_text)
# #
# #     await process_sausage_throw(bot, chat_id, attacker, target_data.username)
# #
# #
# # @sausage_game_r.message(Command("random_sausage", "случайнаясосиска"))
# # async def random_sausage_throw_handler(message: Message, bot: Bot):
# #     """Обработчик команды /random_sausage: кидаем сосиску в случайного участника игры."""
# #     if message.chat.type == "private":
# #         await message.reply(
# #             "Эту команду можно использовать только в групповых чатах! 🌭"
# #         )
# #         return
# #
# #     chat_id = message.chat.id
# #     attacker = message.from_user
# #
# #     attacker_data = await get_user_by_id(attacker.id, chat_id)
# #     if not attacker_data or not attacker_data.in_game:
# #         await message.reply("Ты не в игре! Сначала вступи в чат и стань участником.")
# #         return
# #
# #     # Проверка очков перед броском
# #     SAUSAGE_THROW_COST = (
# #         await get_game_setting("sausage_throw_cost") or 2
# #     )  # Установлено 2
# #     attacker_points = await get_user_points(attacker.id, chat_id)
# #     if attacker_points < SAUSAGE_THROW_COST:
# #         await handle_no_points(
# #             bot, chat_id, attacker, attacker_points, SAUSAGE_THROW_COST, is_random=True
# #         )
# #         return
# #
# #     target_data = await get_random_user(chat_id)
# #     if not target_data:
# #         await message.reply("В чате нет активных участников для сосисочной атаки!")
# #         return
# #
# #     if not target_data.username or target_data.telegram_id == attacker.id:
# #         old_target = target_data.username or "кого-то без юзернейма"
# #         target_data = await get_random_user(chat_id)
# #         if (
# #             not target_data
# #             or not target_data.username
# #             or target_data.telegram_id == attacker.id
# #         ):
# #             await message.reply("Не удалось найти подходящую жертву с юзернеймом! 🌭")
# #             return
# #         message_text = random.choice(NO_USERNAME_MESSAGES).format(
# #             old_target=old_target, new_target=target_data.username
# #         )
# #         await message.reply(message_text)
# #
# #     await process_sausage_throw(bot, chat_id, attacker, target_data.username)
# #
# #
# # async def handle_no_points(
# #     bot: Bot, chat_id: int, attacker, points: int, cost: int, is_random: bool = False
# # ):
# #     """Обработка ситуации, когда у пользователя недостаточно очков для броска."""
# #     global attempts_counter
# #
# #     # Инициализируем счетчик для чата, если его нет
# #     if chat_id not in attempts_counter:
# #         attempts_counter[chat_id] = {}
# #
# #     # Увеличиваем счетчик попыток для пользователя
# #     user_attempts = attempts_counter[chat_id].get(attacker.id, 0) + 1
# #     attempts_counter[chat_id][attacker.id] = user_attempts
# #
# #     if user_attempts >= 3:
# #         # Третья попытка — выводим доходчивое сообщение и сбрасываем счетчик
# #         message_text = NO_POINTS_THIRD_ATTEMPT_MESSAGE.format(
# #             username=attacker.username, points=points, cost=cost
# #         )
# #         await bot.send_message(chat_id, message_text)
# #         attempts_counter[chat_id][attacker.id] = 0  # Сбрасываем счетчик
# #         logger.info(
# #             f"@{attacker.username} получил предупреждение после 3 попыток без очков в чате {chat_id}"
# #         )
# #     else:
# #         # Обычное сообщение о нехватке очков
# #         messages = NO_POINTS_RANDOM_MESSAGES if is_random else NO_POINTS_MESSAGES
# #         message_text = random.choice(messages).format(
# #             username=attacker.username, points=points, cost=cost
# #         )
# #         await bot.send_message(chat_id, message_text)
# #         logger.info(
# #             f"@{attacker.username} пытался бросить сосиску без очков ({points}/{cost}), попытка {user_attempts}"
# #         )
# #
# #
# # async def process_sausage_throw(bot: Bot, chat_id: int, attacker, target_username: str):
# #     """Общая логика броска сосиски для обеих команд."""
# #     global attempts_counter
# #
# #     SAUSAGE_THROW_COST = (
# #         await get_game_setting("sausage_throw_cost") or 2
# #     )  # Установлено 2
# #     SAUSAGE_HIT_DAMAGE = await get_game_setting("sausage_hit_damage") or 3
# #     SAUSAGE_PENALTY = await get_game_setting("sausage_penalty") or 3
# #     SAUSAGE_BONUS = await get_game_setting("sausage_bonus") or 3
# #     MISS_CHANCE = await get_game_setting("miss_chance") or 10
# #
# #     attacker_data = await get_user_by_id(attacker.id, chat_id)
# #     if not attacker_data or not attacker_data.in_game:
# #         await bot.send_message(
# #             chat_id, "Ты не в игре! Сначала вступи в чат и стань участником."
# #         )
# #         return
# #
# #     target_data = await get_user_by_username(chat_id, target_username)
# #     if not target_data or not target_data.username:
# #         await bot.send_message(
# #             chat_id, f"Не удалось найти @{target_username} с юзернеймом!"
# #         )
# #         return
# #
# #     try:
# #         chat_member = await bot.get_chat_member(chat_id, target_data.telegram_id)
# #         if chat_member.status in ["left", "kicked"]:
# #             message_text = random.choice(NOT_IN_CHAT_MESSAGES).format(
# #                 attacker=attacker.username, target=target_data.username
# #             )
# #             await bot.send_message(chat_id, message_text)
# #             return
# #     except Exception as e:
# #         await bot.send_message(
# #             chat_id, f"Не удалось проверить @{target_username} в чате!"
# #         )
# #         logger.error(
# #             f"Ошибка проверки статуса @{target_username} в чате {chat_id}: {e}"
# #         )
# #         return
# #
# #     if not target_data.in_game:
# #         await bot.send_message(
# #             chat_id, f"@{target_username} не в игре, нельзя кинуть сосиску!"
# #         )
# #         return
# #
# #     # Сообщение о броске
# #     throw_message = random.choice(THROW_MESSAGES).format(
# #         attacker=attacker.username, target=target_data.username
# #     )
# #     await bot.send_message(chat_id, throw_message)
# #     await asyncio.sleep(1)  # Задержка для эффекта
# #
# #     # Уменьшаем баллы атакующего за бросок
# #     attacker_points = await get_user_points(attacker.id, chat_id)
# #     new_attacker_points = attacker_points - SAUSAGE_THROW_COST
# #     await update_user_points(attacker.id, chat_id, -SAUSAGE_THROW_COST)
# #
# #     # Сбрасываем счетчик попыток, так как бросок успешен
# #     if chat_id in attempts_counter and attacker.id in attempts_counter[chat_id]:
# #         attempts_counter[chat_id][attacker.id] = 0
# #
# #     # Проверяем, не обнулились ли баллы атакующего после броска
# #     if new_attacker_points == 0:
# #         await reset_user_on_zero_points(attacker.id, chat_id)
# #         message_text = random.choice(ZERO_POINTS_MESSAGES).format(
# #             username=attacker.username
# #         )
# #         await bot.send_message(chat_id, message_text)
# #         return
# #
# #     # Проверяем вероятность промаха
# #     if random.randint(1, 100) <= MISS_CHANCE:
# #         message_text = random.choice(MISS_MESSAGES).format(
# #             attacker=attacker.username, target=target_data.username
# #         )
# #         await bot.send_message(chat_id, message_text)
# #         return
# #
# #     # Получаем баллы и булочки жертвы
# #     target_points = await get_user_points(target_data.telegram_id, chat_id)
# #     target_buns = await get_user_buns_stats(target_data.telegram_id, chat_id)
# #
# #     # Проверяем, есть ли у жертвы булочка с частичным совпадением "сосиска"
# #     has_sausage = any("сосиска" in bun["bun"].lower() for bun in target_buns)
# #
# #     # Обрабатываем попадание
# #     if target_points > 0:
# #         if has_sausage:
# #             new_target_points = target_points + SAUSAGE_BONUS
# #             await update_user_points(target_data.telegram_id, chat_id, SAUSAGE_BONUS)
# #             message_text = random.choice(SAUSAGE_BONUS_MESSAGES).format(
# #                 attacker=attacker.username,
# #                 target=target_data.username,
# #                 bonus=SAUSAGE_BONUS,
# #                 new_points=new_target_points,
# #             )
# #             await bot.send_message(chat_id, message_text)
# #             await bot.send_message(chat_id, HOTDOG_EMOJI)
# #         else:
# #             new_target_points = max(0, target_points - SAUSAGE_HIT_DAMAGE)
# #             await update_user_points(
# #                 target_data.telegram_id, chat_id, -SAUSAGE_HIT_DAMAGE
# #             )
# #             message_text = random.choice(HIT_MESSAGES).format(
# #                 attacker=attacker.username,
# #                 target=target_data.username,
# #                 old_points=target_points,
# #                 new_points=new_target_points,
# #             )
# #             await bot.send_message(chat_id, message_text)
# #             await bot.send_message(chat_id, HIT_EMOJI)
# #
# #             # Проверяем, не обнулились ли баллы жертвы
# #             if new_target_points == 0:
# #                 await reset_user_on_zero_points(target_data.telegram_id, chat_id)
# #                 message_text = random.choice(ZERO_POINTS_MESSAGES).format(
# #                     username=target_data.username
# #                 )
# #                 await bot.send_message(chat_id, message_text)
# #     else:
# #         new_attacker_points = max(0, new_attacker_points - SAUSAGE_PENALTY)
# #         await update_user_points(attacker.id, chat_id, -SAUSAGE_PENALTY)
# #         message_text = random.choice(PENALTY_MESSAGES).format(
# #             attacker=attacker.username,
# #             target=target_data.username,
# #             penalty=SAUSAGE_PENALTY,
# #             new_points=new_attacker_points,
# #         )
# #         await bot.send_message(chat_id, message_text)
# #         await bot.send_message(chat_id, PENALTY_EMOJI)
# #
# #         # Проверяем, не обнулились ли баллы атакующего после штрафа
# #         if new_attacker_points == 0:
# #             await reset_user_on_zero_points(attacker.id, chat_id)
# #             message_text = random.choice(ZERO_POINTS_MESSAGES).format(
# #                 username=attacker.username
# #             )
# #             await bot.send_message(chat_id, message_text)
# from aiogram import Bot, Router
# from aiogram.types import Message
# from aiogram.filters import Command
# from database.queries import (
#     get_user_by_id,
#     get_user_points,
#     update_user_points,
#     get_user_by_username,
#     get_user_buns_stats,
#     get_random_user,
#     get_game_setting,
#     reset_user_on_zero_points,
# )
# from logger import logger
# import random
# import asyncio
#
# sausage_game_r = Router()
#
# # Эмодзи для разных случаев
# HOTDOG_EMOJI = "🌭"  # Бонус за сосиску
# HIT_EMOJI = "💥"  # Успешное попадание
# PENALTY_EMOJI = "😢"  # Штраф за атаку безоружного
#
# # Счетчик попыток броска без очков: {chat_id: {user_id: int}}
# attempts_counter = {}
#
# # Юмористические фразы
# NO_POINTS_MESSAGES = [
#     "У тебя не хватает сосисочных баллов ({points}/{cost})! Иди испеки булочку!",
#     "Сосиски не бесплатные, @{username}! У тебя только {points}/{cost} баллов.",
#     "Твои карманы пусты, @{username}! {points}/{cost} — это не сосисочный уровень.",
#     "Без баллов сосиску не кинешь, @{username}! ({points}/{cost})",
# ]
#
# NO_POINTS_RANDOM_MESSAGES = [
#     "@{username} попытался швырнуть случайную сосиску, но баллов нет ({points}/{cost})!",
#     "Сосиска осталась в кармане у @{username} — не хватает баллов ({points}/{cost})!",
#     "@{username} хотел кинуть сосиску наугад, но пустые карманы сказали 'нет' ({points}/{cost})!",
#     "Рандомная сосиска? Не сегодня, @{username}! Баллов мало ({points}/{cost}).",
# ]
#
# NO_POINTS_THIRD_ATTEMPT_MESSAGE = (
#     "Эй, @{username}, хватит пытаться! У тебя {points} баллов, а нужно {cost}, чтобы кинуть сосиску. "
#     "Пока не наберешь баллы, ничего не выйдет! Иди за булочками! 🌭"
# )
#
# NO_POINTS_AFTER_THROW_MESSAGES = [
#     "Баллы закончились, @{username}! У тебя теперь {points}/{cost} — пора за булочками!",
#     "Сосиска улетела, а с ней и твои баллы, @{username}! Осталось {points}/{cost}.",
#     "@{username}, ты в нуле ({points}/{cost})! Булки зовут!",
#     "Бросок был, но баллы растаяли, @{username}! ({points}/{cost})",
# ]
#
# THROW_MESSAGES = [
#     "🌭💨 @{attacker} швыряет сосиску в @{target}! Летит...",
#     "🌭💨 @{attacker} метнул сосиску в @{target}! Смотрим...",
#     "🌭💨 Сосиска от @{attacker} устремилась к @{target}! Что будет?",
#     "🌭💨 @{attacker} зарядил сосиску в сторону @{target}! Ждем...",
#     "🌭💨 @{attacker} бросил сосиску в @{target}! В полете...",
# ]
#
# HIT_MESSAGES = [
#     "@{attacker} метко попал сосиской в @{target}! У @{target} было {old_points}, стало {new_points}.",
#     "@{attacker} зарядил сосиской прямо в @{target}! Теперь у жертвы {new_points} вместо {old_points}.",
#     "Бам! @{attacker} угодил сосиской в @{target}! Баллы упали с {old_points} до {new_points}.",
#     "@{attacker} устроил сосисочный сюрприз для @{target}! Осталось {new_points} баллов вместо {old_points}.",
#     "Сосиска от @{attacker} прилетела в @{target}! Баллы тают: {old_points} → {new_points}.",
# ]
#
# PENALTY_MESSAGES = [
#     "@{attacker} кинул сосиску в @{target}, но тот был безоружен! Расплата: минус {penalty} баллов, осталось {new_points}.",
#     "@{attacker} зря швырнул сосиску в пустые карманы @{target}! Штраф {penalty}, теперь у тебя {new_points} баллов.",
#     "Ой-ой, @{attacker}! @{target} оказался без баллов, и сосиска вернулась бумерангом: -{penalty}, осталось {new_points}.",
#     "@{attacker} попал сосиской в @{target}, но без толку! Штраф за подлость: -{penalty}, итого {new_points}.",
#     "Сосиска от @{attacker} угодила в @{target}, но без толку! @{attacker} теряет {penalty}, теперь {new_points} баллов.",
# ]
#
# NOT_IN_CHAT_MESSAGES = [
#     "Сосиска улетела в пустоту, @{target} давно сбежал!",
#     "@{target} где-то спрятался, и твоя сосиска пропала зря, @{attacker}!",
#     "Куда кинул, @{attacker}? @{target} уже не в чате, сосиска потерялась!",
#     "@{attacker} швырнул сосиску, но @{target} испарился из чата!",
#     "Сосиска не долетела — @{target} сбежал от булочной битвы!",
# ]
#
# SAUSAGE_BONUS_MESSAGES = [
#     "@{attacker} кинул сосиску в @{target}, но у того уже была сосиска в тесте! Преимущество: +{bonus} баллов, теперь {new_points}!",
#     "Сосиска от @{attacker} попала в @{target}, и тот обрадовался — он сосисочный мастер! +{bonus}, итого {new_points}.",
#     "@{target} поймал сосиску от @{attacker} и вспомнил свои сосисочные корни! Бонус: +{bonus}, стало {new_points}.",
#     "@{attacker}, твоя сосиска сделала @{target} счастливее! Он получает +{bonus} баллов, теперь {new_points}.",
#     "Бум! @{attacker} попал в @{target}, но сосиска оказалась на его стороне! +{bonus}, итого {new_points}.",
# ]
#
# RANDOM_Sausage_MESSAGES = [
#     "@{attacker} швырнул сосиску наугад и целится в @{target}!",
#     "Сосиска от @{attacker} улетела в случайного прохожего — @{target}!",
#     "@{attacker} решил сыграть в сосисочную рулетку — @{target} под прицелом!",
#     "Случайный бросок от @{attacker}, и @{target} стал мишенью!",
#     "@{attacker} кинул сосиску в толпу, а попал в @{target}!",
# ]
#
# MISS_MESSAGES = [
#     "@{attacker} промахнулся! Сосиска улетела в закат.",
#     "Ой! @{attacker} не попал в @{target}, она пролетела мимо!",
#     "@{attacker} метил в @{target}, но сосиска решила уйти в свободный полёт!",
#     "Промах! @{attacker} не угодил в @{target}, сосиска пропала зря.",
#     "Сосиска от @{attacker} не долетела до @{target} — точность подкачала!",
# ]
#
# SELF_HIT_MESSAGES = [
#     "Сосиска чуть не попала в тебя самого, @{username}, но ты увернулся!",
#     "@{username} швырнул сосиску и чуть не стал жертвой сам — ловкость спасла!",
#     "Ой-ой, @{username}! Сосиска сделала круг и чуть не вернулась к тебе!",
#     "@{username} метнул сосиску в воздух, но она решила поиграть с тобой в догонялки!",
#     "Сосиска от @{username} чуть не устроила автогол, но ты вовремя отпрыгнул!",
#     "@{username}, ты чуть не угостил себя сосиской — аккуратнее с рандомом!",
# ]
#
# ZERO_POINTS_MESSAGES = [
#     "@{username} остался без баллов и вылетел из гонки! Все булки растаяли.",
#     "Баллы @{username} обнулились — прощай, сосисочная слава и булки!",
#     "@{username} достиг дна: 0 баллов, 0 булок, 0 шансов!",
#     "Сосисочная карьера @{username} рухнула — 0 баллов, булки конфискованы!",
#     "@{username} теперь официально банкрот булочной войны — ни баллов, ни булок!",
# ]
#
# NO_USERNAME_MESSAGES = [
#     "У @{old_target} нет юзернейма, кидаем в @{new_target}!",
#     "@{old_target} скрыл свой юзернейм, попал под раздачу @{new_target}!",
#     "Без юзернейма у @{old_target}? Лови, @{new_target}!",
#     "@{old_target} оказался безымянным, сосиска улетела к @{new_target}!",
# ]
#
#
# @sausage_game_r.message(Command("sausage", "сосиска"))
# async def sausage_throw_handler(message: Message, bot: Bot):
#     """Обработчик команды /sausage или /сосиска @username: кидаем сосиску в другого участника с юмором."""
#     if message.chat.type == "private":
#         await message.reply(
#             "Эту команду можно использовать только в групповых чатах! 🌭"
#         )
#         return
#
#     chat_id = message.chat.id
#     attacker = message.from_user
#
#     if not message.text.split(maxsplit=1)[1:]:
#         await message.reply(
#             "Укажи, в кого кинуть сосиску! Пример: /sausage @username или /сосиска @username"
#         )
#         return
#
#     target_username = message.text.split(maxsplit=1)[1].strip()
#     if not target_username.startswith("@"):
#         await message.reply(
#             "Юзернейм должен начинаться с @! Пример: /sausage @username или /сосиска @username"
#         )
#         return
#     target_username = target_username[1:]
#
#     # Проверка очков перед броском
#     SAUSAGE_THROW_COST = (
#         await get_game_setting("sausage_throw_cost") or 2
#     )  # Установлено 2
#     attacker_points = await get_user_points(attacker.id, chat_id)
#     if attacker_points < SAUSAGE_THROW_COST:
#         await handle_no_points(
#             bot, chat_id, attacker, attacker_points, SAUSAGE_THROW_COST
#         )
#         return
#
#     target_data = await get_user_by_username(chat_id, target_username)
#     if not target_data or not target_data.username:
#         old_target = target_username
#         target_data = await get_random_user(chat_id)
#         if not target_data or not target_data.username:
#             await message.reply("В чате нет участников с юзернеймами для атаки! 🌭")
#             return
#         if target_data.telegram_id == attacker.id:
#             target_data = await get_random_user(chat_id)
#             if (
#                 not target_data
#                 or not target_data.username
#                 or target_data.telegram_id == attacker.id
#             ):
#                 await message.reply(
#                     "Не удалось найти подходящую жертву с юзернеймом! 🌭"
#                 )
#                 return
#         message_text = random.choice(NO_USERNAME_MESSAGES).format(
#             old_target=old_target, new_target=target_data.username
#         )
#         await message.reply(message_text)
#
#     await process_sausage_throw(bot, chat_id, attacker, target_data.username)
#
#
# @sausage_game_r.message(Command("random_sausage", "случайнаясосиска"))
# async def random_sausage_throw_handler(message: Message, bot: Bot):
#     """Обработчик команды /random_sausage: кидаем сосиску в случайного участника игры."""
#     if message.chat.type == "private":
#         await message.reply(
#             "Эту команду можно использовать только в групповых чатах! 🌭"
#         )
#         return
#
#     chat_id = message.chat.id
#     attacker = message.from_user
#
#     attacker_data = await get_user_by_id(attacker.id, chat_id)
#     if not attacker_data or not attacker_data.in_game:
#         await message.reply("Ты не в игре! Сначала вступи в чат и стань участником.")
#         return
#
#     # Проверка очков перед броском
#     SAUSAGE_THROW_COST = (
#         await get_game_setting("sausage_throw_cost") or 2
#     )  # Установлено 2
#     attacker_points = await get_user_points(attacker.id, chat_id)
#     if attacker_points < SAUSAGE_THROW_COST:
#         await handle_no_points(
#             bot, chat_id, attacker, attacker_points, SAUSAGE_THROW_COST, is_random=True
#         )
#         return
#
#     target_data = await get_random_user(chat_id)
#     if not target_data:
#         await message.reply("В чате нет активных участников для сосисочной атаки!")
#         return
#
#     if not target_data.username or target_data.telegram_id == attacker.id:
#         old_target = target_data.username or "кого-то без юзернейма"
#         target_data = await get_random_user(chat_id)
#         if (
#             not target_data
#             or not target_data.username
#             or target_data.telegram_id == attacker.id
#         ):
#             await message.reply("Не удалось найти подходящую жертву с юзернеймом! 🌭")
#             return
#         message_text = random.choice(NO_USERNAME_MESSAGES).format(
#             old_target=old_target, new_target=target_data.username
#         )
#         await message.reply(message_text)
#
#     await process_sausage_throw(bot, chat_id, attacker, target_data.username)
#
#
# async def handle_no_points(
#     bot: Bot, chat_id: int, attacker, points: int, cost: int, is_random: bool = False
# ):
#     """Обработка ситуации, когда у пользователя недостаточно очков для броска до начала."""
#     global attempts_counter
#
#     # Инициализируем счетчик для чата, если его нет
#     if chat_id not in attempts_counter:
#         attempts_counter[chat_id] = {}
#
#     # Увеличиваем счетчик попыток для пользователя
#     user_attempts = attempts_counter[chat_id].get(attacker.id, 0) + 1
#     attempts_counter[chat_id][attacker.id] = user_attempts
#
#     if user_attempts >= 3:
#         # Третья попытка — выводим доходчивое сообщение и сбрасываем счетчик
#         message_text = NO_POINTS_THIRD_ATTEMPT_MESSAGE.format(
#             username=attacker.username, points=points, cost=cost
#         )
#         await bot.send_message(chat_id, message_text)
#         attempts_counter[chat_id][attacker.id] = 0  # Сбрасываем счетчик
#         logger.info(
#             f"@{attacker.username} получил предупреждение после 3 попыток без очков в чате {chat_id}"
#         )
#     else:
#         # Обычное сообщение о нехватке очков
#         messages = NO_POINTS_RANDOM_MESSAGES if is_random else NO_POINTS_MESSAGES
#         message_text = random.choice(messages).format(
#             username=attacker.username, points=points, cost=cost
#         )
#         await bot.send_message(chat_id, message_text)
#         logger.info(
#             f"@{attacker.username} пытался бросить сосиску без очков ({points}/{cost}), попытка {user_attempts}"
#         )
#
#
# async def process_sausage_throw(bot: Bot, chat_id: int, attacker, target_username: str):
#     """Общая логика броска сосиски для обеих команд."""
#     global attempts_counter
#
#     SAUSAGE_THROW_COST = (
#         await get_game_setting("sausage_throw_cost") or 2
#     )  # Установлено 2
#     SAUSAGE_HIT_DAMAGE = await get_game_setting("sausage_hit_damage") or 3
#     SAUSAGE_PENALTY = await get_game_setting("sausage_penalty") or 3
#     SAUSAGE_BONUS = await get_game_setting("sausage_bonus") or 3
#     MISS_CHANCE = await get_game_setting("miss_chance") or 10
#
#     attacker_data = await get_user_by_id(attacker.id, chat_id)
#     if not attacker_data or not attacker_data.in_game:
#         await bot.send_message(
#             chat_id, "Ты не в игре! Сначала вступи в чат и стань участником."
#         )
#         return
#
#     target_data = await get_user_by_username(chat_id, target_username)
#     if not target_data or not target_data.username:
#         await bot.send_message(
#             chat_id, f"Не удалось найти @{target_username} с юзернеймом!"
#         )
#         return
#
#     try:
#         chat_member = await bot.get_chat_member(chat_id, target_data.telegram_id)
#         if chat_member.status in ["left", "kicked"]:
#             message_text = random.choice(NOT_IN_CHAT_MESSAGES).format(
#                 attacker=attacker.username, target=target_data.username
#             )
#             await bot.send_message(chat_id, message_text)
#             return
#     except Exception as e:
#         await bot.send_message(
#             chat_id, f"Не удалось проверить @{target_username} в чате!"
#         )
#         logger.error(
#             f"Ошибка проверки статуса @{target_username} в чате {chat_id}: {e}"
#         )
#         return
#
#     if not target_data.in_game:
#         await bot.send_message(
#             chat_id, f"@{target_username} не в игре, нельзя кинуть сосиску!"
#         )
#         return
#
#     # Сообщение о броске
#     throw_message = random.choice(THROW_MESSAGES).format(
#         attacker=attacker.username, target=target_data.username
#     )
#     await bot.send_message(chat_id, throw_message)
#     await asyncio.sleep(1)  # Задержка для эффекта
#
#     # Уменьшаем баллы атакующего за бросок
#     attacker_points = await get_user_points(attacker.id, chat_id)
#     new_attacker_points = attacker_points - SAUSAGE_THROW_COST
#     await update_user_points(attacker.id, chat_id, -SAUSAGE_THROW_COST)
#
#     # Сбрасываем счетчик попыток, так как бросок успешен
#     if chat_id in attempts_counter and attacker.id in attempts_counter[chat_id]:
#         attempts_counter[chat_id][attacker.id] = 0
#
#     # Проверяем, не обнулились ли баллы атакующего после броска
#     if new_attacker_points == 0:
#         await reset_user_on_zero_points(attacker.id, chat_id)
#         message_text = random.choice(ZERO_POINTS_MESSAGES).format(
#             username=attacker.username
#         )
#         await bot.send_message(chat_id, message_text)
#         return
#
#     # Проверяем вероятность промаха
#     if random.randint(1, 100) <= MISS_CHANCE:
#         message_text = random.choice(MISS_MESSAGES).format(
#             attacker=attacker.username, target=target_data.username
#         )
#         await bot.send_message(chat_id, message_text)
#         # Если после промаха очков не осталось, уведомляем
#         if new_attacker_points < SAUSAGE_THROW_COST:
#             no_points_message = random.choice(NO_POINTS_AFTER_THROW_MESSAGES).format(
#                 username=attacker.username,
#                 points=new_attacker_points,
#                 cost=SAUSAGE_THROW_COST,
#             )
#             await bot.send_message(chat_id, no_points_message)
#         return
#
#     # Получаем баллы и булочки жертвы
#     target_points = await get_user_points(target_data.telegram_id, chat_id)
#     target_buns = await get_user_buns_stats(target_data.telegram_id, chat_id)
#
#     # Проверяем, есть ли у жертвы булочка с частичным совпадением "сосиска"
#     has_sausage = any("сосиска" in bun["bun"].lower() for bun in target_buns)
#
#     # Обрабатываем попадание
#     if target_points > 0:
#         if has_sausage:
#             new_target_points = target_points + SAUSAGE_BONUS
#             await update_user_points(target_data.telegram_id, chat_id, SAUSAGE_BONUS)
#             message_text = random.choice(SAUSAGE_BONUS_MESSAGES).format(
#                 attacker=attacker.username,
#                 target=target_data.username,
#                 bonus=SAUSAGE_BONUS,
#                 new_points=new_target_points,
#             )
#             await bot.send_message(chat_id, message_text)
#             await bot.send_message(chat_id, HOTDOG_EMOJI)
#         else:
#             new_target_points = max(0, target_points - SAUSAGE_HIT_DAMAGE)
#             await update_user_points(
#                 target_data.telegram_id, chat_id, -SAUSAGE_HIT_DAMAGE
#             )
#             message_text = random.choice(HIT_MESSAGES).format(
#                 attacker=attacker.username,
#                 target=target_data.username,
#                 old_points=target_points,
#                 new_points=new_target_points,
#             )
#             await bot.send_message(chat_id, message_text)
#             await bot.send_message(chat_id, HIT_EMOJI)
#
#             # Проверяем, не обнулились ли баллы жертвы
#             if new_target_points == 0:
#                 await reset_user_on_zero_points(target_data.telegram_id, chat_id)
#                 message_text = random.choice(ZERO_POINTS_MESSAGES).format(
#                     username=target_data.username
#                 )
#                 await bot.send_message(chat_id, message_text)
#         # Если после попадания у атакующего не хватает очков на следующий бросок
#         if new_attacker_points < SAUSAGE_THROW_COST:
#             no_points_message = random.choice(NO_POINTS_AFTER_THROW_MESSAGES).format(
#                 username=attacker.username,
#                 points=new_attacker_points,
#                 cost=SAUSAGE_THROW_COST,
#             )
#             await bot.send_message(chat_id, no_points_message)
#     else:
#         new_attacker_points = max(0, new_attacker_points - SAUSAGE_PENALTY)
#         await update_user_points(attacker.id, chat_id, -SAUSAGE_PENALTY)
#         message_text = random.choice(PENALTY_MESSAGES).format(
#             attacker=attacker.username,
#             target=target_data.username,
#             penalty=SAUSAGE_PENALTY,
#             new_points=new_attacker_points,
#         )
#         await bot.send_message(chat_id, message_text)
#         await bot.send_message(chat_id, PENALTY_EMOJI)
#
#         # Проверяем, не обнулились ли баллы атакующего после штрафа
#         if new_attacker_points == 0:
#             await reset_user_on_zero_points(attacker.id, chat_id)
#             message_text = random.choice(ZERO_POINTS_MESSAGES).format(
#                 username=attacker.username
#             )
#             await bot.send_message(chat_id, message_text)
from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.filters import Command
from database.queries import (
    get_user_by_id,
    get_user_points,
    update_user_points,
    get_user_by_username,
    get_user_buns_stats,
    get_random_user,
    get_game_setting,
    reset_user_on_zero_points,
)
from logger import logger
import random
import asyncio

sausage_game_r = Router()

# Эмодзи для разных случаев
HOTDOG_EMOJI = "🌭"  # Бонус за сосиску
HIT_EMOJI = "💥"  # Успешное попадание
PENALTY_EMOJI = "😢"  # Штраф за атаку безоружного

# Счетчик попыток броска без очков: {chat_id: {user_id: int}}
attempts_counter = {}

# Юмористические фразы
NO_POINTS_MESSAGES = [
    "У тебя не хватает сосисочных баллов ({points}/{cost})! Иди испеки булочку!",
    "Сосиски не бесплатные, @{username}! У тебя только {points}/{cost} баллов.",
    "Твои карманы пусты, @{username}! {points}/{cost} — это не сосисочный уровень.",
    "Без баллов сосиску не кинешь, @{username}! ({points}/{cost})",
]

NO_POINTS_RANDOM_MESSAGES = [
    "@{username} попытался швырнуть случайную сосиску, но баллов нет ({points}/{cost})!",
    "Сосиска осталась в кармане у @{username} — не хватает баллов ({points}/{cost})!",
    "@{username} хотел кинуть сосиску наугад, но пустые карманы сказали 'нет' ({points}/{cost})!",
    "Рандомная сосиска? Не сегодня, @{username}! Баллов мало ({points}/{cost}).",
]

NO_POINTS_THIRD_ATTEMPT_MESSAGE = (
    "Эй, @{username}, хватит пытаться! У тебя {points} баллов, а нужно {cost}, чтобы кинуть сосиску. "
    "Пока не наберешь баллы, ничего не выйдет! Иди за булочками! 🌭"
)

NO_POINTS_AFTER_THROW_MESSAGES = [
    "Баллы закончились, @{username}! У тебя теперь {points}/{cost} — пора за булочками!",
    "Сосиска улетела, а с ней и твои баллы, @{username}! Осталось {points}/{cost}.",
    "@{username}, ты в нуле ({points}/{cost})! Булки зовут!",
    "Бросок был, но баллы растаяли, @{username}! ({points}/{cost})",
]

THROW_MESSAGES = [
    "🌭💨 @{attacker} швыряет сосиску в @{target}! Летит...",
    "🌭💨 @{attacker} метнул сосиску в @{target}! Смотрим...",
    "🌭💨 Сосиска от @{attacker} устремилась к @{target}! Что будет?",
    "🌭💨 @{attacker} зарядил сосиску в сторону @{target}! Ждем...",
    "🌭💨 @{attacker} бросил сосиску в @{target}! В полете...",
]

HIT_MESSAGES = [
    "@{attacker} метко попал сосиской в @{target}! У @{target} было {old_points}, стало {new_points}.",
    "@{attacker} зарядил сосиской прямо в @{target}! Теперь у жертвы {new_points} вместо {old_points}.",
    "Бам! @{attacker} угодил сосиской в @{target}! Баллы упали с {old_points} до {new_points}.",
    "@{attacker} устроил сосисочный сюрприз для @{target}! Осталось {new_points} баллов вместо {old_points}.",
    "Сосиска от @{attacker} прилетела в @{target}! Баллы тают: {old_points} → {new_points}.",
]

PENALTY_MESSAGES = [
    "@{attacker} кинул сосиску в @{target}, но тот был безоружен! Расплата: минус {penalty} баллов, осталось {new_points}.",
    "@{attacker} зря швырнул сосиску в пустые карманы @{target}! Штраф {penalty}, теперь у тебя {new_points} баллов.",
    "Ой-ой, @{attacker}! @{target} оказался без баллов, и сосиска вернулась бумерангом: -{penalty}, осталось {new_points}.",
    "@{attacker} попал сосиской в @{target}, но без толку! Штраф за подлость: -{penalty}, итого {new_points}.",
    "Сосиска от @{attacker} угодила в @{target}, но без толку! @{attacker} теряет {penalty}, теперь {new_points} баллов.",
]

NOT_IN_CHAT_MESSAGES = [
    "Сосиска улетела в пустоту, @{target} давно сбежал!",
    "@{target} где-то спрятался, и твоя сосиска пропала зря, @{attacker}!",
    "Куда кинул, @{attacker}? @{target} уже не в чате, сосиска потерялась!",
    "@{attacker} швырнул сосиску, но @{target} испарился из чата!",
    "Сосиска не долетела — @{target} сбежал от булочной битвы!",
]

SAUSAGE_BONUS_MESSAGES = [
    "@{attacker} кинул сосиску в @{target}, но у того уже была сосиска в тесте! Преимущество: +{bonus} баллов, теперь {new_points}!",
    "Сосиска от @{attacker} попала в @{target}, и тот обрадовался — он сосисочный мастер! +{bonus}, итого {new_points}.",
    "@{target} поймал сосиску от @{attacker} и вспомнил свои сосисочные корни! Бонус: +{bonus}, стало {new_points}.",
    "@{attacker}, твоя сосиска сделала @{target} счастливее! Он получает +{bonus} баллов, теперь {new_points}.",
    "Бум! @{attacker} попал в @{target}, но сосиска оказалась на его стороне! +{bonus}, итого {new_points}.",
]

RANDOM_Sausage_MESSAGES = [
    "@{attacker} швырнул сосиску наугад и целится в @{target}!",
    "Сосиска от @{attacker} улетела в случайного прохожего — @{target}!",
    "@{attacker} решил сыграть в сосисочную рулетку — @{target} под прицелом!",
    "Случайный бросок от @{attacker}, и @{target} стал мишенью!",
    "@{attacker} кинул сосиску в толпу, а попал в @{target}!",
]

MISS_MESSAGES = [
    "@{attacker} промахнулся! Сосиска улетела в закат.",
    "Ой! @{attacker} не попал в @{target}, она пролетела мимо!",
    "@{attacker} метил в @{target}, но сосиска решила уйти в свободный полёт!",
    "Промах! @{attacker} не угодил в @{target}, сосиска пропала зря.",
    "Сосиска от @{attacker} не долетела до @{target} — точность подкачала!",
]

SELF_HIT_MESSAGES = [
    "Сосиска чуть не попала в тебя самого, @{username}, но ты увернулся!",
    "@{username} швырнул сосиску и чуть не стал жертвой сам — ловкость спасла!",
    "Ой-ой, @{username}! Сосиска сделала круг и чуть не вернулась к тебе!",
    "@{username} метнул сосиску в воздух, но она решила поиграть с тобой в догонялки!",
    "Сосиска от @{username} чуть не устроила автогол, но ты вовремя отпрыгнул!",
    "@{username}, ты чуть не угостил себя сосиской — аккуратнее с рандомом!",
]

ZERO_POINTS_MESSAGES = [
    "@{username} остался без баллов и вылетел из гонки! Все булки растаяли.",
    "Баллы @{username} обнулились — прощай, сосисочная слава и булки!",
    "@{username} достиг дна: 0 баллов, 0 булок, 0 шансов!",
    "Сосисочная карьера @{username} рухнула — 0 баллов, булки конфискованы!",
    "@{username} теперь официально банкрот булочной войны — ни баллов, ни булок!",
]

NO_USERNAME_MESSAGES = [
    "У @{old_target} нет юзернейма, кидаем в @{new_target}!",
    "@{old_target} скрыл свой юзернейм, попал под раздачу @{new_target}!",
    "Без юзернейма у @{old_target}? Лови, @{new_target}!",
    "@{old_target} оказался безымянным, сосиска улетела к @{new_target}!",
]


@sausage_game_r.message(Command("sausage", "сосиска"))
async def sausage_throw_handler(message: Message, bot: Bot):
    """Обработчик команды /sausage или /сосиска @username: кидаем сосиску в другого участника с юмором."""
    if message.chat.type == "private":
        await message.reply(
            "Эту команду можно использовать только в групповых чатах! 🌭"
        )
        return

    chat_id = message.chat.id
    attacker = message.from_user

    if not message.text.split(maxsplit=1)[1:]:
        await message.reply(
            "Укажи, в кого кинуть сосиску! Пример: /sausage @username или /сосиска @username"
        )
        return

    target_username = message.text.split(maxsplit=1)[1].strip()
    if not target_username.startswith("@"):
        await message.reply(
            "Юзернейм должен начинаться с @! Пример: /sausage @username или /сосиска @username"
        )
        return
    target_username = target_username[1:]

    # Проверка очков перед броском
    SAUSAGE_THROW_COST = (
        await get_game_setting("sausage_throw_cost") or 2
    )  # Установлено 2
    attacker_points = await get_user_points(attacker.id, chat_id)
    if attacker_points < SAUSAGE_THROW_COST:
        await handle_no_points(
            bot, chat_id, attacker, attacker_points, SAUSAGE_THROW_COST
        )
        return

    target_data = await get_user_by_username(chat_id, target_username)
    if not target_data or not target_data.username:
        old_target = target_username
        target_data = await get_random_user(chat_id)
        if not target_data or not target_data.username:
            await message.reply("В чате нет участников с юзернеймами для атаки! 🌭")
            return
        if target_data.telegram_id == attacker.id:
            target_data = await get_random_user(chat_id)
            if (
                not target_data
                or not target_data.username
                or target_data.telegram_id == attacker.id
            ):
                await message.reply(
                    "Не удалось найти подходящую жертву с юзернеймом! 🌭"
                )
                return
        message_text = random.choice(NO_USERNAME_MESSAGES).format(
            old_target=old_target, new_target=target_data.username
        )
        await message.reply(message_text)

    await process_sausage_throw(bot, chat_id, attacker, target_data.username)


@sausage_game_r.message(Command("random_sausage", "случайнаясосиска"))
async def random_sausage_throw_handler(message: Message, bot: Bot):
    """Обработчик команды /random_sausage: кидаем сосиску в случайного участника игры."""
    if message.chat.type == "private":
        await message.reply(
            "Эту команду можно использовать только в групповых чатах! 🌭"
        )
        return

    chat_id = message.chat.id
    attacker = message.from_user

    attacker_data = await get_user_by_id(attacker.id, chat_id)
    if not attacker_data or not attacker_data.in_game:
        await message.reply("Ты не в игре! Сначала вступи в чат и стань участником.")
        return

    # Проверка очков перед броском
    SAUSAGE_THROW_COST = (
        await get_game_setting("sausage_throw_cost") or 2
    )  # Установлено 2
    attacker_points = await get_user_points(attacker.id, chat_id)
    if attacker_points < SAUSAGE_THROW_COST:
        await handle_no_points(
            bot, chat_id, attacker, attacker_points, SAUSAGE_THROW_COST, is_random=True
        )
        return

    target_data = await get_random_user(chat_id)
    if not target_data:
        await message.reply("В чате нет активных участников для сосисочной атаки!")
        return

    if not target_data.username or target_data.telegram_id == attacker.id:
        old_target = target_data.username or "кого-то без юзернейма"
        target_data = await get_random_user(chat_id)
        if (
            not target_data
            or not target_data.username
            or target_data.telegram_id == attacker.id
        ):
            await message.reply("Не удалось найти подходящую жертву с юзернеймом! 🌭")
            return
        message_text = random.choice(NO_USERNAME_MESSAGES).format(
            old_target=old_target, new_target=target_data.username
        )
        await message.reply(message_text)

    await process_sausage_throw(bot, chat_id, attacker, target_data.username)


async def handle_no_points(
    bot: Bot, chat_id: int, attacker, points: int, cost: int, is_random: bool = False
):
    """Обработка ситуации, когда у пользователя недостаточно очков для броска до начала."""
    global attempts_counter

    # Инициализируем счетчик для чата, если его нет
    if chat_id not in attempts_counter:
        attempts_counter[chat_id] = {}

    # Увеличиваем счетчик попыток для пользователя
    user_attempts = attempts_counter[chat_id].get(attacker.id, 0) + 1
    attempts_counter[chat_id][attacker.id] = user_attempts

    if user_attempts >= 3:
        # Третья попытка — выводим доходчивое сообщение и сбрасываем счетчик
        message_text = NO_POINTS_THIRD_ATTEMPT_MESSAGE.format(
            username=attacker.username, points=points, cost=cost
        )
        await bot.send_message(chat_id, message_text)
        attempts_counter[chat_id][attacker.id] = 0  # Сбрасываем счетчик
        logger.info(
            f"@{attacker.username} получил предупреждение после 3 попыток без очков в чате {chat_id}"
        )
    else:
        # Обычное сообщение о нехватке очков
        messages = NO_POINTS_RANDOM_MESSAGES if is_random else NO_POINTS_MESSAGES
        message_text = random.choice(messages).format(
            username=attacker.username, points=points, cost=cost
        )
        await bot.send_message(chat_id, message_text)
        logger.info(
            f"@{attacker.username} пытался бросить сосиску без очков ({points}/{cost}), попытка {user_attempts}"
        )


async def process_sausage_throw(bot: Bot, chat_id: int, attacker, target_username: str):
    """Общая логика броска сосиски для обеих команд."""
    global attempts_counter

    SAUSAGE_THROW_COST = (
        await get_game_setting("sausage_throw_cost") or 2
    )  # Установлено 2
    SAUSAGE_HIT_DAMAGE = await get_game_setting("sausage_hit_damage") or 3
    SAUSAGE_PENALTY = await get_game_setting("sausage_penalty") or 3
    SAUSAGE_BONUS = await get_game_setting("sausage_bonus") or 3
    MISS_CHANCE = await get_game_setting("miss_chance") or 10

    attacker_data = await get_user_by_id(attacker.id, chat_id)
    if not attacker_data or not attacker_data.in_game:
        await bot.send_message(
            chat_id, "Ты не в игре! Сначала вступи в чат и стань участником."
        )
        return

    target_data = await get_user_by_username(chat_id, target_username)
    if not target_data or not target_data.username:
        await bot.send_message(
            chat_id, f"Не удалось найти @{target_username} с юзернеймом!"
        )
        return

    try:
        chat_member = await bot.get_chat_member(chat_id, target_data.telegram_id)
        if chat_member.status in ["left", "kicked"]:
            message_text = random.choice(NOT_IN_CHAT_MESSAGES).format(
                attacker=attacker.username, target=target_data.username
            )
            await bot.send_message(chat_id, message_text)
            return
    except Exception as e:
        await bot.send_message(
            chat_id, f"Не удалось проверить @{target_username} в чате!"
        )
        logger.error(
            f"Ошибка проверки статуса @{target_username} в чате {chat_id}: {e}"
        )
        return

    if not target_data.in_game:
        await bot.send_message(
            chat_id, f"@{target_username} не в игре, нельзя кинуть сосиску!"
        )
        return

    # Сообщение о броске
    throw_message = random.choice(THROW_MESSAGES).format(
        attacker=attacker.username, target=target_data.username
    )
    await bot.send_message(chat_id, throw_message)
    await asyncio.sleep(1)  # Задержка для эффекта

    # Уменьшаем баллы атакующего за бросок
    attacker_points = await get_user_points(attacker.id, chat_id)
    new_attacker_points = attacker_points - SAUSAGE_THROW_COST
    await update_user_points(attacker.id, chat_id, -SAUSAGE_THROW_COST)

    # Сбрасываем счетчик попыток, так как бросок успешен
    if chat_id in attempts_counter and attacker.id in attempts_counter[chat_id]:
        attempts_counter[chat_id][attacker.id] = 0

    # Проверяем вероятность промаха
    if random.randint(1, 100) <= MISS_CHANCE:
        message_text = random.choice(MISS_MESSAGES).format(
            attacker=attacker.username, target=target_data.username
        )
        await bot.send_message(chat_id, message_text)
    else:
        # Получаем баллы и булочки жертвы
        target_points = await get_user_points(target_data.telegram_id, chat_id)
        target_buns = await get_user_buns_stats(target_data.telegram_id, chat_id)

        # Проверяем, есть ли у жертвы булочка с частичным совпадением "сосиска"
        has_sausage = any("сосиска" in bun["bun"].lower() for bun in target_buns)

        # Обрабатываем попадание
        if target_points > 0:
            if has_sausage:
                new_target_points = target_points + SAUSAGE_BONUS
                await update_user_points(
                    target_data.telegram_id, chat_id, SAUSAGE_BONUS
                )
                message_text = random.choice(SAUSAGE_BONUS_MESSAGES).format(
                    attacker=attacker.username,
                    target=target_data.username,
                    bonus=SAUSAGE_BONUS,
                    new_points=new_target_points,
                )
                await bot.send_message(chat_id, message_text)
                await bot.send_message(chat_id, HOTDOG_EMOJI)
            else:
                new_target_points = max(0, target_points - SAUSAGE_HIT_DAMAGE)
                await update_user_points(
                    target_data.telegram_id, chat_id, -SAUSAGE_HIT_DAMAGE
                )
                message_text = random.choice(HIT_MESSAGES).format(
                    attacker=attacker.username,
                    target=target_data.username,
                    old_points=target_points,
                    new_points=new_target_points,
                )
                await bot.send_message(chat_id, message_text)
                await bot.send_message(chat_id, HIT_EMOJI)

                # Проверяем, не обнулились ли баллы жертвы
                if new_target_points == 0:
                    await reset_user_on_zero_points(target_data.telegram_id, chat_id)
                    message_text = random.choice(ZERO_POINTS_MESSAGES).format(
                        username=target_data.username
                    )
                    await bot.send_message(chat_id, message_text)
        else:
            new_attacker_points = max(0, new_attacker_points - SAUSAGE_PENALTY)
            await update_user_points(attacker.id, chat_id, -SAUSAGE_PENALTY)
            message_text = random.choice(PENALTY_MESSAGES).format(
                attacker=attacker.username,
                target=target_data.username,
                penalty=SAUSAGE_PENALTY,
                new_points=new_attacker_points,
            )
            await bot.send_message(chat_id, message_text)
            await bot.send_message(chat_id, PENALTY_EMOJI)

    # Проверяем баллы атакующего после всех действий
    if new_attacker_points == 0:
        await reset_user_on_zero_points(attacker.id, chat_id)
        message_text = random.choice(ZERO_POINTS_MESSAGES).format(
            username=attacker.username
        )
        await bot.send_message(chat_id, message_text)
    elif new_attacker_points < SAUSAGE_THROW_COST:
        no_points_message = random.choice(NO_POINTS_AFTER_THROW_MESSAGES).format(
            username=attacker.username,
            points=new_attacker_points,
            cost=SAUSAGE_THROW_COST,
        )
        await bot.send_message(chat_id, no_points_message)
