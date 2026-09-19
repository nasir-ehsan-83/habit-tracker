from typing import (
    Annotated,
    Dict,
    List
)
from beanie import BeanieObjectId
from fastapi import (
    APIRouter,
    Body, 
    Depends,
    Path,
    Query,
    Request,
    status
)

from app.dependencies import (
    get_current_user,
    required_role
)
from app.utils.enum import HabitCategory
from app.utils import limiter
from app.models import Habit
from app.schemas import (
    HabitCreate, 
    HabitPrivateOut,
    HabitUpdate,
    TokenData
)
from app.services.habits_service import(
    create_habit_service,
    get_habit_service,
    get_all_habits_service,
    get_habits_by_category_service,
    update_habit_service,
    delete_habit_service,
    archive_habit_service,
    unarchive_habit_service,
    get_archived_habits_service
)




router = APIRouter(
    prefix = '/api/habits',
    tags = ["Habits"],
    dependencies = [
        Depends(required_role(["USER"]))
    ]
)




@router.post(
    '/', 
    response_model = HabitPrivateOut,
    status_code = status.HTTP_201_CREATED,
    summary = "Create a new habit",
    description = "Creates a new habit for the authenticated user with the provided details."
)
@limiter.limit('3/minute')
async def create_habit_route(
    request:        Request,
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit:          Annotated[HabitCreate, Body(description = "Habit creation data including name, category, and frequency.")], 
) -> Habit:
    
    """Create a new habit.

    Args:
        request: FastAPI request object for rate limiting.
        current_user: The authenticated user's token data.
        habit: Habit creation data.

    Returns:
        HabitPrivateOut: The created habit with all details.
    """
    
    return await create_habit_service(habit, current_user.id)




@router.get(
    '/', 
    response_model = List[HabitPrivateOut],
    summary = "Retrieve all habits",
    description = "Fetches a paginated list of user's habits with optional category and completion filtering."
)
async def get_all_habits_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)], 
    category:       Annotated[HabitCategory, Query(description = "Filter habits by category.")],
    completed:      Annotated[bool, Query(description = "Filter by completion status.")] = False,
    page:           Annotated[int, Query(gt = 0, description = "Page number for pagination.")] = 1, 
    limit:          Annotated[int, Query(gt = 0, description = "Number of habits per page.")] = 10
) -> List[Habit]:
    
    """Get all habits with pagination and filtering.

    Args:
        current_user: The authenticated user.
        category: Filter by habit category.
        completed: Filter by completion status.
        page: Page number.
        limit: Items per page.

    Returns:
        List[HabitPrivateOut]: List of habits matching the criteria.
    """
    
    return await get_all_habits_service(current_user.id, category, completed, page, limit)




@router.get(
    '/{id}', 
    response_model = HabitPrivateOut,
    summary = "Retrieve a habit by ID",
    description = "Fetches a specific habit by its unique identifier."
)
async def get_habit_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)], 
    id:             Annotated[BeanieObjectId, Path(description = "The habit ID to retrieve.")]
) -> Habit:

    """Get a habit by ID.

    Args:
        current_user: The authenticated user.
        id: The habit ID.

    Returns:
        HabitPrivateOut: The requested habit.
    """

    return await get_habit_service(id, current_user.id)




@router.get(
    '/category/{category}',
    response_model = List[HabitPrivateOut],
    summary = "Retrieve habits by category",
    description = "Fetches all habits belonging to a specific category."
)
async def get_habit_by_category_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)], 
    category:       Annotated[HabitCategory, Path(description = "The category to filter habits by.")]
) -> List[Habit]:
    
    """Get habits by category.

    Args:
        current_user: The authenticated user.
        category: The habit category.

    Returns:
        List[HabitPrivateOut]: List of habits in the specified category.
    """
    
    return await get_habits_by_category_service(current_user.id, category)




@router.patch(
    '/{id}', 
    response_model = HabitPrivateOut,
    summary = "Update a habit",
    description = "Updates an existing habit with new information."
)
async def update_habit_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)], 
    id:             Annotated[BeanieObjectId, Path(description = "The habit ID to update.")], 
    update_data:    Annotated[HabitUpdate, Body(description = "Updated habit fields (all optional).")]
) -> Habit:
    
    """Update a habit.

    Args:
        current_user: The authenticated user.
        id: The habit ID.
        update_data: Updated habit fields.

    Returns:
        HabitPrivateOut: The updated habit.
    """
    
    return await update_habit_service(id, current_user.id, update_data)




@router.delete(
    '/{id}',
    summary = "Delete a habit",
    description = "Permanently deletes a habit (soft delete)."
)
async def delete_habit_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)], 
    id:             Annotated[BeanieObjectId, Path(description = "The habit ID to delete.")]
) :

    """Delete a habit (soft delete).

    Args:
        current_user: The authenticated user.
        id: The habit ID.

    Returns:
        Response: 204 No Content on success.
    """

    return await delete_habit_service(id, current_user.id)




@router.post(
    '/{id}/archive',
    response_model = Dict[str, str],
    summary = "Archive a habit",
    description = "Archives a habit to remove it from the active list."
)
async def archive_habit_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)], 
    id:             Annotated[BeanieObjectId, Path(description = "The habit ID to archive.")]
) -> Dict[str, str]:
    
    """Archive a habit.

    Args:
        current_user: The authenticated user.
        id: The habit ID.

    Returns:
        Dict[str, str]: Success message.
    """
    
    return await archive_habit_service(id, current_user.id)




@router.post(
    '/{id}/unarchive',
    response_model = Dict[str, str],
    summary = "Unarchive a habit",
    description = "Restores an archived habit to the active list."
)
async def unarchive_habit_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    id:             Annotated[BeanieObjectId, Path(description = "The habit ID to unarchive.")]
) -> Dict[str, str]:
    
    """Unarchive a habit.

    Args:
        current_user: The authenticated user.
        id: The habit ID.

    Returns:
        Dict[str, str]: Success message.
    """
    
    return await unarchive_habit_service(id, current_user.id)




@router.get(
    '/archived',
    response_model = List[HabitPrivateOut],
    summary = "Retrieve archived habits",
    description = "Fetches a paginated list of all archived habits for the user."
)
async def get_archived_habits_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    page:           Annotated[int, Query(gt = 0, description = "Page number for pagination.")] = 1, 
    limit:          Annotated[int, Query(gt = 0, description = "Number of habits per page.")] = 10
) -> List[Habit]:
    
    """Get archived habits with pagination.

    Args:
        current_user: The authenticated user.
        page: Page number.
        limit: Items per page.

    Returns:
        List[HabitPrivateOut]: List of archived habits.
    """
    
    return await get_archived_habits_service(current_user.id, page, limit)