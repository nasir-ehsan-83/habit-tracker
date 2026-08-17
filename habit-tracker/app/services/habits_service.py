from typing import (
    Any, 
    Dict, 
    List
)
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
from app.models import (
    Habit,
    Streak
)
from app.schemas import (
    HabitCreate, 
    HabitUpdate
)
from app.config import logger
from app.utils.enum import HabitCategory
from app.utils import paginate



async def create_habit_service(
    habit_in:   HabitCreate, 
    owner_id:   BeanieObjectId
) -> Habit:
    try:
        
        found_habit: Habit | None = await Habit.find_one(
            Habit.name == habit_in.name,
            Habit.owner_id == owner_id,
            Habit.status != "deleted"
        )
        
        if found_habit:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Habit already exists"
            )
        
        new_habit: Habit = Habit(
            **habit_in.model_dump(),
            owner_id = owner_id
        )

        await new_habit.insert() # type: ignore

        new_streak: Streak = Streak(
            owner_id = owner_id,
            habit_id = BeanieObjectId(new_habit.id )
        )

        await new_streak.insert() # type: ignore

        return new_habit

    except HTTPException:
        raise
    
    except DuplicateKeyError as error:
        logger.error(f"Duplicate Key Error while creating habit: {error}", exc_info = True)
       
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Conflict: A habit with this name already exists for this user."
        )
    
    except Exception as error:
        logger.error(f"Unexpected error in create_habit_service: {error}", exc_info = True)
       
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_all_habits_service(
    owner_id:   BeanieObjectId, 
    category:   HabitCategory | str = "",
    completed:  bool = False,
    page:       int = 1, 
    limit:      int = 10
) -> List[Habit]:
    try:
        
        skip, limit_val = paginate(page, limit)

        query: Dict[str, Any] = {
            "owner_d": owner_id,
            "status": "deleted",
            "category": category
        }

        if completed:
            query["status"] = "completed"
        
        return await Habit.find(query).skip(skip).limit(limit_val).sort("+created_at").to_list()

    except Exception as error:
        logger.error(f"Unexpected error in get_all_habits_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_habit_service(
    habit_id:   BeanieObjectId,
    owner_id:   BeanieObjectId
) -> Habit:
    try:
        
        existing_habit = await Habit.find_one(
            Habit.id == habit_id,
            Habit.owner_id == owner_id,
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
        logger.error(f"Unexpected error in get_habit_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_habits_by_category_service(
    owner_id:       BeanieObjectId,
    category:       HabitCategory
) -> List[Habit]:
    
    try:
        
        return await Habit.find(
            Habit.owner_id == owner_id, 
            Habit.status != "deleted",
            Habit.category == category
        ).sort("created_at").to_list()

    except Exception as error:
        logger.error(f"Unexpected error in get_habit_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )





async def update_habit_service(
    habit_id:             BeanieObjectId, 
    owner_id:             BeanieObjectId,
    update_habit:   HabitUpdate,
) -> Habit:
    try:
        
        existing_habit = await Habit.find_one(
            Habit._class_id == habit_id,
            Habit.owner_id == owner_id,
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
        
        await existing_habit.set(**update_data)
        
        await existing_habit.sync()
        
        return existing_habit
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in update_habit_service: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )    




async def delete_habit_service(
    habit_id:   BeanieObjectId,
    owner_id:   BeanieObjectId
) -> Response:
    try:
    
        existing_habit = await Habit.find_one(
            Habit.id == habit_id,
            Habit.owner_id == owner_id,
            Habit.status != "deleted"
        )
        
        if not existing_habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        await existing_habit.set({
            "status": "deleted"
        })

        return Response(status_code = status.HTTP_204_NO_CONTENT)
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in delete_habit_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    



async def archive_habit_service(
    habit_id:   BeanieObjectId,
    owner_id:   BeanieObjectId
) -> Dict[str, str]:
    
    try:

        habit = await Habit.find_one(
            Habit.id == habit_id,
            Habit.owner_id == owner_id,
            Habit.status != "deleted"
        )
        
        if not habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        await habit.set({
            "status": "archived"
        })

        return {
            "message": "Habit archived successfully"
        }

    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in archive_habit_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    



async def unarchive_habit_service(
    habit_id:   BeanieObjectId,
    owner_id:   BeanieObjectId
) -> Dict[str, str]:
    
    try:
        habit = await Habit.find_one(
            Habit.id == habit_id,
            Habit.owner_id == owner_id,
            Habit.status != "archived"
        )
        
        if not habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        await habit.set({
            "status": "active"
        })
     
        return {
            "message": "Habit archived successfully"
        }
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in unarchive_habit_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )   




async def get_archived_habits_service(
    owner_id:   BeanieObjectId,
    page:       int,
    limit:      int
) -> List[Habit]:

    try:

        skip, limit_val = paginate(page, limit)

        return await Habit.find(
            Habit.owner_id == owner_id,
            Habit.status == "archived"
        ).skip(skip).limit(limit_val).sort("+created_at").to_list()

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )