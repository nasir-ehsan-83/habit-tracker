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
    HabitUpdate
)
from app.services.habits_service import(
    create_new_habit,
    get_habit,
    get_all_habits,
    get_habits_by_category,
    update_habit,
    delete_habit
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
    user_role: str = Depends(require_role(["USER"])),
    habit: HabitCreate = Body(...), 
) -> Habit:
    
    return await create_new_habit(habit, current_user)




@router.get(
    '/', 
    response_model = List[HabitPrivateOut]
)
async def get_habits(
    current_user: TokenData = Depends(get_current_user), 
    user_role: str = Depends(require_role(["USER"])),
    category: HabitCategory = Query(default = ""),
    completed: bool = Query(default = False),
    page: int = Query(default = 1, gt = 0), 
    limit: int = Query(default = 10, gt = 0)
) -> List[Habit]:
    
    return await get_all_habits(current_user.id, category, completed, page, limit)




@router.get(
    '/{id}', 
    response_model = HabitPrivateOut
)
async def get_habit_id(
    current_user: TokenData = Depends(get_current_user), 
    user_role: str = Depends(require_role(["USER"])),
    id: BeanieObjectId = Path()
) -> Habit:

    return await get_habit(id, current_user)




@router.get(
    '/category/{category}',
    response_model = HabitPrivateOut
)
async def get_habit_category(
    current_user: TokenData = Depends(get_current_user), 
    user_role: str = Depends(require_role(["USER"])), 
    category: HabitCategory = Path()
) -> List[Habit]:
    
    return await get_habits_by_category(current_user.id, category)




@router.patch(
    '/{id}', 
    response_model = HabitPrivateOut
)
async def update_habit_id(
    current_user: TokenData = Depends(get_current_user),
    user_role: str = Depends(require_role(["USER"])),
    id: BeanieObjectId = Path(), 
    update_data: HabitUpdate = Body(...)
) -> Habit:
    
    return await update_habit(id, update_data, current_user)




@router.delete('/{id}')
async def delete_habit_id(
    current_user: TokenData = Depends(get_current_user),
    user_role: str = Depends(require_role(["USER"])),
    id: BeanieObjectId = Path()
) :

    return await delete_habit(id, current_user)