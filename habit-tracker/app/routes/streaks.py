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
    CurrentStreakOut
)
from app.services.streaks_service import (
    get_current_streak_service
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
    response_model = CurrentStreakOut
)
async def get_current_streak_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit_id:       Annotated[BeanieObjectId, Query()]
) -> CurrentStreakOut:
    
    return await get_current_streak_service(current_user.id, habit_id)

