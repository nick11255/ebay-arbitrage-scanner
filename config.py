"""Configuration — environment variables and constants."""

import os
from dotenv import load_dotenv

load_dotenv()

# eBay API credentials
EBAY_APP_ID = os.getenv("EBAY_APP_ID", "")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID", "")
EBAY_AUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_BROWSE_URL = "https://api.ebay.com/buy/browse/v1"

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

# Deal thresholds
MIN_PROFIT = float(os.getenv("MIN_PROFIT", "10.00"))
MIN_MARGIN = float(os.getenv("MIN_MARGIN", "15.0"))
MIN_SCORE = 60

# eBay fee structure
EBAY_FEE_PERCENT = 13.25
EBAY_FEE_FIXED = 0.30
SHIPPING_ESTIMATE = 8.00

# Scan interval in minutes
SCAN_INTERVAL = 30
