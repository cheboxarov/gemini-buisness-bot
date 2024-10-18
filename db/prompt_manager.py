from .core import DataBaseManager
from sqlalchemy.future import select
from .models import PromptElement
from loguru import logger
import json
from sqlalchemy import text


class PromptManager(DataBaseManager):

    async def get(self) -> list[dict[str, str | list[str]]] | None:
        async with self.async_session() as session:
            try:
                query = select(PromptElement)
                result = await session.execute(query)
                prompt_elements = result.scalars().all()
                prompt = []
                for element in prompt_elements:
                    prompt.append({
                        "role": "user",
                        "parts": [
                            element.user_question
                        ]
                    })
                    prompt.append({
                        "role": "model",
                        "parts": [
                            element.model_answer
                        ]
                    })
                return prompt
            except Exception as err:
                logger.error(f"Error to get prompt: {err}")
                return None

    async def reset_prompt(self, file_path: str):
        async with self.async_session() as session:
            try:
                await session.execute(text("DELETE FROM prompt"))
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    prompts = json.load(file)
                user_question = None
                model_answer = None
                for item in prompts:
                    if user_question is None:
                        user_question = item['parts'][0] if item['role'] == 'user' else None
                    if model_answer is None:
                        model_answer = item['parts'][0] if item['role'] == 'model' else None
                    if user_question is not None and model_answer is not None:
                        prompt_element = PromptElement(user_question=user_question, model_answer=model_answer)
                        user_question = None
                        model_answer = None
                        session.add(prompt_element)

                await session.commit()
                logger.info("Prompt reset successfully.")
            except Exception as err:
                logger.error(f"Error resetting prompt: {err}")

    async def add(self, role: str, content: str):
        if role not in ["user", "model"]:
            raise ValueError("Role must be either 'user' or 'model'")
        
        async with self.async_session() as session:
            try:
                if role == "user":
                    prompt_element = PromptElement(user_question=content)
                else:
                    prompt_element = PromptElement(model_answer=content)
                
                session.add(prompt_element)
                await session.commit()
                logger.info("Prompt element added successfully.")
            except Exception as err:
                logger.error(f"Error adding prompt element: {err}")


db_prompt_manager = PromptManager()