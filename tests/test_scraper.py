"""Tests for the scraper utility functions."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import trim_outliers, filter_comps_by_condition  # noqa: E402


class TestOutlierTrimming:
    """Test that comp outlier trimming removes top and bottom 10%."""

    def test_trims_extremes(self):
        comps = [{"price": p, "title": f"item {p}"} for p in
                 [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]
        trimmed = trim_outliers(comps, pct=0.10)
        prices = [c["price"] for c in trimmed]
        assert 10 not in prices  # bottom 10% removed
        assert 100 not in prices  # top 10% removed

    def test_preserves_middle(self):
        comps = [{"price": p} for p in [5, 20, 30, 40, 50, 60, 70, 80, 95, 200]]
        trimmed = trim_outliers(comps, pct=0.10)
        prices = [c["price"] for c in trimmed]
        assert 30 in prices
        assert 50 in prices
        assert 70 in prices

    def test_small_list_unchanged(self):
        comps = [{"price": p} for p in [10, 20, 30]]
        trimmed = trim_outliers(comps, pct=0.10)
        assert len(trimmed) == len(comps)

    def test_reduces_count(self):
        comps = [{"price": i * 10} for i in range(1, 21)]  # 20 items
        trimmed = trim_outliers(comps, pct=0.10)
        assert len(trimmed) < len(comps)
        # Should trim 2 from each end (10% of 20 = 2)
        assert len(trimmed) == 16


class TestConditionFiltering:
    """Test that condition matching filters correctly."""

    def test_used_only_when_used(self):
        comps = [
            {"price": 100, "condition": "Pre-Owned"},
            {"price": 120, "condition": "Brand New"},
            {"price": 90, "condition": "Used"},
            {"price": 110, "condition": "Pre-Owned"},
            {"price": 130, "condition": "New"},
        ]
        filtered = filter_comps_by_condition(comps, "Used - Good")
        assert all(
            "used" in c["condition"].lower() or "pre-owned" in c["condition"].lower()
            for c in filtered
        )

    def test_new_only_when_new(self):
        comps = [
            {"price": 100, "condition": "Pre-Owned"},
            {"price": 120, "condition": "Brand New"},
            {"price": 130, "condition": "New"},
            {"price": 110, "condition": "Used"},
            {"price": 140, "condition": "New"},
        ]
        filtered = filter_comps_by_condition(comps, "New")
        assert all("new" in c["condition"].lower() for c in filtered)

    def test_fallback_when_too_few(self):
        comps = [
            {"price": 100, "condition": "New"},
            {"price": 120, "condition": "New"},
            {"price": 90, "condition": "Used"},
        ]
        # Only 1 used comp, should fall back to all
        filtered = filter_comps_by_condition(comps, "Used")
        assert len(filtered) == len(comps)

    def test_no_condition_returns_all(self):
        comps = [{"price": 100, "condition": "New"}, {"price": 90, "condition": "Used"}]
        filtered = filter_comps_by_condition(comps, "")
        assert len(filtered) == len(comps)
