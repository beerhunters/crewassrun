# database/repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func  # Исправленный импорт

from database.models import User, Bun, UserBun, GameSetting
from typing import List, Dict, Optional
import random
from logger import logger

# --- Общие функции для работы с базой ---


async def fetch_all(session: AsyncSession, model) -> List:
    result = await session.execute(select(model))
    return result.scalars().all()


async def fetch_one(session: AsyncSession, model, **filters) -> Optional:
    result = await session.execute(select(model).filter_by(**filters))
    return result.scalar_one_or_none()


async def create_or_update(session: AsyncSession, instance):
    session.add(instance)
    try:
        await session.commit()
        return instance
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при создании/обновлении: {str(e)}")
        raise


async def delete_instance(session: AsyncSession, instance):
    await session.delete(instance)
    await session.commit()


# --- User ---
async def get_users(session: AsyncSession) -> List[User]:
    return await fetch_all(session, User)


async def get_user_by_id(
    session: AsyncSession, telegram_id: int, chat_id: int
) -> Optional[User]:
    return await fetch_one(session, User, telegram_id=telegram_id, chat_id=chat_id)


async def add_user(
    session: AsyncSession, telegram_id: int, chat_id: int, username: str, full_name: str
) -> User:
    user = await get_user_by_id(session, telegram_id, chat_id)
    if user:
        if not user.in_game:
            user.in_game = True
            await session.commit()
        return user
    new_user = User(
        telegram_id=telegram_id,
        chat_id=chat_id,
        username=username,
        full_name=full_name,
        in_game=True,
    )
    return await create_or_update(session, new_user)


async def toggle_user_game(
    session: AsyncSession, telegram_id: int, chat_id: int
) -> bool:
    user = await get_user_by_id(session, telegram_id, chat_id)
    if not user:
        return False
    user.in_game = not user.in_game
    await session.commit()
    return True


async def get_random_user(session: AsyncSession, chat_id: int) -> Optional[User]:
    result = await session.execute(
        select(User).where(User.chat_id == chat_id, User.in_game == True)
    )
    users = result.scalars().all()
    return random.choice(users) if users else None


# --- Bun ---
async def get_buns(session: AsyncSession) -> List[Bun]:
    return await fetch_all(session, Bun)


async def add_bun(session: AsyncSession, name: str, points: int) -> Optional[Bun]:
    bun = await fetch_one(session, Bun, name=name)
    if bun:
        return None
    new_bun = Bun(name=name, points=points)
    return await create_or_update(session, new_bun)


async def update_bun(session: AsyncSession, name: str, points: int) -> Optional[Bun]:
    bun = await fetch_one(session, Bun, name=name)
    if not bun:
        return None
    bun.points = points
    await session.commit()
    return bun


async def delete_bun(session: AsyncSession, name: str) -> bool:
    bun = await fetch_one(session, Bun, name=name)
    if not bun:
        return False
    await delete_instance(session, bun)
    return True


# --- UserBun ---
async def get_user_buns(session: AsyncSession) -> List[UserBun]:
    return await fetch_all(session, UserBun)


async def add_or_update_user_bun(
    session: AsyncSession, user_id: int, bun: str, chat_id: int
) -> Optional[UserBun]:
    bun_record = await fetch_one(session, Bun, name=bun)
    if not bun_record:
        logger.error(f"Булочка '{bun}' не найдена в таблице buns")
        return None
    points_per_bun = bun_record.points

    user_bun = await fetch_one(
        session, UserBun, user_id=user_id, bun=bun, chat_id=chat_id
    )
    if user_bun:
        user_bun.count += 1
        user_bun.points = user_bun.count * points_per_bun
    else:
        user_bun = UserBun(
            user_id=user_id, bun=bun, chat_id=chat_id, count=1, points=points_per_bun
        )
    return await create_or_update(session, user_bun)


async def update_user_bun(
    session: AsyncSession, id: int, count: int, points: int
) -> Optional[UserBun]:
    user_bun = await fetch_one(session, UserBun, id=id)
    if not user_bun:
        return None
    user_bun.count = count
    user_bun.points = points
    await session.commit()
    return user_bun


async def delete_user_bun(session: AsyncSession, id: int) -> bool:
    user_bun = await fetch_one(session, UserBun, id=id)
    if not user_bun:
        return False
    await delete_instance(session, user_bun)
    return True


# --- GameSetting ---
async def get_game_settings(session: AsyncSession) -> List[GameSetting]:
    return await fetch_all(session, GameSetting)


async def get_game_setting(session: AsyncSession, key: str) -> Optional[int]:
    setting = await fetch_one(session, GameSetting, key=key)
    return setting.value if setting else 0


async def get_all_game_settings(session: AsyncSession) -> Dict[str, int]:
    settings = await get_game_settings(session)
    return {setting.key: setting.value for setting in settings}


async def add_game_setting(
    session: AsyncSession, key: str, value: int, description: Optional[str] = None
) -> Optional[GameSetting]:
    setting = await fetch_one(session, GameSetting, key=key)
    if setting:
        return None
    new_setting = GameSetting(key=key, value=value, description=description)
    return await create_or_update(session, new_setting)


async def update_game_setting(
    session: AsyncSession, key: str, value: int, description: Optional[str] = None
) -> Optional[GameSetting]:
    setting = await fetch_one(session, GameSetting, key=key)
    if not setting:
        return None
    setting.value = value
    if description is not None:
        setting.description = description
    await session.commit()
    return setting


async def delete_game_setting(session: AsyncSession, key: str) -> bool:
    setting = await fetch_one(session, GameSetting, key=key)
    if not setting:
        return False
    await delete_instance(session, setting)
    return True
