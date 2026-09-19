from beanie import BeanieObjectId
from pydantic import (
    BaseModel,
    Field,
    field_validator
)


class Token(BaseModel):
    """Token response model for authentication."""

    access_token: str = Field(
        ...,
        min_length = 1,
        description = "JWT access token for authentication"
    )
    """JWT access token."""

    token_type: str = Field(
        default = "bearer",
        min_length = 1,
        max_length = 20,
        description = "Type of the token (e.g., bearer, refresh)"
    )
    """Token type (bearer, refresh)."""

    @field_validator("access_token")
    @classmethod
    def validate_access_token(cls, v: str) -> str:
        """Ensure access token is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Access token cannot be empty")
        return v.strip()

    @field_validator("token_type")
    @classmethod
    def validate_token_type(cls, v: str) -> str:
        """Ensure token type is not empty and normalize to lowercase."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Token type cannot be empty")
        return v.strip().lower()


class TokenData(BaseModel):
    """Decoded token payload data."""

    id: BeanieObjectId = Field(
        ...,
        description = "User ID stored in the token payload"
    )
    """User ID from token payload."""

    role: str = Field(
        ...,
        min_length = 1,
        max_length = 20,
        description = "User role (e.g., admin, user, moderator)"
    )
    """User role from token payload."""

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure role is not empty and normalize to lowercase."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Role cannot be empty")
        return v.strip().lower()