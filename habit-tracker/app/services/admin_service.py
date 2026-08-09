from typing import (
    List, 
    Any, 
    Dict
)
from beanie import BeanieObjectId
from fastapi import (
    HTTPException,
    status
)

from app.utils import paginate
from app.config import logger
from app.models import (
    User, 
    Habit,
    Streak
)
from app.schemas import AppStatsOut




async def get_all_users_service(
    is_active:  bool = False, 
    page:       int = 1, 
    limit:      int = 10
) -> List[User]:

    try:
        skip, limit_val = paginate(page, limit)
        
        query: Dict[str, Any] = {}

        if is_active:
            query["status"] = "active"

        return await User.find(query).skip(skip).limit(limit_val).to_list()
    
    except Exception as exc:
        logger.error(f"Unexpected error in get_all_users_service: {exc}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_user_service(
    user_id:    BeanieObjectId
) -> User:
    
    try: 

        user: User | None = await User.get(user_id)

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        return user
    
    except HTTPException:
        raise
    
    except Exception as exc:
        logger.error(f"Unexpected error in get_user_service: {exc}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def block_user_service(
    user_id:    BeanieObjectId
) -> User:
    
    try:
        user: User | None = await User.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        await user.set({"status": "block"})

        return user
        
    except HTTPException:
        raise
        
    except Exception as exc:
        logger.error(f"Unexpected error in block_user_service: {exc}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    



async def get_all_habits_service(
    owner_id:   BeanieObjectId | None = None, 
    category:   str | None = None,
    page:       int = 1, 
    limit:      int = 10
) -> List[Habit]:
    
    try:
        skip, limit_val = paginate(page, limit)
        
        query: Dict[str, Any] = {}
        
        if owner_id is not None:
            query["owner_id"] = owner_id
        
        if category:
            query["category"] = category

        return await Habit.find(query).skip(skip).limit(limit_val).sort("+created_at").to_list()
    
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_all_habits_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_app_stats_service() -> AppStatsOut:

    try:

        total_users = await User.count()

        active_users = await User.find(User.status == "active" ).count()

        total_habits = await Habit.count()

        total_streaks = await Streak.count()

        return AppStatsOut(
            total_users = total_users,
            active_users = active_users,
            total_habits = total_habits,
            total_streaks = total_streaks
        )
    
    except HTTPException:
        raise
        
    except Exception as exc:
        logger.error(f"Unexpected error in get_app_stats_service: {exc}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    