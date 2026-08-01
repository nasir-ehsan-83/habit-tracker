from datetime import (
    datetime, 
    timezone
)
from pydantic import (
    EmailStr, 
    Field
)
from beanie import Document
from pymongo import (
    IndexModel, 
    ASCENDING
)

from app.utils.enum import (
    UserRole, 
    UserStatus
)



class User(Document):

    name:           str
    username:       str
    email:          EmailStr  
    password:       str

    avatar:         str | None = None
    role:           str = UserRole.user
    status:         UserStatus = UserStatus.active
    
    created_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    updated_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))

    refresh_token:  str | None = None
    

    class Settings:
    
        name = "users"

        indexes = [
            IndexModel(
                [("email", ASCENDING)], 
                unique = True
            ),
            IndexModel(
                [("username", ASCENDING)], 
                unique = True
            ),
        ]
