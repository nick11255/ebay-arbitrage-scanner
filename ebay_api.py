"""eBay Browse API client with OAuth2 and rate limiting."""

import asyncio
import base64
import time
import logging
from datetime import datetime, timezone
from typing import Optional
import aiohttp

import config

logger = logging.getLogger(__name__)


class EbayAPI:
    """eBay Browse API client with automatic token refresh and rate limiting."""

    def __init__(self):
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0
        self.session: Optional[aiohttp.ClientSession] = None
        self.api_calls_today: int = 0
        self.api_calls_reset: datetime = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        self._lock = asyncio.Lock()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    def _check_daily_reset(self):
        now = datetime.now(timezone.utc)
        if now.date() > self.api_calls_reset.date():
            self.api_calls_today = 0
            self.api_calls_reset = now.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

    def can_make_call(self) -> bool:
        self._check_daily_reset()
        return self.api_calls_today < config.DAILY_API_LIMIT

    def get_api_usage(self) -> dict:
        self._check_daily_reset()
        return {
            "used": self.api_calls_today,
            "limit": config.DAILY_API_LIMIT,
            "remaining": config.DAILY_API_LIMIT - self.api_calls_today,
            "percent": round(self.api_calls_today / config.DAILY_API_LIMIT * 100, 1),
        }

    async def _authenticate(self):
        """Get OAuth2 token using client credentials."""
        async with self._lock:
            if self.access_token and time.time() < self.token_expiry - 60:
                return

            credentials = base64.b64encode(
                f"{config.EBAY_APP_ID}:{config.EBAY_CERT_ID}".encode()
            ).decode()

            session = await self._get_session()
            async with session.post(
                config.EBAY_AUTH_URL,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {credentials}",
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "https://api.ebay.com/oauth/api_scope",
                },
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"eBay auth failed ({resp.status}): {text}")
                data = await resp.json()
                self.access_token = data["access_token"]
                self.token_expiry = time.time() + data.get("expires_in", 7200)
                logger.info("eBay OAuth token refreshed")

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        """Make authenticated API request with rate limiting."""
        if not self.can_make_call():
            raise Exception(
                f"Daily API limit reached ({config.DAILY_API_LIMIT} calls)"
            )

        await self._authenticate()
        session = await self._get_session()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["X-EBAY-C-MARKETPLACE-ID"] = config.EBAY_MARKETPLACE
        headers["X-EBAY-C-ENDUSERCTX"] = (
            f"contextualLocation=country=US,zip={config.DEFAULT_LOCATION}"
        )

        async with session.request(method, url, headers=headers, **kwargs) as resp:
            self.api_calls_today += 1

            if resp.status == 200:
                return await resp.json()
            elif resp.status == 429:
                logger.warning("Rate limited by eBay API, waiting 60s")
                await asyncio.sleep(60)
                return await self._request(method, url, headers=headers, **kwargs)
            else:
                text = await resp.text()
                logger.error(f"eBay API error ({resp.status}): {text}")
                return {}

    async def search_items(
        self,
        query: str,
        category_id: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        condition: Optional[str] = None,
        limit: int = 50,
        sort: str = "newlyListed",
    ) -> list[dict]:
        """Search eBay Browse API for active listings."""
        params = {
            "q": query,
            "limit": str(min(limit, 200)),
            "sort": sort,
        }

        filters = []
        if category_id:
            params["category_ids"] = category_id
        if min_price is not None:
            filters.append(f"price:[{min_price}..],priceCurrency:USD")
        if max_price is not None:
            filters.append(f"price:[..{max_price}],priceCurrency:USD")
        if condition:
            filters.append(f"conditionIds:{{{condition}}}")
        if filters:
            params["filter"] = ",".join(filters)

        url = f"{config.EBAY_BROWSE_URL}/item_summary/search"
        data = await self._request("GET", url, params=params)

        items = data.get("itemSummaries", [])
        logger.info(f"Search '{query}': found {len(items)} items")
        return items

    async def get_item(self, item_id: str) -> dict:
        """Get detailed item info from Browse API."""
        url = f"{config.EBAY_BROWSE_URL}/item/{item_id}"
        return await self._request("GET", url)

    async def search_with_exclusions(
        self,
        query: str,
        exclude_keywords: list[str],
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search and filter out items matching exclude keywords."""
        items = await self.search_items(
            query=query,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
        )

        if not exclude_keywords:
            return items

        exclude_lower = [kw.lower() for kw in exclude_keywords]
        filtered = []
        for item in items:
            title = item.get("title", "").lower()
            if not any(kw in title for kw in exclude_lower):
                filtered.append(item)

        logger.info(
            f"Filtered {len(items) - len(filtered)} items by exclusions, "
            f"{len(filtered)} remaining"
        )
        return filtered
