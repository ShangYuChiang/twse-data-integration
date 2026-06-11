"""
快取機制 - 支援記憶體和 Redis 快取
"""

import logging
import json
from typing import Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class BaseCache(ABC):
    """快取基類"""
    
    def __init__(self, ttl: int = 3600):
        """
        初始化快取
        
        Args:
            ttl: 過期時間（秒），預設 1 小時
        """
        self.ttl = ttl
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """取得快取值"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """設定快取值"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """刪除快取值"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """清空所有快取"""
        pass
    
    def generate_key(self, *args, **kwargs) -> str:
        """
        生成快取鍵
        
        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            str: 快取鍵
        """
        key_str = json.dumps(
            {"args": args, "kwargs": kwargs},
            sort_keys=True,
            default=str
        )
        return hashlib.md5(key_str.encode()).hexdigest()


class MemoryCache(BaseCache):
    """記憶體快取實現"""
    
    def __init__(self, ttl: int = 3600):
        """初始化記憶體快取"""
        super().__init__(ttl)
        self._cache: dict = {}
        self._expiry: dict = {}
    
    def get(self, key: str) -> Optional[Any]:
        """取得快取值"""
        if key not in self._cache:
            return None
        
        # 檢查是否過期
        if key in self._expiry:
            if datetime.now() > self._expiry[key]:
                self.delete(key)
                return None
        
        logger.debug(f"Cache hit: {key}")
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """設定快取值"""
        try:
            self._cache[key] = value
            
            if ttl is None:
                ttl = self.ttl
            
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
            logger.debug(f"Cache set: {key}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """刪除快取值"""
        try:
            if key in self._cache:
                del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            return False
    
    def clear(self) -> bool:
        """清空所有快取"""
        try:
            self._cache.clear()
            self._expiry.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


class RedisCache(BaseCache):
    """Redis 快取實現"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", ttl: int = 3600):
        """
        初始化 Redis 快取
        
        Args:
            redis_url: Redis 連線 URL
            ttl: 過期時間（秒）
        """
        super().__init__(ttl)
        
        try:
            import redis
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None
    
    def get(self, key: str) -> Optional[Any]:
        """取得快取值"""
        if self.redis is None:
            return None
        
        try:
            value = self.redis.get(key)
            if value is not None:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """設定快取值"""
        if self.redis is None:
            return False
        
        try:
            if ttl is None:
                ttl = self.ttl
            
            self.redis.setex(key, ttl, json.dumps(value, default=str))
            logger.debug(f"Cache set: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """刪除快取值"""
        if self.redis is None:
            return False
        
        try:
            self.redis.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            return False
    
    def clear(self) -> bool:
        """清空所有快取"""
        if self.redis is None:
            return False
        
        try:
            self.redis.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


def get_cache(cache_type: str = "memory", **kwargs) -> BaseCache:
    """
    工廠函數 - 取得快取實例
    
    Args:
        cache_type: 快取類型 ("memory" 或 "redis")
        **kwargs: 傳遞給快取類初始化的參數
        
    Returns:
        BaseCache: 快取實例
    """
    if cache_type == "redis":
        return RedisCache(**kwargs)
    else:
        return MemoryCache(**kwargs)
