import pytest

from providers import ProviderManager
from providers.demo_provider import DemoDataProvider


class TestProviderManager:
    def test_initializes_with_demo_mode(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://x:x@localhost/x")
        from config import get_settings
        get_settings.cache_clear()
        manager = ProviderManager()
        assert manager.mode == "demo"
        get_settings.cache_clear()

    def test_get_provider_returns_demo(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://x:x@localhost/x")
        from config import get_settings
        get_settings.cache_clear()
        manager = ProviderManager()
        provider = manager.get_provider(session=None)
        assert isinstance(provider, DemoDataProvider)
        get_settings.cache_clear()

    def test_switch_mode_to_shopify_fails_without_credentials(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://x:x@localhost/x")
        from config import get_settings
        get_settings.cache_clear()
        manager = ProviderManager()
        with pytest.raises(ValueError, match="no Shopify credentials"):
            manager.switch_mode("shopify")
        get_settings.cache_clear()

    def test_switch_mode_invalid(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://x:x@localhost/x")
        from config import get_settings
        get_settings.cache_clear()
        manager = ProviderManager()
        with pytest.raises(ValueError, match="Invalid mode"):
            manager.switch_mode("invalid")
        get_settings.cache_clear()

    def test_switch_mode_to_demo(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://x:x@localhost/x")
        from config import get_settings
        get_settings.cache_clear()
        manager = ProviderManager()
        manager.switch_mode("demo")
        assert manager.mode == "demo"
        get_settings.cache_clear()
