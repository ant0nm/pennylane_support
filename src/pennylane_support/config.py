from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Application config.
    project_name: str = "PennyLane Support API"
    project_version: str = "1.0.0"

    # PostgreSQL config.
    postgres_db: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: Optional[int] = None


@lru_cache
def get_settings():
    return Settings()
