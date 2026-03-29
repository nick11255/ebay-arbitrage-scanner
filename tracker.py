"""Product health tracking, purchase/sale logging, and API usage tracking."""

from __future__ import annotations

import json
import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from types_ import ProductHealth, TradeEntry, UnderperformerInfo, UserStats

logger = logging.getLogger(__name__)

DATA_DIR: str = "data"
HEALTH_FILE: str = os.path.join(DATA_DIR, "product_health.json")
TRADES_FILE: str = os.path.join(DATA_DIR, "trades.json")
API_LOG_FILE: str = os.path.join(DATA_DIR, "api_usage.json")
POSTED_DEALS_FILE: str = os.path.join(DATA_DIR, "posted_deals.json")


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(filepath: str) -> dict:
    _ensure_data_dir()
    if os.path.exists(filepath):
        try:
            with open(filepath) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def _save_json(filepath: str, data: dict | list) -> None:
    _ensure_data_dir()
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ==================== Product Health ====================

def record_scan(product_name: str, listings_found: int, deals_found: int) -> None:
    """Record scan results for a product."""
    health: dict = _load_json(HEALTH_FILE)
    now: str = datetime.now(timezone.utc).isoformat()

    if product_name not in health:
        health[product_name] = {
            "total_scans": 0,
            "total_listings": 0,
            "total_deals": 0,
            "total_claims": 0,
            "first_scan": now,
            "last_scan": now,
            "last_deal": None,
        }

    h: dict = health[product_name]
    h["total_scans"] += 1
    h["total_listings"] += listings_found
    h["total_deals"] += deals_found
    h["last_scan"] = now
    if deals_found > 0:
        h["last_deal"] = now

    _save_json(HEALTH_FILE, health)


def record_claim(product_name: str) -> None:
    """Record a deal claim for a product."""
    health: dict = _load_json(HEALTH_FILE)
    if product_name in health:
        health[product_name]["total_claims"] = (
            health[product_name].get("total_claims", 0) + 1
        )
        _save_json(HEALTH_FILE, health)


def get_product_health(product_name: Optional[str] = None) -> dict:
    """Get health data for one or all products."""
    health: dict = _load_json(HEALTH_FILE)
    if product_name:
        return health.get(product_name, {})
    return health


def get_underperformers(min_scans: int = 10) -> list[UnderperformerInfo]:
    """Find products with poor performance for auto-purge suggestions.

    Criteria:
    - Scanned at least min_scans times
    - Zero deals found, OR
    - Very low deal-to-scan ratio (< 2%)
    """
    health: dict = _load_json(HEALTH_FILE)
    underperformers: list[UnderperformerInfo] = []

    for name, h in health.items():
        if h["total_scans"] < min_scans:
            continue

        deal_ratio: float = h["total_deals"] / h["total_scans"] if h["total_scans"] > 0 else 0

        if h["total_deals"] == 0 or deal_ratio < 0.02:
            underperformers.append({
                "name": name,
                "scans": h["total_scans"],
                "deals": h["total_deals"],
                "claims": h.get("total_claims", 0),
                "deal_ratio": round(deal_ratio * 100, 1),
                "last_deal": h.get("last_deal", "Never"),
            })

    underperformers.sort(key=lambda x: x["deal_ratio"])
    return underperformers


def format_product_health() -> str:
    """Format product health report."""
    health: dict = _load_json(HEALTH_FILE)
    if not health:
        return "No product health data yet. Run some scans first!"

    lines: list[str] = ["**Product Health Report**", ""]

    # Sort by deal ratio descending
    sorted_products: list[tuple[str, dict]] = sorted(
        health.items(),
        key=lambda x: x[1]["total_deals"] / max(x[1]["total_scans"], 1),
        reverse=True,
    )

    for name, h in sorted_products[:25]:
        scans: int = h["total_scans"]
        deals: int = h["total_deals"]
        claims: int = h.get("total_claims", 0)
        ratio: float = deals / scans * 100 if scans > 0 else 0

        if ratio >= 10:
            status = "HOT"
        elif ratio >= 5:
            status = "GOOD"
        elif ratio >= 2:
            status = "OK"
        else:
            status = "COLD"

        lines.append(
            f"[{status}] **{name}**: {deals} deals / {scans} scans "
            f"({ratio:.1f}%) | {claims} claims"
        )

    if len(health) > 25:
        lines.append(f"\n... and {len(health) - 25} more products")

    return "\n".join(lines)


def format_autopurge() -> str:
    """Format auto-purge suggestions."""
    underperformers: list[UnderperformerInfo] = get_underperformers()
    if not underperformers:
        return "No underperformers found. All products are performing adequately."

    lines: list[str] = [
        "**Auto-Purge Suggestions**",
        "These products have consistently low performance:",
        "",
    ]

    for u in underperformers[:15]:
        lines.append(
            f"- **{u['name']}**: {u['deals']} deals in {u['scans']} scans "
            f"({u['deal_ratio']}%) | Last deal: {u['last_deal']}"
        )

    return "\n".join(lines)


# ==================== Trade Tracking ====================

def log_purchase(
    user_id: str, item: str, price: float, notes: str = ""
) -> TradeEntry:
    """Log a purchase (bought item)."""
    trades: dict = _load_json(TRADES_FILE)
    if "purchases" not in trades:
        trades["purchases"] = []

    entry: TradeEntry = {
        "user_id": user_id,
        "item": item,
        "price": price,
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sold": False,
    }
    trades["purchases"].append(entry)
    _save_json(TRADES_FILE, trades)
    return entry


def log_sale(
    user_id: str, item: str, price: float, notes: str = ""
) -> TradeEntry:
    """Log a sale (sold item). Tries to match with a purchase."""
    trades: dict = _load_json(TRADES_FILE)
    if "sales" not in trades:
        trades["sales"] = []

    entry: TradeEntry = {
        "user_id": user_id,
        "item": item,
        "price": price,
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    trades["sales"].append(entry)

    # Try to match with an unsold purchase
    for purchase in trades.get("purchases", []):
        if (
            purchase["user_id"] == user_id
            and purchase["item"].lower() == item.lower()
            and not purchase.get("sold", False)
        ):
            purchase["sold"] = True
            purchase["sold_price"] = price
            purchase["sold_date"] = entry["timestamp"]
            break

    _save_json(TRADES_FILE, trades)
    return entry


def get_user_stats(user_id: str) -> UserStats:
    """Get trading stats for a user."""
    trades: dict = _load_json(TRADES_FILE)

    purchases: list[dict] = [
        p for p in trades.get("purchases", []) if p["user_id"] == user_id
    ]
    sales: list[dict] = [
        s for s in trades.get("sales", []) if s["user_id"] == user_id
    ]

    total_spent: float = sum(p["price"] for p in purchases)
    total_revenue: float = sum(s["price"] for s in sales)
    total_profit: float = total_revenue - total_spent

    # Matched trades (purchase + sale)
    matched: list[dict] = [p for p in purchases if p.get("sold")]
    matched_profit: float = sum(
        p.get("sold_price", 0) - p["price"] for p in matched
    )

    unsold: list[dict] = [p for p in purchases if not p.get("sold")]
    unsold_value: float = sum(p["price"] for p in unsold)

    return {
        "total_purchases": len(purchases),
        "total_sales": len(sales),
        "total_spent": round(total_spent, 2),
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "matched_trades": len(matched),
        "matched_profit": round(matched_profit, 2),
        "unsold_items": len(unsold),
        "unsold_value": round(unsold_value, 2),
    }


def format_user_stats(user_id: str, username: str = "You") -> str:
    """Format user trading stats."""
    stats: UserStats = get_user_stats(user_id)

    profit_emoji: str = "+" if stats["total_profit"] >= 0 else ""

    return (
        f"**Trading Stats for {username}**\n"
        f"\n"
        f"Purchases: {stats['total_purchases']} (${stats['total_spent']:.2f})\n"
        f"Sales: {stats['total_sales']} (${stats['total_revenue']:.2f})\n"
        f"Net P&L: {profit_emoji}${stats['total_profit']:.2f}\n"
        f"\n"
        f"Matched Trades: {stats['matched_trades']} "
        f"(Profit: ${stats['matched_profit']:.2f})\n"
        f"Unsold Inventory: {stats['unsold_items']} items "
        f"(${stats['unsold_value']:.2f} invested)"
    )


# ==================== Deal Posting Tracker ====================

def record_posted_deal(
    product_name: str,
    buy_price: float,
    sold_median: float,
    estimated_profit: float,
    margin: float,
    deal_score: int,
    seller_rating: float,
    url: str,
) -> None:
    """Record a deal that was posted to Discord."""
    _ensure_data_dir()
    filepath: str = POSTED_DEALS_FILE
    deals: list[dict]
    if os.path.exists(filepath):
        try:
            with open(filepath) as f:
                deals = json.load(f)
        except (json.JSONDecodeError, IOError):
            deals = []
    else:
        deals = []

    deals.append({
        "date": datetime.now(timezone.utc).isoformat(),
        "product": product_name,
        "buy_price": buy_price,
        "sold_median": sold_median,
        "estimated_profit": estimated_profit,
        "margin": margin,
        "deal_score": deal_score,
        "seller_rating": seller_rating,
        "url": url,
    })
    _save_json(filepath, deals)


def get_posted_deals() -> list[dict]:
    """Get all posted deals."""
    filepath: str = POSTED_DEALS_FILE
    if os.path.exists(filepath):
        try:
            with open(filepath) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def get_dashboard_stats() -> dict:
    """Compute analytics dashboard statistics."""
    health: dict = _load_json(HEALTH_FILE)
    deals: list[dict] = get_posted_deals()
    now: datetime = datetime.now(timezone.utc)
    today_start: datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start: datetime = today_start - timedelta(days=today_start.weekday())

    # Count scans and deals by time period
    total_scanned_all: int = sum(h.get("total_listings", 0) for h in health.values())
    total_scans_all: int = sum(h.get("total_scans", 0) for h in health.values())

    scanned_today: int = 0
    scanned_week: int = 0
    for h in health.values():
        last_scan_str: str = h.get("last_scan", "")
        if last_scan_str:
            try:
                last_scan = datetime.fromisoformat(last_scan_str.replace("Z", "+00:00"))
                if last_scan >= today_start:
                    scanned_today += h.get("total_listings", 0)
                if last_scan >= week_start:
                    scanned_week += h.get("total_listings", 0)
            except (ValueError, TypeError):
                pass

    # Posted deals by time period
    posted_today: int = 0
    posted_week: int = 0
    posted_all: int = len(deals)
    scores: list[int] = []

    for d in deals:
        scores.append(d.get("deal_score", 0))
        try:
            dt = datetime.fromisoformat(d["date"].replace("Z", "+00:00"))
            if dt >= today_start:
                posted_today += 1
            if dt >= week_start:
                posted_week += 1
        except (ValueError, TypeError, KeyError):
            pass

    avg_score: float = sum(scores) / len(scores) if scores else 0

    # Category breakdown
    categories: dict[str, int] = {}
    for d in deals:
        cat: str = d.get("product", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1

    # Top/bottom products by hit rate
    product_rates: list[tuple[str, float, int]] = []
    for name, h in health.items():
        if h["total_scans"] >= 1:
            ratio: float = h["total_deals"] / h["total_scans"] * 100
            product_rates.append((name, ratio, h["total_deals"]))

    product_rates.sort(key=lambda x: -x[1])
    top_5: list[tuple[str, float, int]] = product_rates[:5]
    bottom_5: list[tuple[str, float, int]] = product_rates[-5:] if len(product_rates) >= 5 else product_rates

    return {
        "scanned_today": scanned_today,
        "scanned_week": scanned_week,
        "scanned_all": total_scanned_all,
        "total_scans": total_scans_all,
        "posted_today": posted_today,
        "posted_week": posted_week,
        "posted_all": posted_all,
        "avg_score": round(avg_score, 1),
        "categories": categories,
        "top_5": top_5,
        "bottom_5": bottom_5,
    }
