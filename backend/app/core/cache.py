"""
Модуль для работы с кэшем Redis
"""
import json
import time
from typing import Optional, Any

import redis.asyncio as redis

from app.core.config import settings


class RedisCache:
	"""Класс для работы с Redis кэшем"""

	def __init__(self):
		self.redis_client: Optional[redis.Redis] = None
		self._unavailable_until = 0.0

	async def connect(self):
		"""Подключиться к Redis (быстрый fail, без повторных долгих попыток)."""
		if self.redis_client:
			return
		if time.time() < self._unavailable_until:
			return
		try:
			redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
			client = redis.from_url(
				redis_url,
				encoding="utf-8",
				decode_responses=True,
				socket_connect_timeout=0.3,
				socket_timeout=0.5,
			)
			await client.ping()
			self.redis_client = client
			self._unavailable_until = 0.0
		except Exception as e:
			print(f"⚠️ Не удалось подключиться к Redis: {e}")
			print("ℹ️ Используется fallback без кэша")
			self.redis_client = None
			# не долбим DNS/connect на каждый запрос
			self._unavailable_until = time.time() + 60

	async def disconnect(self):
		"""Отключиться от Redis"""
		if self.redis_client:
			await self.redis_client.close()
			self.redis_client = None

	async def get(self, key: str) -> Optional[Any]:
		"""Получить данные из кэша"""
		try:
			await self.connect()
			if not self.redis_client:
				return None
			value = await self.redis_client.get(key)
			if value:
				return json.loads(value)
		except Exception as e:
			print(f"⚠️ Ошибка получения из кэша: {e}")
			self.redis_client = None
			self._unavailable_until = time.time() + 60
			return None

	async def set(self, key: str, value: Any, expire: int = 60):
		"""Сохранить данные в кэш"""
		try:
			await self.connect()
			if not self.redis_client:
				return
			await self.redis_client.setex(
				key,
				expire,
				json.dumps(value, default=str, ensure_ascii=False),
			)
		except Exception as e:
			print(f"⚠️ Ошибка сохранения в кэш: {e}")
			self.redis_client = None
			self._unavailable_until = time.time() + 60

	async def delete(self, key: str):
		"""Удалить данные из кэша"""
		try:
			await self.connect()
			if not self.redis_client:
				return
			await self.redis_client.delete(key)
		except Exception as e:
			print(f"⚠️ Ошибка удаления из кэша: {e}")
			self.redis_client = None
			self._unavailable_until = time.time() + 60


# Глобальный экземпляр кэша
redis_cache = RedisCache()
