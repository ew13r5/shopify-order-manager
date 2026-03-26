from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_db
from models import Store

router = APIRouter(prefix="/api", tags=["stores"])

@router.get("/stores")
def list_stores(db: Session = Depends(get_db)):
    stores = db.query(Store).all()
    return [{"id": str(s.id), "name": s.name, "shopify_domain": s.shopify_domain, "is_demo": s.is_demo} for s in stores]

@router.post("/stores/{store_id}/sync")
def trigger_sync(store_id: str):
    return {"task_id": "placeholder", "status": "pending"}
