import dotenv
import os


dotenv.load_dotenv()

# К примеру postgresql+asyncpg://username:password@localhost/dbname
DATABASE_URL = os.getenv("DATABASE_URL")
