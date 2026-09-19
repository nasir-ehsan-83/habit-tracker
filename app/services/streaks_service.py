from beanie import BeanieObjectId
from fastapi import (
    HTTPException,
    status
)
from datetime import date

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

    """Retrieves the current active streak for a specific habit.

    This service calculates and returns the user's current consecutive
    completion streak for a given habit. The streak is counted from the
    most recent completion day, going backward in time.

    Args:
        owner_id: The MongoDB ObjectId of the user owning the streak.
        habit_id: The MongoDB ObjectId of the habit to check.

    Returns:
        CurrentStreakOut: Current streak informations
        
    Raises:
        HTTPException 404: If no streak record is found for the habit.
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """

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
    
    """Retrieves the user's all-time best streak for a specific habit.

    This service calculates and returns the user's longest consecutive
    completion streak ever achieved for a given habit. This represents
    the user's personal best performance.

    Args:
        owner_id: The MongoDB ObjectId of the user owning the streak.
        habit_id: The MongoDB ObjectId of the habit to check.

    Returns:
        BestStreakOut: Best streak informations

    Raises:
        HTTPException 404: If no streak record is found for the habit.
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """
    
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




async def update_streak_service(
    owner_id:   BeanieObjectId,
    habit_id:   BeanieObjectId,
    track_date: date
) -> None:
    
    """Updates or creates a streak record for a habit track.

    This service is called whenever a user tracks a habit completion.
    It updates the user's streak based on the completion date, handling
    continuation, reset, or creation of streaks.

    **Streak Logic:**
    - If no streak exists: Creates a new streak with count = 1
    - If track_date is consecutive (1 day after last_tracked): Increments streak
    - If track_date has a gap (>1 day difference): Resets streak to 1
    - If track_date is the same day: No changes made

    Args:
        owner_id: The MongoDB ObjectId of the user.
        habit_id: The MongoDB ObjectId of the habit being tracked.
        track_date: The date of the habit completion.

    Returns:
        None: This service updates the database but doesn't return data.

    Raises:
        HTTPException 500: If an internal server error occurs during 
            database operations.

    Note:
        This service is typically called automatically when a track is created
        and should not be exposed directly as an API endpoint.
    """
    
    try:
        streak: Streak | None = await Streak.find_one({
            "owner_id": owner_id,
            "habit_id": habit_id
        })
        
        if not streak:
            new_streak = Streak(
                owner_id = owner_id,
                habit_id = habit_id,
                current_streak = 1,
                longest_streak = 1,
                start_date = track_date,
                last_tracked = track_date,
                status = "active"
            )
            await new_streak.insert() # type: ignore
            return
        
        day_diff: int
        
        if streak.last_tracked:
            day_diff = (track_date - streak.last_tracked).days
        else:
            day_diff = 1
        
        if day_diff == 1:
            streak.current_streak += 1
            streak.last_tracked = track_date
            
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
                
        elif day_diff > 1:
            streak.current_streak = 1
            streak.start_date = track_date
            streak.last_tracked = track_date
            
        else:
            return
        
        await streak.save() # type: ignore
        
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in update_streak_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )