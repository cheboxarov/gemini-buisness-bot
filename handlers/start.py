from core import dp
from aiogram.types import Message
from loguru import logger
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from messages import START_MESSAGE
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import get_user_scheme_from_user
from db.users_manager import db_users_manager


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_scheme  = await get_user_scheme_from_user(message.from_user)
    user = await db_users_manager.get_or_create(user_scheme)
    
    logger.debug(
        f"New message from {message.from_user.username} ({user.id}), message text: {message.text}"
    )

    #markup_list = [[InlineKeyboardButton(text="Начать бриф", callback_data="start_brief")]]
    markup_list = [[InlineKeyboardButton(text="Заполнить бриф", callback_data="letters-start")]]
    if user.is_admin:
        markup_list.append([InlineKeyboardButton(text="Admin panel", callback_data='admin-menu')])
    markup = InlineKeyboardMarkup(
        inline_keyboard=markup_list
    )
    await message.answer(START_MESSAGE, reply_markup=markup)
