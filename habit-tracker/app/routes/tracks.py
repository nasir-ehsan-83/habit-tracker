from typing import Annotated
from beanie import BeanieObjectId
from fastapi import (
    APIRouter, 
    Depends,
    Body
)

from app.dependencies import (
    get_current_user,
    required_role
)
from app.models import Track
from app.schemas import (
    TokenData,
    TrackCreate,
    TrackOut
)
from app.services.tracks import(
    create_track
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
async def track(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    track:          Annotated[TrackCreate, Body(...)]
) -> Track:
    
    return await create_track(current_user.id, track)