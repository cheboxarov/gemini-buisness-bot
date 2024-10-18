import aiogram
import asyncio
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru_config import configure_loguru
from loguru import logger
from core import dp, bot
import handlers
from db.core import DataBaseManager


async def main():
    await DataBaseManager.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    configure_loguru("DEBUG")
    logger.debug("running bot")
    asyncio.run(main())
