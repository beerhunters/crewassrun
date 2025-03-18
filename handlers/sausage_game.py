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
    get_game_setting,  # Добавляем функцию для получения настроек
)
from logger import logger
import random

sausage_game_r = Router()

# Эмодзи для разных случаев
HOTDOG_EMOJI = "🌭"  # Бонус за сосиску
HIT_EMOJI = "💥"  # Успешное попадание
PENALTY_EMOJI = "😢"  # Штраф за атаку безоружного

# Юмористические фразы
NO_POINTS_MESSAGES = [
    "У тебя не хватает сосисочных баллов ({points}/{cost})! Иди испеки булочку!",
    "Сосиски не бесплатные, @{username}! У тебя только {points}/{cost} баллов.",
    "Твои карманы пусты, @{username}! {points}/{cost} — это не сосисочный уровень.",
    "Без баллов сосиску не кинешь, @{username}! ({points}/{cost})",
]

HIT_MESSAGES = [
    "@{attacker} метко швырнул сосиску в @{target}! Попадание! У @{target} было {old_points}, стало {new_points}.",
    "@{attacker} зарядил сосиской прямо в @{target}! Теперь у жертвы {new_points} вместо {old_points}.",
    "Бам! @{attacker} попал сосиской в @{target}! Баллы упали с {old_points} до {new_points}.",
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
    "@{attacker} швырнул сосиску наугад и попал в @{target}!",
    "Сосиска от @{attacker} улетела в случайного прохожего — @{target}!",
    "@{attacker} решил сыграть в сосисочную рулетку — @{target} под раздачей!",
    "Случайный бросок от @{attacker}, и @{target} стал мишенью!",
    "@{attacker} кинул сосиску в толпу, а попал в @{target}!",
]

MISS_MESSAGES = [
    "@{attacker} швырнул сосиску в @{target}, но промахнулся! Сосиска улетела в закат.",
    "Ой! @{attacker} кинул сосиску в @{target}, но она пролетела мимо!",
    "@{attacker} метил в @{target}, но сосиска решила уйти в свободный полёт!",
    "Промах! @{attacker} не попал в @{target}, сосиска пропала зря.",
    "Сосиска от @{attacker} не долетела до @{target} — точность подкачала!",
]


@sausage_game_r.message(Command("sausage"))
async def sausage_throw_handler(message: Message, bot: Bot):
    """Обработчик команды /sausage @username: кидаем сосиску в другого участника с юмором."""
    chat_id = message.chat.id
    attacker = message.from_user

    # Проверяем, указан ли юзернейм жертвы
    if not message.text.split(maxsplit=1)[1:]:
        await message.reply("Укажи, в кого кинуть сосиску! Пример: /sausage @username")
        return

    # Получаем юзернейм жертвы
    target_username = message.text.split(maxsplit=1)[1].strip()
    if not target_username.startswith("@"):
        await message.reply(
            "Юзернейм должен начинаться с @! Пример: /sausage @username"
        )
        return
    target_username = target_username[1:]  # Убираем @

    await process_sausage_throw(bot, chat_id, attacker, target_username)


@sausage_game_r.message(Command("random_sausage"))
async def random_sausage_throw_handler(message: Message, bot: Bot):
    """Обработчик команды /random_sausage: кидаем сосиску в случайного участника игры."""
    chat_id = message.chat.id
    attacker = message.from_user

    # Проверяем атакующего
    attacker_data = await get_user_by_id(attacker.id, chat_id)
    if not attacker_data or not attacker_data.in_game:
        await message.reply("Ты не в игре! Сначала вступи в чат и стань участником.")
        logger.debug(f"Пользователь {attacker.id} не в игре в чате {chat_id}")
        return

    # Получаем случайного участника
    target_data = await get_random_user(chat_id)
    if not target_data:
        await message.reply("В чате нет активных участников для сосисочной атаки!")
        logger.debug(f"Нет активных участников в чате {chat_id}")
        return

    # Исключаем попадание в самого себя
    if target_data.telegram_id == attacker.id:
        await message.reply("Сосиска чуть не попала в тебя самого, но ты увернулся!")
        logger.info(
            f"{attacker.username} (ID: {attacker.id}) чуть не попал в себя в чате {chat_id}"
        )
        return

    target_username = target_data.username
    await message.reply(
        random.choice(RANDOM_Sausage_MESSAGES).format(
            attacker=attacker.username, target=target_username
        )
    )
    await process_sausage_throw(bot, chat_id, attacker, target_username)


