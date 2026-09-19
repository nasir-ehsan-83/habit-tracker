from typing import Annotated
from beanie import BeanieObjectId
from fastapi import (
    APIRouter,
    Depends,
    Query
)

from app.dependencies import (
    get_current_user,
    required_role
)
from app.schemas import (
    TokenData,
    CurrentStreakOut,
    BestStreakOut
)
from app.services.streaks_service import (
    get_current_streak_service,
    get_best_streak_service
)




router: APIRouter = APIRouter(
    prefix = '/api/streak',
    tags = ["Streak"],
    dependencies = [
        Depends(required_role(["USER"]))
    ]
)




@router.get(
    '/current',
    response_model = CurrentStreakOut,
    summary = "Retrieve current streak",
    description = "Fetches the current active streak for a specific habit, showing how many consecutive days the user has completed the habit."
)
async def get_current_streak_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit_id:       Annotated[BeanieObjectId, Query(description = "The MongoDB ObjectId of the habit to check the current streak for.")]
) -> CurrentStreakOut:
    
    """Retrieves the current active streak for a specific habit.

    This endpoint calculates and returns the user's current consecutive
    completion streak for a given habit. The streak is counted from the
    most recent completion day, going backward in time.

    **Response Codes:**
    - 200: Current streak retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User role required
    - 404: Habit not found or user doesn't have access
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        habit_id: The MongoDB ObjectId of the habit to check.

    Returns:
        CurrentStreakOut: Current streak informations
    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 404: If habit not found or doesn't belong to user.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_current_streak_service(current_user.id, habit_id)




@router.get(
    '/best',
    response_model = BestStreakOut,
    summary = "Retrieve best streak",
    description = "Fetches the user's all-time best streak for a specific habit, showing their highest consecutive completion record."
)
async def get_best_streak_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit_id:       Annotated[BeanieObjectId, Query(description = "The MongoDB ObjectId of the habit to check the best streak for.")]
) -> BestStreakOut:
    
    """Retrieves the user's all-time best streak for a specific habit.

    This endpoint calculates and returns the user's longest consecutive
    completion streak ever achieved for a given habit. This represents
    the user's personal best performance.

    **Response Codes:**
    - 200: Best streak retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User role required
    - 404: Habit not found or user doesn't have access
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        habit_id: The MongoDB ObjectId of the habit to check.

    Returns:
        BestStreakOut: Best streak informations
    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 404: If habit not found or doesn't belong to user.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_best_streak_service(current_user.id, habit_id)