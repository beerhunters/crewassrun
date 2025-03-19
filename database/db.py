import functools
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

load_dotenv()
DOCKER_ENV = os.getenv("DOCKER_ENV", "False") == "True"

DATABASE_URL = (
    os.getenv("DATABASE_URL") if DOCKER_ENV else os.getenv("DATABASE_URL_LOCAL")
)

engine = create_async_engine(url=DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def with_session(func):
    """Декоратор для автоматического создания и закрытия сессии"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return wrapper
