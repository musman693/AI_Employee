from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Employee CRM"
    app_env: str = "development"
    debug: bool = True
    database_url: str = "sqlite:///./crm.db"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
    )


settings = Settings()
