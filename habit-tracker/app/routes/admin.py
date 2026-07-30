from typing import List
from beanie import BeanieObjectId
from fastapi import (
    APIRouter, 
    Depends,
    Path,
    Query
)
from app.dependencies.current_user import get_current_user
from app.dependencies.check_roles import require_role
from app.models.users import User
from app.schemas.users import UserAdminOut
from app.schemas.token import TokenData
from app.services.admin_service import block_user, get_all_users



router: APIRouter = APIRouter(
    prefix = '/api/admin',
    tags = ["Admin"]
)



@router.get(
    '/users',
    response_model = List[UserAdminOut]
)
async def get_users(
    current_user: TokenData = Depends(get_current_user),
    user: TokenData = Depends(require_role(["ADMIN"])),
    is_actived: bool = Query(default = False),
    page: int = Query(default = 1,  gt = 0, lt = 100),
    limit: int = Query(default = 0, gt = 0, lt = 100)
) -> List[User]:
    
    return await get_all_users(is_actived, page, limit)



@router.patch(
    '/users/{user_id}/ban',
    response_model = UserAdminOut
)
async def user_ban(
    current_user: TokenData = Depends(get_current_user),
    user: TokenData = Depends(require_role(["ADMIN"])),
    user_id: BeanieObjectId = Path()
) -> User | None:

    return await block_user(user_id)