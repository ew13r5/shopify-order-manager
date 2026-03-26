from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.deps import get_store_id

router = APIRouter(prefix="/api/export", tags=["export"])


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
def export_gsheets(store_id: UUID = Depends(get_store_id)):
    return {"task_id": "placeholder", "status": "pending"}
