from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

T = TypeVar("T")


@dataclass
class OrderFilters:
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None
    fulfillment_status: Optional[str] = None
    search_query: Optional[str] = None
    sku: Optional[str] = None
    product_id: Optional[UUID] = None
    page: int = 1
    per_page: int = 20
    sort_by: Optional[str] = None
    sort_dir: Optional[str] = None


@dataclass
class ProductFilters:
    search: Optional[str] = None
    page: int = 1
    per_page: int = 20


@dataclass
class DateRange:
    start: datetime = None
    end: datetime = None


@dataclass
class PaginatedResult:
    items: list = field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    has_next: bool = False


@dataclass
class SyncResult:
    orders_synced: int = 0
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0


class DataProvider(ABC):
    @abstractmethod
    def get_orders(self, store_id: UUID, filters: OrderFilters) -> PaginatedResult:
        ...

    @abstractmethod
    def get_order_detail(self, store_id: UUID, order_id: UUID) -> Any:
        ...

    @abstractmethod
    def get_products(self, store_id: UUID, filters: ProductFilters) -> list:
        ...

    @abstractmethod
    def get_payouts(self, store_id: UUID, date_range: DateRange) -> list:
        ...

    @abstractmethod
    def get_adjustments(self, store_id: UUID, date_range: DateRange) -> list:
        ...

    @abstractmethod
    def sync_orders(self, store_id: UUID) -> SyncResult:
        ...
