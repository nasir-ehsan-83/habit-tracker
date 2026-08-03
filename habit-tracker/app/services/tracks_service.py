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
    TrackUpdate
)
from app.config import logger
from app.models import Track




async def create_track_service(
    owner_id:   BeanieObjectId,
    track_in:   TrackCreate
) -> Track:
    
    try:
        track_data: Dict[str, Any] = track_in.model_dump(exclude_unset = True)
        track_date = track_data.get("date")
        
        query: Dict[str, Any] = {
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

        return await new_track.insert() # type: ignore

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
    try:
        track = await Track.find_one(
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




async def get_daily_tracks_service(
    owner_id:       BeanieObjectId,
    habit_id:       BeanieObjectId | None,
    target_date:    date

) -> List[Track]:
    try:
        query: Dict[str, Any] = {
            "owner_id": owner_id,
            "date": target_date

        }

        if habit_id is not None:
            query["habit_id"] = habit_id

        tracks = await Track.find(query).to_list()

        return tracks
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_daily_tracks_service: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )