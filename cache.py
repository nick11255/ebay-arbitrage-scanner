"""Redis caching layer with in-memory fallback for sold price data."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional

import config

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Fallback cache using a plain dict with TTL tracking."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}  # key -> (value_json, expire_time)
        self.hits: int = 0
        self.misses: int = 0

    def get(self, key: str) -> Optional[Any]:
        """Get a value by key. Returns None if missing or expired."""
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None
        value_json, expire_time = entry
        if expire_time > 0 and time.time() > expire_time:
            del self._store[key]
            self.misses += 1
            return None
        self.hits += 1
        return json.loads(value_json)

    def set(self, key: str, value: Any, ttl_seconds: int = 0) -> None:
        """Store a value with optional TTL (0 = no expiration)."""
        expire_time: float = time.time() + ttl_seconds if ttl_seconds > 0 else 0
        self._store[key] = (json.dumps(value, default=str), expire_time)

    def delete(self, key: str) -> None:
        """Remove a key."""
        self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        """Check if a key exists and is not expired."""
        entry = self._store.get(key)
        if entry is None:
            return False
        _, expire_time = entry
        if expire_time > 0 and time.time() > expire_time:
            del self._store[key]
            return False
        return True

    def get_many(self, pattern: str) -> dict[str, Any]:
        """Get all keys matching a simple glob pattern (supports trailing *)."""
        self._cleanup_expired()
        prefix: str = pattern.rstrip("*")
        results: dict[str, Any] = {}
        for key, (value_json, expire_time) in list(self._store.items()):
            if key.startswith(prefix):
                if expire_time > 0 and time.time() > expire_time:
                    del self._store[key]
                    continue
                results[key] = json.loads(value_json)
        return results

    def flush_expired(self) -> dict[str, int]:
        """Remove expired entries and return cache stats."""
        removed: int = self._cleanup_expired()
        return {
            "total_keys": len(self._store),
            "removed": removed,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / max(self.hits + self.misses, 1) * 100, 1),
        }

    def _cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        now: float = time.time()
        expired_keys: list[str] = [
            k for k, (_, exp) in self._store.items()
            if exp > 0 and now > exp
        ]
        for k in expired_keys:
            del self._store[k]
        return len(expired_keys)

    def key_count(self) -> int:
        """Return total number of non-expired keys."""
        self._cleanup_expired()
        return len(self._store)

    def keys_expiring_within(self, seconds: int) -> int:
        """Count keys expiring within the given number of seconds."""
        now: float = time.time()
        cutoff: float = now + seconds
        count: int = 0
        for _, (_, exp) in self._store.items():
            if 0 < exp <= cutoff:
                count += 1
        return count

    def memory_estimate_bytes(self) -> int:
        """Rough estimate of memory usage in bytes."""
        total: int = 0
        for key, (val, _) in self._store.items():
            total += len(key) + len(val) + 8  # 8 bytes for float
        return total


class RedisCache:
    """Redis-backed cache with automatic fallback to in-memory."""

    def __init__(
        self,
        host: str = "",
        port: int = 6379,
        db: int = 0,
    ) -> None:
        self._host: str = host or getattr(config, "REDIS_HOST", "localhost")
        self._port: int = port or getattr(config, "REDIS_PORT", 6379)
        self._db: int = db or getattr(config, "REDIS_DB", 0)
        self._redis: Optional[Any] = None
        self._fallback: InMemoryCache = InMemoryCache()
        self._using_fallback: bool = False
        self.hits: int = 0
        self.misses: int = 0
        self._connect()

    def _connect(self) -> None:
        """Try to connect to Redis; fall back to in-memory on failure."""
        try:
            import redis
            self._redis = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )
            self._redis.ping()
            self._using_fallback = False
            logger.info(f"Connected to Redis at {self._host}:{self._port}")
        except Exception as e:
            logger.warning(
                f"Redis unavailable ({e}), using in-memory fallback cache"
            )
            self._redis = None
            self._using_fallback = True

    @property
    def is_fallback(self) -> bool:
        """True if using in-memory fallback instead of Redis."""
        return self._using_fallback

    def get(self, key: str) -> Optional[Any]:
        """Get a value by key. Returns None if missing or expired."""
        if self._using_fallback:
            result = self._fallback.get(key)
            self.hits = self._fallback.hits
            self.misses = self._fallback.misses
            return result
        try:
            raw: Optional[str] = self._redis.get(key)
            if raw is None:
                self.misses += 1
                return None
            self.hits += 1
            return json.loads(raw)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self.misses += 1
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 0) -> None:
        """Store a value with optional TTL."""
        serialized: str = json.dumps(value, default=str)
        if self._using_fallback:
            self._fallback.set(key, value, ttl_seconds)
            return
        try:
            if ttl_seconds > 0:
                self._redis.setex(key, ttl_seconds, serialized)
            else:
                self._redis.set(key, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            self._fallback.set(key, value, ttl_seconds)

    def delete(self, key: str) -> None:
        """Remove a key."""
        if self._using_fallback:
            self._fallback.delete(key)
            return
        try:
            self._redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        if self._using_fallback:
            return self._fallback.exists(key)
        try:
            return bool(self._redis.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    def get_many(self, pattern: str) -> dict[str, Any]:
        """Get all keys matching a glob pattern."""
        if self._using_fallback:
            return self._fallback.get_many(pattern)
        try:
            keys: list[str] = self._redis.keys(pattern)
            if not keys:
                return {}
            results: dict[str, Any] = {}
            for key in keys:
                raw: Optional[str] = self._redis.get(key)
                if raw is not None:
                    results[key] = json.loads(raw)
            return results
        except Exception as e:
            logger.error(f"Redis get_many error: {e}")
            return {}

    def flush_expired(self) -> dict[str, int]:
        """Return cache stats. Redis handles TTL expiration automatically."""
        if self._using_fallback:
            stats = self._fallback.flush_expired()
            self.hits = self._fallback.hits
            self.misses = self._fallback.misses
            return stats
        try:
            info: dict = self._redis.info("keyspace", "memory")
            db_info: dict = info.get(f"db{self._db}", {})
            total_keys: int = db_info.get("keys", 0) if isinstance(db_info, dict) else 0
            return {
                "total_keys": total_keys,
                "removed": 0,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": round(
                    self.hits / max(self.hits + self.misses, 1) * 100, 1
                ),
            }
        except Exception as e:
            logger.error(f"Redis flush_expired error: {e}")
            return {
                "total_keys": 0, "removed": 0,
                "hits": self.hits, "misses": self.misses, "hit_rate": 0,
            }

    def key_count(self) -> int:
        """Return total number of keys."""
        if self._using_fallback:
            return self._fallback.key_count()
        try:
            return self._redis.dbsize()
        except Exception:
            return 0

    def keys_expiring_within(self, seconds: int) -> int:
        """Count keys expiring within the given number of seconds."""
        if self._using_fallback:
            return self._fallback.keys_expiring_within(seconds)
        try:
            count: int = 0
            cursor: int = 0
            while True:
                cursor, keys = self._redis.scan(cursor=cursor, count=100)
                for key in keys:
                    ttl: int = self._redis.ttl(key)
                    if 0 < ttl <= seconds:
                        count += 1
                if cursor == 0:
                    break
            return count
        except Exception:
            return 0

    def memory_estimate_bytes(self) -> int:
        """Estimate memory usage."""
        if self._using_fallback:
            return self._fallback.memory_estimate_bytes()
        try:
            info: dict = self._redis.info("memory")
            return info.get("used_memory", 0)
        except Exception:
            return 0


# Global cache instance — initialized on first import
_cache: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get or create the global cache instance."""
    global _cache
    if _cache is None:
        _cache = RedisCache()
    return _cache


