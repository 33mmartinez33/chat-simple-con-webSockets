from pydantic_settings import BaseSettings

ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

class Settings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str
    ALGORITHM: str

    class Config:
        env_file = ".env"

settings = Settings()
print("ACCESS_TOKEN_EXPIRE_MINUTES:", settings.ACCESS_TOKEN_EXPIRE_MINUTES)