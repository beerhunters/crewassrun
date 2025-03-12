# handlers/random_user.py
import asyncio
import random
from aiogram import Bot
from buns_data import SHURSHU_MESSAGES, MESSAGES  # Убираем BUNS_POINTS
from database.queries import get_random_user, add_or_update_user_bun, get_all_buns
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

    # Получаем булочки из базы
    buns_points = await get_all_buns()
    if not buns_points:
        await bot.send_message(chat_id, "Булочки ещё не добавлены в базу! 😱")
        logger.error(f"Таблица buns пуста для чата {chat_id}")
        return

    # 1. Вступительное сообщение
    pre_message = random.choice(SHURSHU_MESSAGES)
    await bot.send_message(
        chat_id, pre_message.format(user=display_name), parse_mode="HTML"
    )
    await asyncio.sleep(1)

    # 2. Анимация "рулетки" булочек
    bun_names = list(buns_points.keys())
    text = "Крутим барабан булочек... 🎡"
    msg = await bot.send_message(chat_id, text, parse_mode="HTML")

    animation_buns = random.sample(bun_names, min(5, len(bun_names)))
    for random_bun in animation_buns:
        await msg.edit_text(f"Крутим барабан булочек... 🎡\nТекущая: {random_bun}")
        await asyncio.sleep(0.8)

    # 3. Финальный "барабанный бой"
    effects = ["🥁 Шур-шур...", "🥁 Бум-бум...", "🥁 Тадам!"]
    for effect in effects:
        await msg.edit_text(effect)
        await asyncio.sleep(1)

    # 4. Раскрытие булочки
    bun, points_per_bun = random.choice(list(buns_points.items()))
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
