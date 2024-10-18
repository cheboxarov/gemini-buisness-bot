from core import dp
from aiogram.types import Message, CallbackQuery
from loguru import logger
from aiogram.fsm.context import FSMContext
from filters import ContextValueFilter, CallbackDataFilter
import brief
from core import bot
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from .letters import letters_start
import messages


@dp.callback_query(CallbackDataFilter(expected_data="start_brief"))
async def brief_start_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(status="brief")
    await state.update_data(question_index=0)
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        brief.BRIEF_QUESTIONS[0],
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Остановить бриф")]], resize_keyboard=True
        ),
    )


@dp.message(ContextValueFilter(key="status", expected_value="brief"))
async def brief_handler(message: Message, state: FSMContext):

    if message.text == "Остановить бриф":
        await message.answer(
            messages.BRIEF_STOP,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Начать заново", callback_data="start_brief"
                        )
                    ]
                ]
            ),
        )
        await message.delete()
        await state.clear()
        return

    data = await state.get_data()
    question_index = data.get("question_index", 1)
    await state.update_data({f"brief_answer_{question_index}": message.text})
    next_question_index = question_index + 1

    answers = await state.get_data()
    result_message = "\n".join(
        [
            f"{val}: {answers.get(f'brief_answer_{i}', 'NONE')}"
            for i, val in enumerate(brief.BRIEF_QUESTIONS)
        ]
    )
    logger.debug(
        f"New message in brief brief from {message.from_user.username}, message text: {message.text}\nStep: {question_index}\nAnswers:\n{result_message}"
    )

    if next_question_index < len(brief.BRIEF_QUESTIONS):
        await state.update_data(question_index=next_question_index)
        await message.answer(brief.BRIEF_QUESTIONS[next_question_index])
    else:
        answers = await state.get_data()
        result_message = "\n".join(
            [
                f"{val}: {answers.get(f'brief_answer_{i}', 'NONE')}"
                for i, val in enumerate(brief.BRIEF_QUESTIONS)
            ]
        )
        await message.answer(result_message)
        await state.update_data(status="letters")
        await letters_start(message.from_user.id)
