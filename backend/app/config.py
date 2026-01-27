from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # API
    PROJECT_NAME: str = "EcoModel Hub"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./ecomodel.db"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
