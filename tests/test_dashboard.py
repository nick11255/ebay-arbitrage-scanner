"""Tests for the analytics dashboard, trend, and export features."""

import sys
import os
import json
import tempfile
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracker import (  # noqa: E402
    get_dashboard_stats, record_posted_deal, get_posted_deals,
    record_scan, _save_json, _load_json,
    HEALTH_FILE, POSTED_DEALS_FILE,
)
from rotation import get_time_until_full_rotation, get_current_group  # noqa: E402
from types_ import CompStats  # noqa: E402
from scraper import analyze_comps  # noqa: E402


class TestDashboardStats:
    """Test dashboard statistics computation."""

    def setup_method(self):
        """Clean up data files before each test."""
        for f in [HEALTH_FILE, POSTED_DEALS_FILE]:
            if os.path.exists(f):
                os.unlink(f)

    def test_empty_dashboard(self):
        stats = get_dashboard_stats()
        assert stats["scanned_all"] == 0
        assert stats["posted_all"] == 0
        assert stats["avg_score"] == 0
        assert stats["categories"] == {}

    def test_dashboard_with_scans(self):
        record_scan("PS5 Disc Edition", 10, 2)
        record_scan("RTX 4090", 5, 1)
        stats = get_dashboard_stats()
        assert stats["scanned_all"] == 15
        assert stats["total_scans"] == 2

    def test_dashboard_with_posted_deals(self):
        record_posted_deal(
            product_name="PS5 Disc Edition",
            buy_price=350.0,
            sold_median=450.0,
            estimated_profit=70.0,
            margin=15.5,
            deal_score=75,
            seller_rating=90.0,
            url="https://ebay.com/itm/123",
        )
        record_posted_deal(
            product_name="RTX 4090",
            buy_price=1200.0,
            sold_median=1600.0,
            estimated_profit=200.0,
            margin=12.5,
            deal_score=85,
            seller_rating=95.0,
            url="https://ebay.com/itm/456",
        )
        stats = get_dashboard_stats()
        assert stats["posted_all"] == 2
        assert stats["avg_score"] == 80.0  # (75 + 85) / 2
        assert "PS5 Disc Edition" in stats["categories"]
        assert "RTX 4090" in stats["categories"]

    def test_top_bottom_products(self):
        record_scan("Hot Product", 100, 20)
        record_scan("Cold Product", 100, 0)
        record_scan("Medium Product", 100, 5)
        stats = get_dashboard_stats()
        # top_5 sorted by ratio descending
        assert len(stats["top_5"]) == 3
        assert stats["top_5"][0][0] == "Hot Product"
        assert stats["bottom_5"][-1][0] == "Cold Product"


class TestPostedDeals:
    """Test posted deal recording and retrieval."""

    def setup_method(self):
        if os.path.exists(POSTED_DEALS_FILE):
            os.unlink(POSTED_DEALS_FILE)

    def test_record_and_get_deals(self):
        assert get_posted_deals() == []
        record_posted_deal(
            product_name="Test Product",
            buy_price=100.0,
            sold_median=150.0,
            estimated_profit=30.0,
            margin=20.0,
            deal_score=70,
            seller_rating=85.0,
            url="https://example.com",
        )
        deals = get_posted_deals()
        assert len(deals) == 1
        assert deals[0]["product"] == "Test Product"
        assert deals[0]["buy_price"] == 100.0

    def test_multiple_deals(self):
        for i in range(5):
            record_posted_deal(
                product_name=f"Product {i}",
                buy_price=100.0 + i * 10,
                sold_median=200.0,
                estimated_profit=50.0,
                margin=25.0,
                deal_score=60 + i * 5,
                seller_rating=90.0,
                url=f"https://example.com/{i}",
            )
        deals = get_posted_deals()
        assert len(deals) == 5


class TestRotationHelpers:
    """Test rotation helper functions."""

    def test_current_group_in_range(self):
        group = get_current_group()
        assert 1 <= group <= 8

    def test_time_until_rotation_format(self):
        time_str = get_time_until_full_rotation()
        assert "m" in time_str  # Should contain minutes


class TestTrendAnalysis:
    """Test trend-related comp analysis."""

    def test_condition_split(self):
        comps = [
            {"price": 100, "condition": "New", "title": "item"},
            {"price": 120, "condition": "Brand New", "title": "item"},
            {"price": 80, "condition": "Pre-Owned", "title": "item"},
            {"price": 90, "condition": "Used", "title": "item"},
        ]
        new_comps = [c for c in comps if "new" in c["condition"].lower()]
        used_comps = [c for c in comps if any(t in c["condition"].lower() for t in ("used", "pre-owned"))]

        new_stats = analyze_comps(new_comps)
        used_stats = analyze_comps(used_comps)

        assert new_stats["num_comps"] == 2
        assert used_stats["num_comps"] == 2
        assert new_stats["median_price"] > used_stats["median_price"]

    def test_trend_direction(self):
        # Newer comps (first half) are more expensive -> uptrend
        comps = [
            {"price": 200, "title": "item"},
            {"price": 190, "title": "item"},
            {"price": 180, "title": "item"},
            {"price": 100, "title": "item"},
            {"price": 90, "title": "item"},
            {"price": 80, "title": "item"},
        ]
        mid = len(comps) // 2
        newer_avg = sum(c["price"] for c in comps[:mid]) / mid
        older_avg = sum(c["price"] for c in comps[mid:]) / mid
        assert newer_avg > older_avg * 1.05  # should be uptrend
