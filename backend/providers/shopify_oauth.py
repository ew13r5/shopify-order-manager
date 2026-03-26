import hashlib
import hmac
import secrets
from typing import Optional, Tuple
from urllib.parse import urlencode

import httpx

from config import get_settings

REQUIRED_SCOPES = "read_orders,read_products,read_inventory,read_customers,read_shopify_payments_payouts,read_shopify_payments_disputes"


def generate_auth_url(store_domain: str, redirect_uri: str) -> Tuple[str, str]:
    settings = get_settings()
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.SHOPIFY_API_KEY,
        "scope": REQUIRED_SCOPES,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    url = f"https://{store_domain}/admin/oauth/authorize?{urlencode(params)}"
    return url, state


def validate_hmac(query_params: dict, api_secret: str) -> bool:
    received_hmac = query_params.get("hmac", "")
    params_to_verify = {k: v for k, v in sorted(query_params.items()) if k != "hmac"}
    message = urlencode(params_to_verify)
    computed = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, received_hmac)


def exchange_token(store_domain: str, code: str) -> str:
    settings = get_settings()
    response = httpx.post(
        f"https://{store_domain}/admin/oauth/access_token",
        json={
            "client_id": settings.SHOPIFY_API_KEY,
            "client_secret": settings.SHOPIFY_API_SECRET,
            "code": code,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]
