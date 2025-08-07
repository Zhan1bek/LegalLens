from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

env_path = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    openai_api_key: str = ""
    database_url: PostgresDsn
    ollama_url: str = "http://localhost:11434"

    model_config = SettingsConfigDict(
        env_file=env_path,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
