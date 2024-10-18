from pydantic import BaseModel
from typing import Optional


class UserScheme(BaseModel):
    tg_id: int
    username: str
    is_admin: Optional[bool] = False