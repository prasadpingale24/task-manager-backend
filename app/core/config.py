from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import field_validator, AnyHttpUrl


class Settings(BaseSettings):
    PROJECT_NAME: str = "Team Tasks Manager"
    API_V1_PREFIX: str = "/api/v1"

    # PLACEHOLDERS: These should be overridden by .env or environment variables
    DATABASE_URL: str = "sqlite:///./change_me_in_env.db"
    SECRET_KEY: str = "NOT_A_SECRET_CHANGE_ME_IN_ENV"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS Origins - can be a list of strings or a single comma-separated string
    BACKEND_CORS_ORIGINS: Union[List[str], str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
