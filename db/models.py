from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Boolean, TIMESTAMP
from sqlalchemy.orm import declarative_base
from core import bot

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    tg_id = Column(BigInteger, unique=True, index=True)
    is_admin = Column(Boolean, default=False)
    contacts_received = Column(Boolean, default=False)
    next_contacts_question_date = Column(TIMESTAMP, nullable=True)
    

    async def send_message(self, message):
        await bot.send_message(self.tg_id, message)


class PromptElement(Base):
    __tablename__ = "prompt"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    user_question = Column(String)
    model_answer = Column(String)
