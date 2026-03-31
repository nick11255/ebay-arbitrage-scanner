"""Deal analyzer — profit calculation and deal scoring."""

import config


def calculate_profit(buy_price, sell_price):
    """Calculate profit after eBay fees and shipping.

    Returns dict with profit, margin, fees, and shipping.
    """
    ebay_fee = sell_price * (config.EBAY_FEE_PERCENT / 100) + config.EBAY_FEE_FIXED
    total_costs = ebay_fee + config.SHIPPING_ESTIMATE
    profit = sell_price - buy_price - total_costs
    margin = (profit / sell_price * 100) if sell_price > 0 else 0

    return {
        "profit": round(profit, 2),
        "margin": round(margin, 1),
        "fees": round(ebay_fee, 2),
        "shipping": config.SHIPPING_ESTIMATE,
    }


def score_deal(buy_price, sell_price, num_comps, seller_feedback):
    """Score a deal from 0-100 based on three factors.

    - Profit margin:      up to 50 points
    - Number of comps:    up to 25 points
    - Seller feedback %:  up to 25 points

    Returns an integer score 0-100.
    """
    info = calculate_profit(buy_price, sell_price)
    margin = info["margin"]

    # Margin score (0-50 points)
    if margin >= 40:
        margin_pts = 50
    elif margin >= 30:
        margin_pts = 40
    elif margin >= 20:
        margin_pts = 30
    elif margin >= 15:
        margin_pts = 20
    elif margin >= 10:
        margin_pts = 10
    else:
        margin_pts = 0

    # Comp score (0-25 points) — more comps = more confidence
    if num_comps >= 15:
        comp_pts = 25
    elif num_comps >= 10:
        comp_pts = 20
    elif num_comps >= 5:
        comp_pts = 15
    elif num_comps >= 3:
        comp_pts = 10
    else:
        comp_pts = 5

    # Seller score (0-25 points) — based on feedback percentage
    seller_pts = min(25, int(seller_feedback / 100 * 25))

    total = margin_pts + comp_pts + seller_pts
    return max(0, min(100, total))
