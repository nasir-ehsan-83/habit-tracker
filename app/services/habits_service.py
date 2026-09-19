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
    
    """Creates a new habit for the authenticated user.

    This service creates a new habit with the provided details and also
    initializes a streak record for tracking habit consistency.

    Args:
        habit_in: Habit creation data 

    Returns:
        Habit: The created habit object with all fields populated.

    Raises:
        HTTPException 400: If a habit with the same name already exists.
        HTTPException 409: If a duplicate key conflict occurs.
        HTTPException 500: If an internal server error occurs.
    """
    
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
    
    """Retrieves all habits for a user with optional filtering.

    This service returns a paginated list of a user's habits with support
    for filtering by category and completion status.

    Args:
        owner_id: The MongoDB ObjectId of the user whose habits to retrieve.
        category: Optional category filter (e.g., HEALTH, SPORT, STUDY).
        completed: If True, filters to only completed habits.
        page: Page number for pagination (starts from 1).
        limit: Maximum number of habits to return per page.

    Returns:
        List[Habit]: A list of habit objects matching the query criteria,
            sorted by creation date ascending.

    Raises:
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """
    
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
    
    """Retrieves a specific habit by its ID for a user.

    This service fetches a single habit that belongs to the specified user
    and is not marked as deleted.

    Args:
        habit_id: The MongoDB ObjectId of the habit to retrieve.
        owner_id: The MongoDB ObjectId of the user owning the habit.

    Returns:
        Habit: The habit object with all details.

    Raises:
        HTTPException 404: If habit is not found or doesn't belong to user.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        
        existing_habit: Habit | None = await Habit.find_one(
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
    
    """Retrieves all habits belonging to a specific category.

    This service returns all active habits (not deleted) for a user that
    belong to the specified category.

    Args:
        owner_id: The MongoDB ObjectId of the user whose habits to retrieve.
        category: The category to filter habits by.

    Returns:
        List[Habit]: A list of habit objects in the specified category,
            sorted by creation date ascending.

    Raises:
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """
    
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
    
    """Updates an existing habit with new information.

    This service allows users to update their habit details including
    name, category, description, target count, and other settings.

    Args:
        habit_id: The MongoDB ObjectId of the habit to update.
        owner_id: The MongoDB ObjectId of the user owning the habit.
        update_habit: Habit update data(all optional)

    Returns:
        Habit: The updated habit object with all fields.

    Raises:
        HTTPException 404: If habit is not found or doesn't belong to user.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        
        existing_habit: Habit | None = await Habit.find_one(
            Habit._class_id == habit_id,
            Habit.owner_id == owner_id,
            Habit.status != "deleted"
        )

        if not existing_habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        update_data: Dict[str, Any] = update_habit.model_dump(
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
    
    """Permanently deletes a habit (soft delete).

    This service marks a habit as deleted by updating its status to 'deleted'.
    The habit remains in the database but is excluded from most queries.

    Args:
        habit_id: The MongoDB ObjectId of the habit to delete.
        owner_id: The MongoDB ObjectId of the user owning the habit.

    Returns:
        Response: Empty response with status code 204 (No Content) on success.

    Raises:
        HTTPException 404: If habit is not found or doesn't belong to user.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
    
        existing_habit: Habit | None = await Habit.find_one(
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
    
    """Archives a habit to remove it from the active list.

    This service moves a habit to the archived status, hiding it from
    the active habits list while preserving its data for future reference.

    Args:
        habit_id: The MongoDB ObjectId of the habit to archive.
        owner_id: The MongoDB ObjectId of the user owning the habit.

    Returns:
        Dict[str, str]: A success message confirming the archive operation.

    Raises:
        HTTPException 404: If habit is not found or doesn't belong to user.
        HTTPException 500: If an internal server error occurs.
    """

    try:

        habit: Habit | None = await Habit.find_one(
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
    
    """Restores an archived habit to the active list.

    This service moves a habit from archived status back to active,
    making it visible and trackable again.

    Args:
        habit_id: The MongoDB ObjectId of the habit to unarchive.
        owner_id: The MongoDB ObjectId of the user owning the habit.

    Returns:
        Dict[str, str]: A success message confirming the unarchive operation.

    Raises:
        HTTPException 404: If habit is not found or doesn't belong to user.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        habit: Habit | None = await Habit.find_one(
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

    """Retrieves all archived habits for a user with pagination.

    This service returns a paginated list of all habits that have been
    archived by the user, sorted by creation date.

    Args:
        owner_id: The MongoDB ObjectId of the user whose archived habits to retrieve.
        page: Page number for pagination (starts from 1).
        limit: Maximum number of archived habits to return per page.

    Returns:
        List[Habit]: A list of archived habit objects, sorted by creation date
            ascending.

    Raises:
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """

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