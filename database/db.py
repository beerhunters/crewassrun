import functools

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import DATABASE_URL

# engine = create_async_engine(url="sqlite+aiosqlite:////app/db.sqlite3", echo=True)
# engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3", echo=True)
engine = create_async_engine(url=DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def with_session(func):
    """Декоратор для автоматического создания и закрытия сессии"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return wrapper
