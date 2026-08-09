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

from app.dependencies import (
    get_current_user, 
    required_role
)
from app.schemas import (
    UserAdminOut, 
    HabitAdminOut
)
from app.services.admin_service import (
    block_user_service,
    get_all_habits_service, 
    get_all_users_service, 
    get_user_service
)
from app.models import (
    User,
    Habit
)
from app.utils.enum import HabitCategory




router: APIRouter = APIRouter(
    prefix = '/api/admin',
    tags = ["Admin"],
    dependencies = [
        Depends(get_current_user),
        Depends(required_role(["ADMIN"]))
    ]
)




@router.get(
    '/users',
    response_model = List[UserAdminOut]
)
async def get_all_users_route(
    is_active:  Annotated[bool, Query(default = True)], 
    page:       Annotated[int, Query(default = 1, gt = 0, lt = 100)],
    limit:      Annotated[int, Query(default = 10, gt = 0, lt = 100)] 
) -> List[User]: 

    return await get_all_users_service(is_active, page, limit)





@router.get(
    '/users/{user_id}',
    response_model = UserAdminOut
)
async def get_user_route(
    user_id:    Annotated[BeanieObjectId, Path()]
) -> User: 

    return await get_user_service(user_id)




@router.patch(
    '/users/{user_id}/ban',
    response_model = UserAdminOut
)
async def user_ban_route(
    user_id:    Annotated[BeanieObjectId, Path()]
) -> User: 
    
    return await block_user_service(user_id)




@router.get(
    '/habits', 
    response_model = List[HabitAdminOut]
)
async def get_all_habits_route(
    owner_id:   Annotated[BeanieObjectId | None, Query(default = None)], 
    category:   Annotated[HabitCategory | None, Query(default = None)], 
    page:       Annotated[int, Query(default = 1, gt = 0)], 
    limit:      Annotated[int, Query(default = 10, gt = 0)], 
) -> List[Habit]: 

    return await get_all_habits_service(owner_id, category, page, limit)
