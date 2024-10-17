import threading
from sqlalchemy import create_engine

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import  AsyncGenerator

from modules.database import DATABASE_NAME, DATABASE_PASSWORD, DATABASE_PORT, DATABASE_URI, DATABASE_USERNAME
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class SingletonDBManager(type):
    _instances = {}
    _thread = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock(): # lock to ensure thread safety
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DataBaseError(Exception):
    pass


@dataclass
class DataBaseManager(metaclass=SingletonDBManager):
    pool_size: int = 20
    max_overflow: int = 5
    pool_recycle: int = 60

    def __init__(self):
        self._engine = None
        self._sync_engine = None
        self._async_engine = None

    def __enter__(self):
        self._session = self.session()
        return self._session

    async def __aenter__(self):
        self._async_session = await self.async_session()
        return self._async_session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._async_session.close()

    def sync_engine(self):
        try:
            if self._engine is None:
                self._engine = create_engine(
                    f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_URI}:"
                    f"{DATABASE_PORT}/{DATABASE_NAME}",
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_recycle=self.pool_recycle,
                    pool_timeout=10
                )
            return self._engine
        except Exception as e:
            raise DataBaseError(f"Error creating sync engine: {e}") from e

    async def async_engine(self):
        try:
            if self._async_engine is None:
                self._async_engine = create_async_engine(
                    f"postgresql+asyncpg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_URI}:"
                    f"{DATABASE_PORT}/{DATABASE_NAME}",
                    future=True,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_recycle=self.pool_recycle,
                    pool_timeout=10,
                    pool_pre_ping=True,
                )
            return self._async_engine
        except Exception as e:
            raise DataBaseError(f"Error creating async engine: {e}") from e

    def session(self):
        return sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=self.sync_engine())()

    async def async_session(self):
        return scoped_session(sessionmaker(bind=await self.async_engine(), class_=AsyncSession, expire_on_commit=False,
                                           autoflush=False, autocommit=False))()


db_manager = DataBaseManager()


@asynccontextmanager
async def get_async_session():
    db = await db_manager.async_session()
    try:
        yield db
    finally:
        await db.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session() as db:
        yield db