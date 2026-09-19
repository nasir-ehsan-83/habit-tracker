from types import FunctionType
from typing import List
from fastapi import (
    Depends, 
    HTTPException, 
    status
)
from app.dependencies.current_user import get_current_user
from app.schemas.token import TokenData



def required_role(allowed_roles: List[str]) -> FunctionType:
    """Role-based access control dependency.

    Creates a dependency that checks if the authenticated user has
    one of the allowed roles.

    Args:
        allowed_roles: List of roles permitted to access the endpoint.

    Returns:
        FunctionType: FastAPI dependency that validates user role.

    Raises:
        HTTPException 403: If user role is not in allowed_roles.

    Example:
        @router.get("/admin")
        async def admin_route(
            current_user: str = Depends(required_role(["ADMIN"]))
        ):
            return {"message": "Admin access granted"}
    """
    
    async def role_checker(current_user: TokenData = Depends(get_current_user)) -> str:
        """Check if current user has an allowed role."""
        
        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Access denied"
            )
        
        return current_user.role
    
    return role_checker