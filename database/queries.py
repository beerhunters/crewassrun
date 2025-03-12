from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import with_session
from database.models import User, UserBun, Bun
import random

from logger import logger


@with_session
async def add_user(
    session: AsyncSession, telegram_id: int, chat_id: int, username: str, full_name: str
):
    """Добавление нового пользователя или обновление статуса в игре."""
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()
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
    session.add(new_user)
    await session.commit()
    return new_user


@with_session
async def get_user_by_id(session: AsyncSession, telegram_id: int, chat_id: int):
    """Получение пользователя по telegram_id и chat_id."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id, User.chat_id == chat_id)
    )
    return result.scalars().first()


@with_session
async def add_user_to_game(session: AsyncSession, telegram_id: int, chat_id: int):
    """Включение пользователя в игру."""
    user = await session.execute(
        select(User).where(User.telegram_id == telegram_id, User.chat_id == chat_id)
    )
    user = user.scalar_one_or_none()
    if user and not user.in_game:
        user.in_game = True
        await session.commit()
        return True
    return False


@with_session
async def set_user_out_of_game(session: AsyncSession, telegram_id: int, chat_id: int):
    """Установка статуса in_game=False для пользователя, покинувшего чат."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id, User.chat_id == chat_id)
    )
    user = result.scalars().first()
    if user and user.in_game:
        user.in_game = False
        await session.commit()
        return True
    return False


@with_session
async def get_random_user(session: AsyncSession, chat_id: int):
    """Получение случайного пользователя из чата."""
    result = await session.execute(
        select(User).where(User.chat_id == chat_id, User.in_game == True)
    )
    users = result.scalars().all()
    return random.choice(users) if users else None


# @with_session
# async def add_or_update_user_bun(
#     session: AsyncSession, user_id: int, bun: str, chat_id: int
# ):
#     """Добавление или обновление записи о булочке для пользователя с учетом очков."""
#     from buns_data import BUNS_POINTS  # Импортируем внутри функции, если нужно
#
#     points_per_bun = BUNS_POINTS.get(bun, 0)  # Очки за одну булочку, по умолчанию 0
#     try:
#         result = await session.execute(
#             select(UserBun).where(
#                 UserBun.user_id == user_id,
#                 UserBun.bun == bun,
#                 UserBun.chat_id == chat_id,
#             )
#         )
#         user_bun = result.scalars().first()
#         if user_bun:
#             user_bun.count += 1
#             user_bun.points = user_bun.count * points_per_bun  # Обновляем очки
#         else:
#             session.add(
#                 UserBun(
#                     user_id=user_id,
#                     bun=bun,
#                     chat_id=chat_id,
#                     count=1,
#                     points=points_per_bun,  # Начальные очки для новой булочки
#                 )
#             )
#         await session.commit()
#     except IntegrityError:
#         await session.rollback()
@with_session
async def add_or_update_user_bun(
    session: AsyncSession, user_id: int, bun: str, chat_id: int
):
    """Добавление или обновление записи о булочке для пользователя с учетом очков."""
    # Получаем баллы за булочку из таблицы buns
    result = await session.execute(select(Bun).where(Bun.name == bun))
    bun_record = result.scalar_one_or_none()

    if not bun_record:
        logger.error(f"Булочка '{bun}' не найдена в таблице buns")
        return  # Или можно выбросить исключение, если это критично

    points_per_bun = bun_record.points  # Баллы за одну булочку из базы

    try:
        # Проверяем, есть ли уже запись для этой булочки у пользователя
        result = await session.execute(
            select(UserBun).where(
                UserBun.user_id == user_id,
                UserBun.bun == bun,
                UserBun.chat_id == chat_id,
            )
        )
        user_bun = result.scalar_one_or_none()

        if user_bun:
            # Если запись существует, увеличиваем счётчик и пересчитываем очки
            user_bun.count += 1
            user_bun.points = user_bun.count * points_per_bun
            logger.debug(
                f"Обновлена запись для user_id={user_id}, bun={bun}, count={user_bun.count}, points={user_bun.points}"
            )
        else:
            # Если записи нет, создаём новую
            user_bun = UserBun(
                user_id=user_id,
                bun=bun,
                chat_id=chat_id,
                count=1,
                points=points_per_bun,
            )
            session.add(user_bun)
            logger.info(
                f"Добавлена новая булочка '{bun}' для user_id={user_id} в чате {chat_id}"
            )

        await session.commit()
        return user_bun  # Можно вернуть объект для дальнейшего использования
    except IntegrityError as e:
        await session.rollback()
        logger.error(
            f"Ошибка целостности при добавлении булочки '{bun}' для user_id={user_id}: {e}"
        )
        raise
    except Exception as e:
        await session.rollback()
        logger.error(
            f"Неизвестная ошибка при обновлении булочки '{bun}' для user_id={user_id}: {e}"
        )
        raise


