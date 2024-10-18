from aiogram import Bot, Dispatcher
import dotenv
import os

dotenv.load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
