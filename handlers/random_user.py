# handlers/random_user.py
import asyncio
import random
from aiogram import Bot
from database.queries import get_random_user, add_or_update_user_bun, get_all_buns
from logger import logger


MESSAGES = [
    "@{user}, сегодня ты та самая булочка, которую все хотят попробовать! {bun} дня! 🥐✨",
    "@{user}, ты свеж, как утренний {bun}, а твоя харизма слаще самой вкусной глазури! 🍯",
    "@{user}, сегодня мир немного вкуснее, потому что ты — {bun}! 😋",
    "@{user}, тебя хочется унести домой и наслаждаться целый день, ведь ты — {bun}! 🍰",
    "@{user}, хрустишь, сияешь и радуешь всех вокруг, как идеальный {bun}! 🥐💛",
    "@{user}, если бы день был десертом, то ты был бы его самой сладкой частью — {bun}! 🍫",
    "@{user}, ты не просто {bun}, ты – произведение кондитерского искусства! 🎨🍩",
    "@{user}, обнять тебя – всё равно что съесть теплый {bun} с чашечкой кофе! ☕💕",
    "@{user}, ты – как идеальный {bun}: мягкий внутри, но с хрустящей корочкой! 🔥",
    "@{user}, быть {bun} – значит приносить радость, а ты делаешь это каждый день! 🎉",
]

SHURSHU_MESSAGES = [
    "Шуршу-муршу... На чьей стороне удача будет сегодня? 🤔✨",
    "Внимание! Судьба уже подготавливает тебя к великому событию! Кто будет булочкой дня? 🧐",
    "Мурчу и шуршу... Время узнать, кто сегодня зажжет! 🔥💥",
    "Секунду... подождите, магия только начинается! Кто же станет булочкой дня? 🧙‍♂️✨",
    "Готовы? Шуршу... Кто сегодня попадает в сладкую ловушку? 🍩🎯",
    "Тайна раскрыта! Но кто же станет булочкой дня? 😏",
    "Мур-мур... Судьба на твоей стороне? 🐾🍞",
    "Итак, шуршу! Кто сегодня окажется в центре сладкой славы? 🍰",
    "Все в ожидании... Кто будет той самой булочкой дня? 🍩💫",
    "Мурчу... Время загадок и сладких сюрпризов! Ты готов к чуду? ✨🍪",
]


async def send_random_message(bot: Bot, chat_id: int):
    """Отправка интерактивного сообщения с выбором случайной булочки."""
    user = await get_random_user(chat_id=chat_id)
    if not user:
        await bot.send_message(chat_id, "В этом чате нет активных игроков! 😔")
        logger.warning(f"Нет активных пользователей в чате {chat_id}")
        return

    display_name = f"@{user.username}" if user.username else user.full_name

    buns_points = await get_all_buns()
    if not buns_points:
        await bot.send_message(chat_id, "Булочки ещё не добавлены в базу! 😱")
        logger.error(f"Таблица buns пуста для чата {chat_id}")
        return

    pre_message = random.choice(SHURSHU_MESSAGES)
    await bot.send_message(
        chat_id, pre_message.format(user=display_name), parse_mode="HTML"
    )
    await asyncio.sleep(1)

    bun_names = list(buns_points.keys())
    text = "Крутим барабан булочек... 🎡"
    msg = await bot.send_message(chat_id, text, parse_mode="HTML")

    animation_buns = random.sample(bun_names, min(5, len(bun_names)))
    for random_bun in animation_buns:
        await msg.edit_text(f"Крутим барабан булочек... 🎡\nТекущая: {random_bun}")
        await asyncio.sleep(0.8)

    effects = ["🥁 Шур-шур...", "🥁 Бум-бум...", "🥁 Тадам!"]
    for effect in effects:
        await msg.edit_text(effect)
        await asyncio.sleep(1)

    bun, points_per_bun = random.choice(list(buns_points.items()))
    final_message = random.choice(MESSAGES).format(user=display_name, bun=bun)
    await msg.edit_text(
        f"{final_message}\n\nОчков за булочку: <b>{points_per_bun}</b> 🍰",
        parse_mode="HTML",
    )

    try:
        await add_or_update_user_bun(user_id=user.id, bun=bun, chat_id=chat_id)
        logger.info(f"Булочка {bun} добавлена для {display_name} в чате {chat_id}")
    except Exception as e:
        logger.error(
            f"Ошибка при сохранении булочки для {user.id} в чате {chat_id}: {e}"
        )
        await bot.send_message(
            chat_id, "Ой! Не удалось сохранить булочку, попробуй позже! 😓"
        )
