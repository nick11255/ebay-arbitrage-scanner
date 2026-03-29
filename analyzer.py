"""Deal analysis engine: comp refinement, scoring, and channel routing."""

from __future__ import annotations

import re
import logging
from typing import Optional

import config
from types_ import (
    CompData, CompStats, DealScore, FeeBreakdown, ProfitInfo, ProductConfig,
    ScoreBreakdown,
)

logger = logging.getLogger(__name__)


def calculate_fees(
    sell_price: float, shipping_cost: Optional[float] = None
) -> FeeBreakdown:
    """Calculate eBay fees and net profit components.

    Args:
        sell_price: Expected selling price
        shipping_cost: Shipping cost (uses default if None)

    Returns:
        Dict with ebay_fee, shipping, total_costs
    """
    if shipping_cost is None:
        shipping_cost = config.SHIPPING_ESTIMATE

    ebay_fee = sell_price * (config.EBAY_FEE_PERCENT / 100) + config.EBAY_FEE_FIXED

    return {
        "ebay_fee": round(ebay_fee, 2),
        "shipping": round(shipping_cost, 2),
        "total_costs": round(ebay_fee + shipping_cost, 2),
    }


def calculate_profit(
    buy_price: float, sell_price: float, shipping_cost: Optional[float] = None
) -> ProfitInfo:
    """Calculate profit and margin for a deal.

    Returns:
        Dict with profit, margin, roi, fees breakdown
    """
    fees = calculate_fees(sell_price, shipping_cost)
    profit = sell_price - buy_price - fees["total_costs"]
    margin = (profit / sell_price * 100) if sell_price > 0 else 0
    roi = (profit / buy_price * 100) if buy_price > 0 else 0

    return {
        "buy_price": round(buy_price, 2),
        "sell_price": round(sell_price, 2),
        "profit": round(profit, 2),
        "margin": round(margin, 1),
        "roi": round(roi, 1),
        **fees,
    }


def extract_model_id(title: str) -> Optional[str]:
    """Extract model number/ID from a product title.

    Looks for alphanumeric model identifiers (e.g., DCD771C2, RTX4090, A2842).

    Returns:
        The extracted model ID string, or None if not found.
    """
    # Match patterns like DCD771C2, RTX4090, MX-500, A2842
    # Must have both letters and digits, at least 4 chars
    patterns: list[str] = [
        r'\b([A-Z]{1,5}[-]?\d{2,}[A-Z0-9]*)\b',   # Letters then digits: DCD771C2, RTX4090
        r'\b([A-Z]\d+[A-Z]{2,}[A-Z0-9]*)\b',        # Letter+digits+letters: A7III
        r'\b(\d{1,3}[A-Z]{1,5}\d+[A-Z0-9]*)\b',     # Digits then letters: 5600X, 3070Ti
        r'\b([A-Z]\d{4,})\b',                         # Single letter + digits: A2842
    ]
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None


def refine_comps(comps: list[CompData], product: ProductConfig) -> list[CompData]:
    """Model-specific comp refinement.

    Filters comps to only include items that match the product's
    model identifiers, removing generic or mismatched results.

    Args:
        comps: Raw comp data from scraper
        product: Product entry with model_keywords

    Returns:
        Filtered list of relevant comps
    """
    model_keywords: list[str] = product.get("model_keywords", [])
    if not model_keywords:
        return comps

    refined: list[CompData] = []
    for comp in comps:
        title_lower = comp.get("title", "").lower()
        if all(kw.lower() in title_lower for kw in model_keywords):
            refined.append(comp)

    if len(refined) < 3 and len(comps) > 0:
        # Fall back to partial matching if strict match yields too few
        partial: list[CompData] = []
        for comp in comps:
            title_lower = comp.get("title", "").lower()
            matches = sum(1 for kw in model_keywords if kw.lower() in title_lower)
            if matches >= len(model_keywords) * 0.6:
                partial.append(comp)
        if len(partial) > len(refined):
            refined = partial

    logger.info(f"Comp refinement: {len(comps)} -> {len(refined)} comps")
    return refined


