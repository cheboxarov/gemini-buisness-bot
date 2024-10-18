from .core import DataBaseManager
from sqlalchemy.future import select
from .models import User
from loguru import logger
from schemas import UserScheme
from sqlalchemy.exc import IntegrityError, NoResultFound


class UsersManager(DataBaseManager):

    def __init__(self):
        super().__init__()

    async def get(self, filters: dict) -> User | None:
        async with self.async_session() as session:
            try:
                query = select(User)
                for attr, value in filters.items():
                    query = query.where(getattr(User, attr) == value)
                result = await session.execute(query)
                user = result.scalars().one()
                return user
            except NoResultFound as err:
                return None
            except Exception as err:
                logger.error(f"Error to get user: {err}") 
                return None

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        return await self.get(filters={"tg_id": tg_id})
    
    async def get_or_create(self, user_schema: UserScheme) -> User:
        user = await self.get_by_tg_id(user_schema.tg_id)
        if user is not None:
            return user
        user = await self.create(user_schema)
        return user

    async def all(self, filters: dict = None) -> list[User]:
        async with self.async_session() as session:
            try:
                query = select(User)
                if filters:
                    for attr, value in filters.items():
                        query = query.where(getattr(User, attr) == value)
                result = await session.execute(query)
                users = result.scalar().all()
                return users
            except Exception as err:
                logger.error(f"error to get users: {err}")
                return []

    async def admins(self) -> list[User]:
        return await self.all(filters={"is_admin": True})

    async def create(self, user: UserScheme) -> User | None:
        user_data = user.model_dump()
        async with self.async_session() as session:
            new_user = User(**user_data)
            session.add(new_user)
            try:
                await session.commit()
                return new_user
            except IntegrityError as error:
                await session.rollback()
                logger.error(f"Error to create user: {error}")
                return None


db_users_manager = UsersManager()
