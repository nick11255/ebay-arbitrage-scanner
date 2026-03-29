"""Tests for the deal analysis engine."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer import score_deal, extract_model_id, calculate_fees, calculate_profit  # noqa: E402
from description import check_red_flags  # noqa: E402
from seller import score_seller  # noqa: E402


class TestDealScoring:
    """Test that deal scoring returns a score between 0-100."""

    def test_score_in_range_high_margin(self):
        comp_stats = {
            "avg_price": 200,
            "num_comps": 25,
            "sell_through": "high",
        }
        result = score_deal(buy_price=80, comp_stats=comp_stats, seller_score=95, red_flags=0)
        assert 0 <= result["score"] <= 100

    def test_score_in_range_low_margin(self):
        comp_stats = {
            "avg_price": 105,
            "num_comps": 3,
            "sell_through": "low",
        }
        result = score_deal(buy_price=100, comp_stats=comp_stats, seller_score=50, red_flags=3)
        assert 0 <= result["score"] <= 100

    def test_score_in_range_zero_avg(self):
        comp_stats = {"avg_price": 0, "num_comps": 0, "sell_through": "low"}
        result = score_deal(buy_price=50, comp_stats=comp_stats)
        assert result["score"] == 0

    def test_score_includes_grade_and_channel(self):
        comp_stats = {"avg_price": 200, "num_comps": 20, "sell_through": "high"}
        result = score_deal(buy_price=80, comp_stats=comp_stats, seller_score=100, red_flags=0)
        assert result["grade"] in ("A+", "A", "B+", "B", "C", "D", "F")
        assert result["channel"] in ("hot_deals", "deals", "watch", "skip")

    def test_higher_margin_gives_higher_score(self):
        comp_stats = {"avg_price": 300, "num_comps": 15, "sell_through": "medium"}
        high = score_deal(buy_price=50, comp_stats=comp_stats, seller_score=80, red_flags=0)
        low = score_deal(buy_price=280, comp_stats=comp_stats, seller_score=80, red_flags=0)
        assert high["score"] > low["score"]


class TestModelIdExtraction:
    """Test that model ID extraction correctly extracts model numbers from titles."""

    def test_dewalt_model(self):
        assert extract_model_id("DeWalt DCD771C2 20V MAX Drill") == "DCD771C2"

    def test_gpu_model(self):
        assert extract_model_id("NVIDIA GeForce RTX4090 Graphics Card") == "RTX4090"

    def test_apple_model(self):
        result = extract_model_id("Apple MacBook Air M2 A2681 Laptop")
        assert result == "A2681"

    def test_no_model(self):
        assert extract_model_id("Generic USB Cable Pack of 3") is None

    def test_camera_model(self):
        result = extract_model_id("Sony Alpha A7III Mirrorless Camera")
        assert result == "A7III"


class TestRedFlagDetection:
    """Test that description red flag detection catches problem keywords."""

    def test_catches_as_is(self):
        result = check_red_flags("Phone sold as-is", "")
        assert result["count"] > 0
        keywords = [f["keyword"] for f in result["flags"]]
        assert any("as-is" in k.lower() or "as is" in k.lower() or "As-is" in k for k in keywords)

    def test_catches_for_parts(self):
        result = check_red_flags("Laptop for parts only", "")
        assert result["count"] > 0

    def test_catches_untested(self):
        result = check_red_flags("Console untested powers on", "")
        assert result["count"] > 0
        keywords = [f["keyword"].lower() for f in result["flags"]]
        assert any("untested" in k for k in keywords)

    def test_clean_listing(self):
        result = check_red_flags("Brand New PS5 Disc Edition Sealed", "")
        assert result["risk_level"] == "clean"

    def test_danger_level_many_flags(self):
        result = check_red_flags(
            "Broken cracked damaged phone as-is for parts untested defective"
        )
        assert result["risk_level"] == "danger"


class TestSellerScoring:
    """Test that seller scoring penalizes zero-feedback sellers."""

    def test_zero_feedback_low_score(self):
        result = score_seller({
            "feedbackPercentage": "0",
            "feedbackScore": 0,
            "topRatedSeller": False,
        })
        assert result["score"] < 30

    def test_zero_feedback_gets_warnings(self):
        result = score_seller({
            "feedbackPercentage": "0",
            "feedbackScore": 0,
            "topRatedSeller": False,
        })
        assert len(result["warnings"]) > 0

    def test_excellent_seller_high_score(self):
        result = score_seller({
            "feedbackPercentage": "99.8",
            "feedbackScore": 15000,
            "topRatedSeller": True,
            "returnPolicy": {"returnsAccepted": True, "returnPeriod": {"value": 30}},
        })
        assert result["score"] >= 85
        assert result["grade"] == "A"

    def test_low_feedback_count_penalized(self):
        high_count = score_seller({
            "feedbackPercentage": "99.0",
            "feedbackScore": 5000,
            "topRatedSeller": False,
        })
        low_count = score_seller({
            "feedbackPercentage": "99.0",
            "feedbackScore": 10,
            "topRatedSeller": False,
        })
        assert high_count["score"] > low_count["score"]


class TestFeeCalculation:
    """Test that fee calculation uses correct category-specific rates."""

    def test_fee_structure(self):
        fees = calculate_fees(100.0)
        # 13.25% of 100 + 0.30 = 13.55
        assert fees["ebay_fee"] == 13.55
        assert fees["shipping"] == 8.00
        assert fees["total_costs"] == 13.55 + 8.00

    def test_profit_calculation(self):
        result = calculate_profit(50.0, 100.0)
        assert result["buy_price"] == 50.0
        assert result["sell_price"] == 100.0
        assert result["profit"] > 0
        assert result["margin"] > 0
        assert result["roi"] > 0

    def test_custom_shipping(self):
        fees = calculate_fees(100.0, shipping_cost=15.0)
        assert fees["shipping"] == 15.0

    def test_zero_sell_price(self):
        result = calculate_profit(50.0, 0.0)
        assert result["margin"] == 0
