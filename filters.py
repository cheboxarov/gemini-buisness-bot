from aiogram import types
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from utils import get_user_scheme_from_user
from db.users_manager import db_users_manager


class ContextValueFilter(BaseFilter):
    def __init__(self, key: str, expected_value: str):
        self.key = key
        self.expected_value = expected_value

    async def __call__(self, message: types.Message, state: FSMContext) -> bool:
        data = await state.get_data()
        return data.get(self.key) == self.expected_value


class CallbackDataFilter(BaseFilter):
    def __init__(self, expected_data: str):
        self.expected_data = expected_data

    async def __call__(self, callback_query: types.CallbackQuery) -> bool:
        return callback_query.data == self.expected_data


class CallbackAdminOnly(BaseFilter):

    async def __call__(self, callback_query: types.CallbackQuery) -> bool:
        user = await db_users_manager.get_or_create(await get_user_scheme_from_user(callback_query.from_user))
        return user.is_admin