from beanie import BeanieObjectId
from fastapi import (
    HTTPException,
    status
)

from app.config import logger
from app.models import Streak
from app.schemas import (
    CurrentStreakOut,
    BestStreakOut
)




async def get_current_streak_service(
    owner_id:   BeanieObjectId,
    habit_id:   BeanieObjectId
) -> CurrentStreakOut:

    try:
        streak: Streak | None = await Streak.find_one(
            Streak.owner_id == owner_id,
            Streak.habit_id == habit_id
        )

        if not streak:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Streak not found"
            )
        
        return CurrentStreakOut(
            owner_id = owner_id,
            habit_id = habit_id,
            current_streak = streak.current_streak,
            start_date = streak.start_date,
            last_tracked = streak.last_tracked,
            status = streak.status,
            created_at = streak.created_at,
            updated_at = streak.updated_at
        )
        
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_current_streak_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_best_streak_service(
    owner_id: BeanieObjectId,
    habit_id: BeanieObjectId
) -> BestStreakOut:
    
    try:
        streak: Streak | None = await Streak.find_one(
            Streak.owner_id == owner_id,
            Streak.habit_id == habit_id
        )

        if not streak:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Streak not found"
            )
        
        return BestStreakOut(
            owner_id = owner_id,
            habit_id = habit_id,
            best_streak = streak.best_streak,
            status = streak.status,
            created_at = streak.created_at,
            updated_at = streak.updated_at
        )
          
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_best_streak_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )