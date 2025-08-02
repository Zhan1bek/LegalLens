from functools import lru_cache
from pathlib import Path
from pydantic import PostgresDsn
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseSettings):
    openai_api_key: str = ""
    database_url: PostgresDsn

    class Config:
        env_file = ".env"
        env_prefix = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
