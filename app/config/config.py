from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings are loaded from the .env file.
    """
    
    # MongoDB Configuration
    MONGO_URL:                      str
    """MongoDB connection string for the main database."""
    
    MONGO_URL_TEST:                 str
    """MongoDB connection string for test database."""
    
    DATABASE_NAME:                  str
    """Name of the main database."""
    
    DATABASE_NAME_TEST:             str
    """Name of the test database."""
    
    # Redis Configuration
    REDIS_HOST:                     str
    """Redis server hostname."""
    
    REDIS_PORT:                     int
    """Redis server port."""
    
    # JWT Authentication
    ACCESS_SECRET_KEY:              str
    """Secret key for signing JWT access tokens."""
    
    REFRESH_SECRET_KEY:             str
    """Secret key for signing JWT refresh tokens."""
    
    ALGORITHM:                      str
    """JWT signing algorithm (e.g., HS256)."""
    
    ACCESS_TOKEN_EXPIRE_MINUTES:    int
    """Access token expiration time in minutes."""
    
    REFRESH_TOKEN_EXPIRE_DAYS:      int
    """Refresh token expiration time in days."""
    
    # SMTP Email Configuration
    SMTP_HOST:                      str
    """SMTP server hostname for sending emails."""
    
    SMTP_PORT:                      int
    """SMTP server port."""
    
    SMTP_USER:                      str
    """SMTP username for authentication."""
    
    SMTP_PASSWORD:                  str
    """SMTP password for authentication."""

    class Config:
        env_file = ".env"
        """Load environment variables from .env file."""


settings: Settings = Settings() # type: ignore
"""Global settings instance for the application."""