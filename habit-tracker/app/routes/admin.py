from typing import (
    Annotated, 
    List
)
from beanie import BeanieObjectId
from fastapi import (
    APIRouter, 
    Depends,
    Path,
    Query
)
from app.dependencies.current_user import get_current_user
from app.dependencies.check_roles import require_role
from app.models.habits import Habit
from app.models.users import User
from app.schemas.habits import HabitAdminOut
from app.schemas.users import UserAdminOut
from app.services.admin_service import (
    block_user,
    get_all_habits, 
    get_all_users, 
    get_one_user
)
from app.utils.enum import HabitCategory




router: APIRouter = APIRouter(
    prefix = '/api/admin',
    tags = ["Admin"],
    dependencies = [
        Depends(get_current_user),
        Depends(require_role(["ADMIN"]))
    ]
)




@router.get(
    '/users',
    response_model = List[UserAdminOut]
)
async def get_users(
    is_active:  Annotated[bool, Query(default = False)], 
    page:       Annotated[int, Query(default = 1,  gt = 0, lt = 100)],
    limit:      Annotated[int, Query(default = 10, gt = 0, lt = 100)] 
) -> List[User]:
    return await get_all_users(is_active, page, limit)





@router.get(
    '/users/{user_id}',
    response_model = UserAdminOut
)
async def get_user(
    user_id:    Annotated[BeanieObjectId, Path()]
) -> User | None:
    
    return await get_one_user(user_id)




@router.patch(
    '/users/{user_id}/ban',
    response_model = UserAdminOut
)
async def user_ban(
    user_id:    Annotated[BeanieObjectId, Path()]
) -> User | None:
    
    return await block_user(user_id)




@router.get(
    '/habits', 
    response_model = List[HabitAdminOut]
)
async def get_habits(
    owner_id:   Annotated[BeanieObjectId | None, Query(default = None)], 
    category:   Annotated[HabitCategory, Query(default = None)],
    page:       Annotated[int, Query(default = 1, gt = 0)], 
    limit:      Annotated[int, Query(default = 10, gt = 0)], 
) -> List[Habit]:
    
    return await get_all_habits(owner_id, category, page, limit)
