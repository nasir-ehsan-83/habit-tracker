from beanie import BeanieObjectId
from pydantic import (
    BaseModel, 
    EmailStr, 
    ConfigDict, 
    Field, 
    field_validator
)
from datetime import datetime

from app.utils.enum import (
    UserStatus, 
    UserRole
)



class UserBase(BaseModel):
    
    name:       str = Field(
        min_length = 3, 
        max_length = 50
    )
    
    username:   str = Field(
        min_length = 3, 
        max_length = 30
    )
    
    email:      EmailStr
    avatar:     str | None = None



class  UserCreate(UserBase):
    password: str = Field(min_length = 8)



class UserPrivateOut(UserBase):
    
    id:         BeanieObjectId | None= Field(
        default = None, 
        alias = "_id"
    )
    
    role:       UserRole
    status:     UserStatus

    
    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

    
    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v: BeanieObjectId):
        return str(v)



class UserAdminOut(UserBase):
    
    id:         BeanieObjectId = Field(alias = "_id")
    status:     UserStatus
    role:       UserRole
    created_at: datetime
    updated_at: datetime
    
    
    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

    
    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v: BeanieObjectId):
        return str(v) 
    


class UserUpdate(BaseModel):
    
    name:       str | None      = None
    username:   str | None      = None
    email:      EmailStr | None = None
    password:   str | None      = None
    avatar:     str | None      = None
    status:     str | None      = None