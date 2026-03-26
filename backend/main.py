import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import get_settings
from database import SessionLocal
from models import Store
from providers import ProviderManager

logger = logging.getLogger(__name__)


def auto_seed_demo():
    """Seed demo data if the database is empty. Uses advisory lock to prevent races."""
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT pg_try_advisory_lock(12345)"))
        locked = result.scalar()
        if not locked:
            logger.info("Another worker is seeding demo data, skipping")
            return

        try:
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
    app.state.provider_manager = ProviderManager()
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

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
from api.routes import mode, auth, stores, orders, line_items, payouts, analytics, export, demo

app.include_router(mode.router)
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(orders.router)
app.include_router(line_items.router)
app.include_router(payouts.router)
app.include_router(analytics.router)
app.include_router(export.router)
app.include_router(demo.router)


# Global error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail), "code": f"HTTP_{exc.status_code}", "detail": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "code": "VALIDATION_ERROR", "detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": "INTERNAL_ERROR", "detail": None},
    )


@app.get("/api/health")
def health_check():
    pm = getattr(app.state, "provider_manager", None)
    return {"status": "ok", "mode": pm.mode if pm else "unknown"}
