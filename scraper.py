"""Playwright scraper — get sold listing prices from eBay."""

import re
from statistics import median

# Lazy browser init
_browser = None
_playwright = None


async def _get_browser():
    """Launch browser on first use."""
    global _browser, _playwright
    if _browser is None:
        from playwright.async_api import async_playwright
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
    return _browser


async def close_browser():
    """Shut down the browser."""
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None


def _parse_price(text):
    """Extract a float price from text like '$29.99' or '+$12.00 shipping'."""
    match = re.search(r"\$?([\d,]+\.?\d*)", text.replace(",", ""))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


async def scrape_sold_comps(query):
    """Scrape eBay sold listings and return a list of prices."""
    browser = await _get_browser()
    page = await browser.new_page()
    prices = []

    try:
        url = (
            f"https://www.ebay.com/sch/i.html?"
            f"_nkw={query.replace(' ', '+')}"
            f"&LH_Complete=1&LH_Sold=1&_sop=13"
        )
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        items = await page.query_selector_all(".s-item")

        for item in items[:30]:
            title_el = await item.query_selector(".s-item__title")
            price_el = await item.query_selector(".s-item__price")

            if not title_el or not price_el:
                continue

            title = (await title_el.inner_text()).strip()
            if title.lower() in ("shop on ebay", "results matching fewer words"):
                continue

            price = _parse_price(await price_el.inner_text())
            if price is not None:
                prices.append(price)
    except Exception:
        pass
    finally:
        await page.close()

    return prices


def get_median(prices):
    """Return the median of a list of prices, or 0 if empty."""
    if not prices:
        return 0
    return round(median(prices), 2)
