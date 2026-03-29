"""8-group scan rotation system for staying within 5,000/day API limit."""

import json
import os
import logging
from datetime import datetime, timezone

import config
from products import get_products_by_group, PRODUCTS

logger = logging.getLogger(__name__)

STATE_FILE = "data/rotation_state.json"


def _ensure_data_dir():
    os.makedirs("data", exist_ok=True)


def _load_state() -> dict:
    """Load rotation state from disk."""
    _ensure_data_dir()
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "current_group": 1,
        "last_scan": {},
        "scan_count": 0,
    }


def _save_state(state: dict):
    """Persist rotation state to disk."""
    _ensure_data_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def get_current_group() -> int:
    """Get the current group number to scan."""
    state = _load_state()
    return state["current_group"]


def get_next_scan_group() -> tuple[int, list[dict]]:
    """Get the next group to scan and its products.

    Returns:
        Tuple of (group_number, list of product dicts)
    """
    state = _load_state()
    group = state["current_group"]
    products = get_products_by_group(group)

    # Estimate API calls for this group
    estimated_calls = len(products) * config.CALLS_PER_PRODUCT
    logger.info(
        f"Next scan: Group {group} ({len(products)} products, "
        f"~{estimated_calls} API calls)"
    )

    return group, products


def advance_group():
    """Move to the next scan group after completing current scan."""
    state = _load_state()
    current = state["current_group"]
    now = datetime.now(timezone.utc).isoformat()

    state["last_scan"][str(current)] = now
    state["scan_count"] += 1
    state["current_group"] = (current % config.NUM_GROUPS) + 1

    _save_state(state)
    logger.info(
        f"Advanced from group {current} to {state['current_group']} "
        f"(total scans: {state['scan_count']})"
    )


def get_rotation_status() -> dict:
    """Get current rotation status for display."""
    state = _load_state()
    groups = {}
    for g in range(1, config.NUM_GROUPS + 1):
        products = get_products_by_group(g)
        last = state["last_scan"].get(str(g), "Never")
        groups[g] = {
            "products": len(products),
            "last_scan": last,
            "is_next": g == state["current_group"],
        }

    return {
        "current_group": state["current_group"],
        "total_scans": state["scan_count"],
        "groups": groups,
        "total_products": len(PRODUCTS),
    }


def estimate_daily_calls() -> dict:
    """Estimate total daily API calls based on rotation schedule.

    With 8 groups and scans every SCAN_INTERVAL_MINUTES:
    - scans_per_day = 1440 / interval
    - calls_per_scan = products_in_group * CALLS_PER_PRODUCT
    """
    interval = config.SCAN_INTERVAL_MINUTES
    scans_per_day = 1440 // interval

    # Each scan covers 1 group, so we cycle through all 8 groups
    total_calls = 0
    for g in range(1, config.NUM_GROUPS + 1):
        products = get_products_by_group(g)
        total_calls += len(products) * config.CALLS_PER_PRODUCT

    # In a day we go through scans_per_day scans, each hitting one group
    # Full cycles = scans_per_day / NUM_GROUPS
    full_cycles = scans_per_day / config.NUM_GROUPS
    estimated_daily = int(total_calls * full_cycles)

    return {
        "scans_per_day": scans_per_day,
        "calls_per_full_cycle": total_calls,
        "estimated_daily_calls": estimated_daily,
        "daily_limit": config.DAILY_API_LIMIT,
        "headroom": config.DAILY_API_LIMIT - estimated_daily,
        "within_limit": estimated_daily <= config.DAILY_API_LIMIT,
    }


def format_rotation_status() -> str:
    """Format rotation status for display."""
    status = get_rotation_status()
    estimate = estimate_daily_calls()

    lines = [
        f"**Scan Rotation Status**",
        f"Current Group: {status['current_group']} of {config.NUM_GROUPS}",
        f"Total Scans: {status['total_scans']}",
        f"Total Products: {status['total_products']}",
        "",
        "**Groups:**",
    ]

    for g, info in sorted(status["groups"].items()):
        marker = " << NEXT" if info["is_next"] else ""
        lines.append(
            f"  Group {g}: {info['products']} products | "
            f"Last: {info['last_scan']}{marker}"
        )

    lines.extend([
        "",
        "**API Budget:**",
        f"  Est. daily calls: ~{estimate['estimated_daily_calls']}",
        f"  Daily limit: {estimate['daily_limit']}",
        f"  Headroom: {estimate['headroom']}",
        f"  Status: {'OK' if estimate['within_limit'] else 'OVER LIMIT'}",
    ])

    return "\n".join(lines)
