"""Description verification and red flag detection for eBay listings."""

import re
import logging
import config

logger = logging.getLogger(__name__)


def check_red_flags(title: str, description: str = "") -> dict:
    """Scan listing title and description for red flags.

    Args:
        title: Listing title
        description: Listing description HTML/text

    Returns:
        Dict with flags found, count, risk_level, details
    """
    text = f"{title} {description}".lower()
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    found_flags = []
    for keyword in config.RED_FLAG_KEYWORDS:
        if keyword.lower() in text:
            # Determine if it's in title or description
            location = []
            if keyword.lower() in title.lower():
                location.append("title")
            if description and keyword.lower() in description.lower():
                location.append("description")
            found_flags.append({
                "keyword": keyword,
                "location": " & ".join(location) if location else "text",
            })

    # Additional pattern checks
    patterns = [
        (r"(?:no|without|missing)\s+(?:box|manual|accessories|charger|cable|remote)",
         "Missing components"),
        (r"(?:crack|chip|scratch|dent|ding)\s*(?:ed|s|ing)?",
         "Physical damage mentioned"),
        (r"(?:does\s+not|doesn\'t|won\'t|can\'t)\s+(?:work|turn|power|charge|connect)",
         "Functionality issue"),
        (r"(?:selling|sold)\s+(?:as[- ]is|for parts)",
         "As-is / for parts sale"),
        (r"(?:icloud|frp|activation)\s*lock",
         "Account lock issue"),
        (r"(?:blacklist|bad\s+(?:esn|imei))",
         "Blacklisted device"),
    ]

    for pattern, label in patterns:
        if re.search(pattern, text):
            if not any(f["keyword"] == label for f in found_flags):
                found_flags.append({"keyword": label, "location": "pattern"})

    count = len(found_flags)
    if count == 0:
        risk = "clean"
    elif count <= 2:
        risk = "caution"
    elif count <= 4:
        risk = "warning"
    else:
        risk = "danger"

    return {
        "flags": found_flags,
        "count": count,
        "risk_level": risk,
    }


def verify_listing(item: dict) -> dict:
    """Full listing verification combining description and seller checks.

    Args:
        item: eBay item dict from Browse API

    Returns:
        Dict with red_flags, condition_match, listing_quality score
    """
    title = item.get("title", "")
    description = item.get("description", "")
    condition = item.get("condition", "")

    red_flags = check_red_flags(title, description)

    # Check condition consistency
    condition_issues = []
    condition_lower = condition.lower() if condition else ""
    title_lower = title.lower()
    desc_lower = description.lower() if description else ""

    if "new" in condition_lower:
        used_indicators = ["used", "open box", "opened", "tested", "pre-owned"]
        for indicator in used_indicators:
            if indicator in title_lower or indicator in desc_lower:
                condition_issues.append(
                    f"Listed as '{condition}' but '{indicator}' found in listing"
                )

    if "pre-owned" in condition_lower or "used" in condition_lower:
        if "sealed" in title_lower or "factory sealed" in desc_lower:
            condition_issues.append(
                f"Listed as '{condition}' but 'sealed' mentioned"
            )

    # Listing quality score (0-100)
    quality = 100
    quality -= red_flags["count"] * 10
    quality -= len(condition_issues) * 15
    if not description:
        quality -= 20  # No description is a red flag
    elif len(description) < 50:
        quality -= 10  # Very short description
    quality = max(0, min(100, quality))

    return {
        "red_flags": red_flags,
        "condition_issues": condition_issues,
        "listing_quality": quality,
        "title": title,
        "condition": condition,
    }


def format_risk_report(verification: dict) -> str:
    """Format listing verification into readable risk report."""
    rf = verification["red_flags"]
    lines = [
        f"**Listing Risk Assessment**",
        f"Quality Score: {verification['listing_quality']}/100",
        f"Red Flag Level: {rf['risk_level'].upper()}",
        "",
    ]

    if rf["flags"]:
        lines.append(f"**Red Flags ({rf['count']}):**")
        for flag in rf["flags"]:
            lines.append(f"- {flag['keyword']} (in {flag['location']})")
    else:
        lines.append("No red flags detected.")

    if verification["condition_issues"]:
        lines.append("")
        lines.append("**Condition Mismatches:**")
        for issue in verification["condition_issues"]:
            lines.append(f"- {issue}")

    return "\n".join(lines)
