from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_provider_manager
from providers import ProviderManager
from seed.demo_seeder import seed_demo_data

router = APIRouter(prefix="/api/demo", tags=["demo"])

@router.post("/seed")
def seed_demo(db: Session = Depends(get_db), pm: ProviderManager = Depends(get_provider_manager)):
    if pm.mode != "demo":
        raise HTTPException(403, detail="Seed is only available in demo mode")
    result = seed_demo_data(db, num_orders=500, num_products=50)
    return result

@router.post("/reset")
def reset_demo(db: Session = Depends(get_db), pm: ProviderManager = Depends(get_provider_manager)):
    if pm.mode != "demo":
        raise HTTPException(403, detail="Reset is only available in demo mode")
    from models import Store
    demo_stores = db.query(Store).filter(Store.is_demo.is_(True)).all()
    for store in demo_stores:
        db.delete(store)
    db.commit()
    result = seed_demo_data(db, num_orders=500, num_products=50)
    return result
