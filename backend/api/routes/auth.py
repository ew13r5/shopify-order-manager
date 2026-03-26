from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/shopify/connect")
def shopify_connect(body: dict):
    return {"auth_url": "https://placeholder.shopify.com/oauth"}

@router.post("/shopify/token")
def shopify_token(body: dict):
    return {"status": "connected"}
