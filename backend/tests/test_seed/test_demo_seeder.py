import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Adjustment, LineItem, Order, Payout, PayoutItem, Product, Store
from seed.demo_seeder import seed_demo_data


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


class TestDemoSeeder:
    def test_creates_all_entities(self, session):
        result = seed_demo_data(session, num_orders=10, num_products=5)
        assert result["products"] == 5
        assert result["orders"] == 10
        assert result["line_items"] > 0
        assert result["payouts"] > 0
        assert result["adjustments"] > 0

    def test_generates_requested_counts(self, session):
        result = seed_demo_data(session, num_orders=20, num_products=8)
        assert session.query(Order).count() >= 20  # >= because previous test data
        assert result["orders"] == 20
        assert result["products"] == 8

    def test_line_items_linked_to_products(self, session):
        result = seed_demo_data(session, num_orders=5, num_products=3)
        store_id = uuid.UUID(result["store_id"])
        orders = session.query(Order).filter(Order.store_id == store_id).all()
        for order in orders:
            items = session.query(LineItem).filter(LineItem.order_id == order.id).all()
            assert len(items) > 0
            for item in items:
                assert item.product_id is not None

    def test_payouts_have_realistic_fees(self, session):
        result = seed_demo_data(session, num_orders=10, num_products=5)
        store_id = uuid.UUID(result["store_id"])
        payout_items = (
            session.query(PayoutItem)
            .join(Payout)
            .filter(Payout.store_id == store_id)
            .all()
        )
        for pi in payout_items:
            if pi.gross_amount and pi.gross_amount > 0:
                fee_rate = pi.fee_amount / pi.gross_amount
                assert Decimal("0.02") <= fee_rate <= Decimal("0.03"), (
                    f"Fee rate {fee_rate} outside 2-3% range"
                )
