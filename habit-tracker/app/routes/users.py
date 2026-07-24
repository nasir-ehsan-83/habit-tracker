from beanie import BeanieObjectId
from fastapi import (
    APIRouter,
    Body, 
    Depends,
    Path,
    Query,
    Request
)
from typing import List

from app.dependencies.current_user import get_current_user
from app.dependencies.check_roles import require_role
from app.models.users import User
from app.schemas.token import TokenData
from app.utils.limiter import limiter
from app.schemas.users import (
    UserCreate, 
    UserPrivateOut, 
    UserAdminOut, 
    UserUpdate
)
from app.services.users_service import (
    create_user, 
    get_all_users,
    get_user_by_email, 
    update_user_by_id, 
    delete_user_id
)




router = APIRouter(
    prefix = '/api/users',
    tags = ['User']
)




# create new user
@router.post(
    '/', 
    response_model = UserPrivateOut
)
@limiter.limit('3/minute')
async def create_new_user(
    request: Request, 
    user_in: UserCreate = Body(...)
) -> User:
    
    return await create_user(user_in)




# get all users's information by admin access
@router.get(
    '/admin-only', 
    response_model = List[UserAdminOut]
)
async def get_users(
    current_user: TokenData = Depends(get_current_user),
    user: str = Depends(require_role(["admin"])), 
    page: int = Query(gt = 0, default = 1), 
    limit: int = Query(gt = 0, default = 10)
) -> List[User]:

    return await get_all_users(page, limit)




# get user's information by email and owner access
@router.get(
    '/{email}', 
    response_model = UserPrivateOut
)
async def get_user_email(
    current_user: TokenData = Depends(get_current_user),
    email: str = Path()
) -> User:

    return await get_user_by_email(email, current_user)




# update user's information by email and owner acccess
@router.patch(
    '/{id}', 
    response_model = UserPrivateOut
)
async def update_user(
    current_user: TokenData = Depends(get_current_user),
    id: BeanieObjectId = Path(),
    user_data: UserUpdate = Body(...)
) -> User :

    return await update_user_by_id(id, user_data, current_user)




# delete user's information by email and owner access
@router.delete(
    '/{id}'
)
async def delete_user(
    current_user: TokenData = Depends(get_current_user),
    id: BeanieObjectId = Path()
):

    return await delete_user_id(id, current_user)