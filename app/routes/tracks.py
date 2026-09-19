from datetime import date
from typing import (
    Annotated,
    List
)
from beanie import BeanieObjectId
from fastapi import (
    APIRouter, 
    Depends,
    Body,
    Path,
    Query,
    Response
)

from app.dependencies import (
    get_current_user,
    required_role
)
from app.models import Track
from app.schemas import (
    TokenData,
    TrackCreate,
    TrackOut,
    TrackUpdate,
    MissedDaysResponse
)
from app.services.tracks_service import(
    create_track_service,
    get_track_history_service,
    update_track_service,
    get_daily_tracks_service,
    delete_track_service,
    get_missed_days_service
)



router: APIRouter = APIRouter(
    prefix = '/api/tracks',
    tags = ["Tracks"],
    dependencies = [
        Depends(required_role(["USER"]))
    ]
)


@router.post(
    '/',
    response_model = TrackOut,
    status_code = 201,
    summary = "Create track record",
    description = "Creates a new track record for a habit completion on a specific date."
)
async def create_track_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    track:          Annotated[TrackCreate, Body(description = "Track creation data including habit ID, date, and completion status.")]
) -> Track:
    
    """Creates a new track record for a habit completion.

    This endpoint allows users to log their habit completions by creating
    a track record for a specific date. Each track represents a single
    habit completion event.

    **Response Codes:**
    - 201: Track created successfully
    - 400: Invalid track data or duplicate entry
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User role required
    - 404: Habit not found
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        track: Track creation data

    Returns:
        TrackOut: The created track record

    Raises:
        HTTPException 400: If track data is invalid or duplicate.
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 404: If habit doesn't exist.
        HTTPException 500: If an internal server error occurs.
    """

    return await create_track_service(current_user.id, track)




@router.patch(
    '/{id}',
    response_model = TrackOut,
    summary = "Update track record",
    description = "Updates an existing track record with new information or status."
)
async def update_track_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    id:             Annotated[BeanieObjectId, Path(description = "The MongoDB ObjectId of the track to update.")],
    updated_data:   Annotated[TrackUpdate, Body(description = "Updated track fields (all fields optional).")]
) -> Track:
    
    """Updates an existing track record.

    This endpoint allows users to modify their habit tracking records,
    such as changing completion status, updating notes, or modifying dates.

    **Response Codes:**
    - 200: Track updated successfully
    - 400: Invalid update data
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User doesn't own this track
    - 404: Track not found
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        id: The MongoDB ObjectId of the track to update.
        updated_data: Updated track fields (all optional)

    Returns:
        TrackOut: The updated track record with all fields.

    Raises:
        HTTPException 400: If update data is invalid.
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't own the track.
        HTTPException 404: If track doesn't exist.
        HTTPException 500: If an internal server error occurs.
    """

    return await update_track_service(id, current_user.id, updated_data)




@router.delete(
    '/{id}',
    response_model = Response,
    summary = "Delete track record",
    description = "Permanently deletes a track record by its unique identifier."
)
async def delete_track_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    id:             Annotated[BeanieObjectId, Path(description = "The MongoDB ObjectId of the track to delete.")]
) -> Response:

    """Permanently deletes a track record.

    This endpoint removes a track record from the system. This action
    cannot be undone and may affect streak calculations.

    **Response Codes:**
    - 204: Track deleted successfully (No Content)
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User doesn't own this track
    - 404: Track not found
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        id: The MongoDB ObjectId of the track to delete.

    Returns:
        Response: Empty response with status code 204 on success.

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't own the track.
        HTTPException 404: If track doesn't exist.
        HTTPException 500: If an internal server error occurs.
    """

    return await delete_track_service(id, current_user.id)




@router.get(
    '/daily',
    response_model = List[TrackOut],
    summary = "Retrieve daily tracks",
    description = "Fetches all tracks for a specific date, optionally filtered by habit."
)
async def get_daily_tracks_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    target_date:    Annotated[date, Query(description = "The target date to retrieve tracks for (YYYY-MM-DD).")],
    habit_id:       Annotated[BeanieObjectId | None, Query(description = "Optional habit ID to filter tracks by a specific habit.")] = None,
) -> List[Track]:
    
    """Retrieves all tracks for a specific date.

    This endpoint returns all habit tracking records for a given date,
    allowing users to review their completions and progress for that day.

    **Response Codes:**
    - 200: Tracks retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User role required
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        target_date: The date to retrieve tracks for.
        habit_id: Optional habit ID to filter results.

    Returns:
        List[TrackOut]: List of track records for the specified date,
            sorted by creation time.

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_daily_tracks_service(current_user.id, habit_id, target_date)




@router.get(
    '/history',
    response_model = List[TrackOut],
    summary = "Retrieve track history",
    description = "Fetches track history for a specific habit within a date range."
)
async def get_track_history_router(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit_id:       Annotated[BeanieObjectId, Query(description = "The habit ID to retrieve track history for.")],
    from_date:      Annotated[date, Query(description = "Start date for the history range (inclusive, YYYY-MM-DD).")],
    to_date:        Annotated[date, Query(description = "End date for the history range (inclusive, YYYY-MM-DD).")]
) -> List[Track]:
    
    """Retrieves track history for a specific habit within a date range.

    This endpoint provides a chronological history of all tracks for a
    habit within the specified date range, useful for progress analysis.

    **Response Codes:**
    - 200: Track history retrieved successfully
    - 400: Invalid date range (from_date > to_date)
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User doesn't own this habit
    - 404: Habit not found
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        habit_id: The MongoDB ObjectId of the habit to retrieve history for.
        from_date: Start date for the history range.
        to_date: End date for the history range.

    Returns:
        List[TrackOut]: List of track records within the date range,
            ordered by completion_date ascending.

    Raises:
        HTTPException 400: If from_date is after to_date.
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't own the habit.
        HTTPException 404: If habit doesn't exist.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_track_history_service(current_user.id, habit_id, from_date, to_date)




@router.get(
    '/missed-days', 
    response_model = MissedDaysResponse,
    summary = "Retrieve missed days",
    description = "Fetches a list of days where the user missed habit completions, optionally filtered by habit."
)
async def get_missed_days_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit_id:       Annotated[BeanieObjectId | None, Query(description = "Optional habit ID to filter missed days for a specific habit.")] = None, 
) -> MissedDaysResponse:
    
    """Retrieves a list of days where habit completions were missed.

    This endpoint analyzes the user's tracking data to identify days
    where habits were not completed, helping users identify patterns
    and areas for improvement.

    **Response Codes:**
    - 200: Missed days retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User role required
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        habit_id: Optional habit ID to filter missed days for a specific habit.
            If not provided, returns missed days across all habits.

    Returns:
        MissedDaysResponse: Missed days information

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_missed_days_service(current_user.id, habit_id)