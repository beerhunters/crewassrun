from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    chat_id = Column(Integer, nullable=False)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    in_game = Column(Boolean, default=True)  # Добавляем статус пользователя в игре


class UserBun(Base):
    __tablename__ = "user_buns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    bun = Column(String, nullable=False)
    count = Column(Integer, default=1)
    chat_id = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id", "bun", name="unique_user_bun"
        ),  # Уникальная пара user_id + bun
    )
