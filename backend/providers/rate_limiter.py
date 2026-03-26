import logging
import random
import time

logger = logging.getLogger(__name__)


class ShopifyRateLimiter:
    def __init__(self, max_retries: int = 5):
        self.max_retries = max_retries
        self.available_points = 1000
        self.restore_rate = 50

    def check_before_request(self, estimated_cost: int = 10):
        if estimated_cost > self.available_points:
            sleep_time = (estimated_cost - self.available_points) / self.restore_rate
            logger.info("Rate limit: sleeping %.1f seconds", sleep_time)
            time.sleep(sleep_time)

    def update_from_response(self, throttle_status: dict):
        if throttle_status:
            self.available_points = throttle_status.get("currentlyAvailable", self.available_points)
            self.restore_rate = throttle_status.get("restoreRate", self.restore_rate)

    def handle_429(self, retry_after: float = None, attempt: int = 0):
        if attempt >= self.max_retries:
            raise Exception("Max retries exceeded for Shopify rate limit")
        if retry_after:
            time.sleep(retry_after)
        else:
            delay = min(1 * (2 ** attempt) + random.random(), 60)
            time.sleep(delay)
