"""Lightweight TTL cache for hot auth lookups (Redis if available, else process memory)."""
from __future__ import annotations

import time
from typing import Any, Optional

_AUTH_TTL = 45
_memory: dict[str, tuple[float, Any]] = {}


def _mem_get(key: str) -> Optional[Any]:
	item = _memory.get(key)
	if not item:
		return None
	expires, value = item
	if expires < time.time():
		_memory.pop(key, None)
		return None
	return value


def _mem_set(key: str, value: Any, ttl: int = _AUTH_TTL) -> None:
	_memory[key] = (time.time() + ttl, value)


def _mem_delete(key: str) -> None:
	_memory.pop(key, None)


async def cache_get(key: str) -> Optional[Any]:
	cached = _mem_get(key)
	if cached is not None:
		return cached
	try:
		from app.core.cache import redis_cache

		value = await redis_cache.get(key)
		if value is not None:
			_mem_set(key, value)
		return value
	except Exception:
		return None


async def cache_set(key: str, value: Any, ttl: int = _AUTH_TTL) -> None:
	_mem_set(key, value, ttl)
	try:
		from app.core.cache import redis_cache

		await redis_cache.set(key, value, expire=ttl)
	except Exception:
		pass


async def cache_delete(key: str) -> None:
	_mem_delete(key)
	try:
		from app.core.cache import redis_cache

		await redis_cache.delete(key)
	except Exception:
		pass


def user_cache_key(user_id: int) -> str:
	return f"auth:user:{user_id}"
