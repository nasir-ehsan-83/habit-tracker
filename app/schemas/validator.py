from pydantic import (
    BaseModel, 
    EmailStr,
    Field,
    field_validator
)


class VerifyEmail(BaseModel):
    """Request model for email verification."""

    email:      EmailStr = Field(
        ...,
        description = "Email address to verify"
    )
    """Email address to verify."""

    verify_code: int = Field(
        ...,
        ge = 100000,
        le = 999999,
        description = "6-digit verification code sent to the email"
    )
    """6-digit verification code (100000-999999)."""

    @field_validator("verify_code")
    @classmethod
    def validate_verify_code(cls, v: int) -> int:
        """Ensure verification code is a 6-digit number."""
        if v < 100000 or v > 999999:
            raise ValueError("Verification code must be a 6-digit number")
        return v


class ResetPassword(BaseModel):
    """Request model for password reset."""

    email:          EmailStr = Field(
        ...,
        description = "Email address of the user requesting password reset"
    )
    """Email address for password reset."""

    new_password:   str = Field(
        ...,
        min_length = 8,
        description = "New password for the user account (minimum 8 characters)"
    )
    """New password (min 8 characters)."""

    verify_token:   str = Field(
        ...,
        min_length = 1,
        description = "Verification token received via email for password reset"
    )
    """Verification token from email."""

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Ensure password is at least 8 characters."""
        if not v or len(v.strip()) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v.strip()

    @field_validator("verify_token")
    @classmethod
    def validate_verify_token(cls, v: str) -> str:
        """Ensure verification token is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Verification token cannot be empty")
        return v.strip()