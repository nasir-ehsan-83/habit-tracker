from typing import Any, Dict
from beanie import BeanieObjectId
from fastapi import (
    HTTPException,
    status
)

from app.schemas import (
    TrackCreate
)
from app.config import logger
from app.models import Track




async def create_track(
    owner_id:   BeanieObjectId,
    track:      TrackCreate
) -> Track:
    
    try:
        track_data: Dict[str, Any] = track.model_dump(exclude_unset = True)
        track_date = track_data.get("date")
        
        query: Dict[str, Any] = {
            "owner_id": owner_id,
            "habit_id": track.habit_id,
            "date": track_date
        }

        found_track: Track | None = await Track.find_one(query)

        if found_track:
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
