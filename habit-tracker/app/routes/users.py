from typing import Annotated, List, Sequence, Tuple
from beanie import BeanieObjectId
from fastapi import (
    APIRouter,
    Body, 
    Depends,
    Path,
    Query,
    Request
)

from app.dependencies.current_user import get_current_user
from app.dependencies.check_roles import require_role
from app.models.users import User
from app.models.habits import Habit
from app.schemas.token import TokenData
from app.utils.limiter import limiter
from app.schemas.users import (
    UserPrivateOut,
    UserUpdate
)
from app.services.users_service import (
    get_user,
    update_avatar, 
    update_user,
    get_stats
)




router = APIRouter(
    prefix = '/api/users',
    tags = ['User'],
    dependencies = [
        Depends(require_role(["ADMIN", "USER"]))
    ]
)




@router.get(
    '/me', 
    response_model = UserPrivateOut
)
async def get_user_id(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
) -> User:

    return await get_user(current_user.id)




@router.patch(
    '/me', 
    response_model = UserPrivateOut
)
async def update_user_id(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    user_data:      Annotated[UserUpdate, Body(...)]
) -> User :

    return await update_user(current_user.id, user_data)



@router.patch(
    '/me/avatar'
)
async def update_user_avatar(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    new_url:        str
) -> User:
    
    return await update_avatar(current_user.id, new_url)




@router.get(
    '/me/stats',
    response_model = Tuple[User, List[Habit]] 
)
async def get_user_stats(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
) -> Tuple[User, List[Habit]]:
    
    return await get_stats(current_user.id)