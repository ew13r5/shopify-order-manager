from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.deps import get_current_provider, get_store_id
from providers.base import DataProvider, DateRange

router = APIRouter(prefix="/api", tags=["payouts"])


@router.get("/payouts")
def list_payouts(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    period: str = Query("month"),
    store_id: UUID = Depends(get_store_id),
    provider: DataProvider = Depends(get_current_provider),
):
    date_range = DateRange(start=date_from, end=date_to)
    payouts = provider.get_payouts(store_id, date_range)
    result = []
    for p in payouts:
        items = [
            {
                "line_item_id": str(pi.line_item_id) if pi.line_item_id else None,
                "gross_amount": float(pi.gross_amount or 0),
                "fee_amount": float(pi.fee_amount or 0),
                "net_amount": float(pi.net_amount or 0),
            }
            for pi in (p.items or [])
        ]
        result.append({
            "id": str(p.id),
            "date": str(p.date) if p.date else None,
            "amount": float(p.amount or 0),
            "status": p.status.value if p.status else None,
            "items": items,
        })
    return result


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
