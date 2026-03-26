from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from models import Adjustment, LineItem, Order, Payout, PayoutItem, Product
from providers.base import (
    DataProvider,
    DateRange,
    OrderFilters,
    PaginatedResult,
    ProductFilters,
    SyncResult,
)


class DemoDataProvider(DataProvider):
    def __init__(self, session: Session):
        self.session = session

    def get_orders(self, store_id: UUID, filters: OrderFilters) -> PaginatedResult:
        query = self.session.query(Order).filter(Order.store_id == store_id)

        if filters.date_from:
            query = query.filter(Order.order_created_at >= filters.date_from)
        if filters.date_to:
            query = query.filter(Order.order_created_at <= filters.date_to)
        if filters.status:
            query = query.filter(Order.financial_status == filters.status)
        if filters.fulfillment_status:
            query = query.filter(Order.fulfillment_status == filters.fulfillment_status)
        if filters.sku:
            query = query.join(LineItem).filter(
                LineItem.sku_cleaned.ilike(f"%{filters.sku}%")
            )
        if filters.search_query:
            search = f"%{filters.search_query}%"
            query = query.filter(
                (Order.order_number.ilike(search))
                | (Order.customer_name.ilike(search))
            )

        total = query.count()
        offset = (filters.page - 1) * filters.per_page

        if filters.sort_by:
            col = getattr(Order, filters.sort_by, None)
            if col is not None:
                if filters.sort_dir == "desc":
                    query = query.order_by(col.desc())
                else:
                    query = query.order_by(col.asc())
        else:
            query = query.order_by(Order.order_created_at.desc())

        items = query.options(joinedload(Order.line_items)).offset(offset).limit(filters.per_page).all()

        return PaginatedResult(
            items=items,
            total=total,
            page=filters.page,
            per_page=filters.per_page,
            has_next=(offset + filters.per_page) < total,
        )

    def get_order_detail(self, store_id: UUID, order_id: UUID):
        return (
            self.session.query(Order)
            .filter(Order.store_id == store_id, Order.id == order_id)
            .options(joinedload(Order.line_items).joinedload(LineItem.product))
            .first()
        )

    def get_products(self, store_id: UUID, filters: ProductFilters) -> list:
        query = self.session.query(Product).filter(Product.store_id == store_id)
        if filters.search:
            search = f"%{filters.search}%"
            query = query.filter(
                (Product.title.ilike(search))
                | (Product.sku.ilike(search))
                | (Product.sku_cleaned.ilike(search))
            )
        return query.offset((filters.page - 1) * filters.per_page).limit(filters.per_page).all()

    def get_payouts(self, store_id: UUID, date_range: DateRange) -> list:
        query = (
            self.session.query(Payout)
            .filter(Payout.store_id == store_id)
            .options(joinedload(Payout.items))
        )
        if date_range and date_range.start:
            query = query.filter(Payout.date >= date_range.start)
        if date_range and date_range.end:
            query = query.filter(Payout.date <= date_range.end)
        return query.all()

    def get_adjustments(self, store_id: UUID, date_range: DateRange) -> list:
        query = self.session.query(Adjustment).filter(Adjustment.store_id == store_id)
        if date_range and date_range.start:
            query = query.filter(Adjustment.created_at >= date_range.start)
        if date_range and date_range.end:
            query = query.filter(Adjustment.created_at <= date_range.end)
        return query.all()

    def sync_orders(self, store_id: UUID) -> SyncResult:
        return SyncResult(orders_synced=0, errors=[], duration_seconds=0.0)
