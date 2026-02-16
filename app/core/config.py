from pydantic_settings import BaseSettings 
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Task Manager API"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./task_manager.db"

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",      # React dev
        "http://127.0.0.1:3000",
        "http://localhost:19006",     # Expo web
    ]
    SECRET_KEY: str = "bf48c8d48eb5ca844764226e2dd51335"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
