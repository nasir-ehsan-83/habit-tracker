from typing import List
from fastapi import (
    HTTPException, 
    Response, 
    status
)
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from beanie import BeanieObjectId

from app.core.security import hash
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate
from app.schemas.token import TokenData
from app.utils.pagination import paginate
from app.config.logging_handler import logger 




# Create a new user and store their profile in the database
async def create_user(user: UserCreate) -> User:
    try:
        # Check if the email is already taken
        if await User.find_one(User.email == user.email):
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "Email exists"
            )
        
        # Check if the username is already taken
        if await User.find_one(User.username == user.username):
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT, 
                detail = "Username exists"
            )
        
        new_user = User(
            **user.model_dump(exclude = {"password"}),
            password = await hash(user.password)
        )

        # Persist new user instance
        return await new_user.insert()
    
    except HTTPException:
        raise
    
    except DuplicateKeyError as error:
        logger.error(f"Duplicate Key Error while registering user: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Data conflict: The provided credentials are already in use."
        )
    
    except Exception as error:
        logger.error(f"Unexpected error in create_user: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




# Retrieve a paginated list of all system users (Admin privileged access)
async def get_all_users(
    page: int = 1, 
    limit: int = 10
) -> List[User]:

    try:
        skip, limit_val = paginate(page, limit)
        users = await User.find_all(skip = skip, limit = limit_val).to_list()

        return users
    
    except Exception as error:
        logger.error(f"Unexpected error in get_all_users: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




# Retrieve individual profile parameters using email values (Owner privileged access)
async def get_user_by_email(
    email: str, 
    current_user: TokenData
) -> User:
    try:
        # Fetch the active user matching both email identity and ownership context
        user = await User.find_one(
            User.email == email,
            User.id == BeanieObjectId(current_user.id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, 
                detail = "User not found"
            )
        
        return user
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_user_by_email: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




# Update explicit profile entries using input payload data (Owner privileged access)
async def update_user_by_id(
    id: int, 
    data: UserUpdate,
    current_user: TokenData
) -> User:
    
    if BeanieObjectId(id) != BeanieObjectId(current_user.id):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Unauthorized"
        )
    
    try:
        user = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        # Strip out omitted fields or explicitly declared null properties
        update_data = data.model_dump(
            exclude_unset = True, 
            exclude_none = True
        )
        
        # Securely process password mutations if modified
        if "password" in update_data:
            update_data["password"] = await hash(update_data["password"])

        update_data["updated_at"] = datetime.now(timezone.utc)

        # Apply structural mutations against targeted dataset criteria
        await user.update({ 
            "$set": update_data
        })

        # Synchronize local object state with downstream state shifts
        await user.sync()
        return user
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in update_user_by_email: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




# soft-delete a targeted registration target
async def delete_user_id(
    id: int, 
    current_user: TokenData
):
    
    if BeanieObjectId(id) != BeanieObjectId(current_user.id):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Unauthorized"
        )
    
    try:
        user = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        # Modify active registry context parameters instead of issuing hard-drops
        await user.delete()

        return Response(status_code = status.HTTP_204_NO_CONTENT)
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in delete_user_by_email: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
