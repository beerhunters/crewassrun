# api/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database.db import engine, async_session
from database.models import User, Bun, UserBun
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


# --- Эндпоинты для пользователей ---
@app.get("/users/", response_model=List[UserModel])
async def get_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return [UserModel(**user.__dict__) for user in users]


@app.delete("/users/{telegram_id}/{chat_id}")
async def delete_user(telegram_id: int, chat_id: int):
    async with async_session() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id, User.chat_id == chat_id)
        )
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await session.delete(user)
        await session.commit()
        return {"message": f"User {telegram_id} deleted from chat {chat_id}"}


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
