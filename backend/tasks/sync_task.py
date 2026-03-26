import logging

from celery.exceptions import SoftTimeLimitExceeded

from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="tasks.sync_orders",
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    max_retries=3,
)
def sync_orders_task(self, store_id: str):
    """Sync orders from Shopify for a given store."""
    from database import SessionLocal
    from models import SyncLog
    from models.enums import SyncStatus
    from services.sync_service import sync_store
    from uuid import UUID

    session = SessionLocal()
    try:
        # Check for running sync (idempotent)
        running = (
            session.query(SyncLog)
            .filter(SyncLog.store_id == UUID(store_id), SyncLog.status == SyncStatus.running)
            .first()
        )
        if running:
            return {"skipped": True, "reason": "sync_already_running"}

        from providers import ProviderManager
        pm = ProviderManager()
        provider = pm.get_provider(session=session)

        try:
            result = sync_store(session, provider, UUID(store_id))
            return {
                "orders_synced": result.orders_synced,
                "errors": len(result.errors),
            }
        except SoftTimeLimitExceeded:
            logger.warning("Sync task timed out for store %s", store_id)
            return {"error": "timeout"}

    finally:
        session.close()
