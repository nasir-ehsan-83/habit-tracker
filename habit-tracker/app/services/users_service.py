from typing import (
    List, 
    Tuple
)
from fastapi import (
    HTTPException, 
    Response, 
    status
)
from datetime import (
    datetime, 
    timezone
)
from beanie import BeanieObjectId

from app.core import hash_password
from app.config import logger 
from app.models import (
    User,
    Habit,
    UserPreference
)
from app.schemas import UserUpdate
from app.services.habits_service import get_all_habits_service



async def get_user(
    id: BeanieObjectId
) -> User:
    try:

        user = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, 
                detail = "User not found"
            )
        
        return user
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_user: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_user(
    id:     BeanieObjectId, 
    data:   UserUpdate
) -> User:
    
    try:
        user = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        update_data = data.model_dump(
            exclude_unset = True, 
            exclude_none = True
        )
        
        if "password" in update_data:
            update_data["password"] = await hash_password(update_data["password"])

        update_data["updated_at"] = datetime.now(timezone.utc)

        await user.set({ 
            **update_data
        })
        
        await user.sync()
        return user
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in update_user: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_avatar(
    id:     BeanieObjectId,
    url:    str
) -> User:
    
    try:

        user = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        await user.set({
            "vavatar": url
        })
        await user.sync()

        return user

    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in update_avatar: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    


    
async def get_stats_service(
    id:     BeanieObjectId
) -> Tuple[User, List[Habit]]:
    
    try:
        user = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        habits: List[Habit] = await get_all_habits_service(id)

        return user, habits
    

    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_stats: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_preference_service(
    owner_id: BeanieObjectId
) -> UserPreference:
    try:
        preference = await UserPreference.find_one(UserPreference.owner_id == owner_id)

        if not preference:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User preferences not found"
            )

        return preference

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in get_preference: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )