from aiogram.fsm.context import FSMContext
from core import bot
from loguru import logger
from ai.gemini import GeminiClient
import ai.config as gemini_config
from utils import split_by_length, delete_markdown
from .get_contacts import get_contacts


async def start_gemini_analyze(user_id: int, letters: str, state: FSMContext):
    logger.debug(f"Начинаю обработку писем: {letters[:50]}")
    gemini_client = GeminiClient(gemini_config.COOKIES, gemini_config.HEADERS, gemini_config.GEMINI_API_KEY, gemini_config.PROMPT)
    await gemini_client.get_or_load_prompt()
    answer = await gemini_client.ask_to_prompt(letters)
    answers = split_by_length(answer, 3000)
    for ans in answers:
        await bot.send_message(user_id, text=delete_markdown(ans))
    await get_contacts(user_id, state)
    
async def gemini_update_prompt():
    gemini_client = GeminiClient(gemini_config.COOKIES, gemini_config.HEADERS, gemini_config.GEMINI_API_KEY, gemini_config.PROMPT)
    if len(await gemini_client.get_prompt(gemini_config.PROMPT)) == 0:
        raise ValueError("Cant get prompt")
    gemini_client.save_prompt_to_json()