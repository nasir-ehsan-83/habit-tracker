from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config.config import settings
from app.models.users import User
from app.models.habits import Habit
from app.config.logging import logger 

# Provide connection with MongoDB
async def init_db():
    try:
        client = AsyncIOMotorClient(settings.MONGO_URL)

        await init_beanie(
            database = client[settings.DATABASE_NAME],
            document_models = [User, Habit]
        )
    except Exception as error:
        logger.critical(f"Database Initialization Failed: {error}", exc_info = True)
        raise error
