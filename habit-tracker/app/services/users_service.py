from fastapi import (
    HTTPException, 
    Response, 
    status
)
from datetime import datetime, timezone
from beanie import BeanieObjectId

from app.core.security import hash
from app.models.users import User
from app.schemas.users import UserUpdate
from app.schemas.token import TokenData
from app.config.logging_handler import logger 




async def get_user_by_id(
    id: BeanieObjectId
) -> User:
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
        
        return user
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_user_by_email: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_user_by_id(
    id: BeanieObjectId, 
    data: UserUpdate
) -> User:
    
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
        
        update_data = data.model_dump(
            exclude_unset = True, 
            exclude_none = True
        )
        
        if "password" in update_data:
            update_data["password"] = await hash(update_data["password"])

        update_data["updated_at"] = datetime.now(timezone.utc)

        await user.update({ 
            "$set": update_data
        })
        
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



