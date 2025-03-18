# api/main.py
import argparse
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database.db import engine, async_session
from database.models import User, Bun, UserBun, GameSetting
from sqlalchemy.future import select
from sqlalchemy import delete, update

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API lifespan")
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Bun.metadata.create_all)
        await conn.run_sync(UserBun.metadata.create_all)
        await conn.run_sync(GameSetting.metadata.create_all)
    logger.info("API lifespan started successfully")
    yield
    logger.info("Shutting down API lifespan")


app = FastAPI(title="Bun Bot API", lifespan=lifespan)

logger.info("API initialized")


# Модели для валидации данных
class UserModel(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    full_name: str
    chat_id: int
    in_game: bool


class BunModel(BaseModel):
    name: str
    points: int


class UserBunModel(BaseModel):
    id: int
    user_id: int
    bun: str
    chat_id: int
    count: int
    points: int


class GameSettingModel(BaseModel):  # Новая модель для настроек
    id: int
    key: str
    value: int
    description: Optional[str] = None


# Pydantic-модель для валидации тела запроса
class PointsUpdateRequest(BaseModel):
    chat_id: int
    telegram_ids: List[int] = []  # По умолчанию пустой список
    points: int


# --- Эндпоинты для пользователей ---
@app.get("/users/", response_model=List[UserModel])
async def get_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return [UserModel(**user.__dict__) for user in users]


@app.put("/users/{telegram_id}/{chat_id}/toggle_game")
async def toggle_user_game(telegram_id: int, chat_id: int):
    async with async_session() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id, User.chat_id == chat_id)
        )
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user.in_game = not user.in_game  # Переключаем статус
        action = "выведен из игры" if not user.in_game else "возвращён в игру"
        await session.commit()
        return {"message": f"Пользователь {telegram_id} {action} в чате {chat_id}"}


# --- Эндпоинты для булочек ---
@app.get("/buns/", response_model=List[BunModel])
async def get_buns():
    async with async_session() as session:
        result = await session.execute(select(Bun))
        buns = result.scalars().all()
        return [BunModel(**bun.__dict__) for bun in buns]


@app.post("/buns/", response_model=BunModel)
async def create_bun(bun: BunModel):
    async with async_session() as session:
        new_bun = Bun(name=bun.name, points=bun.points)
        session.add(new_bun)
        try:
            await session.commit()
            return bun
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=f"Bun already exists: {str(e)}")


@app.put("/buns/{name}", response_model=BunModel)
async def update_bun(name: str, bun: BunModel):
    async with async_session() as session:
        stmt = update(Bun).where(Bun.name == name).values(points=bun.points)
        result = await session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Bun not found")
        await session.commit()
        return bun


@app.delete("/buns/{name}")
async def delete_bun(name: str):
    async with async_session() as session:
        bun = await session.execute(select(Bun).where(Bun.name == name))
        bun = bun.scalar_one_or_none()
        if not bun:
            raise HTTPException(status_code=404, detail="Bun not found")
        await session.delete(bun)
        await session.commit()
        return {"message": f"Bun {name} deleted"}


# --- Эндпоинты для результатов (UserBun) ---
@app.get("/user_buns/", response_model=List[UserBunModel])
async def get_user_buns():
    async with async_session() as session:
        result = await session.execute(select(UserBun))
        user_buns = result.scalars().all()
        return [UserBunModel(**ub.__dict__) for ub in user_buns]


@app.put("/user_buns/{id}", response_model=UserBunModel)
async def update_user_bun(id: int, user_bun: UserBunModel):
    async with async_session() as session:
        stmt = (
            update(UserBun)
            .where(UserBun.id == id)
            .values(count=user_bun.count, points=user_bun.points)
        )
        result = await session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="UserBun not found")
        await session.commit()
        return user_bun


@app.delete("/user_buns/{id}")
async def delete_user_bun(id: int):
    async with async_session() as session:
        user_bun = await session.execute(select(UserBun).where(UserBun.id == id))
        user_bun = user_bun.scalar_one_or_none()
        if not user_bun:
            raise HTTPException(status_code=404, detail="UserBun not found")
        await session.delete(user_bun)
        await session.commit()
        return {"message": f"UserBun {id} deleted"}


# --- Эндпоинты для настроек игры (GameSetting) ---
@app.get("/game_settings/", response_model=List[GameSettingModel])
async def get_game_settings():
    async with async_session() as session:
        result = await session.execute(select(GameSetting))
        settings = result.scalars().all()
        return [GameSettingModel(**setting.__dict__) for setting in settings]


