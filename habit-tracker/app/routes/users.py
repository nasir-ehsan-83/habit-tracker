from typing import (
    Annotated, 
    List, 
    Tuple
)
from fastapi import (
    APIRouter,
    Body, 
    Depends,
)

from app.utils import limiter
from app.dependencies import (
    get_current_user,
    required_role
)
from app.models import (
    User, 
    Habit,
    UserPreference
)
from app.schemas import (
    UserPrivateOut,
    UserUpdate,
    TokenData,
    PreferenceOut,
    PreferenceUpdate
)
from app.services.users_service import (
    get_user_service,
    update_avatar_service, 
    update_user_service,
    get_stats_service,
    get_preference_service,
    update_preference_service
)




router = APIRouter(
    prefix = '/api/users',
    tags = ['User'],
    dependencies = [
        Depends(required_role(["ADMIN", "USER"]))
    ]
)




@router.get(
    '/me', 
    response_model = UserPrivateOut
)
async def get_user_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
) -> User:

    return await get_user_service(current_user.id)




@router.patch(
    '/me', 
    response_model = UserPrivateOut
)
async def update_user_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    user_data:      Annotated[UserUpdate, Body(...)]
) -> User :

    return await update_user_service(current_user.id, user_data)



@router.patch(
    '/me/avatar'
)
async def update_user_avatar_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    new_url:        str
) -> User:
    
    return await update_avatar_service(current_user.id, new_url)




@router.get(
    '/me/stats',
    response_model = Tuple[User, List[Habit]] 
)
async def get_user_stats_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
) -> Tuple[User, List[Habit]]:
    
    return await get_stats_service(current_user.id)




@router.get(
    '/preference',
    response_model = PreferenceOut
)
async def get_user_preference_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)]
) -> UserPreference:

    return await get_preference_service(current_user.id)




@router.put(
    '/preference',
    response_model = PreferenceOut
)
async def create_or_update_user_preference_route(
    current_user:       Annotated[TokenData, Depends(get_current_user)],
    preference_data:    Annotated[PreferenceUpdate, Body(...)]
) -> UserPreference:

    return await update_preference_service(current_user.id, preference_data)


