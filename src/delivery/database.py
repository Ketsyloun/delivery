import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DATABASE_URL = "postgresql+asyncpg://postgres:123@localhost:5432/delivery"


engine = create_async_engine(DATABASE_URL) #движок для ассинхронного

# транзакция - набор инструкций в бд (атомарные)/ сессии
# передается сам движок, класс для ассинхронности, false чтобы сессиии не истекали при коммите
asyncs_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# для работы с миграциями
class Base(DeclarativeBase):
    pass
