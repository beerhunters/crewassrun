# from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
#
# Base = declarative_base()
#
#
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, unique=True, nullable=False)
#     chat_id = Column(Integer, nullable=False)
#     username = Column(String, nullable=True)
#     full_name = Column(String, nullable=True)
#     in_game = Column(Boolean, default=True)  # Добавляем статус пользователя в игре
#
#     # Связь с UserBun
#     user_buns = relationship("UserBun", back_populates="user")
#
#
# class UserBun(Base):
#     __tablename__ = "user_buns"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     username = Column(String, nullable=True)
#     full_name = Column(String, nullable=False)
#     bun = Column(String, nullable=False)
#     count = Column(Integer, default=1)
#     chat_id = Column(Integer, nullable=False)
#
#     # Связь с User
#     user = relationship("User", back_populates="user_buns")
#
#     __table_args__ = (
#         UniqueConstraint(
#             "user_id", "bun", name="unique_user_bun"
#         ),  # Уникальная пара user_id + bun
#     )
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(
        Integer, unique=True, nullable=False
    )  # Telegram ID пользователя
    username = Column(String, nullable=True)  # Username (может быть null)
    full_name = Column(String, nullable=False)  # Полное имя
    chat_id = Column(Integer, nullable=False)  # Чат, в котором пользователь играет
    in_game = Column(Boolean, default=False)  # Статус в игре
    buns = relationship("UserBun", back_populates="user")  # Связь с булочками


class UserBun(Base):
    __tablename__ = "user_buns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Связь с пользователем
    bun = Column(String, nullable=False)  # Название булочки
    count = Column(Integer, default=0)  # Сколько раз выпадала эта булочка
    chat_id = Column(Integer, nullable=False)  # Чат, в котором это произошло
    points = Column(Integer, nullable=False, default=0)  # Новая колонка
    user = relationship("User", back_populates="buns")  # Обратная связь
    __table_args__ = (
        UniqueConstraint(
            "user_id", "bun", "chat_id", name="unique_user_bun_chat"
        ),  # Уникальность связки
    )
