from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

start_r = Router()


@start_r.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет-привет, я Бот Булочка Дня! 🥐🤖\n\n"
        "Я здесь не просто так – моя миссия крайне важна! Я встречаю новых участников с теплом, как свежую выпечку из печи, "
        "и каждый день объявляю, кто у нас самая сладкая, румяная и аппетитная булочка! 🍰🔥\n\n"
        "Так что готовьтесь к потоку муки… ой, в смысле – любви и комплиментов! 💖\n\n"
        "_Проект будет развиваться по мере того, как его создатель прокачивает свой интеллект (а пока он ест булочки и пишет код). 🧐🍩_"
    )
