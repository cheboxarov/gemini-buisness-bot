from core import dp, bot
from filters import CallbackAdminOnly, CallbackDataFilter
from aiogram import types
from aiogram.fsm.context import FSMContext
from db.prompt_manager import db_prompt_manager
from utils import split_by_length
import json


@dp.callback_query(CallbackAdminOnly(), CallbackDataFilter(expected_data="admin-menu"))
async def admin_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    markup_buttons = [
        [types.InlineKeyboardButton(text="Сбросить промпт", callback_data="admin-reset-prompt")],
        [types.InlineKeyboardButton(text="Получить промпт", callback_data="admin-get-prompt")]
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)
    await bot.send_message(callback.from_user.id, "Админ панель", reply_markup=markup)
    await callback.answer()

@dp.callback_query(CallbackAdminOnly(), CallbackDataFilter(expected_data="admin-reset-prompt"))
async def admin_reset_prompt_handler(callback: types.CallbackQuery, state: FSMContext):
    await db_prompt_manager.reset_prompt("default_prompt.json")
    await callback.answer("Промпт сброшен")

@dp.callback_query(CallbackAdminOnly(), CallbackDataFilter(expected_data="admin-get-prompt"))
async def admin_get_prompt_handler(callback: types.CallbackQuery, state: FSMContext):
    prompt = await db_prompt_manager.get()
    prompt_str = json.dumps(prompt, ensure_ascii=False)
    prompt_str_chunks = split_by_length(prompt_str, 500)
    for chunk in prompt_str_chunks:
        await bot.send_message(callback.from_user.id, chunk)