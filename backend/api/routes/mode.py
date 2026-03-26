from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_provider_manager
from api.schemas.common import ModeResponse
from providers import ProviderManager

router = APIRouter(prefix="/api", tags=["mode"])

@router.get("/mode", response_model=ModeResponse)
def get_mode(pm: ProviderManager = Depends(get_provider_manager)):
    return ModeResponse(mode=pm.mode, connection_status="connected" if pm.mode == "shopify" else "demo")

@router.post("/mode", response_model=ModeResponse)
def switch_mode(body: dict, pm: ProviderManager = Depends(get_provider_manager)):
    mode = body.get("mode")
    if not mode:
        raise HTTPException(400, detail="mode is required")
    try:
        pm.switch_mode(mode)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return ModeResponse(mode=pm.mode, connection_status="connected" if pm.mode == "shopify" else "demo")
