from core import bot, dp
from aiogram.fsm.context import FSMContext
from messages import (FIRST_GET_CONTACTS, 
                      FIRST_GET_CONTACTS_ANS, 
                      AFTER_GET_CONTACTS_FIRST,
                      AFTER_GET_CONTACTS_ANS,
                      AFTER_GET_CONTACTS_SECOND,
                      FIRST_GET_CONTACTS1)
from filters import ContextValueFilter, CallbackDataFilter
from aiogram.types import Message, CallbackQuery
from db.users_manager import db_users_manager
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CONTACTS_GROUP
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from loguru import logger


async def get_contacts(user_id: int, state: FSMContext):
    await db_users_manager.assign_following_message(user_id)
    await bot.send_message(user_id, FIRST_GET_CONTACTS1, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Хочу консультацию", callback_data="get-contacts1")]]))

@dp.callback_query(CallbackDataFilter(expected_data="get-contacts1"))
async def get_contacts_handler(callback: CallbackQuery, state: FSMContext):
    contact_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Скинуть ваш номер телефона", request_contact=True)]], resize_keyboard=True)
    await bot.send_message(callback.from_user.id, FIRST_GET_CONTACTS, reply_markup=contact_button)

    


@dp.message(ContextValueFilter(key="status", expected_value="get_contacts"))
async def get_contacts_handler(message: Message, state: FSMContext):
    try:
        contact = message.contact.phone_number
        await send_contacts_to_group(message, contact)
        await db_users_manager.contacts_received(message.from_user.id)
        await message.answer(FIRST_GET_CONTACTS_ANS)
    except Exception as err:
        logger.error(f"Ошибка при отправке контактов {err}")
        await message.answer("Нажмите на кнопку, для того, чтобы поделиться контактом.")


async def get_contacts_after_time(user_id: int, state: FSMContext):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обсудить проект", callback_data="get-contacts")]
    ])
    await db_users_manager.assign_following_message(user_id)
    await bot.send_message(user_id, AFTER_GET_CONTACTS_FIRST, reply_markup=markup)


@dp.callback_query(CallbackDataFilter(expected_data="get-contacts"))
async def get_contacts_after_time_callback_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    contact_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Скинуть ваш номер телефона", request_contact=True)]], resize_keyboard=True)
    await bot.send_message(callback.from_user.id, AFTER_GET_CONTACTS_SECOND, reply_markup=contact_button)
    await state.update_data(status="get-contacts-second")


@dp.message(ContextValueFilter(key="status", expected_value="get-contacts-second"))
async def get_contacts_after_time_handler(message: Message, state: FSMContext):
    await send_contacts_to_group(message)
    await db_users_manager.contacts_received(message.from_user.id)
    await message.answer(AFTER_GET_CONTACTS_ANS)
    state.clear()


async def send_contacts_to_group(message: Message, contact):
    await bot.send_message(CONTACTS_GROUP, f"""Контакты от @{message.from_user.username}: {contact}""")