from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    max_transfer_amount: float = 50_000
    max_agent_steps: int = 8
    daily_transfer_limit: float = 100_000


@lru_cache
def get_settings() -> Settings:
    return Settings()