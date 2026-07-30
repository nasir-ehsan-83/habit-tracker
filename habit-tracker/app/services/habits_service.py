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

        return await new_habit.insert() # type: ignore

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




async def get_all_habits(
    id: BeanieObjectId, 
    category: str = "",
    completed: bool = False,
    page: int = 1, 
    limit: int = 10
) -> List[Habit]:
    try:
        
        skip, limit_val = paginate(page, limit)

        habits: List[Habit]

        if completed:
            habits: List[Habit] = await Habit.find_all(
                Habit.owner_id == BeanieObjectId(id), 
                Habit.status == "completed",
                Habit.category == category # type: ignore
            ).skip(skip).limit(limit_val).sort("created_at").to_list() # type: ignore

        else:
            habits: List[Habit] = await Habit.find_all(
                Habit.owner_id == BeanieObjectId(id), 
                Habit.status != "deleted"
            ).skip(skip).limit(limit_val).sort("created_at").to_list()
        
        return habits

    except Exception as error:
        logger.error(f"Unexpected error in get_all_habits_owner: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_habit(
    id: BeanieObjectId, 
    current_user: TokenData
) -> Habit:
    try:
        
        existing_habit = await Habit.find_one(
            Habit.id == BeanieObjectId(id),
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




async def update_habit(
    id: BeanieObjectId, 
    update_habit: HabitUpdate, 
    current_user: TokenData
) -> Habit:
    try:
        
        existing_habit = await Habit.find_one(
            Habit._class_id == BeanieObjectId(id),
            Habit.owner_id == BeanieObjectId(current_user.id),
            Habit.status != "deleted"
        )

        if not existing_habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        update_data = update_habit.model_dump(
            exclude_unset = True, 
            exclude_none = True
        )

        update_data.update({
            "updated_at": datetime.now(timezone.utc)
        })
        
        await existing_habit.update({
            "$set": update_data
        })
        
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




async def delete_habit(
    id: BeanieObjectId, 
    current_user: TokenData
) -> Response:
    try:
    
        existing_habit = await Habit.find_one(
            Habit.id == BeanieObjectId(id),
            Habit.owner_id == BeanieObjectId(current_user.id),
            Habit.status != "deleted"
        )
        
        if not existing_habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
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