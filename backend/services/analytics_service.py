from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Adjustment, LineItem, Order, Payout, PayoutItem, Product
from models.enums import FinancialStatus, FulfillmentStatus


def get_summary(
    session: Session,
    store_id,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    compare: bool = False,
) -> Dict[str, Any]:
    """Return 5 summary card values with optional period comparison."""
    current = _compute_summary(session, store_id, date_from, date_to)

    result = {**current}

    if compare and date_from and date_to:
        period_length = date_to - date_from
        prev_to = date_from
        prev_from = prev_to - period_length

        previous = _compute_summary(session, store_id, prev_from, prev_to)

        comparison = {}
        for key in ["total_orders", "revenue", "average_order_value", "refund_rate", "fulfillment_rate"]:
            prev_val = previous.get(key, 0)
            curr_val = current.get(key, 0)
            if prev_val and prev_val != 0:
                change = ((curr_val - prev_val) / prev_val) * 100
                comparison[f"{key}_change"] = round(float(change), 1)
            else:
                comparison[f"{key}_change"] = None
        result["comparison"] = comparison

    return result


def _compute_summary(session, store_id, date_from, date_to) -> dict:
    query = session.query(Order).filter(Order.store_id == store_id)
    if date_from:
        query = query.filter(Order.order_created_at >= date_from)
    if date_to:
        query = query.filter(Order.order_created_at <= date_to)

    total_orders = query.count()
    revenue_result = session.query(func.sum(Order.total_price)).filter(
        Order.store_id == store_id
    )
    if date_from:
        revenue_result = revenue_result.filter(Order.order_created_at >= date_from)
    if date_to:
        revenue_result = revenue_result.filter(Order.order_created_at <= date_to)
    revenue = revenue_result.scalar() or Decimal("0")

    avg = float(revenue) / total_orders if total_orders > 0 else 0

    refunded_count = query.filter(
        Order.financial_status.in_([FinancialStatus.refunded, FinancialStatus.partially_refunded])
    ).count()
    refund_rate = (refunded_count / total_orders * 100) if total_orders > 0 else 0

    fulfilled_query = session.query(Order).filter(
        Order.store_id == store_id,
        Order.fulfillment_status == FulfillmentStatus.fulfilled,
    )
    if date_from:
        fulfilled_query = fulfilled_query.filter(Order.order_created_at >= date_from)
    if date_to:
        fulfilled_query = fulfilled_query.filter(Order.order_created_at <= date_to)
    fulfilled_count = fulfilled_query.count()
    fulfillment_rate = (fulfilled_count / total_orders * 100) if total_orders > 0 else 0

    return {
        "total_orders": total_orders,
        "revenue": float(revenue),
        "average_order_value": round(avg, 2),
        "refund_rate": round(refund_rate, 1),
        "fulfillment_rate": round(fulfillment_rate, 1),
    }


def get_chart_data(
    session: Session,
    store_id,
    chart_type: str,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    period: str = "month",
) -> Dict[str, Any]:
    """Return chart data for the specified type."""
    handlers = {
        "revenue": _revenue_timeline,
        "revenue_timeline": _revenue_timeline,
        "top_products": _top_products,
        "order_status": _order_status,
        "payout_timeline": _payout_timeline,
        "payout_status": _payout_status,
    }
    handler = handlers.get(chart_type)
    if handler:
        if handler in (_revenue_timeline,):
            return handler(session, store_id, date_from, date_to, period)
        return handler(session, store_id, date_from, date_to)
    return {"type": chart_type, "data": []}


def _revenue_timeline(session, store_id, date_from, date_to, period="day"):
    query = session.query(Order).filter(Order.store_id == store_id)
    if date_from:
        query = query.filter(Order.order_created_at >= date_from)
    if date_to:
        query = query.filter(Order.order_created_at <= date_to)

    orders = query.all()
    # Use sortable key for chronological order, display key for labels
    revenue_by_sort_key = defaultdict(float)
    display_labels = {}
    for o in orders:
        if o.order_created_at and o.total_price:
            if period == "day":
                sort_key = o.order_created_at.strftime("%Y-%m-%d")
                display_labels[sort_key] = o.order_created_at.strftime("%b %d")
            elif period == "week":
                sort_key = o.order_created_at.strftime("%Y-W%W")
                display_labels[sort_key] = o.order_created_at.strftime("W%W %Y")
            else:
                sort_key = o.order_created_at.strftime("%Y-%m")
                display_labels[sort_key] = o.order_created_at.strftime("%b %Y")
            revenue_by_sort_key[sort_key] += float(o.total_price)

    data = [
        {"date": display_labels[k], "revenue": round(revenue_by_sort_key[k], 2)}
        for k in sorted(revenue_by_sort_key.keys())
    ]
    return {"type": "revenue", "data": data}


