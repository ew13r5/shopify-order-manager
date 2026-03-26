import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from models import LineItem, Product, SyncLog
from models.enums import SyncStatus
from providers.base import DataProvider, SyncResult
from services.sku_cleaner import clean_sku

logger = logging.getLogger(__name__)


def sync_store(session: Session, provider: DataProvider, store_id: UUID) -> SyncResult:
    """Orchestrate the sync process with SyncLog tracking."""
    sync_log = SyncLog(store_id=store_id, status=SyncStatus.running)
    session.add(sync_log)
    session.flush()

    try:
        result = provider.sync_orders(store_id)

        # Apply SKU cleaning to newly synced items
        items_to_clean = (
            session.query(LineItem)
            .join(LineItem.order)
            .filter(LineItem.order.has(store_id=store_id))
            .filter(LineItem.sku_cleaned.is_(None))
            .filter(LineItem.sku.isnot(None))
            .all()
        )
        for item in items_to_clean:
            item.sku_cleaned = clean_sku(item.sku)

        products_to_clean = (
            session.query(Product)
            .filter(Product.store_id == store_id)
            .filter(Product.sku_cleaned.is_(None))
            .filter(Product.sku.isnot(None))
            .all()
        )
        for product in products_to_clean:
            product.sku_cleaned = clean_sku(product.sku)

        sync_log.status = SyncStatus.completed
        sync_log.completed_at = datetime.now(timezone.utc)
        sync_log.orders_synced = result.orders_synced
        sync_log.errors = [str(e) for e in result.errors] if result.errors else None
        session.commit()

        return result

    except Exception as e:
        sync_log.status = SyncStatus.failed
        sync_log.completed_at = datetime.now(timezone.utc)
        sync_log.errors = [str(e)]
        session.commit()
        raise
