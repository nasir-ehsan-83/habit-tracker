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
    TrackUpdate
)
from app.services.tracks_service import(
    create_track_service,
    get_track_history_service,
    update_track_service,
    get_daily_tracks_service,
    delete_track_service,
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
    '/{id}',
    response_model = TrackOut
)
async def update_track_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    id:             Annotated[BeanieObjectId, Path()],
    updated_data:   Annotated[TrackUpdate, Body(...)]
) -> Track:
    
    return await update_track_service(id, current_user.id, updated_data)




@router.delete(
    '/{id}',
    response_model = Response
)
async def delete_track_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    id:             Annotated[BeanieObjectId, Path()]
) -> Response:

    return await delete_track_service(id, current_user.id)




@router.get(
    '/daily',
    response_model = List[TrackOut]
)
async def get_daily_tracks_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit_id:       Annotated[BeanieObjectId, Query(default = None)],
    target_date:    Annotated[date, Query()],
) -> List[Track]:
    
    return await get_daily_tracks_service(current_user.id, habit_id, target_date)




@router.get(
    '/history',
    response_model = List[TrackOut]
)
async def get_track_history_router(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit_id:       Annotated[BeanieObjectId, Query()],
    from_date:      Annotated[date, Query()],
    to_date:    Annotated[date, Query()]
) -> List[Track]:
    
    return await get_track_history_service(current_user.id, habit_id, from_date, to_date)