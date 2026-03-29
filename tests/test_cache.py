"""Tests for the Redis caching layer with in-memory fallback."""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cache import (  # noqa: E402
    InMemoryCache, RedisCache,
    make_comp_cache_key, cache_comps, get_cached_comps,
    cache_comps_detail, get_cached_comps_detail, COMP_TTL,
)


class TestInMemoryFallback:
    """Test that the in-memory fallback cache works when Redis is unavailable."""

    def test_fallback_activates(self):
        """RedisCache should fall back to in-memory when Redis is unreachable."""
        cache = RedisCache(host="192.0.2.1", port=1)  # non-routable
        assert cache.is_fallback is True

    def test_fallback_basic_operations(self):
        """Fallback cache should support basic get/set/delete."""
        cache = RedisCache(host="192.0.2.1", port=1)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        cache.delete("key1")
        assert cache.get("key1") is None


class TestSetGetDelete:
    """Test set/get/delete operations."""

    def test_set_and_get(self):
        cache = InMemoryCache()
        cache.set("name", "test-value")
        assert cache.get("name") == "test-value"

    def test_get_missing_key(self):
        cache = InMemoryCache()
        assert cache.get("nonexistent") is None

    def test_delete(self):
        cache = InMemoryCache()
        cache.set("to_delete", 42)
        assert cache.get("to_delete") == 42
        cache.delete("to_delete")
        assert cache.get("to_delete") is None

    def test_exists(self):
        cache = InMemoryCache()
        assert cache.exists("nope") is False
        cache.set("yep", True)
        assert cache.exists("yep") is True

    def test_overwrite(self):
        cache = InMemoryCache()
        cache.set("key", "old")
        cache.set("key", "new")
        assert cache.get("key") == "new"

    def test_get_many(self):
        cache = InMemoryCache()
        cache.set("comps:ps5:new", [1, 2])
        cache.set("comps:ps5:used", [3, 4])
        cache.set("other:key", "nope")
        results = cache.get_many("comps:ps5:*")
        assert len(results) == 2
        assert "comps:ps5:new" in results
        assert "comps:ps5:used" in results


class TestTTLExpiration:
    """Test TTL-based expiration."""

    def test_ttl_expires(self):
        cache = InMemoryCache()
        cache.set("short_lived", "value", ttl_seconds=1)
        assert cache.get("short_lived") == "value"
        time.sleep(1.1)
        assert cache.get("short_lived") is None

    def test_no_ttl_persists(self):
        cache = InMemoryCache()
        cache.set("forever", "value", ttl_seconds=0)
        assert cache.get("forever") == "value"

    def test_exists_respects_ttl(self):
        cache = InMemoryCache()
        cache.set("expiring", "val", ttl_seconds=1)
        assert cache.exists("expiring") is True
        time.sleep(1.1)
        assert cache.exists("expiring") is False

    def test_keys_expiring_within(self):
        cache = InMemoryCache()
        cache.set("soon", "val", ttl_seconds=30)
        cache.set("later", "val", ttl_seconds=7200)
        cache.set("permanent", "val", ttl_seconds=0)
        assert cache.keys_expiring_within(3600) == 1  # only "soon"


class TestJSONSerialization:
    """Test JSON serialization of complex objects."""

    def test_list_of_dicts(self):
        cache = InMemoryCache()
        data = [
            {"title": "PS5 Console", "price": 450.0, "condition": "New"},
            {"title": "PS5 Used", "price": 380.0, "condition": "Pre-Owned"},
        ]
        cache.set("comps:ps5:all", data)
        result = cache.get("comps:ps5:all")
        assert result == data
        assert isinstance(result, list)
        assert result[0]["title"] == "PS5 Console"

    def test_nested_dict(self):
        cache = InMemoryCache()
        data = {
            "stats": {"avg_price": 425.0, "num_comps": 15},
            "products": ["PS5", "Xbox"],
        }
        cache.set("complex", data)
        assert cache.get("complex") == data

    def test_numeric_types(self):
        cache = InMemoryCache()
        cache.set("int_val", 42)
        cache.set("float_val", 3.14)
        cache.set("bool_val", True)
        assert cache.get("int_val") == 42
        assert cache.get("float_val") == 3.14
        assert cache.get("bool_val") is True


class TestCacheKeyFormat:
    """Test that cache keys are correctly formatted."""

    def test_comp_cache_key(self):
        key = make_comp_cache_key("PS5 Disc Edition", "new")
        assert key == "comps:PS5 Disc Edition:new"

    def test_comp_cache_key_default_condition(self):
        key = make_comp_cache_key("RTX 4090")
        assert key == "comps:RTX 4090:all"

    def test_comp_cache_key_used(self):
        key = make_comp_cache_key("iPhone 14 Pro", "used")
        assert key == "comps:iPhone 14 Pro:used"


class TestCacheStats:
    """Test cache statistics tracking."""

    def test_hit_miss_tracking(self):
        cache = InMemoryCache()
        cache.get("miss1")
        cache.get("miss2")
        cache.set("hit", "value")
        cache.get("hit")
        assert cache.hits == 1
        assert cache.misses == 2

    def test_flush_expired_stats(self):
        cache = InMemoryCache()
        cache.set("a", 1, ttl_seconds=1)
        cache.set("b", 2, ttl_seconds=0)
        cache.set("c", 3, ttl_seconds=1)
        time.sleep(1.1)
        stats = cache.flush_expired()
        assert stats["removed"] == 2
        assert stats["total_keys"] == 1  # only "b" remains

    def test_memory_estimate(self):
        cache = InMemoryCache()
        cache.set("key", "value")
        mem = cache.memory_estimate_bytes()
        assert mem > 0

    def test_key_count(self):
        cache = InMemoryCache()
        assert cache.key_count() == 0
        cache.set("a", 1)
        cache.set("b", 2)
        assert cache.key_count() == 2
