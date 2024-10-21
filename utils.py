from schemas import UserScheme

async def get_user_scheme_from_user(from_user) -> UserScheme:
    return UserScheme(
        tg_id=from_user.id,
        username=from_user.username,
        is_admin=True
    )

def split_by_length(text: str, length: int) -> list[str]:
    """Разделяет строку на части заданной длины."""
    return [text[i:i + length] for i in range(0, len(text), length)]

def delete_markdown(text: str) -> str:
    return text.replace("*", "").replace("[", "").replace("]", "").replace("#", "")