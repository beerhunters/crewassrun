from sqlalchemy import func, cast, String, asc, literal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import with_session
from database.models import User, UserBun
import random


@with_session
async def add_user(
    session: AsyncSession,
    user_id: int,
    chat_id: int,
    username: str,
    full_name: str,
):
    """Добавляет пользователя в базу данных или обновляет его статус, если он уже есть."""
    # Проверяем, есть ли пользователь в базе данных
    result = await session.execute(select(User).where(User.user_id == user_id))
    user = result.scalars().first()

    if user:
        # Если пользователь найден, проверяем его статус
        if not user.in_game:
            user.in_game = True  # Если он не в игре, то меняем его статус на "в игре"
            await session.commit()  # Сохраняем изменения
        return  # Уже есть в базе

    # Если пользователя нет в базе, создаем нового
    new_user = User(
        user_id=user_id, chat_id=chat_id, username=username, full_name=full_name
    )
    session.add(new_user)
    await session.commit()


@with_session
async def get_user_by_id(session: AsyncSession, user_id: int, chat_id: int):
    result = await session.execute(
        select(User).where(User.user_id == user_id, User.chat_id == chat_id)
    )
    return result.scalars().first()  # Возвращает объект User или None


@with_session
async def add_user_to_game(session: AsyncSession, user_id: int):
    """Добавляем пользователя в игру, если его еще нет."""
    user = await session.execute(select(User).where(User.user_id == user_id))
    user = user.scalars().first()

    if user and not user.in_game:
        user.in_game = True  # Устанавливаем, что пользователь теперь в игре
        await session.commit()
        return True  # Успешно добавлен в игру
    return False  # Если пользователь уже в игре


@with_session
async def get_random_user(session: AsyncSession):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return random.choice(users) if users else None


@with_session
async def add_or_update_user_bun(
    session: AsyncSession,
    user_id: int,
    chat_id: int,
    username: str,
    full_name: str,
    bun: str,
):
    """Добавляет запись или увеличивает количество, если пользователь уже был этой булочкой в данном чате"""
    try:
        result = await session.execute(
            select(UserBun).where(
                UserBun.user_id == user_id,
                UserBun.chat_id == chat_id,  # Фильтр по чату
                UserBun.bun == bun,
            )
        )
        user_bun = result.scalars().first()

        if user_bun:
            user_bun.count += 1  # Увеличиваем счетчик
        else:
            session.add(
                UserBun(
                    user_id=user_id,
                    chat_id=chat_id,  # Сохраняем chat_id
                    username=username,
                    full_name=full_name,
                    bun=bun,
                )
            )

        await session.commit()
    except IntegrityError:
        await session.rollback()


@with_session
async def get_top_buns_with_users(
    session: AsyncSession, chat_id: int, limit: int = 10, offset: int = 0
):
    # Используем оператор "+" вместо "||" для SQLite в SQLAlchemy
    query = (
        select(
            UserBun.bun,
            func.group_concat(
                literal("@")
                + UserBun.username
                + literal(" (")
                + cast(UserBun.count, String)
                + literal(" раз)"),
                ", ",
            ).label("users"),
            func.max(UserBun.count).label("max_repeats"),
        )
        .where(UserBun.chat_id == chat_id)
        .group_by(UserBun.bun)
        .order_by(func.max(UserBun.count).asc())  # Сортировка по количеству повторов
        .limit(limit)
        .offset(offset)
    )

    result = await session.execute(query)
    top_buns = result.fetchall()

    # Обрабатываем результат
    return [
        {"bun": bun, "users": users.split(", "), "max_repeats": max_repeats}
        for bun, users, max_repeats in top_buns
        if users
    ]


@with_session
async def get_user_buns_stats(session: AsyncSession, user_id: int, chat_id: int):
    # Запрос для получения булочек конкретного пользователя с использованием связи
    query = select(UserBun.bun, func.sum(UserBun.count).label("count")).join(
        User, User.id == UserBun.user_id
    )  # Соединяем UserBun с User по user_id
    query = query.filter(
        User.user_id == user_id, UserBun.chat_id == chat_id
    )  # Фильтруем по user_id и chat_id
    query = query.group_by(UserBun.bun)  # Группируем по булочкам
    query = query.order_by(asc("count"))  # Сортируем по количеству повторов

    result = await session.execute(query)

    # Получаем результат
    user_buns = result.fetchall()

    # Преобразуем в нужный формат
    return [{"bun": bun, "count": count} for bun, count in user_buns]


# Функции в database/queries.py с декоратором @with_session
@with_session
async def get_all_users(session: AsyncSession):
    result = await session.execute(select(User))
    return result.scalars().all()