# ==================== Comp Cache Helpers ====================

COMP_TTL: int = 43200  # 12 hours in seconds


def cache_comps(product_name: str, condition: str, comps: list[dict]) -> None:
    """Cache comp data for a product+condition."""
    cache: RedisCache = get_cache()
    key: str = f"comps:{product_name}:{condition}"
    cache.set(key, comps, ttl_seconds=COMP_TTL)


def get_cached_comps(product_name: str, condition: str) -> Optional[list[dict]]:
    """Get cached comp data. Returns None on cache miss."""
    cache: RedisCache = get_cache()
    key: str = f"comps:{product_name}:{condition}"
    return cache.get(key)


def cache_comps_detail(product_name: str, comps: list[dict]) -> None:
    """Cache full comp details (title, price, condition) for a product."""
    cache: RedisCache = get_cache()
    key: str = f"comps_detail:{product_name}"
    cache.set(key, comps, ttl_seconds=COMP_TTL)


def get_cached_comps_detail(product_name: str) -> Optional[list[dict]]:
    """Get cached full comp details. Returns None on cache miss."""
    cache: RedisCache = get_cache()
    key: str = f"comps_detail:{product_name}"
    return cache.get(key)


def make_comp_cache_key(product_name: str, condition: str = "all") -> str:
    """Build a cache key for comp data."""
    return f"comps:{product_name}:{condition}"
