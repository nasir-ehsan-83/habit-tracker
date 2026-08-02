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
    Query
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
    TrackUpdate
)
from app.services.tracks_service import(
    create_track_service,
    update_track_service,
    get_tracks_service
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
    response_model = TrackOut
)
async def create_track_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    track:          Annotated[TrackCreate, Body(...)]
) -> Track:
    
    return await create_track_service(current_user.id, track)




@router.patch(
    '/{habit_id}',
    response_model = TrackOut
)
async def update_track_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit_id:       Annotated[BeanieObjectId, Path()],
    updated_data:   Annotated[TrackUpdate, Body(...)]
) -> Track:
    
    return await update_track_service(current_user.id, habit_id, updated_data)




@router.get(
    '/daily',
    response_model = List[TrackOut]
)
async def get_tracks_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit_id:       Annotated[BeanieObjectId, Query(default = None)],
    from_date:      Annotated[date, Query()],
    to_date:        Annotated[date, Query()]
) -> List[Track]:
    
    return await get_tracks_service(current_user.id, habit_id, from_date, to_date)