def score_deal(
    buy_price: float,
    comp_stats: CompStats,
    seller_score: float = 100,
    red_flags: int = 0,
) -> DealScore:
    """Calculate composite deal score with channel routing.

    Scoring factors:
    - Profit margin (0-35 pts)
    - Sell-through rate (0-25 pts)
    - Comp confidence (0-15 pts) - based on number of comps
    - Seller trust (0-15 pts)
    - Description quality (0-10 pts) - penalized by red flags

    Returns:
        Dict with score, grade, channel, breakdown
    """
    avg_price: float = comp_stats.get("avg_price", 0)
    if avg_price <= 0:
        return {
            "score": 0, "grade": "F", "channel": "skip",
            "breakdown": {}, "profit_info": {},
        }

    profit_info: ProfitInfo = calculate_profit(buy_price, avg_price)

    # Profit margin score (0-35)
    margin: float = profit_info["margin"]
    if margin >= 40:
        margin_score = 35
    elif margin >= 30:
        margin_score = 30
    elif margin >= 20:
        margin_score = 25
    elif margin >= 15:
        margin_score = 20
    elif margin >= 10:
        margin_score = 15
    elif margin >= 5:
        margin_score = 8
    else:
        margin_score = 0

    # Sell-through score (0-25)
    sell_through: str = comp_stats.get("sell_through", "low")
    sell_scores: dict[str, int] = {"high": 25, "medium": 15, "low": 5}
    sell_score: int = sell_scores.get(sell_through, 5)

    # Comp confidence score (0-15)
    num_comps: int = comp_stats.get("num_comps", 0)
    if num_comps >= 20:
        comp_score = 15
    elif num_comps >= 10:
        comp_score = 12
    elif num_comps >= 5:
        comp_score = 8
    elif num_comps >= 3:
        comp_score = 5
    else:
        comp_score = 2

    # Seller trust score (0-15)
    seller_pts: int = min(15, int(seller_score / 100 * 15))

    # Description quality score (0-10)
    desc_score: int = max(0, 10 - red_flags * 3)

    total: int = margin_score + sell_score + comp_score + seller_pts + desc_score
    total = min(100, max(0, total))

    # Grade
    if total >= 85:
        grade = "A+"
    elif total >= 75:
        grade = "A"
    elif total >= 65:
        grade = "B+"
    elif total >= 55:
        grade = "B"
    elif total >= 45:
        grade = "C"
    elif total >= 35:
        grade = "D"
    else:
        grade = "F"

    # Channel routing
    if total >= config.HOT_DEAL_SCORE:
        channel = "hot_deals"
    elif total >= config.GOOD_DEAL_SCORE:
        channel = "deals"
    elif total >= config.WATCH_DEAL_SCORE:
        channel = "watch"
    else:
        channel = "skip"

    return {
        "score": total,
        "grade": grade,
        "channel": channel,
        "profit_info": profit_info,
        "breakdown": {
            "margin": margin_score,
            "sell_through": sell_score,
            "comp_confidence": comp_score,
            "seller_trust": seller_pts,
            "description": desc_score,
        },
    }


def format_deal_summary(item: dict, deal: DealScore) -> str:
    """Format a deal into a readable summary string."""
    profit = deal["profit_info"]
    return (
        f"**{item.get('title', 'Unknown')}**\n"
        f"Score: {deal['score']}/100 ({deal['grade']})\n"
        f"Buy: ${profit['buy_price']:.2f} | "
        f"Sell: ${profit['sell_price']:.2f} | "
        f"Profit: ${profit['profit']:.2f} ({profit['margin']:.1f}%)\n"
        f"Fees: ${profit['ebay_fee']:.2f} | "
        f"Shipping: ${profit['shipping']:.2f}"
    )