@with_session
async def get_user_buns_stats(session: AsyncSession, telegram_id: int, chat_id: int):
    """Получение статистики булочек пользователя: булочка - количество - очки."""
    query = (
        select(UserBun.bun, UserBun.count, UserBun.points)
        .join(User, User.id == UserBun.user_id)
        .where(User.telegram_id == telegram_id, UserBun.chat_id == chat_id)
    )
    result = await session.execute(query)
    user_buns = result.fetchall()
    return (
        [
            {"bun": bun, "count": count, "points": points}
            for bun, count, points in user_buns
        ]
        if user_buns
        else []
    )


@with_session
async def get_top_users_by_points(session: AsyncSession, chat_id: int):
    """Получение топ-10 пользователей по очкам с их лучшей булочкой."""
    # Подзапрос для получения максимальных очков по булочке для каждого пользователя
    subquery = (
        select(
            UserBun.user_id,
            func.max(UserBun.points).label("max_points"),
            UserBun.bun.label("top_bun"),
            UserBun.count.label("top_count"),
        )
        .where(UserBun.chat_id == chat_id)
        .group_by(UserBun.user_id)
        .subquery()
    )

    # Основной запрос: соединяем с пользователями и сортируем по очкам
    query = (
        select(
            User.username,
            User.full_name,
            subquery.c.max_points,
            subquery.c.top_bun,
            subquery.c.top_count,
        )
        .join(subquery, User.id == subquery.c.user_id)
        .where(User.chat_id == chat_id, User.in_game == True)
        .order_by(subquery.c.max_points.desc())
        .limit(10)
    )

    result = await session.execute(query)
    top_users = result.fetchall()
    return (
        [
            {
                "username": username,
                "full_name": full_name,
                "points": max_points,
                "bun": top_bun,
                "count": top_count,
            }
            for username, full_name, max_points, top_bun, top_count in top_users
        ]
        if top_users
        else []
    )


@with_session
async def get_all_users(session: AsyncSession):
    """Получение списка всех пользователей."""
    result = await session.execute(
        select(
            User.telegram_id, User.username, User.full_name, User.chat_id, User.in_game
        )
    )
    users = result.fetchall()
    return [
        {
            "telegram_id": telegram_id,
            "username": username,
            "full_name": full_name,
            "chat_id": chat_id,
            "in_game": in_game,
        }
        for telegram_id, username, full_name, chat_id, in_game in users
    ]


@with_session
async def remove_user_from_game(session: AsyncSession, telegram_id: int, chat_id: int):
    """Удаление пользователя из розыгрыша (установка in_game=False)."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id, User.chat_id == chat_id)
    )
    user = result.scalars().first()
    if user and user.in_game:
        user.in_game = False
        await session.commit()
        return True
    return False


@with_session
async def get_active_chat_ids(session: AsyncSession):
    """Получение списка уникальных chat_id, где есть активные пользователи."""
    result = await session.execute(
        select(User.chat_id).where(User.in_game == True).distinct()
    )
    return [row[0] for row in result.fetchall()]


@with_session
async def get_all_buns(session: AsyncSession):
    """Получение всех булочек из таблицы buns."""
    result = await session.execute(select(Bun))
    buns = result.scalars().all()
    return {
        bun.name: bun.points for bun in buns
    }  # Возвращаем словарь вида {name: points}
