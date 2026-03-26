from uuid import UUID

from providers.base import DataProvider, OrderFilters, PaginatedResult
from services.sku_cleaner import has_hidden_chars


def list_orders(provider: DataProvider, store_id: UUID, filters: OrderFilters) -> PaginatedResult:
    """List orders with filters and pagination."""
    return provider.get_orders(store_id, filters)


def get_order_detail(provider: DataProvider, store_id: UUID, order_id: UUID):
    """Get order detail with has_hidden_chars enrichment on line items."""
    order = provider.get_order_detail(store_id, order_id)
    if order and hasattr(order, "line_items"):
        for li in order.line_items:
            li._has_hidden_chars = has_hidden_chars(li.sku)
    return order


def search_orders(provider: DataProvider, store_id: UUID, query: str) -> PaginatedResult:
    """Search orders by query string."""
    filters = OrderFilters(search_query=query)
    return provider.get_orders(store_id, filters)
