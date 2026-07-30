from typing import (
    List, 
    Optional
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
from app.models.habits import Habit
from app.dependencies.current_user import get_current_user
from app.dependencies.check_roles import require_role
from app.schemas.token import TokenData
from app.utils.enum import HabitCategory
from app.utils.limiter import limiter
from app.schemas.habits import (
    HabitCreate, 
    HabitPrivateOut, 
    HabitAdminOut, 
    HabitUpdate
)
from app.services.habits_service import(
    create_new_habit,
    get_all_habits,
    get_all_habits_admin, 
    get_habit_by_name,
    update_habit_by_name,
    delete_habit_by_name
)




router = APIRouter(
    prefix = '/api/habits',
    tags = ["Habits"]
)




@router.post(
    '/', 
    response_model = HabitPrivateOut
)
@limiter.limit('3/minute')
async def create_habit(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    habit: HabitCreate = Body(...), 
) -> Habit:
    
    return await create_new_habit(habit, current_user)




@router.get(
    '/', 
    response_model = List[HabitPrivateOut]
)
async def get_habits(
    current_user: TokenData = Depends(get_current_user), 
    category: HabitCategory = Query(default = ""),
    completed: bool = Query(default = False),
    page: int = Query(default = 1, gt = 0), 
    limit: int = Query(default = 10, gt = 0)
) -> List[Habit]:
    
    return await get_all_habits(current_user.id, category, completed, page, limit)




@router.get(
    '/{name}', 
    response_model = HabitPrivateOut
)
async def get_habit(
    current_user: TokenData = Depends(get_current_user), 
    name: str = Path()
) -> Habit:

    return await get_habit_by_name(name, current_user)




@router.patch(
    '/{name}', 
    response_model = HabitPrivateOut
)
async def update_habit(
    current_user: TokenData = Depends(get_current_user),
    name: str = Path(), 
    update_habit: HabitUpdate = Body(...)
) -> Habit:
    
    return await update_habit_by_name(name, update_habit, current_user)




@router.delete('/{name}')
async def delete_habit(
    current_user: TokenData = Depends(get_current_user),
    name: str = Path()
) :

    return await delete_habit_by_name(name, current_user)