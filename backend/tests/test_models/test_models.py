import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Store, Product, Order, LineItem, Payout, PayoutItem, Adjustment, SyncLog
from models.enums import (
    DataMode, FinancialStatus, FulfillmentStatus, PayoutStatus,
    AdjustmentType, SyncStatus,
)


@pytest.fixture(scope="module")
def engine():
    """In-memory SQLite engine for model tests (no PostgreSQL needed)."""
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


def _make_store(session, **kwargs):
    defaults = dict(
        id=uuid.uuid4(),
        name="Test Store",
        is_demo=True,
        data_mode=DataMode.demo,
    )
    defaults.update(kwargs)
    store = Store(**defaults)
    session.add(store)
    session.flush()
    return store


class TestStoreModel:
    def test_demo_store_no_token(self, session):
        store = _make_store(session, is_demo=True)
        assert store.name == "Test Store"
        assert store.is_demo is True
        assert store.access_token_encrypted is None

    def test_encrypted_column_is_bytes(self, session, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://x:x@localhost/x")
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()
        monkeypatch.setenv("ENCRYPTION_KEY", key)

        # Clear settings cache
        from config import get_settings
        get_settings.cache_clear()

        store = _make_store(session, is_demo=False, data_mode=DataMode.shopify)
        store.access_token = "shpat_test_token_123"
        session.flush()

        assert store.access_token_encrypted is not None
        assert isinstance(store.access_token_encrypted, bytes)
        assert store.access_token == "shpat_test_token_123"

        get_settings.cache_clear()


class TestProductModel:
    def test_sku_and_sku_cleaned(self, session):
        store = _make_store(session)
        product = Product(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_id="prod_1",
            title="Widget",
            sku="SKU\u200B-001",
            sku_cleaned="SKU-001",
        )
        session.add(product)
        session.flush()
        assert product.sku == "SKU\u200B-001"
        assert product.sku_cleaned == "SKU-001"


class TestOrderModel:
    def test_financial_status_enum(self, session):
        store = _make_store(session)
        order = Order(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_id="order_1",
            financial_status=FinancialStatus.paid,
            fulfillment_status=FulfillmentStatus.fulfilled,
            total_price=Decimal("99.99"),
        )
        session.add(order)
        session.flush()
        assert order.financial_status == FinancialStatus.paid
        assert order.fulfillment_status == FulfillmentStatus.fulfilled


class TestLineItemModel:
    def test_order_relationship(self, session):
        store = _make_store(session)
        order = Order(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_id="order_li",
        )
        session.add(order)
        session.flush()

        li = LineItem(
            id=uuid.uuid4(),
            order_id=order.id,
            title="Test Item",
            quantity=2,
            unit_price=Decimal("10.00"),
        )
        session.add(li)
        session.flush()
        assert li.order_id == order.id

    def test_product_id_nullable(self, session):
        store = _make_store(session)
        order = Order(
            id=uuid.uuid4(),
            store_id=store.id,
            shopify_id="order_li2",
        )
        session.add(order)
        session.flush()

        li = LineItem(
            id=uuid.uuid4(),
            order_id=order.id,
            product_id=None,
            title="No Product",
        )
        session.add(li)
        session.flush()
        assert li.product_id is None


class TestPayoutModels:
    def test_payout_items_relationship(self, session):
        store = _make_store(session)
        payout = Payout(
            id=uuid.uuid4(),
            store_id=store.id,
            status=PayoutStatus.paid,
            amount=Decimal("100.00"),
        )
        session.add(payout)
        session.flush()

        item = PayoutItem(
            id=uuid.uuid4(),
            payout_id=payout.id,
            gross_amount=Decimal("100.00"),
            fee_amount=Decimal("2.50"),
            net_amount=Decimal("97.50"),
        )
        session.add(item)
        session.flush()
        assert item.gross_amount == Decimal("100.00")
        assert item.fee_amount == Decimal("2.50")
        assert item.net_amount == Decimal("97.50")


class TestAdjustmentModel:
    def test_adjustment_type(self, session):
        store = _make_store(session)
        adj = Adjustment(
            id=uuid.uuid4(),
            store_id=store.id,
            type=AdjustmentType.refund,
            amount=Decimal("25.00"),
            reason="Customer request",
        )
        session.add(adj)
        session.flush()
        assert adj.type == AdjustmentType.refund
        assert adj.amount == Decimal("25.00")


class TestSyncLogModel:
    def test_sync_log_creation(self, session):
        store = _make_store(session)
        log = SyncLog(
            id=uuid.uuid4(),
            store_id=store.id,
            status=SyncStatus.running,
        )
        session.add(log)
        session.flush()
        assert log.status == SyncStatus.running
        assert log.started_at is not None

    def test_sync_log_errors_json(self, session):
        store = _make_store(session)
        log = SyncLog(
            id=uuid.uuid4(),
            store_id=store.id,
            status=SyncStatus.failed,
            errors=[{"message": "Connection timeout"}],
        )
        session.add(log)
        session.flush()
        assert log.errors == [{"message": "Connection timeout"}]
