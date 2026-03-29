"""Configuration and environment variables for eBay Arbitrage Scanner."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

# eBay API
EBAY_APP_ID: str = os.getenv("EBAY_APP_ID", "")
EBAY_CERT_ID: str = os.getenv("EBAY_CERT_ID", "")
EBAY_MARKETPLACE: str = os.getenv("EBAY_MARKETPLACE", "EBAY_US")
EBAY_AUTH_URL: str = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_BROWSE_URL: str = "https://api.ebay.com/buy/browse/v1"

# Discord
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
DISCORD_DEALS_CHANNEL: int = int(os.getenv("DISCORD_DEALS_CHANNEL", "0"))
DISCORD_HOT_DEALS_CHANNEL: int = int(os.getenv("DISCORD_HOT_DEALS_CHANNEL", "0"))
DISCORD_LOG_CHANNEL: int = int(os.getenv("DISCORD_LOG_CHANNEL", "0"))

# Scanner settings
DAILY_API_LIMIT: int = int(os.getenv("DAILY_API_LIMIT", "5000"))
SCAN_INTERVAL_MINUTES: int = int(os.getenv("SCAN_INTERVAL_MINUTES", "30"))
MIN_PROFIT: float = float(os.getenv("MIN_PROFIT", "10.00"))
MIN_MARGIN: float = float(os.getenv("MIN_MARGIN", "15.0"))
DEFAULT_LOCATION: str = os.getenv("DEFAULT_LOCATION", "90210")

# Scan rotation
NUM_GROUPS: int = 8
CALLS_PER_PRODUCT: int = 2  # 1 search + 1 detail on avg

# Scoring thresholds
HOT_DEAL_SCORE: int = 80
GOOD_DEAL_SCORE: int = 60
WATCH_DEAL_SCORE: int = 40

# eBay fee structure
EBAY_FEE_PERCENT: float = 13.25  # Final value fee %
EBAY_FEE_FIXED: float = 0.30  # Per-order fee
SHIPPING_ESTIMATE: float = 8.00  # Default shipping cost estimate

# Seller trust thresholds
SELLER_MIN_FEEDBACK: float = 95.0
SELLER_MIN_TRANSACTIONS: int = 50

# Red flag keywords in descriptions
RED_FLAG_KEYWORDS: list[str] = [
    "as-is", "as is", "for parts", "for repair", "not working",
    "broken", "damaged", "cracked", "bent", "missing parts",
    "no returns", "sold as is", "untested", "powers on only",
    "read description", "see photos", "defective", "faulty",
    "water damage", "screen burn", "dead pixels", "scratched",
    "dented", "refurbished", "aftermarket", "replica", "knockoff",
    "not genuine", "not original", "third party", "compatible",
    "no charger", "no cable", "no box", "incomplete"
]
