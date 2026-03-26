from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_store_id
from services.analytics_service import get_chart_data, get_summary

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def analytics_summary(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    compare: bool = False,
    store_id: UUID = Depends(get_store_id),
    db: Session = Depends(get_db),
):
    return get_summary(db, store_id, date_from, date_to, compare)


@router.get("/charts/{chart_type}")
def analytics_charts(
    chart_type: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    period: str = Query("month"),
    store_id: UUID = Depends(get_store_id),
    db: Session = Depends(get_db),
):
    return get_chart_data(db, store_id, chart_type, date_from, date_to, period)
