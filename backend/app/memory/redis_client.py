import json
from typing import Optional, Any
from app.core.config import settings
from app.core.logging import logger

class MemoryCache:
    """In-memory cache fallback when Redis is offline."""
    def __init__(self):
        self._store = {}

    def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._store[key] = value
        return True

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def ping(self) -> bool:
        return True

class RedisClientManager:
    def __init__(self):
        self.client = None
        self.is_redis = False
        self._init_connection()

    def _init_connection(self):
        try:
            import redis
            client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=2.0)
            client.ping()
            self.client = client
            self.is_redis = True
            logger.info(f"Connected to Redis at {settings.REDIS_URL}")
        except Exception as e:
            if settings.REDIS_FALLBACK_MEMORY:
                logger.warning(f"Could not connect to Redis ({e}). Initializing in-memory session cache.")
                self.client = MemoryCache()
                self.is_redis = False
            else:
                raise e

    def get_json(self, key: str) -> Optional[Any]:
        val = self.client.get(key)
        if val:
            try:
                return json.loads(val)
            except Exception:
                return val
        return None

    def set_json(self, key: str, value: Any, expire_seconds: int = 86400) -> bool:
        try:
            serialized = json.dumps(value)
            if self.is_redis:
                return self.client.set(key, serialized, ex=expire_seconds)
            else:
                return self.client.set(key, serialized, ex=expire_seconds)
        except Exception as e:
            logger.error(f"Error storing key {key} in memory cache: {e}")
            return False

    def delete(self, key: str) -> bool:
        return bool(self.client.delete(key))

redis_manager = RedisClientManager()
