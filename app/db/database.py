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
    """Initialize database connection with Beanie ODM.

    Creates a MongoDB connection using settings.MONGO_URL and initializes
    Beanie with the defined document models (User, Habit, Track).

    Raises:
        Exception: If database connection or initialization fails.
    """
    try:
        client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_URL)

        await init_beanie(
            database = client[settings.DATABASE_NAME],  # type: ignore
            document_models = [User, Habit, Track]
        )

        logger.info("Database initialized successfully")

    except Exception as error:
        logger.critical(f"Database Initialization Failed: {error}", exc_info = True)
        
        raise error