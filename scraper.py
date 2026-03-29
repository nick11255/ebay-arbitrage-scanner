"""Playwright scraper for eBay sold/completed listing comp data."""

from __future__ import annotations

import asyncio
import re
import logging
from datetime import datetime
from typing import Optional

from types_ import CompData, CompStats

logger = logging.getLogger(__name__)

# Lazy browser init
_browser = None
_playwright = None


async def _get_browser():
    """Initialize Playwright browser lazily."""
    global _browser, _playwright
    if _browser is None:
        from playwright.async_api import async_playwright

        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
        logger.info("Playwright browser launched")
    return _browser


async def close_browser() -> None:
    """Clean shutdown of browser."""
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None


def _parse_price(price_text: str) -> Optional[float]:
    """Extract numeric price from text like '$29.99' or '$1,234.56'."""
    match = re.search(r"\$?([\d,]+\.?\d*)", price_text.replace(",", ""))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def _parse_date(date_text: str) -> Optional[str]:
    """Parse sold date from eBay listing."""
    patterns: list[str] = [
        r"Sold\s+(\w+\s+\d{1,2},?\s*\d{4})",
        r"(\w+\s+\d{1,2},?\s*\d{4})",
        r"(\d{1,2}/\d{1,2}/\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, date_text)
        if match:
            return match.group(1).strip()
    return None


async def scrape_sold_comps(
    query: str,
    model_keywords: Optional[list[str]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    max_results: int = 30,
) -> list[CompData]:
    """Scrape eBay sold listings for comparable sales data.

    Args:
        query: Search query for sold items
        model_keywords: Keywords that must appear in title for model-specific matching
        min_price: Minimum sold price filter
        max_price: Maximum sold price filter
        max_results: Maximum number of comps to return

    Returns:
        List of comp dicts with title, price, date, condition, shipping, url
    """
    browser = await _get_browser()
    page = await browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    )

    comps: list[CompData] = []
    try:
        search_url: str = (
            "https://www.ebay.com/sch/i.html?"
            f"_nkw={query.replace(' ', '+')}"
            "&LH_Complete=1&LH_Sold=1&_sop=13"
        )
        if min_price is not None:
            search_url += f"&_udlo={min_price}"
        if max_price is not None:
            search_url += f"&_udhi={max_price}"

        logger.info(f"Scraping sold comps for: {query}")
        await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        items = await page.query_selector_all(".s-item")

        for item in items[:max_results + 10]:
            try:
                title_el = await item.query_selector(".s-item__title")
                price_el = await item.query_selector(".s-item__price")
                date_el = await item.query_selector(
                    ".s-item__title--tagblock .POSITIVE"
                )
                shipping_el = await item.query_selector(".s-item__shipping")
                condition_el = await item.query_selector(
                    ".SECONDARY_INFO"
                )
                link_el = await item.query_selector(".s-item__link")

                if not title_el or not price_el:
                    continue

                title: str = (await title_el.inner_text()).strip()
                if title.lower() in ("shop on ebay", "results matching fewer words"):
                    continue

                price: Optional[float] = _parse_price(await price_el.inner_text())
                if price is None:
                    continue

                # Model-specific filtering
                if model_keywords:
                    title_lower: str = title.lower()
                    if not all(kw.lower() in title_lower for kw in model_keywords):
                        continue

                sold_date: Optional[str] = None
                if date_el:
                    sold_date = _parse_date(await date_el.inner_text())

                shipping_cost: float = 0.0
                if shipping_el:
                    ship_text: str = (await shipping_el.inner_text()).lower()
                    if "free" in ship_text:
                        shipping_cost = 0.0
                    else:
                        parsed: Optional[float] = _parse_price(ship_text)
                        if parsed is not None:
                            shipping_cost = parsed

                condition: str = ""
                if condition_el:
                    condition = (await condition_el.inner_text()).strip()

                url: str = ""
                if link_el:
                    url = await link_el.get_attribute("href") or ""

                comps.append({
                    "title": title,
                    "price": price,
                    "shipping": shipping_cost,
                    "total": price + shipping_cost,
                    "date": sold_date,
                    "condition": condition,
                    "url": url,
                })

                if len(comps) >= max_results:
                    break

            except Exception as e:
                logger.debug(f"Error parsing comp item: {e}")
                continue

        logger.info(f"Scraped {len(comps)} sold comps for '{query}'")

    except Exception as e:
        logger.error(f"Scraper error for '{query}': {e}")
    finally:
        await page.close()

    return comps


def trim_outliers(comps: list[CompData], pct: float = 0.10) -> list[CompData]:
    """Remove top and bottom percentage of comps by price.

    Args:
        comps: List of comp dicts with 'price' key
        pct: Fraction to trim from each end (default 10%)

    Returns:
        Trimmed list of comps
    """
    if len(comps) < 5:
        return comps

    sorted_comps: list[CompData] = sorted(comps, key=lambda c: c["price"])
    trim_count: int = max(1, int(len(sorted_comps) * pct))
    return sorted_comps[trim_count:-trim_count]


def filter_comps_by_condition(
    comps: list[CompData], condition: str
) -> list[CompData]:
    """Filter comps to match the item's condition.

    When condition is 'used' or 'pre-owned', only return used/pre-owned comps.
    When condition is 'new', only return new comps.
    Falls back to all comps if filtering yields too few results (<3).

    Args:
        comps: List of comp dicts with 'condition' key
        condition: The item's condition string

    Returns:
        Filtered list of comps
    """
    if not condition:
        return comps

    condition_lower: str = condition.lower()

    if "used" in condition_lower or "pre-owned" in condition_lower:
        targets: list[str] = ["used", "pre-owned"]
    elif "new" in condition_lower:
        targets = ["new", "brand new"]
    else:
        return comps

    filtered: list[CompData] = [
        c for c in comps
        if any(t in c.get("condition", "").lower() for t in targets)
    ]

    if len(filtered) < 3:
        return comps

    return filtered


def analyze_comps(comps: list[CompData]) -> CompStats:
    """Analyze scraped comp data to get pricing statistics.

    Returns dict with avg_price, median_price, min_price, max_price,
    price_range, num_comps, sell_through_indicator.
    """
    if not comps:
        return {
            "avg_price": 0, "median_price": 0, "min_price": 0,
            "max_price": 0, "price_range": 0, "num_comps": 0,
            "sell_through": "low",
        }

    prices: list[float] = sorted([c["price"] for c in comps])
    n: int = len(prices)

    avg_price: float = sum(prices) / n
    median_price: float = prices[n // 2] if n % 2 else (prices[n // 2 - 1] + prices[n // 2]) / 2
    min_price: float = prices[0]
    max_price: float = prices[-1]

    # Sell-through indicator based on comp volume
    if n >= 20:
        sell_through = "high"
    elif n >= 10:
        sell_through = "medium"
    else:
        sell_through = "low"

    return {
        "avg_price": round(avg_price, 2),
        "median_price": round(median_price, 2),
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "price_range": round(max_price - min_price, 2),
        "num_comps": n,
        "sell_through": sell_through,
    }
