import logging
from typing import Any, Dict, Optional

import httpx

from config import get_settings

logger = logging.getLogger(__name__)


class ShopifyGraphQLClient:
    def __init__(self, store_domain: str, access_token: str):
        self.store_domain = store_domain
        self.access_token = access_token
        settings = get_settings()
        self.api_version = settings.SHOPIFY_API_VERSION
        self.base_url = f"https://{store_domain}/admin/api/{self.api_version}/graphql.json"
        self.client = httpx.Client(timeout=30.0)

    def execute(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = self.client.post(self.base_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")

        return data

    def close(self):
        self.client.close()
