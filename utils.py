from schemas import UserScheme
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey


async def get_user_scheme_from_user(from_user) -> UserScheme:
    return UserScheme(
        tg_id=from_user.id,
        username=from_user.username,
        is_admin=False
    )

def split_by_length(text: str, length: int) -> list[str]:
    """Разделяет строку на части заданной длины."""
    return [text[i:i + length] for i in range(0, len(text), length)]

def delete_markdown(text: str) -> str:
    return text.replace("*", "").replace("[", "").replace("]", "").replace("#", "")

async def get_state_by_user_id(user_id: int, bot, dp) -> FSMContext:
    return FSMContext(
        storage=dp.storage,
        key=StorageKey(
            chat_id=user_id,
            user_id=user_id,
            bot_id=bot.id
        )
    )