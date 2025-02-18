import redis
import json
import time
from typing import Any, Optional

class CacheManager:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.cache_timeout = 300  # 5 minutes cache timeout

    def set_cache(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Store data in cache"""
        try:
            if timeout is None:
                timeout = self.cache_timeout
            serialized_value = json.dumps(value)
            return self.redis_client.setex(key, timeout, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """Retrieve data from cache"""
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def delete_cache(self, key: str) -> bool:
        """Delete data from cache"""
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def clear_cache(self) -> bool:
        """Clear all cached data"""
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

    def cache_exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"Cache check error: {e}")
            return False
