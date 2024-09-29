from cashews import Cache 
from .utils.logging import logger
import asyncio

cache = Cache()
cache.setup('redis://localhost', client_side=True)

async def pre_process() -> ConfigManager:
    try:
        await cache.ping()
    except (CacheBackendInteractionError, TimeoutError):
        await logger.acritical("Can't connect to RedisDB! Exiting...")

asyncio.run(pre_process())
