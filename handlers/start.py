from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.queries import add_user
from logger import logger

start_r = Router()


@start_r.message(CommandStart())
async def start(message: Message):
    """Обработчик команды /start для активации бота в чате."""
    await message.answer(
        "Привет-привет, я Бот Булочка Дня! 🥐🤖\n\n"
        "Я здесь не просто так – моя миссия крайне важна! Я встречаю новых участников с теплом, как свежую выпечку из печи, "
        "и каждый день объявляю, кто у нас самая сладкая, румяная и аппетитная булочка! 🍰🔥\n\n"
        "Так что готовьтесь к потоку муки… ой, в смысле – любви и комплиментов! 💖\n\n"
        "<i>Проект будет развиваться по мере того, как его создатель прокачивает свой интеллект (а пока он ест булочки и пишет код). 🧐🍩</i>",
        parse_mode="HTML",
    )
    from_user = message.from_user
    chat_id = message.chat.id

    if message.chat.type == "private":
        await message.reply("Эта команда работает только в групповых чатах!")
        return

    if not from_user:
        await message.reply("Не удалось получить информацию о пользователе.")
        return

    # Добавляем пользователя в базу, если его там нет
    user = await add_user(
        telegram_id=from_user.id,
        username=from_user.username,
        full_name=from_user.full_name,
        chat_id=chat_id,
    )
    if user:
        await message.reply(
            f"Бот активирован в этом чате! Используйте /play, чтобы начать игру."
        )
        logger.info(f"Бот активирован в чате {chat_id} пользователем {from_user.id}")
    else:
        await message.reply("Вы уже активировали бота в этом чате!")
