from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie 

from app.config import (
    settings, 
    logger
)
from app.models import (
    User,
    Habit,
    Track
)


async def init_db():
    try:
        client = AsyncIOMotorClient(settings.MONGO_URL)

        await init_beanie(
            database = client[settings.DATABASE_NAME],  # type: ignore
            document_models = [User, Habit, Track]
        )
    except Exception as error:
        logger.critical(f"Database Initialization Failed: {error}", exc_info = True)
        raise error
