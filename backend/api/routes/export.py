import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_store_id
from config import get_settings

router = APIRouter(prefix="/api/export", tags=["export"])
logger = logging.getLogger(__name__)


@router.get("/csv")
def export_csv(
    type: str = Query(...),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    store_id: UUID = Depends(get_store_id),
):
    if not date_from or not date_to:
        raise HTTPException(400, detail="date_from and date_to are required")
    return {"status": "placeholder"}


@router.get("/xlsx")
def export_xlsx(
    type: str = Query(...),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    store_id: UUID = Depends(get_store_id),
):
    if not date_from or not date_to:
        raise HTTPException(400, detail="date_from and date_to are required")
    return {"status": "placeholder"}


@router.post("/gsheets")
def export_gsheets(
    store_id: UUID = Depends(get_store_id),
    db: Session = Depends(get_db),
):
    settings = get_settings()

    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        raise HTTPException(400, detail="GOOGLE_SERVICE_ACCOUNT_JSON not configured")
    if not settings.GOOGLE_SPREADSHEET_ID:
        raise HTTPException(400, detail="GOOGLE_SPREADSHEET_ID not configured")

    from export.sheets_exporter import SheetsExporter

    try:
        exporter = SheetsExporter(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
        result = exporter.export(db, store_id, settings.GOOGLE_SPREADSHEET_ID)
        return {
            "status": "success",
            "url": result["url"],
            "orders": result["orders"],
            "line_items": result["line_items"],
            "payouts": result["payouts"],
        }
    except Exception as e:
        logger.exception("Google Sheets export failed")
        raise HTTPException(500, detail=f"Export failed: {str(e)}")
