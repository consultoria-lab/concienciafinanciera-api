from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    openai_api_key: str
    supabase_url: str
    supabase_secret_key: str
    api_key: str
    openai_model: str = "gpt-4o-mini"
    whisper_model: str = "whisper-1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
