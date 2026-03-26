import os

import pytest


class TestSettings:
    def test_loads_from_env(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")

        from config import Settings

        s = Settings()
        assert s.DATABASE_URL == "postgresql://user:pass@localhost/testdb"
        assert s.REDIS_URL == "redis://localhost:6379/1"

    def test_defaults(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")

        from config import Settings

        s = Settings()
        assert s.DATA_MODE == "demo"
        assert s.DEFAULT_SEED_ORDERS == 500
        assert s.DEFAULT_SEED_PRODUCTS == 50
        assert s.SHOPIFY_API_VERSION == "2025-01"
        assert s.CORS_ORIGINS == "http://localhost:3000"

    def test_cors_origins_list(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, http://localhost:5173")

        from config import Settings

        s = Settings()
        assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:5173"]

    def test_shopify_mode_requires_encryption_key(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("DATA_MODE", "shopify")

        from config import Settings

        with pytest.raises(ValueError, match="ENCRYPTION_KEY is required"):
            Settings()

    def test_shopify_mode_with_encryption_key(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("DATA_MODE", "shopify")
        monkeypatch.setenv("ENCRYPTION_KEY", "test-key-123")

        from config import Settings

        s = Settings()
        assert s.DATA_MODE == "shopify"
        assert s.ENCRYPTION_KEY == "test-key-123"
