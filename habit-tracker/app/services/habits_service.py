from typing import List
from fastapi import (
    HTTPException, 
    Response, 
    status
)
from beanie import BeanieObjectId
from pymongo.errors import DuplicateKeyError
from datetime import (
    datetime,
    timezone
)
from app.models.habits import Habit
from app.schemas.habits import (
    HabitCreate, 
    HabitUpdate
)
from app.config.logging_handler import logger
from app.schemas.token import TokenData
from app.utils.pagination import paginate


async def create_new_habit(
    habit_in: HabitCreate, 
    current_user: TokenData
) -> Habit:
    try:
        # Check if the habit already exists for this specific owner
        found_habit: Habit | None = await Habit.find_one(
            Habit.name == habit_in.name,
            Habit.owner_id == BeanieObjectId(current_user.id),
            Habit.status != "deleted"
        )
        
        if found_habit:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Habit already exists"
            )
        if found_habit:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Habit already exists"
            )
        
        new_habit: Habit = Habit(
            **habit_in.model_dump(),
            owner_id = BeanieObjectId(current_user.id)
        )

        return await new_habit.insert()

    except HTTPException:
        raise
    
    except DuplicateKeyError as error:
        logger.error(f"Duplicate Key Error while creating habit: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Conflict: A habit with this name already exists for this user."
        )
    except Exception as error:
        logger.error(f"Unexpected error in create_new_habit: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_all_habits_owner(
    current_user: TokenData, 
    page: int = 1, 
    limit: int = 10
) -> List[Habit]:
    try:
        # Calculate skip and limit values
        skip, limit_val = paginate(page, limit)

        # Retrieve active habits belonging to the current user
        habits: List[Habit] = await Habit.find_all(
            Habit.owner_id == BeanieObjectId(current_user.id), 
            Habit.status != "deleted"
        ).skip(skip).limit(limit_val).to_list()

        return habits

    except Exception as error:
        logger.error(f"Unexpected error in get_all_habits_owner: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_all_habits_admin(
    owner_id:BeanieObjectId | None = None, 
    page: int = 1, 
    limit: int = 10
) -> List[Habit]:
    try:
        # Calculate skip and limit values
        skip, limit_val = paginate(page, limit)
        
        if owner_id is not None:
            return await Habit.find_all(
                Habit.owner_id == owner_id
            ).skip(skip).limit(limit_val).to_list()

        # Retrieve all habits across all users
        return await Habit.find_all().skip(skip).limit(limit_val).to_list()
    
    except Exception as error:
        logger.error(f"Unexpected error in get_all_habits_admin: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_habit_by_name(
    name: str, 
    current_user: TokenData
) -> Habit:
    try:
        # Retrieve habit by name and specific owner
        existing_habit = await Habit.find_one(
            Habit.name == name,
            Habit.owner_id == BeanieObjectId(current_user.id),
            Habit.status != "deleted"   
        )

        if not existing_habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        return existing_habit
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_habit_by_name: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_habit_by_name(
    name: str, 
    update_habit: HabitUpdate, 
    current_user: TokenData
) -> Habit:
    try:
        # Fetch specific habit from database
        existing_habit = await Habit.find_one(
            Habit.name == name,
            Habit.owner_id == BeanieObjectId(current_user.id),
            Habit.status != "deleted"
        )

        if not existing_habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        # Delete undefined or null values
        update_data = update_habit.model_dump(
            exclude_unset = True, 
            exclude_none = True
        )

        update_data.update({
            "updated_at": datetime.now(timezone.utc)
        })
        
        # Update habit and store changes in the database
        await existing_habit.update({
            "$set": update_data
        })
        
        # Sync local object fields with database changes
        await existing_habit.sync()
        
        return existing_habit
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in update_habit_by_name: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )    




async def delete_habit_by_name(
    name: str, 
    current_user: TokenData
) -> Response:
    try:
        # Fetch specific habit from database
        existing_habit = await Habit.find_one(
            Habit.name == name,
            Habit.owner_id == BeanieObjectId(current_user.id),
            Habit.status != "deleted"
        )
        
        if not existing_habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        # Perform soft-deletion
        await existing_habit.update({
            "$set": {
                "status": "deleted"
            }
        })

        return Response(status_code = status.HTTP_204_NO_CONTENT)
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in delete_habit_by_name: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )