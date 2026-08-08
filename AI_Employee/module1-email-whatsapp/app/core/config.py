import os
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Email & WhatsApp Assistant"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = True
    api_prefix: str = "/"

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    ai_provider: str = "openai"
    ai_timeout_seconds: int = 20
    ai_max_retries: int = 3

    gmail_client_id: str | None = None
    gmail_client_secret: str | None = None
    gmail_redirect_uri: str | None = None
    outlook_client_id: str | None = None
    outlook_client_secret: str | None = None
    outlook_tenant_id: str | None = None
    whatsapp_token: str | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_business_account_id: str | None = None
    whisper_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
