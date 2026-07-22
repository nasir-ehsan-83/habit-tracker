from pydantic_settings import BaseSettings

# provide connection with .env file to use .env data
class Settings(BaseSettings):
    MONGO_URL: str
    MONGO_URL_TEST: str

    DATABASE_NAME: str
    DATABASE_NAME_TEST: str
    
    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str

    ALGORITHM: str
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    class Config:
        env_file = ".env"

settings = Settings()