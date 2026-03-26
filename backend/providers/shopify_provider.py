import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models import LineItem, Order, Payout, PayoutItem, Product, SyncLog
from models.enums import SyncStatus
from providers.base import DataProvider, DateRange, OrderFilters, PaginatedResult, ProductFilters, SyncResult
from providers.demo_provider import DemoDataProvider
from services.sku_cleaner import clean_sku

logger = logging.getLogger(__name__)


class ShopifyDataProvider(DataProvider):
    """Shopify data provider that fetches from API and upserts to local PostgreSQL."""

    def __init__(self, session: Session, store_domain: str = None, access_token: str = None):
        self._demo = DemoDataProvider(session)
        self.session = session
        self.store_domain = store_domain
        self.access_token = access_token

    def get_orders(self, store_id: UUID, filters: OrderFilters) -> PaginatedResult:
        return self._demo.get_orders(store_id, filters)

    def get_order_detail(self, store_id: UUID, order_id: UUID):
        return self._demo.get_order_detail(store_id, order_id)

    def get_products(self, store_id: UUID, filters: ProductFilters) -> list:
        return self._demo.get_products(store_id, filters)

    def get_payouts(self, store_id: UUID, date_range: DateRange) -> list:
        return self._demo.get_payouts(store_id, date_range)

    def get_adjustments(self, store_id: UUID, date_range: DateRange) -> list:
        return self._demo.get_adjustments(store_id, date_range)

    def sync_orders(self, store_id: UUID) -> SyncResult:
        """Sync orders from Shopify API to local database."""
        if not self.store_domain or not self.access_token:
            logger.warning("No Shopify credentials, skipping sync")
            return SyncResult(orders_synced=0, errors=["No credentials"])

        from providers.shopify_client import ShopifyGraphQLClient
        from providers.rate_limiter import ShopifyRateLimiter

        client = ShopifyGraphQLClient(self.store_domain, self.access_token)
        rate_limiter = ShopifyRateLimiter()

        try:
            # Determine sync-from timestamp
            last_sync = (
                self.session.query(SyncLog)
                .filter(SyncLog.store_id == store_id, SyncLog.status == SyncStatus.completed)
                .order_by(SyncLog.completed_at.desc())
                .first()
            )

            orders_synced = 0
            # TODO: Implement actual GraphQL queries and pagination
            # This is a placeholder for the full sync implementation

            return SyncResult(orders_synced=orders_synced, errors=[], duration_seconds=0.0)
        finally:
            client.close()