@app.post("/game_settings/", response_model=GameSettingModel)
async def create_game_setting(setting: GameSettingModel):
    async with async_session() as session:
        new_setting = GameSetting(
            key=setting.key, value=setting.value, description=setting.description
        )
        session.add(new_setting)
        try:
            await session.commit()
            return setting
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=400, detail=f"Setting already exists: {str(e)}"
            )


@app.put("/game_settings/{key}", response_model=GameSettingModel)
async def update_game_setting(key: str, setting: GameSettingModel):
    async with async_session() as session:
        stmt = (
            update(GameSetting)
            .where(GameSetting.key == key)
            .values(value=setting.value, description=setting.description)
        )
        result = await session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Setting not found")
        await session.commit()
        return setting


@app.delete("/game_settings/{key}")
async def delete_game_setting(key: str):
    async with async_session() as session:
        setting = await session.execute(
            select(GameSetting).where(GameSetting.key == key)
        )
        setting = setting.scalar_one_or_none()
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        await session.delete(setting)
        await session.commit()
        return {"message": f"Setting {key} deleted"}


@app.put("/users/points")
async def update_points(request: PointsUpdateRequest):
    async with async_session() as session:
        # Если telegram_ids пустой, выбираем всех активных пользователей чата
        if not request.telegram_ids:
            result = await session.execute(
                select(User).where(
                    User.chat_id == request.chat_id, User.in_game == True
                )
            )
            users = result.scalars().all()
            if not users:
                raise HTTPException(
                    status_code=404, detail="Нет активных пользователей в чате"
                )
        else:
            # Выбираем только указанных пользователей
            result = await session.execute(
                select(User).where(
                    User.chat_id == request.chat_id,
                    User.telegram_id.in_(request.telegram_ids),
                )
            )
            users = result.scalars().all()
            if not users:
                raise HTTPException(
                    status_code=404, detail="Указанные пользователи не найдены"
                )

        updated_count = 0
        for user in users:
            # Получаем текущие булочки пользователя
            buns_result = await session.execute(
                select(UserBun).where(
                    UserBun.user_id == user.id, UserBun.chat_id == request.chat_id
                )
            )
            user_buns = buns_result.scalars().all()

            if not user_buns:  # Если булочек нет, добавляем Круассан
                new_bun = UserBun(
                    user_id=user.id,
                    bun="Круассан",
                    count=1,
                    points=max(0, request.points),
                    chat_id=request.chat_id,
                )
                session.add(new_bun)
                updated_count += 1
                logger.info(
                    f"Добавлен Круассан с {request.points} очками для telegram_id={user.telegram_id}"
                )
            else:
                # Обновляем очки по существующим булочкам
                total_points = sum(bun.points for bun in user_buns)
                new_total = max(0, total_points + request.points)

                if new_total == 0:
                    for bun in user_buns:
                        bun.points = 0
                else:
                    zero_buns = [bun for bun in user_buns if bun.points == 0]
                    non_zero_buns = [bun for bun in user_buns if bun.points > 0]

                    if zero_buns and request.points > 0:
                        points_per_zero = request.points // len(zero_buns)
                        extra_points = request.points % len(zero_buns)
                        for i, bun in enumerate(zero_buns):
                            bun.points = points_per_zero + (
                                1 if i < extra_points else 0
                            )
                    elif request.points > 0:
                        points_per_bun = request.points // len(user_buns)
                        extra_points = request.points % len(user_buns)
                        for i, bun in enumerate(user_buns):
                            bun.points += points_per_bun + (
                                1 if i < extra_points else 0
                            )
                    elif request.points < 0:
                        remaining_loss = abs(request.points)
                        for bun in sorted(
                            user_buns, key=lambda x: x.points, reverse=True
                        ):
                            if remaining_loss <= 0:
                                break
                            loss = min(bun.points, remaining_loss)
                            bun.points -= loss
                            remaining_loss -= loss

                updated_count += 1
                logger.info(
                    f"Обновлены очки для telegram_id={user.telegram_id}, новые очки: {new_total}"
                )

        await session.commit()
        return {
            "message": f"Очки ({request.points}) начислены {updated_count} пользователям в чате {request.chat_id}",
            "updated_count": updated_count,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
