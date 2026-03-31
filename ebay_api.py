"""eBay Browse API client — OAuth2 auth and item search."""

import base64
import time
import aiohttp
import config

# Module-level state for auth
_token = None
_token_expiry = 0
_session = None


async def _get_session():
    """Get or create the aiohttp session."""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session


async def close_session():
    """Close the HTTP session."""
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None


async def authenticate():
    """Get OAuth2 token using client credentials grant."""
    global _token, _token_expiry

    if _token and time.time() < _token_expiry - 60:
        return  # Token still valid

    credentials = base64.b64encode(
        f"{config.EBAY_APP_ID}:{config.EBAY_CERT_ID}".encode()
    ).decode()

    session = await _get_session()
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
        _token = data["access_token"]
        _token_expiry = time.time() + data.get("expires_in", 7200)


async def search_items(query, max_price=None, limit=20):
    """Search eBay for active listings. Returns list of item dicts."""
    await authenticate()

    params = {"q": query, "limit": str(limit), "sort": "newlyListed"}
    if max_price is not None:
        params["filter"] = f"price:[..{max_price}],priceCurrency:USD"

    session = await _get_session()
    url = f"{config.EBAY_BROWSE_URL}/item_summary/search"

    async with session.get(
        url,
        params=params,
        headers={
            "Authorization": f"Bearer {_token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        },
    ) as resp:
        if resp.status != 200:
            return []
        data = await resp.json()
        return data.get("itemSummaries", [])
