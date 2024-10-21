from core import dp, bot
from filters import CallbackAdminOnly, CallbackDataFilter
from aiogram import types
from aiogram.fsm.context import FSMContext
from db.prompt_manager import db_prompt_manager
from utils import split_by_length
import json
from .gemini_analyze import gemini_update_prompt


@dp.callback_query(CallbackAdminOnly(), CallbackDataFilter(expected_data="admin-menu"))
async def admin_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    markup_buttons = [
        [types.InlineKeyboardButton(text="Сбросить промпт", callback_data="admin-reset-prompt")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)
    await bot.send_message(callback.from_user.id, "Админ панель", reply_markup=markup)
    await callback.answer()

@dp.callback_query(CallbackAdminOnly(), CallbackDataFilter(expected_data="admin-reset-prompt"))
async def admin_reset_prompt_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        await gemini_update_prompt()
        await callback.answer("Промпт обновлен")
    except:
        await callback.answer("Ошибка при обновлении промпта")