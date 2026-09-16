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
    """Base user model with common fields."""

    name:       str = Field(
        min_length = 3, 
        max_length = 50,
        description = "Full name of the user"
    )
    """Full name (3-50 characters)."""

    username:   str = Field(
        min_length = 3, 
        max_length = 30,
        description = "Unique username for the user"
    )
    """Unique username (3-30 characters)."""

    email:      EmailStr = Field(
        ...,
        description = "Email address of the user"
    )
    """Email address."""

    avatar:     str | None = Field(
        default = None,
        description = "URL or path to the user's avatar image"
    )
    """Optional avatar URL."""



class UserCreate(UserBase):
    """Request model for user registration."""

    password: str = Field(
        min_length = 8,
        description = "Password for the user account (minimum 8 characters)"
    )
    """Password (min 8 characters)."""



class UserPrivateOut(UserBase):
    """Response model for private user data (user view)."""

    id:     BeanieObjectId | None = Field(
        default = None, 
        alias = "_id",
        description = "Unique identifier for the user"
    )
    """User identifier."""

    role:   UserRole = Field(
        ...,
        description = "Role of the user (e.g., admin, user)"
    )
    """User role."""

    status: UserStatus = Field(
        ...,
        description = "Current status of the user (e.g., active, inactive)"
    )
    """User status."""

    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v: BeanieObjectId):
        """Convert ObjectId to string."""
        return str(v)



class UserAdminOut(UserBase):
    """Response model for admin user data (includes timestamps)."""

    id:         BeanieObjectId = Field(
        alias = "_id",
        description = "Unique identifier for the user"
    )
    """User identifier."""

    status:     UserStatus = Field(
        ...,
        description = "Current status of the user (e.g., active, inactive)"
    )
    """User status."""

    role:       UserRole = Field(
        ...,
        description = "Role of the user (e.g., admin, user)"
    )
    """User role."""

    created_at: datetime = Field(
        ...,
        description = "Timestamp when the user was created"
    )
    """Creation timestamp."""

    updated_at: datetime = Field(
        ...,
        description = "Timestamp when the user was last updated"
    )
    """Last update timestamp."""

    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v: BeanieObjectId):
        """Convert ObjectId to string."""
        return str(v) 



class UserUpdate(BaseModel):
    """Request model for updating user (all fields optional)."""

    name:       str | None = Field(
        default = None,
        min_length = 3,
        max_length = 50,
        description = "Updated full name of the user"
    )
    """Updated full name."""

    username:   str | None = Field(
        default = None,
        min_length = 3,
        max_length = 30,
        description = "Updated username for the user"
    )
    """Updated username."""

    email:      EmailStr | None = Field(
        default = None,
        description = "Updated email address of the user"
    )
    """Updated email."""

    password:   str | None = Field(
        default = None,
        min_length = 8,
        description = "Updated password for the user account"
    )
    """Updated password (will be hashed)."""

    avatar:     str | None = Field(
        default = None,
        description = "Updated URL or path to the user's avatar"
    )
    """Updated avatar URL."""

    status:     str | None = Field(
        default = None,
        description = "Updated status of the user"
    )
    """Updated user status."""