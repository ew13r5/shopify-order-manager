from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from api.deps import get_current_provider, get_db, get_store_id
from models import LineItem, Order, Payout, PayoutItem
from providers.base import DataProvider, DateRange

router = APIRouter(prefix="/api", tags=["payouts"])


@router.get("/payouts")
def list_payouts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    period: str = Query("30d"),
    store_id: UUID = Depends(get_store_id),
    db: Session = Depends(get_db),
):
    """Return payout items enriched with product/SKU data, paginated."""
    query = (
        db.query(PayoutItem)
        .join(Payout, Payout.id == PayoutItem.payout_id)
        .join(LineItem, LineItem.id == PayoutItem.line_item_id)
        .join(Order, Order.id == LineItem.order_id)
        .filter(Payout.store_id == store_id)
        .options(
            joinedload(PayoutItem.line_item),
            joinedload(PayoutItem.payout),
        )
    )

    if search:
        s = f"%{search}%"
        query = query.filter(
            (LineItem.title.ilike(s))
            | (LineItem.sku_cleaned.ilike(s))
            | (Order.order_number.ilike(s))
        )

    total = query.count()
    offset = (page - 1) * per_page

    items = query.order_by(Payout.date.desc(), LineItem.title).offset(offset).limit(per_page).all()

    result_items = []
    for pi in items:
        li = pi.line_item
        result_items.append({
            "id": str(pi.id),
            "payout_date": str(pi.payout.date) if pi.payout and pi.payout.date else None,
            "payout_status": pi.payout.status.value if pi.payout and pi.payout.status else None,
            "order_number": li.order.order_number if li and li.order else None,
            "product": li.title if li else None,
            "sku": li.sku_cleaned if li else None,
            "quantity": li.quantity if li else 0,
            "gross_amount": float(pi.gross_amount or 0),
            "fee_amount": float(pi.fee_amount or 0),
            "discount_amount": float(li.discount_amount or 0) if li else 0,
            "refund_amount": float(li.refund_amount or 0) if li else 0,
            "net_amount": float(pi.net_amount or 0),
        })

    # Compute totals for all matching items (not just current page)
    totals_query = (
        db.query(
            func.sum(PayoutItem.gross_amount),
            func.sum(PayoutItem.fee_amount),
            func.sum(PayoutItem.net_amount),
        )
        .join(Payout, Payout.id == PayoutItem.payout_id)
        .filter(Payout.store_id == store_id)
    )
    totals_row = totals_query.one()

    return {
        "items": result_items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "has_next": (offset + per_page) < total,
        "totals": {
            "gross": float(totals_row[0] or 0),
            "fees": float(totals_row[1] or 0),
            "net": float(totals_row[2] or 0),
        },
    }


@router.get("/adjustments")
def list_adjustments(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    type: Optional[str] = None,
    store_id: UUID = Depends(get_store_id),
    provider: DataProvider = Depends(get_current_provider),
):
    date_range = DateRange(start=date_from, end=date_to)
    adjustments = provider.get_adjustments(store_id, date_range)
    result = []
    for a in adjustments:
        if type and a.type.value != type:
            continue
        result.append({
            "id": str(a.id),
            "order_id": str(a.order_id) if a.order_id else None,
            "type": a.type.value if a.type else None,
            "amount": float(a.amount or 0),
            "reason": a.reason,
            "created_at": str(a.created_at) if a.created_at else None,
        })
    return result
