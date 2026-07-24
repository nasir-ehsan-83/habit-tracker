from types import FunctionType
from typing import List
from fastapi import (
    Depends, 
    HTTPException, 
    status
)
from app.dependencies.current_user import get_current_user
from app.schemas.token import TokenData

def require_role(allowed_roles: List[str]) -> FunctionType:
    
    async def role_checker(current_user: TokenData = Depends(get_current_user)) -> str:
        
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Access denied"
            )
        
        return current_user.role
    
    return role_checker