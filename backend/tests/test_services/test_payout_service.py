from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from services.payout_service import (
    ItemPayout,
    PayoutSummary,
    calculate_item_payout,
    calculate_summary,
    group_payouts_by_period,
)


@dataclass
class MockLineItem:
    id: str = "li-1"
    unit_price: Decimal = Decimal("10.00")
    quantity: int = 3
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    refund_amount: Decimal = Decimal("0")


@dataclass
class MockPayoutItem:
    date: date = None
    payout_date: date = None
    gross_amount: Decimal = Decimal("100.00")
    fee_amount: Decimal = Decimal("2.50")
    refund_amount: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("97.50")


class TestCalculateItemPayout:
    def test_with_fee_amount(self):
        li = MockLineItem()
        result = calculate_item_payout(li, fee_amount=Decimal("0.75"))
        assert result.item_revenue == Decimal("30.00")
        assert result.fee_amount == Decimal("0.75")
        assert result.net_payout == Decimal("29.25")

    def test_with_fee_rate(self):
        li = MockLineItem()
        result = calculate_item_payout(li, fee_rate=Decimal("0.025"))
        assert result.item_revenue == Decimal("30.00")
        assert result.fee_amount == Decimal("0.75")
        assert result.net_payout == Decimal("29.25")

    def test_with_discount(self):
        li = MockLineItem(discount_amount=Decimal("5.00"))
        result = calculate_item_payout(li, fee_amount=Decimal("0"))
        assert result.item_revenue == Decimal("25.00")

    def test_with_tax(self):
        li = MockLineItem(tax_amount=Decimal("2.40"))
        result = calculate_item_payout(li, fee_amount=Decimal("0"))
        assert result.item_revenue == Decimal("32.40")

    def test_with_refund(self):
        li = MockLineItem(refund_amount=Decimal("10.00"))
        result = calculate_item_payout(li, fee_amount=Decimal("0"))
        assert result.net_payout == Decimal("20.00")

    def test_zero_quantity(self):
        li = MockLineItem(quantity=0)
        result = calculate_item_payout(li, fee_amount=Decimal("0"))
        assert result.item_revenue == Decimal("0")

    def test_uses_decimal(self):
        li = MockLineItem()
        result = calculate_item_payout(li, fee_amount=Decimal("0.75"))
        assert isinstance(result.item_revenue, Decimal)
        assert isinstance(result.net_payout, Decimal)


class TestGroupPayoutsByPeriod:
    def test_groups_by_month(self):
        items = [
            MockPayoutItem(date=date(2025, 1, 15)),
            MockPayoutItem(date=date(2025, 1, 20)),
            MockPayoutItem(date=date(2025, 2, 10)),
        ]
        result = group_payouts_by_period(items, "month")
        assert len(result) == 2
        assert result[0].period_label == "2025-01"
        assert result[0].gross_revenue == Decimal("200.00")


class TestCalculateSummary:
    def test_totals(self):
        items = [
            MockPayoutItem(gross_amount=Decimal("100"), fee_amount=Decimal("2.50"), net_amount=Decimal("97.50")),
            MockPayoutItem(gross_amount=Decimal("200"), fee_amount=Decimal("5.00"), net_amount=Decimal("195.00")),
        ]
        result = calculate_summary(items)
        assert result.total_revenue == Decimal("300")
        assert result.total_fees == Decimal("7.50")
        assert result.total_net == Decimal("292.50")
