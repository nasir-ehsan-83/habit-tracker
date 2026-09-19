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
    """User account model for authentication and profile."""

    name:           str
    """Full name of the user."""

    username:       str
    """Unique username for login."""

    email:          EmailStr
    """Unique email address for login and notifications."""

    password:       str
    """Hashed password (bcrypt)."""

    avatar:         str | None = None
    """Optional profile picture URL."""

    role:           str = UserRole.user
    """User role: user or admin."""

    status:         UserStatus = UserStatus.active
    """Account status: active, inactive, blocked."""

    created_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Account creation timestamp."""

    updated_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Last profile update timestamp."""

    class Settings:
        """MongoDB collection configuration."""

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