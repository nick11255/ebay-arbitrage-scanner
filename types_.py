"""Shared type definitions for the eBay Arbitrage Scanner."""

from __future__ import annotations

from typing import TypedDict


# ==================== Product Types ====================

class ProductConfig(TypedDict):
    """A product entry in the scan database."""
    name: str
    query: str
    exclude: list[str]
    category: str
    min_price: float
    max_price: float
    model_keywords: list[str]
    group: int


# ==================== Fee / Profit Types ====================

class FeeBreakdown(TypedDict):
    """eBay fee calculation result."""
    ebay_fee: float
    shipping: float
    total_costs: float


class ProfitInfo(TypedDict):
    """Full profit calculation result."""
    buy_price: float
    sell_price: float
    profit: float
    margin: float
    roi: float
    ebay_fee: float
    shipping: float
    total_costs: float


# ==================== Comp Types ====================

class CompData(TypedDict, total=False):
    """A single sold comparable sale."""
    title: str
    price: float
    shipping: float
    total: float
    date: str | None
    condition: str
    url: str


class CompStats(TypedDict):
    """Aggregate statistics from comparable sales."""
    avg_price: float
    median_price: float
    min_price: float
    max_price: float
    price_range: float
    num_comps: int
    sell_through: str  # "high" | "medium" | "low"


# ==================== Deal Scoring Types ====================

class ScoreBreakdown(TypedDict):
    """Point breakdown for a deal score."""
    margin: int
    sell_through: int
    comp_confidence: int
    seller_trust: int
    description: int


class DealScore(TypedDict):
    """Complete deal scoring result."""
    score: int
    grade: str  # "A+" | "A" | "B+" | "B" | "C" | "D" | "F"
    channel: str  # "hot_deals" | "deals" | "watch" | "skip"
    profit_info: ProfitInfo
    breakdown: ScoreBreakdown


# ==================== Seller Types ====================

class SellerBreakdown(TypedDict):
    """Point breakdown for seller trust score."""
    feedback_quality: int
    history: int
    return_policy: int
    top_rated: int


class SellerScore(TypedDict):
    """Seller trust scoring result."""
    score: int
    grade: str  # "A" | "B" | "C" | "D" | "F"
    risk_level: str  # "low" | "low-medium" | "medium" | "medium-high" | "high"
    feedback_pct: float
    feedback_count: int
    top_rated: bool
    accepts_returns: bool
    warnings: list[str]
    breakdown: SellerBreakdown


# ==================== Red Flag Types ====================

class RedFlag(TypedDict):
    """A single red flag found in a listing."""
    keyword: str
    location: str  # "title" | "description" | "pattern" | "text" | "title & description"


class RedFlagResult(TypedDict):
    """Red flag scan result."""
    flags: list[RedFlag]
    count: int
    risk_level: str  # "clean" | "caution" | "warning" | "danger"


# ==================== Description Verification Types ====================

class ListingVerification(TypedDict):
    """Full listing verification result."""
    red_flags: RedFlagResult
    condition_issues: list[str]
    listing_quality: int
    title: str
    condition: str


# ==================== Tracker Types ====================

class ProductHealth(TypedDict):
    """Health tracking data for a single product."""
    total_scans: int
    total_listings: int
    total_deals: int
    total_claims: int
    first_scan: str
    last_scan: str
    last_deal: str | None


class TradeEntry(TypedDict, total=False):
    """A purchase or sale log entry."""
    user_id: str
    item: str
    price: float
    notes: str
    timestamp: str
    sold: bool
    sold_price: float
    sold_date: str


class UserStats(TypedDict):
    """Trading statistics for a user."""
    total_purchases: int
    total_sales: int
    total_spent: float
    total_revenue: float
    total_profit: float
    matched_trades: int
    matched_profit: float
    unsold_items: int
    unsold_value: float


class UnderperformerInfo(TypedDict):
    """Info about an underperforming product."""
    name: str
    scans: int
    deals: int
    claims: int
    deal_ratio: float
    last_deal: str


# ==================== Rotation Types ====================

class GroupInfo(TypedDict):
    """Status info for a single scan group."""
    products: int
    last_scan: str
    is_next: bool


class RotationStatus(TypedDict):
    """Full rotation status."""
    current_group: int
    total_scans: int
    groups: dict[int, GroupInfo]
    total_products: int


class DailyCallEstimate(TypedDict):
    """Estimated daily API call budget."""
    scans_per_day: int
    calls_per_full_cycle: int
    estimated_daily_calls: int
    daily_limit: int
    headroom: int
    within_limit: bool


# ==================== API Types ====================

class APIUsage(TypedDict):
    """API usage statistics."""
    used: int
    limit: int
    remaining: int
    percent: float
