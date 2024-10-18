from core import dp
from aiogram.types import Message, CallbackQuery
from loguru import logger
from aiogram.fsm.context import FSMContext
from filters import ContextValueFilter, CallbackDataFilter
from core import bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from messages import (
    LETTERS_START_MESSAGE,
    LETTERS_FINISH_MESSAGE,
    LETTERS_ANSWER_VARIANTS,
)
from random import choice


async def letters_start(user_id: int):
    await bot.send_message(user_id, LETTERS_START_MESSAGE)


@dp.callback_query(CallbackDataFilter(expected_data="stop_letters"))
async def stop_letters_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    if data.get("status", "") != "letters":
        return
    await bot.send_message(callback.from_user.id, LETTERS_FINISH_MESSAGE)
    state.update_data(status="none")
    logger.debug(f"letters receiving is stopped, data: {data}")


@dp.message(ContextValueFilter(key="status", expected_value="letters"))
async def letters_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    letters: list[str] = data.get("letters", [])
    letters.append(message.text)
    await state.update_data(letters=letters)
    logger.debug(
        f"New message in letters from {message.from_user.username}, message text: {message.text}\nLetters: {'\n'.join(letters)}"
    )

    await message.answer(
        text=choice(LETTERS_ANSWER_VARIANTS),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Готово", callback_data="stop_letters")]
            ]
        ),
    )
