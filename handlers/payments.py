from aiogram import Bot, Router
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    CallbackQuery,
)
from aiogram.filters import Command
from database.queries import (
    get_user_by_id,
    update_user_points,
    add_or_update_user_bun,
    get_user_buns_stats,
)
from logger import logger

# from config import YOOMONEY_PROVIDER_TOKEN

# config.py
ADMIN = 123456789  # Ваш Telegram ID
YOOMONEY_PROVIDER_TOKEN = "381764678:TEST:YOUR_SECRET_KEY"  # Замените на реальный токен от YooMoney после тестирования

payments_r = Router()

# Сообщения
PAYMENT_SUCCESS_MESSAGE = "Оплата прошла успешно! Начислено {points} баллов!"
NEWBIE_MESSAGE = "@{target} получил стартовый Круассан с {points} очками!"
INVALID_BUY_POINTS_MESSAGE = (
    "Укажи количество баллов для покупки! Пример: /buy_points 100"
)

# Цены на баллы (в копейках, 1 руб = 100 копеек)
POINTS_PRICES = {
    50: 25000,  # 50 баллов = 250 рублей
    100: 45000,  # 100 баллов = 450 рублей
    200: 85000,  # 200 баллов = 850 рублей
}


async def apply_points_to_user(
    telegram_id: int, chat_id: int, points: int
) -> tuple[int, bool]:
    """Применяет очки к пользователю, возвращает новые очки и флаг нового Круассана."""
    user = await get_user_by_id(telegram_id, chat_id)
    if not user:
        logger.warning(
            f"Пользователь telegram_id={telegram_id} не найден в чате {chat_id}"
        )
        return 0, False

    user_id = user.id
    buns = await get_user_buns_stats(telegram_id, chat_id)

    if not buns:  # Если булочек нет, добавляем Круассан с базовыми очками
        user_bun = await add_or_update_user_bun(user_id, "Круассан", chat_id)
        if not user_bun:
            logger.error(
                f"Не удалось добавить Круассан для user_id={user_id} в чате {chat_id}"
            )
            return 0, False

        base_points = user_bun.points
        new_total = max(0, points)
        if new_total != base_points:
            additional_points = new_total - base_points
            total_points = base_points + additional_points
            await update_user_points(telegram_id, chat_id, total_points - base_points)
        logger.info(
            f"Добавлен Круассан с базовыми {base_points} очками, итого: {new_total}"
        )
        return new_total, True
    else:  # Если булочки есть, добавляем только новые очки
        total_points = sum(bun["points"] for bun in buns)
        await update_user_points(telegram_id, chat_id, points)
        new_total = max(0, total_points + points)
        return new_total, False


@payments_r.message(Command("buy_points"))
async def buy_points_handler(message: Message, bot: Bot):
    """Обработчик команды /buy_points — показывает клавиатуру для выбора количества баллов."""
    user = message.from_user
    chat_id = message.chat.id

    # Создаём клавиатуру с вариантами покупки
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="50 баллов", callback_data="buy:50")],
            [InlineKeyboardButton(text="100 баллов", callback_data="buy:100")],
            [InlineKeyboardButton(text="200 баллов", callback_data="buy:200")],
        ]
    )
    await message.reply(
        "Выберите количество баллов для покупки:", reply_markup=keyboard
    )
    logger.debug(f"@{user.username} (ID: {user.id}) запросил покупку баллов")


@payments_r.callback_query(lambda c: c.data.startswith("buy:"))
async def process_buy_callback(callback_query: CallbackQuery, bot: Bot):
    """Обработка выбора количества баллов и отправка инвойса."""
    user = callback_query.from_user
    chat_id = callback_query.message.chat.id
    points = int(callback_query.data.split(":")[1])

    if points not in POINTS_PRICES:
        await callback_query.message.edit_text(
            f"Недопустимое количество баллов. Доступные варианты: {', '.join(map(str, POINTS_PRICES.keys()))}"
        )
        await callback_query.answer()
        return

    price = POINTS_PRICES[points]  # Сумма в копейках
    await bot.send_invoice(
        chat_id=chat_id,
        title=f"Покупка {points} баллов",
        description=f"Начисление {points} баллов для игры",
        payload=f"buy_points:{user.id}:{chat_id}:{points}",  # Уникальный идентификатор
        provider_token=YOOMONEY_PROVIDER_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label="Баллы", amount=price)],
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
    )
    await callback_query.answer()
    logger.info(
        f"@{user.username} (ID: {user.id}) выбрал покупку {points} баллов за {price / 100} RUB"
    )


@payments_r.message(lambda message: message.successful_payment is not None)
async def process_successful_payment(message: Message, bot: Bot):
    """Обработка успешной оплаты через YooMoney."""
    payment = message.successful_payment
    payload = payment.invoice_payload.split(":")
    telegram_id, chat_id, points = int(payload[1]), int(payload[2]), int(payload[3])

    new_points, is_new_croissant = await apply_points_to_user(
        telegram_id, chat_id, points
    )
    await message.reply(PAYMENT_SUCCESS_MESSAGE.format(points=points))
    if is_new_croissant:
        user = await get_user_by_id(telegram_id, chat_id)
        await bot.send_message(
            chat_id, NEWBIE_MESSAGE.format(target=user.username, points=new_points)
        )
    logger.info(
        f"Успешная оплата для telegram_id={telegram_id}: начислено {points} баллов"
    )
