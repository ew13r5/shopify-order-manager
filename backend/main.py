import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from config import get_settings
from database import SessionLocal
from models import Store

logger = logging.getLogger(__name__)


def auto_seed_demo():
    """Seed demo data if the database is empty. Uses advisory lock to prevent races."""
    session = SessionLocal()
    try:
        # Acquire advisory lock (non-blocking)
        result = session.execute(text("SELECT pg_try_advisory_lock(12345)"))
        locked = result.scalar()
        if not locked:
            logger.info("Another worker is seeding demo data, skipping")
            return

        try:
            # Check if demo store exists
            existing = session.query(Store).filter(Store.is_demo.is_(True)).first()
            if existing:
                logger.info("Demo store already exists, skipping seed")
                return

            from seed.demo_seeder import seed_demo_data

            result = seed_demo_data(session)
            logger.info("Demo data seeded: %s", result)
        finally:
            session.execute(text("SELECT pg_advisory_unlock(12345)"))
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.DATA_MODE == "demo":
        try:
            auto_seed_demo()
        except Exception:
            logger.exception("Failed to auto-seed demo data")
    yield


app = FastAPI(
    title="Shopify Order Manager",
    version="1.0.0",
    description="Backend API for Shopify Order Manager dashboard",
    lifespan=lifespan,
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
