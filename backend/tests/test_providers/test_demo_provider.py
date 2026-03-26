import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import LineItem, Order, Payout, PayoutItem, Product, Store, Adjustment
from models.enums import (
    AdjustmentType, DataMode, FinancialStatus, FulfillmentStatus, PayoutStatus,
)
from providers.base import DateRange, OrderFilters, ProductFilters
from providers.demo_provider import DemoDataProvider


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def session(engine):
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.rollback()
    s.close()


@pytest.fixture
def seeded_data(session):
    store = Store(
        id=uuid.uuid4(), name="Test Store", is_demo=True, data_mode=DataMode.demo
    )
    session.add(store)
    session.flush()

    products = []
    for i in range(3):
        p = Product(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_id=f"prod_{i}",
            title=f"Product {i}",
            sku=f"SKU-{i:03d}",
            sku_cleaned=f"SKU-{i:03d}",
            price=Decimal("10.00"),
        )
        products.append(p)
    session.add_all(products)
    session.flush()

    now = datetime.now(timezone.utc)
    orders = []
    for i in range(5):
        o = Order(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_id=f"order_{i}",
            order_number=f"#{1000+i}",
            customer_name=f"Customer {i}",
            financial_status=FinancialStatus.paid if i < 4 else FinancialStatus.refunded,
            fulfillment_status=FulfillmentStatus.fulfilled,
            total_price=Decimal("30.00"),
            order_created_at=now - timedelta(days=i * 10),
        )
        orders.append(o)
    session.add_all(orders)
    session.flush()

    line_items = []
    for order in orders:
        li = LineItem(
            id=uuid.uuid4(),
            order_id=order.id,
            product_id=products[0].id,
            title=products[0].title,
            sku=products[0].sku,
            sku_cleaned=products[0].sku_cleaned,
            quantity=1,
            unit_price=Decimal("10.00"),
            total_price=Decimal("10.00"),
        )
        line_items.append(li)
    session.add_all(line_items)
    session.flush()

    payout = Payout(
        id=uuid.uuid4(),
        store_id=store.id,
        shopify_payout_id="pay_1",
        date=now.date(),
        amount=Decimal("100.00"),
        status=PayoutStatus.paid,
    )
    session.add(payout)
    session.flush()

    pi = PayoutItem(
        id=uuid.uuid4(),
        payout_id=payout.id,
        line_item_id=line_items[0].id,
        gross_amount=Decimal("10.00"),
        fee_amount=Decimal("0.25"),
        net_amount=Decimal("9.75"),
    )
    session.add(pi)

    adj = Adjustment(
        id=uuid.uuid4(),
        store_id=store.id,
        order_id=orders[4].id,
        type=AdjustmentType.refund,
        amount=Decimal("30.00"),
        reason="Test refund",
    )
    session.add(adj)
    session.flush()

    return {"store": store, "products": products, "orders": orders, "line_items": line_items}


class TestDemoDataProvider:
    def test_get_orders_paginated(self, session, seeded_data):
        provider = DemoDataProvider(session)
        result = provider.get_orders(
            seeded_data["store"].id, OrderFilters(page=1, per_page=2)
        )
        assert len(result.items) == 2
        assert result.total == 5
        assert result.has_next is True

    def test_get_orders_filter_status(self, session, seeded_data):
        provider = DemoDataProvider(session)
        result = provider.get_orders(
            seeded_data["store"].id,
            OrderFilters(status=FinancialStatus.refunded),
        )
        assert result.total == 1

    def test_get_orders_search(self, session, seeded_data):
        provider = DemoDataProvider(session)
        result = provider.get_orders(
            seeded_data["store"].id,
            OrderFilters(search_query="Customer 0"),
        )
        assert result.total >= 1

    def test_get_order_detail(self, session, seeded_data):
        provider = DemoDataProvider(session)
        order = seeded_data["orders"][0]
        detail = provider.get_order_detail(seeded_data["store"].id, order.id)
        assert detail is not None
        assert len(detail.line_items) > 0

    def test_get_products(self, session, seeded_data):
        provider = DemoDataProvider(session)
        products = provider.get_products(
            seeded_data["store"].id, ProductFilters()
        )
        assert len(products) == 3

    def test_get_payouts(self, session, seeded_data):
        provider = DemoDataProvider(session)
        payouts = provider.get_payouts(seeded_data["store"].id, DateRange())
        assert len(payouts) >= 1
        assert len(payouts[0].items) > 0

    def test_get_adjustments(self, session, seeded_data):
        provider = DemoDataProvider(session)
        adjustments = provider.get_adjustments(seeded_data["store"].id, DateRange())
        assert len(adjustments) >= 1

    def test_sync_orders_noop(self, session, seeded_data):
        provider = DemoDataProvider(session)
        result = provider.sync_orders(seeded_data["store"].id)
        assert result.orders_synced == 0
