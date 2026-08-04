from typing import (
    Annotated,
    Dict,
    List
)
from beanie import BeanieObjectId
from fastapi import (
    APIRouter,
    Body, 
    Depends,
    Path,
    Query,
    Request
)

from app.dependencies import (
    get_current_user,
    required_role
)
from app.utils.enum import HabitCategory
from app.utils import limiter
from app.models import Habit
from app.schemas import (
    HabitCreate, 
    HabitPrivateOut,
    HabitUpdate,
    TokenData
)
from app.services.habits_service import(
    create_habit_service,
    get_habit_service,
    get_all_habits_service,
    get_habits_by_category_service,
    update_habit_service,
    delete_habit_service,
    archive_habit_service,
    unarchive_habit_service,
    get_archived_habits_service
)




router = APIRouter(
    prefix = '/api/habits',
    tags = ["Habits"],
    dependencies = [
        Depends(required_role(["USER"]))
    ]
)




@router.post(
    '/', 
    response_model = HabitPrivateOut
)
@limiter.limit('3/minute')
async def create_habit_route(
    request:        Request,
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    habit:          Annotated[HabitCreate, Body(...)], 
) -> Habit:
    
    return await create_habit_service(habit, current_user.id)




@router.get(
    '/', 
    response_model = List[HabitPrivateOut]
)
async def get_all_habits_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)], 
    category:       Annotated[HabitCategory, Query(default = "")],
    completed:      Annotated[bool, Query(default = False)],
    page:           Annotated[int, Query(default = 1, gt = 0)], 
    limit:          Annotated[int, Query(default = 10, gt = 0)]
) -> List[Habit]:
    
    return await get_all_habits_service(current_user.id, category, completed, page, limit)




@router.get(
    '/{id}', 
    response_model = HabitPrivateOut
)
async def get_habit_route(
    id: Annotated[BeanieObjectId, Path()]
) -> Habit:

    return await get_habit_service(id)




@router.get(
    '/category/{category}',
    response_model = HabitPrivateOut
)
async def get_habit_by_category_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)], 
    category:       Annotated[HabitCategory, Path()]
) -> List[Habit]:
    
    return await get_habits_by_category_service(current_user.id, category)




@router.patch(
    '/{id}', 
    response_model = HabitPrivateOut
)
async def update_habit_route(
    id:             Annotated[BeanieObjectId, Path()], 
    update_data:    Annotated[HabitUpdate, Body(...)]
) -> Habit:
    
    return await update_habit_service(id, update_data)




@router.delete('/{id}')
async def delete_habit_route(
    id: Annotated[BeanieObjectId, Path()]
) :

    return await delete_habit_service(id)




@router.post(
    '/{id}/archive',
    response_model = Dict[str, str]
)
async def archive_habit_route(
    id: Annotated[BeanieObjectId, Path()]
) -> Dict[str, str]:
    
    return await archive_habit_service(id)




@router.post(
    '/{id}/unarchive',
    response_model = Dict[str, str]
)
async def unarchive_habit_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    id:             Annotated[BeanieObjectId, Path()]
) -> Dict[str, str]:
    
    return await unarchive_habit_service(id, current_user.id)




@router.get(
    '/archived',
    response_model = List[HabitPrivateOut]
)
async def get_archived_habits_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    page:           Annotated[int, Query(default = 1, gt = 0)], 
    limit:          Annotated[int, Query(default = 10, gt = 0)]
) -> List[Habit]:
    
    return await get_archived_habits_service(current_user.id, page, limit)