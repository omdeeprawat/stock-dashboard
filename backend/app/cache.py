import redis.asyncio as aioredis
from app.config import settings

_redis = None

async def get_redis():
  global _redis
  if _redis is None:
    _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
  return _redis

async def get_cache(key: str) -> str | None:
  r = await get_redis()
  return await r.get(key)

async def set_cache(key: str, value: str, ttl: int = 3600):
  r = await get_redis()
  await r.set(key, value, ex=ttl)