def _top_products(session, store_id, date_from, date_to, limit=10):
    query = (
        session.query(
            Product.title,
            func.sum(LineItem.total_price).label("revenue"),
        )
        .join(LineItem, LineItem.product_id == Product.id)
        .join(Order, Order.id == LineItem.order_id)
        .filter(Order.store_id == store_id)
    )
    if date_from:
        query = query.filter(Order.order_created_at >= date_from)
    if date_to:
        query = query.filter(Order.order_created_at <= date_to)

    results = query.group_by(Product.title).order_by(func.sum(LineItem.total_price).desc()).limit(limit).all()
    data = [{"name": r[0], "revenue": float(r[1] or 0)} for r in results]
    return {"type": "top_products", "data": data}


def _order_status(session, store_id, date_from, date_to):
    """Return fulfillment status breakdown for the pie chart."""
    query = session.query(
        Order.fulfillment_status,
        func.count(Order.id),
    ).filter(Order.store_id == store_id)
    if date_from:
        query = query.filter(Order.order_created_at >= date_from)
    if date_to:
        query = query.filter(Order.order_created_at <= date_to)

    results = query.group_by(Order.fulfillment_status).all()

    label_map = {
        "fulfilled": "Fulfilled",
        "unfulfilled": "Unfulfilled",
        "partial": "Partially Fulfilled",
    }

    data = []
    for r in results:
        status_val = r[0].value if r[0] else "unknown"
        data.append({
            "status": label_map.get(status_val, status_val),
            "count": r[1],
        })
    return {"type": "order_status", "data": data}


def _payout_timeline(session, store_id, date_from, date_to):
    """Return payout data grouped by month with gross/fees/net breakdown."""
    query = (
        session.query(Payout)
        .filter(Payout.store_id == store_id)
    )
    if date_from:
        query = query.filter(Payout.date >= date_from)
    if date_to:
        query = query.filter(Payout.date <= date_to)

    payouts = query.all()
    if not payouts:
        return {"type": "payout_timeline", "data": []}

    payout_ids = [p.id for p in payouts]
    items = session.query(PayoutItem).filter(PayoutItem.payout_id.in_(payout_ids)).all()

    # Group items by payout
    payout_item_map = defaultdict(list)
    for item in items:
        payout_item_map[item.payout_id].append(item)

    groups = defaultdict(lambda: {"gross": 0.0, "fees": 0.0, "net": 0.0})
    display_labels = {}
    for p in payouts:
        if p.date:
            sort_key = p.date.strftime("%Y-%m")
            display_labels[sort_key] = p.date.strftime("%b %Y")
        else:
            sort_key = "0000-00"
            display_labels[sort_key] = "Unknown"
        p_items = payout_item_map.get(p.id, [])
        for pi in p_items:
            groups[sort_key]["gross"] += float(pi.gross_amount or 0)
            groups[sort_key]["fees"] += float(pi.fee_amount or 0)
            groups[sort_key]["net"] += float(pi.net_amount or 0)

    data = [
        {
            "date": display_labels[k],
            "gross": round(groups[k]["gross"], 2),
            "fees": round(groups[k]["fees"], 2),
            "net": round(groups[k]["net"], 2),
        }
        for k in sorted(groups.keys())
    ]
    return {"type": "payout_timeline", "data": data}


def _payout_status(session, store_id, date_from, date_to):
    query = session.query(
        Payout.status,
        func.count(Payout.id),
    ).filter(Payout.store_id == store_id)
    if date_from:
        query = query.filter(Payout.date >= date_from)
    if date_to:
        query = query.filter(Payout.date <= date_to)

    results = query.group_by(Payout.status).all()
    data = [{"status": r[0].value if r[0] else "unknown", "count": r[1]} for r in results]
    return {"type": "payout_status", "data": data}
