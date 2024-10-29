from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from .models import Base
from .config import DATABASE_URL
from loguru import logger


class DataBaseManager:
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    @classmethod
    async def init_db(cls):
        logger.debug(f"init database")
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def close(cls):
        await cls.engine.dispose()
