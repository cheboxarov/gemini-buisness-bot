from loguru import logger
import asyncio
from db.users_manager import db_users_manager
from db.models import User
import datetime
from handlers.get_contacts import get_contacts_after_time
from core import dp, bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from utils import get_state_by_user_id
from config import CONTACTS_MESSAGE_DELAY


async def main():
    while True:
        users = await db_users_manager.all()
        users_ids = list(filter(lambda id: id is not None , await asyncio.gather(*(user_contacts_receive_check(user) for user in users))))
        logger.debug(users_ids)
        users = await asyncio.gather(*(user_with_context(user_id) for user_id in users_ids))
        await asyncio.gather(*(get_contacts_after_time(*user) for user in users))
        await asyncio.sleep(60*5)

async def user_with_context(user_id: int) -> tuple[int, FSMContext]:
    context = await get_state_by_user_id(user_id, bot, dp)
    return (user_id, context)

async def user_contacts_receive_check(user: User) -> int:
    return user.tg_id if not user.contacts_received and user.next_contacts_question_date < datetime.datetime.now() else None


if __name__ == "__main__":
    asyncio.run(main())