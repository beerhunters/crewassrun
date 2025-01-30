from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

start_r = Router()


@start_r.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я бот, который приветствует новых участников.")
