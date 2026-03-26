from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


@dataclass
class ItemPayout:
    line_item_id: str
    item_revenue: Decimal
    fee_amount: Decimal
    refund_amount: Decimal
    net_payout: Decimal


@dataclass
class PeriodPayout:
    period_label: str
    gross_revenue: Decimal
    total_fees: Decimal
    total_refunds: Decimal
    net_payout: Decimal


@dataclass
class PayoutSummary:
    total_revenue: Decimal
    total_fees: Decimal
    total_refunds: Decimal
    total_net: Decimal


def calculate_item_payout(
    line_item,
    fee_amount: Optional[Decimal] = None,
    fee_rate: Optional[Decimal] = None,
) -> ItemPayout:
    """Calculate net payout for a single line item."""
    unit_price = getattr(line_item, "unit_price", Decimal("0")) or Decimal("0")
    quantity = getattr(line_item, "quantity", 0) or 0
    discount = getattr(line_item, "discount_amount", Decimal("0")) or Decimal("0")
    tax = getattr(line_item, "tax_amount", Decimal("0")) or Decimal("0")
    refund = getattr(line_item, "refund_amount", Decimal("0")) or Decimal("0")
    li_id = str(getattr(line_item, "id", ""))

    item_revenue = (unit_price * quantity) - discount + tax

    if fee_amount is not None:
        fee = fee_amount
    elif fee_rate is not None:
        fee = round(item_revenue * fee_rate, 2)
    else:
        fee = Decimal("0")

    net_payout = item_revenue - fee - refund

    return ItemPayout(
        line_item_id=li_id,
        item_revenue=item_revenue,
        fee_amount=fee,
        refund_amount=refund,
        net_payout=net_payout,
    )


def group_payouts_by_period(
    payout_items: list,
    period: str = "month",
) -> List[PeriodPayout]:
    """Group payout items by day/week/month."""
    groups = defaultdict(lambda: {"gross": Decimal("0"), "fees": Decimal("0"), "refunds": Decimal("0"), "net": Decimal("0")})

    for item in payout_items:
        date_val = getattr(item, "date", None) or getattr(item, "payout_date", None)
        if date_val is None:
            continue

        if period == "day":
            key = date_val.strftime("%Y-%m-%d")
        elif period == "week":
            key = date_val.strftime("%Y-W%W")
        else:
            key = date_val.strftime("%Y-%m")

        gross = getattr(item, "gross_amount", Decimal("0")) or Decimal("0")
        fee = getattr(item, "fee_amount", Decimal("0")) or Decimal("0")
        refund = getattr(item, "refund_amount", Decimal("0")) or Decimal("0")
        net = getattr(item, "net_amount", Decimal("0")) or Decimal("0")

        groups[key]["gross"] += gross
        groups[key]["fees"] += fee
        groups[key]["refunds"] += refund
        groups[key]["net"] += net

    result = []
    for label in sorted(groups.keys()):
        g = groups[label]
        result.append(PeriodPayout(
            period_label=label,
            gross_revenue=g["gross"],
            total_fees=g["fees"],
            total_refunds=g["refunds"],
            net_payout=g["net"],
        ))
    return result


def calculate_summary(payout_items: list) -> PayoutSummary:
    """Aggregate totals across all payout items."""
    revenue = Decimal("0")
    fees = Decimal("0")
    refunds = Decimal("0")
    net = Decimal("0")

    for item in payout_items:
        revenue += getattr(item, "gross_amount", Decimal("0")) or Decimal("0")
        fees += getattr(item, "fee_amount", Decimal("0")) or Decimal("0")
        refunds += getattr(item, "refund_amount", Decimal("0")) or Decimal("0")
        net += getattr(item, "net_amount", Decimal("0")) or Decimal("0")

    return PayoutSummary(
        total_revenue=revenue,
        total_fees=fees,
        total_refunds=refunds,
        total_net=net,
    )
