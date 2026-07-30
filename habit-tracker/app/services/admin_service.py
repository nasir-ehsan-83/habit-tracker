from typing import List
from beanie import BeanieObjectId
from fastapi import (
    HTTPException,
    status
)
from app.models.habits import Habit
from app.models.users import User
from app.utils.pagination import paginate
from app.config.logging_handler import logger




async def get_all_users(
    is_active: bool = False, 
    page: int = 1, 
    limit: int = 10
) -> List[User]:

    try:
        skip, limit_val = paginate(page, limit)

        if is_active:
            return await User.find_all(skip = skip, limit = limit_val, pymongo_kwargs = {"status": "active"}).to_list()
        
        return await User.find_all(skip = skip, limit = limit_val).to_list()
    
    except Exception as exc:
        logger.error(f"Unexpected error in get_all_users: {exc}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_one_user(
    user_id: BeanieObjectId
) -> User:
    
    try: 

        user: User | None = await User.find_one(User.id == BeanieObjectId(user_id))

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not Found"
            )
        
        return user
    
    except Exception as exc:
        logger.error(f"Unexpected error in get_all_users: {exc}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def block_user(
    user_id: BeanieObjectId
) -> User:
    
    try:
        user: User | None = await User.find_one(User.id == BeanieObjectId(user_id))
        
        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        await user.update({
            "$set": {
                "status": "block"
            }
        })
        await user.sync()

        return user
        
    

        
    except Exception as exc:
        logger.error(f"Unexpected error in get_all_users: {exc}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    



async def get_all_habits(
    owner_id:BeanieObjectId | None = None, 
    category: str = "",
    page: int = 1, 
    limit: int = 10
) -> List[Habit]:
    try:
        
        skip, limit_val = paginate(page, limit)
        
        if owner_id is not None:
            return await Habit.find_all(
                Habit.owner_id == owner_id,
                Habit.category == category
            ).skip(skip).limit(limit_val).sort("created_at").to_list()


        return await Habit.find_all(
            Habit.category == category
        ).skip(skip).limit(limit_val).sort("created_at").to_list()
    
    except Exception as error:
        logger.error(f"Unexpected error in get_all_habits_admin: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
