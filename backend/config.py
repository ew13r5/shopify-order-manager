from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Shopify credentials
    SHOPIFY_STORE_URL: Optional[str] = None
    SHOPIFY_ACCESS_TOKEN: Optional[str] = None
    SHOPIFY_API_KEY: Optional[str] = None
    SHOPIFY_API_SECRET: Optional[str] = None

    # Encryption
    ENCRYPTION_KEY: Optional[str] = None

    # Google Sheets
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None

    # App mode
    DATA_MODE: str = "demo"

    # Seed defaults
    DEFAULT_SEED_ORDERS: int = 500
    DEFAULT_SEED_PRODUCTS: int = 50

    # Shopify API
    SHOPIFY_API_VERSION: str = "2025-01"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @model_validator(mode="after")
    def validate_shopify_mode(self) -> "Settings":
        if self.DATA_MODE == "shopify" and not self.ENCRYPTION_KEY:
            raise ValueError(
                "ENCRYPTION_KEY is required when DATA_MODE is 'shopify'"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
