from typing import Optional

from config import get_settings
from providers.base import DataProvider
from providers.demo_provider import DemoDataProvider


class ProviderManager:
    def __init__(self, session_factory=None):
        settings = get_settings()
        self._mode = settings.DATA_MODE
        self._session_factory = session_factory

    @property
    def mode(self) -> str:
        return self._mode

    def get_provider(self, session=None) -> DataProvider:
        if self._mode == "demo":
            return DemoDataProvider(session)
        elif self._mode == "shopify":
            # ShopifyDataProvider implemented in section-07
            return DemoDataProvider(session)  # Fallback until implemented
        raise ValueError(f"Unknown mode: {self._mode}")

    def switch_mode(self, mode: str):
        if mode not in ("demo", "shopify"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'demo' or 'shopify'")
        if mode == "shopify":
            settings = get_settings()
            has_token = bool(settings.SHOPIFY_ACCESS_TOKEN and settings.SHOPIFY_STORE_URL)
            has_oauth = bool(settings.SHOPIFY_API_KEY and settings.SHOPIFY_API_SECRET)
            if not (has_token or has_oauth):
                raise ValueError(
                    "Cannot switch to shopify mode: no Shopify credentials configured"
                )
        self._mode = mode
