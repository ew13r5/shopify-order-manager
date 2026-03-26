from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import LineItem, Order, Payout, Product
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
    if chart_type == "revenue_timeline":
        return _revenue_timeline(session, store_id, date_from, date_to, period)
    elif chart_type == "top_products":
        return _top_products(session, store_id, date_from, date_to)
    elif chart_type == "order_status":
        return _order_status(session, store_id, date_from, date_to)
    elif chart_type == "payout_status":
        return _payout_status(session, store_id, date_from, date_to)
    return {"type": chart_type, "data": []}


def _revenue_timeline(session, store_id, date_from, date_to, period):
    query = session.query(Order).filter(Order.store_id == store_id)
    if date_from:
        query = query.filter(Order.order_created_at >= date_from)
    if date_to:
        query = query.filter(Order.order_created_at <= date_to)

    orders = query.all()
    from collections import defaultdict
    groups = defaultdict(float)
    for o in orders:
        if o.order_created_at and o.total_price:
            if period == "day":
                key = o.order_created_at.strftime("%Y-%m-%d")
            elif period == "week":
                key = o.order_created_at.strftime("%Y-W%W")
            else:
                key = o.order_created_at.strftime("%Y-%m")
            groups[key] += float(o.total_price)

    data = [{"date": k, "revenue": round(v, 2)} for k, v in sorted(groups.items())]
    return {"type": "revenue_timeline", "data": data}


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
    query = session.query(
        Order.financial_status,
        func.count(Order.id),
    ).filter(Order.store_id == store_id)
    if date_from:
        query = query.filter(Order.order_created_at >= date_from)
    if date_to:
        query = query.filter(Order.order_created_at <= date_to)

    results = query.group_by(Order.financial_status).all()
    data = [{"status": r[0].value if r[0] else "unknown", "count": r[1]} for r in results]
    return {"type": "order_status", "data": data}


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
