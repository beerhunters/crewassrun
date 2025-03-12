# from aiogram import Router
# from aiogram.filters import CommandStart
# from aiogram.types import Message
#
# from database.queries import add_user
# from logger import logger
#
# start_r = Router()
#
#
# @start_r.message(CommandStart())
# async def start(message: Message):
#     """Обработчик команды /start для активации бота в чате."""
#     await message.answer(
#         "Привет-привет, я Бот Булочка Дня! 🥐🤖\n\n"
#         "Я здесь не просто так – моя миссия крайне важна! Я встречаю новых участников с теплом, как свежую выпечку из печи, "
#         "и каждый день объявляю, кто у нас самая сладкая, румяная и аппетитная булочка! 🍰🔥\n\n"
#         "Так что готовьтесь к потоку муки… ой, в смысле – любви и комплиментов! 💖\n\n"
#         "<i>Проект будет развиваться по мере того, как его создатель прокачивает свой интеллект (а пока он ест булочки и пишет код). 🧐🍩</i>",
#         parse_mode="HTML",
#     )
#     from_user = message.from_user
#     chat_id = message.chat.id
#
#     if message.chat.type == "private":
#         await message.reply("Эта команда работает только в групповых чатах!")
#         return
#
#     if not from_user:
#         await message.reply("Не удалось получить информацию о пользователе.")
#         return
#
#     # Добавляем пользователя в базу, если его там нет
#     user = await add_user(
#         telegram_id=from_user.id,
#         username=from_user.username,
#         full_name=from_user.full_name,
#         chat_id=chat_id,
#     )
#     if user:
#         await message.reply(
#             f"Бот активирован в этом чате! Используйте /play, чтобы начать игру."
#         )
#         logger.info(f"Бот активирован в чате {chat_id} пользователем {from_user.id}")
#     else:
#         await message.reply("Вы уже активировали бота в этом чате!")
# handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner
from database.queries import add_user
from logger import logger

start_r = Router()


@start_r.message(CommandStart())
async def start(message: Message):
    """Обработчик команды /start для активации бота в чате или описания в ЛС."""
    from_user = message.from_user
    chat_id = message.chat.id

    if not from_user:
        await message.reply("Не удалось получить информацию о пользователе.")
        return

    # Личное сообщение
    if message.chat.type == "private":
        await message.answer(
            "Привет! Я Бот Булочка Дня! 🥐🤖\n\n"
            "Моя задача — приносить радость в групповые чаты! Я приветствую новых участников стикерами, "
            "каждый день выбираю самую аппетитную булочку среди игроков и раздаю виртуальные вкусности. 🍩✨\n\n"
            "Добавь меня в свой чат, сделай администратором и активируй командой /start. "
            "После этого используй /play, чтобы начать игру! 🎮\n\n"
            "<i>Создан для веселья и булочек.</i>\n"
            "<i>Проект будет развиваться по мере того, как его создатель прокачивает свой интеллект (а пока он ест булочки и пишет код). 🧐🍩</i>",
            parse_mode="HTML",
        )
        return

    # Групповой чат: проверяем, является ли бот администратором
    bot_member = await message.bot.get_chat_member(
        chat_id=chat_id, user_id=message.bot.id
    )
    is_admin = isinstance(bot_member, (ChatMemberAdministrator, ChatMemberOwner))

    if not is_admin:
        await message.reply(
            "Я не могу начать работу, пока не стану администратором! 😔\n"
            "Пожалуйста, сделай меня админом в этом чате, и я начну раздавать булочки! 🥐",
            parse_mode="HTML",
        )
        logger.warning(
            f"Бот не активирован в чате {chat_id}: не является администратором"
        )
        return

    # Бот — админ, добавляем пользователя в базу
    user = await add_user(
        telegram_id=from_user.id,
        username=from_user.username,
        full_name=from_user.full_name,
        chat_id=chat_id,
        in_game=False,  # По умолчанию не в игре, пусть активируется через /play
    )

    display_name = (
        f"@{from_user.username}" if from_user.username else from_user.full_name
    )
    if user:
        await message.reply(
            f"Привет, {display_name}! Я Бот Булочка Дня, и я активирован! 🥐✨\n"
            "Теперь я буду встречать новичков стикерами и каждый день выбирать самую вкусную булочку. "
            "Используй /play, чтобы加入游戏 (присоединиться к игре) и начать получать булочки! 🎮",
            parse_mode="HTML",
        )
        logger.info(f"Бот активирован в чате {chat_id} пользователем {from_user.id}")
    else:
        await message.reply(
            f"Привет, {display_name}! Я уже активирован в этом чате! 🥐\n"
            "Используй /play, чтобы начать игру и получить свою булочку! 🎮",
            parse_mode="HTML",
        )
        logger.debug(
            f"Повторная активация в чате {chat_id} пользователем {from_user.id}"
        )
