from typing import Optional
from pydantic import (
    BaseModel, 
    EmailStr, 
    ConfigDict, 
    Field, 
    field_validator
)
from datetime import datetime
from bson import ObjectId 

from app.utils.enum import UserStatus, UserRole

class UserBase(BaseModel):
    name: str = Field(
        min_length = 3, 
        max_length = 50
    )
    username: str = Field(
        min_length = 3, 
        max_length = 30
    )
    email: EmailStr

class  UserCreate(UserBase):
    password: str = Field(min_length = 8)

class UserPrivateOut(UserBase):
    id: Optional[str] = Field(None, alias = "_id")
    role: UserRole
    status: UserStatus

    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
class UserAdminOut(UserBase):
    id: str = Field(alias = "_id")
    status: UserStatus
    role: UserRole
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v 
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    status: Optional[str] = None