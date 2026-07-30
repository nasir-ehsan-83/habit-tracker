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
from app.schemas.token import TokenData
from app.utils.limiter import limiter
from app.schemas.users import (
    UserPrivateOut,
    UserUpdate
)
from app.services.users_service import (
    get_user_by_id, 
    update_user_by_id
)




router = APIRouter(
    prefix = '/api/users',
    tags = ['User']
)




@router.get(
    '/me', 
    response_model = UserPrivateOut
)
async def get_user(
    current_user: TokenData = Depends(get_current_user),
    user_role: str = Depends(require_role(["ADMIN", "USER"]))
) -> User:

    return await get_user_by_id(current_user.id)




@router.patch(
    '/me', 
    response_model = UserPrivateOut
)
async def update_user(
    current_user: TokenData = Depends(get_current_user),
    user_role: str = Depends(require_role(["ADMIN", "USER"])),
    user_data: UserUpdate = Body(...)
) -> User :

    return await update_user_by_id(current_user.id, user_data)



