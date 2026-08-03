from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    MONGO_URL:                      str
    MONGO_URL_TEST:                 str

    DATABASE_NAME:                  str
    DATABASE_NAME_TEST:             str
    
    REDIS_HOST:                     str
    REDIS_PORT:                     int

    ACCESS_SECRET_KEY:              str
    REFRESH_SECRET_KEY:             str

    ALGORITHM:                      str
    
    ACCESS_TOKEN_EXPIRE_MINUTES:    int
    REFRESH_TOKEN_EXPIRE_DAYS:      int

    SMTP_HOST:                      str
    SMTP_PORT:                      int
    SMTP_USER:                      str
    SMTP_PASSWORD:                  str


    class Config:
        env_file = ".env"


settings: Settings = Settings() # type: ignore