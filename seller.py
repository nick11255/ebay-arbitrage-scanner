"""Seller trust scoring for eBay arbitrage risk assessment."""

import logging
import config

logger = logging.getLogger(__name__)


def score_seller(seller_info: dict) -> dict:
    """Calculate seller trust score from eBay seller data.

    Factors:
    - Feedback percentage (0-35 pts)
    - Feedback count / history (0-25 pts)
    - Return policy (0-20 pts)
    - Top-rated status (0-20 pts)

    Args:
        seller_info: Dict with feedbackPercentage, feedbackScore,
                     topRatedSeller, returnPolicy fields

    Returns:
        Dict with score (0-100), grade, risk_level, details
    """
    feedback_pct = seller_info.get("feedbackPercentage", "0")
    try:
        feedback_pct = float(str(feedback_pct).replace("%", ""))
    except (ValueError, TypeError):
        feedback_pct = 0

    feedback_count = int(seller_info.get("feedbackScore", 0))
    is_top_rated = seller_info.get("topRatedSeller", False)

    # Return policy analysis
    return_policy = seller_info.get("returnPolicy", {})
    accepts_returns = return_policy.get("returnsAccepted", False) if return_policy else False
    return_period = return_policy.get("returnPeriod", {}).get("value", 0) if return_policy else 0

    # Feedback percentage score (0-35)
    if feedback_pct >= 99.5:
        pct_score = 35
    elif feedback_pct >= 99.0:
        pct_score = 30
    elif feedback_pct >= 98.0:
        pct_score = 25
    elif feedback_pct >= 97.0:
        pct_score = 20
    elif feedback_pct >= 95.0:
        pct_score = 15
    elif feedback_pct >= 90.0:
        pct_score = 8
    else:
        pct_score = 0

    # Feedback count / history (0-25)
    if feedback_count >= 10000:
        count_score = 25
    elif feedback_count >= 5000:
        count_score = 22
    elif feedback_count >= 1000:
        count_score = 18
    elif feedback_count >= 500:
        count_score = 15
    elif feedback_count >= 100:
        count_score = 10
    elif feedback_count >= 50:
        count_score = 5
    else:
        count_score = 2

    # Return policy score (0-20)
    if accepts_returns and return_period >= 30:
        return_score = 20
    elif accepts_returns:
        return_score = 15
    else:
        return_score = 5

    # Top-rated seller bonus (0-20)
    top_score = 20 if is_top_rated else 0

    total = pct_score + count_score + return_score + top_score
    total = min(100, max(0, total))

    # Grade
    if total >= 85:
        grade = "A"
        risk = "low"
    elif total >= 70:
        grade = "B"
        risk = "low-medium"
    elif total >= 55:
        grade = "C"
        risk = "medium"
    elif total >= 40:
        grade = "D"
        risk = "medium-high"
    else:
        grade = "F"
        risk = "high"

    # Specific warnings
    warnings = []
    if feedback_pct < config.SELLER_MIN_FEEDBACK:
        warnings.append(
            f"Feedback {feedback_pct}% below {config.SELLER_MIN_FEEDBACK}% threshold"
        )
    if feedback_count < config.SELLER_MIN_TRANSACTIONS:
        warnings.append(
            f"Only {feedback_count} transactions (min: {config.SELLER_MIN_TRANSACTIONS})"
        )
    if not accepts_returns:
        warnings.append("No returns accepted")
    if not is_top_rated and feedback_count >= 100:
        warnings.append("Not a Top Rated Seller despite volume")

    return {
        "score": total,
        "grade": grade,
        "risk_level": risk,
        "feedback_pct": feedback_pct,
        "feedback_count": feedback_count,
        "top_rated": is_top_rated,
        "accepts_returns": accepts_returns,
        "warnings": warnings,
        "breakdown": {
            "feedback_quality": pct_score,
            "history": count_score,
            "return_policy": return_score,
            "top_rated": top_score,
        },
    }


def format_seller_report(result: dict) -> str:
    """Format seller score into readable report."""
    lines = [
        f"**Seller Trust Score: {result['score']}/100 ({result['grade']})**",
        f"Risk Level: {result['risk_level'].upper()}",
        "",
        f"Feedback: {result['feedback_pct']}% "
        f"({result['feedback_count']:,} transactions)",
        f"Top Rated: {'Yes' if result['top_rated'] else 'No'}",
        f"Returns: {'Accepted' if result['accepts_returns'] else 'Not accepted'}",
    ]

    if result["warnings"]:
        lines.append("")
        lines.append("**Warnings:**")
        for w in result["warnings"]:
            lines.append(f"- {w}")

    return "\n".join(lines)
