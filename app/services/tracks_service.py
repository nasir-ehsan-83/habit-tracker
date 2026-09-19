from datetime import date
from typing import (
    Any, 
    Dict,
    List
)
from beanie import BeanieObjectId
from fastapi import (
    HTTPException,
    Response,
    status
)

from app.schemas import (
    TrackCreate,
    TrackUpdate,
    MissedDaysResponse
)
from app.config import logger
from app.models import Track
from app.services.streaks_service import update_streak_service



async def create_track_service(
    owner_id: BeanieObjectId,
    track_in: TrackCreate
) -> Track:
    
    """Creates a new track record for a habit completion.

    This service creates a track record for a habit completion on a specific date.
    After creating the track, it automatically updates the user's streak.

    Args:
        owner_id: The MongoDB ObjectId of the user creating the track.
        track_in: Track creation data 

    Returns:
        Track: The created track record with all fields populated.

    Raises:
        HTTPException 400: If date is not provided in the request.
        HTTPException 409: If a track already exists for this date and habit.
        HTTPException 500: If an internal server error occurs.

    Note:
        This service automatically calls update_streak_service to maintain
        the user's streak consistency.
    """
    
    try:
        track_data: Dict[str, Any] = track_in.model_dump(exclude_unset = True)
        track_date: date | None = track_data.get("date")
        
        if track_date is None:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Date is required"
            )
        
        query: Dict[str, BeanieObjectId | date] = {
            "owner_id": owner_id,
            "habit_id": track_in.habit_id,
            "date": track_date
        }

        track: Track | None = await Track.find_one(query)

        if track:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "Track already exists for this date"
            )
        
        new_track: Track = Track(
            **track_data,
            owner_id = owner_id
        )

        created_track: Track = await new_track.insert() # type: ignore
        
        await update_streak_service(
            owner_id = owner_id,
            habit_id = track_in.habit_id,
            track_date = track_date
        )
        
        return created_track

    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in create_track_service: {error}", exc_info = True)
       
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_track_service(
    id: BeanieObjectId,
    owner_id: BeanieObjectId,
    updated_data: TrackUpdate
) -> Track:
    
    """Updates an existing track record.

    This service allows users to modify their habit tracking records,
    such as changing completion status, updating notes, or modifying dates.

    Args:
        id: The MongoDB ObjectId of the track to update.
        owner_id: The MongoDB ObjectId of the user owning the track.
        updated_data: Updated track fields (all optional)

    Returns:
        Track: The updated track record with all fields.

    Raises:
        HTTPException 404: If the track is not found.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        track: Track | None = await Track.find_one(
            Track.id == id,
            Track.owner_id == owner_id
        )

        if not track:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Track not found"
            )
        
        new_data: Dict[str, Any] = updated_data.model_dump(exclude_unset = True)

        await track.set(new_data)

        return track

    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in update_track_service: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def delete_track_service(
    id: BeanieObjectId,
    owner_id: BeanieObjectId
) -> Response:
    
    """Permanently deletes a track record.

    This service removes a track record from the system. This action
    cannot be undone and may affect streak calculations.

    Args:
        id: The MongoDB ObjectId of the track to delete.
        owner_id: The MongoDB ObjectId of the user owning the track.

    Returns:
        Response: Empty response with status code 204 (No Content) on success.

    Raises:
        HTTPException 404: If the track is not found.
        HTTPException 403: If the user doesn't have permission to delete the track.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        track: Track | None = await Track.get(id)

        if not track:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Track not found"
            )

        if track.owner_id != owner_id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "You do not have permission to delete this track"
            )
        
        await track.delete() # type: ignore

        return Response(status_code = status.HTTP_204_NO_CONTENT)
    
    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in delete_track_service: {error}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_daily_tracks_service(
    owner_id:       BeanieObjectId,
    habit_id:       BeanieObjectId | None,
    target_date:    date

) -> List[Track]:
    
    """Retrieves all tracks for a specific date.

    This service returns all habit tracking records for a given date,
    optionally filtered by habit ID.

    Args:
        owner_id: The MongoDB ObjectId of the user.
        habit_id: Optional habit ID to filter tracks by a specific habit.
        target_date: The date to retrieve tracks for.

    Returns:
        List[Track]: List of track records for the specified date,
            sorted by creation time.

    Raises:
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        query: Dict[str, BeanieObjectId | date] = {
            "owner_id": owner_id,
            "date": target_date

        }

        if habit_id is not None:
            query["habit_id"] = habit_id

        tracks: List[Track] = await Track.find(query).to_list()

        return tracks
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_daily_tracks_service: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    



async def get_track_history_service(
    owner_id: BeanieObjectId,
    habit_id: BeanieObjectId,
    from_date: date,
    to_date: date
) -> List[Track]:
    
    """Retrieves track history for a specific habit within a date range.

    This service provides a chronological history of all tracks for a
    habit within the specified date range, useful for progress analysis.

    Args:
        owner_id: The MongoDB ObjectId of the user.
        habit_id: The MongoDB ObjectId of the habit to retrieve history for.
        from_date: Start date for the history range .
        to_date: End date for the history range.

    Returns:
        List[Track]: List of track records within the date range,
            ordered by completion_date ascending.

    Raises:
        HTTPException 400: If the date range is less than 7 days.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        if (to_date - from_date).days < 7:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Invalid date range. History range must be at least 7 days."
            )
        
        query: Dict[str, BeanieObjectId | Dict[str, date]] = {
            "owner_id": owner_id,
            "habit_id": habit_id,
            "date": {
                "$gte": from_date, 
                "$lte": to_date
            }
        }

        tracks: List[Track] = await Track.find(query).to_list()

        return tracks
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_track_history: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    



async def get_missed_days_service(
    owner_id: BeanieObjectId,
    habit_id: BeanieObjectId | None
) -> MissedDaysResponse: 
    
    """Retrieves a list of days where habit completions were missed.

    This service analyzes the user's tracking data to identify days
    where habits were not completed, helping users identify patterns
    and areas for improvement.

    Args:
        owner_id: The MongoDB ObjectId of the user.
        habit_id: Optional habit ID to filter missed days for a specific habit.
            If not provided, returns missed days across all habits.

    Returns:
        MissedDaysResponse: Missed days informations

    Raises:
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        query: Dict[str, BeanieObjectId] = {
            "owner_id": owner_id
        }
        response_data: Dict[str, BeanieObjectId | List[date]] = {}

        if habit_id:
            query["habit_id"] = habit_id
            response_data["habit_id"] = habit_id

        tracks: List[Track] = await Track.find(query).to_list()

        missed_days_list: List[date] = [track.date for track in tracks] 

        response_data["missed_days"] = missed_days_list

        return MissedDaysResponse(**response_data) # type: ignore
        
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_missed_days_service: {error}", exc_info=True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )