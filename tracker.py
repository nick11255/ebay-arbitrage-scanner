"""Product health tracking, purchase/sale logging, and API usage tracking."""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

DATA_DIR = "data"
HEALTH_FILE = os.path.join(DATA_DIR, "product_health.json")
TRADES_FILE = os.path.join(DATA_DIR, "trades.json")
API_LOG_FILE = os.path.join(DATA_DIR, "api_usage.json")


def _ensure_data_dir():
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


def _save_json(filepath: str, data: dict):
    _ensure_data_dir()
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ==================== Product Health ====================

def record_scan(product_name: str, listings_found: int, deals_found: int):
    """Record scan results for a product."""
    health = _load_json(HEALTH_FILE)
    now = datetime.now(timezone.utc).isoformat()

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

    h = health[product_name]
    h["total_scans"] += 1
    h["total_listings"] += listings_found
    h["total_deals"] += deals_found
    h["last_scan"] = now
    if deals_found > 0:
        h["last_deal"] = now

    _save_json(HEALTH_FILE, health)


def record_claim(product_name: str):
    """Record a deal claim for a product."""
    health = _load_json(HEALTH_FILE)
    if product_name in health:
        health[product_name]["total_claims"] = (
            health[product_name].get("total_claims", 0) + 1
        )
        _save_json(HEALTH_FILE, health)


def get_product_health(product_name: Optional[str] = None) -> dict:
    """Get health data for one or all products."""
    health = _load_json(HEALTH_FILE)
    if product_name:
        return health.get(product_name, {})
    return health


def get_underperformers(min_scans: int = 10) -> list[dict]:
    """Find products with poor performance for auto-purge suggestions.

    Criteria:
    - Scanned at least min_scans times
    - Zero deals found, OR
    - Very low deal-to-scan ratio (< 2%)
    """
    health = _load_json(HEALTH_FILE)
    underperformers = []

    for name, h in health.items():
        if h["total_scans"] < min_scans:
            continue

        deal_ratio = h["total_deals"] / h["total_scans"] if h["total_scans"] > 0 else 0

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
    health = _load_json(HEALTH_FILE)
    if not health:
        return "No product health data yet. Run some scans first!"

    lines = ["**Product Health Report**", ""]

    # Sort by deal ratio descending
    sorted_products = sorted(
        health.items(),
        key=lambda x: x[1]["total_deals"] / max(x[1]["total_scans"], 1),
        reverse=True,
    )

    for name, h in sorted_products[:25]:
        scans = h["total_scans"]
        deals = h["total_deals"]
        claims = h.get("total_claims", 0)
        ratio = deals / scans * 100 if scans > 0 else 0

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
    underperformers = get_underperformers()
    if not underperformers:
        return "No underperformers found. All products are performing adequately."

    lines = [
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

def log_purchase(user_id: str, item: str, price: float, notes: str = "") -> dict:
    """Log a purchase (bought item)."""
    trades = _load_json(TRADES_FILE)
    if "purchases" not in trades:
        trades["purchases"] = []

    entry = {
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


def log_sale(user_id: str, item: str, price: float, notes: str = "") -> dict:
    """Log a sale (sold item). Tries to match with a purchase."""
    trades = _load_json(TRADES_FILE)
    if "sales" not in trades:
        trades["sales"] = []

    entry = {
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


def get_user_stats(user_id: str) -> dict:
    """Get trading stats for a user."""
    trades = _load_json(TRADES_FILE)

    purchases = [
        p for p in trades.get("purchases", []) if p["user_id"] == user_id
    ]
    sales = [
        s for s in trades.get("sales", []) if s["user_id"] == user_id
    ]

    total_spent = sum(p["price"] for p in purchases)
    total_revenue = sum(s["price"] for s in sales)
    total_profit = total_revenue - total_spent

    # Matched trades (purchase + sale)
    matched = [p for p in purchases if p.get("sold")]
    matched_profit = sum(
        p.get("sold_price", 0) - p["price"] for p in matched
    )

    unsold = [p for p in purchases if not p.get("sold")]
    unsold_value = sum(p["price"] for p in unsold)

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
    stats = get_user_stats(user_id)

    profit_emoji = "+" if stats["total_profit"] >= 0 else ""

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
