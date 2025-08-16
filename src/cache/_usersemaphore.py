import asyncio
from dataclasses import dataclass

from cachetools import LRUCache
from loguru import logger


@dataclass(frozen=True, slots=True)
class SemaphoreConfig:
    user_max_rate: int = 1
    user_cache_size: int = 1024


class UserSemaphore:
    __slots__ = ("_config", "_semaphore")

    def __init__(self):
        cfg = SemaphoreConfig()
        self._config = cfg
        self._semaphore: LRUCache[int, asyncio.Semaphore] = LRUCache(
            maxsize=cfg.user_cache_size)

    async def initialize(self, name: str) -> None:
        logger.debug(f"{self.__class__.__name__} Initialized for {name}")

    async def shutdown(self, name: str) -> None:
        self._semaphore.clear()
        logger.debug(f"{self.__class__.__name__} Shutdown for {name}")

    def _get_semaphore(self, user_id: int) -> asyncio.Semaphore:
        if user_id not in self._semaphore:
            self._semaphore[user_id] = asyncio.Semaphore(
                self._config.user_max_rate)
        return self._semaphore[user_id]

    def get(self, user_id: int) -> asyncio.Semaphore:
        return self._get_semaphore(user_id=user_id)
