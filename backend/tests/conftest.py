import os
import sys

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set required env vars before any app imports
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/shopify_orders")


@pytest.fixture(scope="session")
def test_db_url():
    """Create a test database and return its URL."""
    base_url = os.environ.get(
        "DATABASE_URL", "postgresql://user:pass@localhost:5432/shopify_orders"
    )
    # Connect to default postgres database to create test DB
    admin_url = base_url.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    test_db_name = "test_shopify_orders"
    test_url = base_url.rsplit("/", 1)[0] + f"/{test_db_name}"

    with admin_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
        conn.execute(text(f"CREATE DATABASE {test_db_name}"))

    yield test_url

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(
            text(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{test_db_name}'"
            )
        )
        conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))


@pytest.fixture(scope="session")
def test_engine(test_db_url):
    """Create engine bound to test database."""
    engine = create_engine(test_db_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def run_migrations(test_engine, test_db_url, monkeypatch_session):
    """Run Alembic migrations on test database."""
    monkeypatch_session.setenv("DATABASE_URL", test_db_url)

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def monkeypatch_session():
    """Session-scoped monkeypatch."""
    from _pytest.monkeypatch import MonkeyPatch

    m = MonkeyPatch()
    yield m
    m.undo()


@pytest.fixture
def db_session(test_engine):
    """Yields a session with transaction rollback per test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, expire_on_commit=False)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden DB dependency."""
    from fastapi.testclient import TestClient

    from database import get_db
    from main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
