from typing import (
    Any, 
    Dict
)
from beanie import BeanieObjectId
from fastapi import (
    HTTPException,
    status
)

from app.schemas import (
    TrackCreate,
    TrackUpdate
)
from app.config import logger
from app.models import Track




async def create_track(
    owner_id:   BeanieObjectId,
    track_in:      TrackCreate
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

        return await new_track.insert()

    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in create_track: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_track(
    owner_id:       BeanieObjectId,
    habit_id:       BeanieObjectId,
    updated_data:   TrackUpdate
) -> Track:
    
    try:
        query: Dict[str, Any] = {
            "owner_id": owner_id,
            "habit_id": habit_id
        }

        track: Track | None = await Track.find_one(query)

        if not track:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Track does not exist"
            )
        
        new_data: Dict[str, Any] = updated_data.model_dump(exclude_unset = True)

        await track.set({
            **new_data
        })
        await track.sync()

        return track

    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in udpate_track: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )