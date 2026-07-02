import json
import redis.asyncio as aioredis
from typing import Any

_pool: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _pool
    if _pool is None:
        _pool = aioredis.from_url("redis://localhost:6379", decode_responses=True)
    return _pool


async def cache_get(key: str) -> Any | None:
    raw = await get_redis().get(key)
    return json.loads(raw) if raw else None


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    await get_redis().set(key, json.dumps(value), ex=ttl)


async def cache_delete(key: str) -> None:
    await get_redis().delete(key)


async def cache_delete_pattern(pattern: str) -> None:
    async for key in get_redis().scan_iter(pattern):
        await get_redis().delete(key)

# task: Redis cache layer
