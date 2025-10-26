"""
Модуль для работы с кэшем Redis
"""
import json
import redis.asyncio as redis
from typing import Optional, Any
from app.core.config import settings


class RedisCache:
    """Класс для работы с Redis кэшем"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Подключиться к Redis"""
        if not self.redis_client:
            try:
                self.redis_client = await redis.from_url(
                    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                    encoding="utf-8",
                    decode_responses=True
                )
            except Exception as e:
                print(f"⚠️ Не удалось подключиться к Redis: {e}")
                self.redis_client = None
    
    async def disconnect(self):
        """Отключиться от Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить данные из кэша"""
        if not self.redis_client:
            await self.connect()
        
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"⚠️ Ошибка получения из кэша: {e}")
        return None
    
    async def set(self, key: str, value: Any, expire: int = 60):
        """Сохранить данные в кэш"""
        if not self.redis_client:
            await self.connect()
        
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.setex(
                key,
                expire,
                json.dumps(value, default=str, ensure_ascii=False)
            )
        except Exception as e:
            print(f"⚠️ Ошибка сохранения в кэш: {e}")
    
    async def delete(self, key: str):
        """Удалить данные из кэша"""
        if not self.redis_client:
            await self.connect()
        
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            print(f"⚠️ Ошибка удаления из кэша: {e}")


# Глобальный экземпляр кэша
redis_cache = RedisCache()

