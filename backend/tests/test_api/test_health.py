import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

from fastapi.testclient import TestClient
from main import app
from providers import ProviderManager

# Initialize provider_manager on app.state for tests (lifespan doesn't run in TestClient by default)
if not hasattr(app.state, "provider_manager"):
    app.state.provider_manager = ProviderManager()

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_404_returns_standard_error():
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "code" in data


def test_mode_endpoint():
    response = client.get("/api/mode")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert data["mode"] in ("demo", "shopify")