async def process_sausage_throw(bot: Bot, chat_id: int, attacker, target_username: str):
    """Общая логика броска сосиски для обеих команд."""
    # Получаем настройки из базы данных
    SAUSAGE_THROW_COST = await get_game_setting("sausage_throw_cost") or 5
    SAUSAGE_HIT_DAMAGE = await get_game_setting("sausage_hit_damage") or 3
    SAUSAGE_PENALTY = await get_game_setting("sausage_penalty") or 3
    SAUSAGE_BONUS = await get_game_setting("sausage_bonus") or 3
    MISS_CHANCE = await get_game_setting("miss_chance") or 10  # По умолчанию 10%

    # Проверяем атакующего
    attacker_data = await get_user_by_id(attacker.id, chat_id)
    if not attacker_data or not attacker_data.in_game:
        await bot.send_message(
            chat_id, "Ты не в игре! Сначала вступи в чат и стань участником."
        )
        logger.debug(f"Пользователь {attacker.id} не в игре в чате {chat_id}")
        return

    # Получаем текущие баллы атакующего
    attacker_points = await get_user_points(attacker.id, chat_id)
    if attacker_points < SAUSAGE_THROW_COST:
        message_text = random.choice(NO_POINTS_MESSAGES).format(
            username=attacker.username, points=attacker_points, cost=SAUSAGE_THROW_COST
        )
        await bot.send_message(chat_id, message_text)
        logger.info(
            f"У {attacker.username} (ID: {attacker.id}) недостаточно баллов: {attacker_points}"
        )
        return

    # Ищем жертву по юзернейму в базе данных
    target_data = await get_user_by_username(chat_id, target_username)
    if not target_data:
        await bot.send_message(
            chat_id, f"Пользователь @{target_username} не найден в игре в этом чате!"
        )
        logger.debug(f"Жертва @{target_username} не найдена в базе для чата {chat_id}")
        return

    # Проверяем, активен ли пользователь в чате
    try:
        chat_member = await bot.get_chat_member(chat_id, target_data.telegram_id)
        if chat_member.status in ["left", "kicked"]:
            message_text = random.choice(NOT_IN_CHAT_MESSAGES).format(
                attacker=attacker.username, target=target_username
            )
            await bot.send_message(chat_id, message_text)
            logger.debug(
                f"Жертва @{target_username} (ID: {target_data.telegram_id}) не активна в чате {chat_id}"
            )
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
        logger.debug(f"Жертва {target_data.telegram_id} не в игре в чате {chat_id}")
        return

    # Уменьшаем баллы атакующего за бросок
    new_attacker_points = attacker_points - SAUSAGE_THROW_COST
    await update_user_points(
        attacker.id, chat_id, -SAUSAGE_THROW_COST
    )  # Используем разницу
    logger.info(
        f"{attacker.username} (ID: {attacker.id}) бросил сосиску, баллы: {attacker_points} -> {new_attacker_points}"
    )

    # Проверяем вероятность промаха (в процентах от 1 до 100)
    if random.randint(1, 100) <= MISS_CHANCE:  # MISS_CHANCE% шанс промаха
        message_text = random.choice(MISS_MESSAGES).format(
            attacker=attacker.username, target=target_username
        )
        await bot.send_message(chat_id, message_text)
        logger.info(
            f"{attacker.username} (ID: {attacker.id}) промахнулся по @{target_username} с шансом {MISS_CHANCE}%"
        )
        return  # Завершаем выполнение, если промах

    # Получаем баллы и булочки жертвы
    target_points = await get_user_points(target_data.telegram_id, chat_id)
    target_buns = await get_user_buns_stats(target_data.telegram_id, chat_id)

    # Проверяем, есть ли у жертвы булочка с частичным совпадением "сосиска"
    has_sausage = any("сосиска" in bun["bun"].lower() for bun in target_buns)

    # Обрабатываем попадание
    if target_points > 0:
        if has_sausage:
            # Жертва получает бонус за наличие сосиски
            new_target_points = target_points + SAUSAGE_BONUS
            await update_user_points(
                target_data.telegram_id,
                chat_id,
                SAUSAGE_BONUS,  # Передаём только изменение
            )
            message_text = random.choice(SAUSAGE_BONUS_MESSAGES).format(
                attacker=attacker.username,
                target=target_username,
                bonus=SAUSAGE_BONUS,
                new_points=new_target_points,
            )
            await bot.send_message(chat_id, message_text)
            await bot.send_message(chat_id, HOTDOG_EMOJI)
            logger.info(
                f"Бонус! У {target_username} (ID: {target_data.telegram_id}) была сосиска, баллы: {target_points} -> {new_target_points}"
            )
        else:
            # У жертвы есть баллы, но нет сосиски — отнимаем баллы
            new_target_points = max(0, target_points - SAUSAGE_HIT_DAMAGE)
            await update_user_points(
                target_data.telegram_id,
                chat_id,
                -SAUSAGE_HIT_DAMAGE,  # Передаём только изменение
            )
            message_text = random.choice(HIT_MESSAGES).format(
                attacker=attacker.username,
                target=target_username,
                old_points=target_points,
                new_points=new_target_points,
            )
            await bot.send_message(chat_id, message_text)
            await bot.send_message(chat_id, HIT_EMOJI)
            logger.info(
                f"Попадание! У {target_username} (ID: {target_data.telegram_id}) баллы: {target_points} -> {new_target_points}"
            )
    else:
        # У жертвы нет баллов, штрафуем атакующего
        new_attacker_points = max(0, new_attacker_points - SAUSAGE_PENALTY)
        await update_user_points(
            attacker.id, chat_id, -SAUSAGE_PENALTY
        )  # Передаём только изменение
        message_text = random.choice(PENALTY_MESSAGES).format(
            attacker=attacker.username,
            target=target_username,
            penalty=SAUSAGE_PENALTY,
            new_points=new_attacker_points,
        )
        await bot.send_message(chat_id, message_text)
        await bot.send_message(chat_id, PENALTY_EMOJI)
        logger.info(
            f"Штраф! У {attacker.username} (ID: {attacker.id}) баллы: {new_attacker_points + SAUSAGE_PENALTY} -> {new_attacker_points}"
        )
