from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Tuple

from aiolimiter import AsyncLimiter
from cachetools import LRUCache, TTLCache
from loguru import logger

from src.utils import extract_data

if TYPE_CHECKING:
    from telegram import Update


@dataclass(frozen=True, slots=True)
class UserUpdatesConfig:
    update_cache_size: int = 2048
    update_ttl: int = 2

    user_max_rate: int = 1
    user_time_period: int = 1
    user_cache_size: int = 1024


class UserUpdates:
    __slots__ = ("_config", "_updates", "_user_limiters")

    def __init__(self):
        cfg = UserUpdatesConfig()
        self._config = cfg
        self._updates: TTLCache[str, bytes] = TTLCache(
            maxsize=cfg.update_cache_size, ttl=cfg.update_ttl)
        self._user_limiters: LRUCache[int, AsyncLimiter] = LRUCache(
            maxsize=cfg.user_cache_size)

    async def initialize(self, name: str) -> None:
        logger.debug(f"{self.__class__.__name__} Initialized for {name}")

    async def shutdown(self, name: str) -> None:
        self._updates.clear()
        self._user_limiters.clear()
        logger.debug(f"{self.__class__.__name__} Shutdown for {name}")

    def _get_user_limiter(self, user_id: int) -> AsyncLimiter:
        if user_id not in self._user_limiters:
            self._user_limiters[user_id] = AsyncLimiter(
                max_rate=self._config.user_max_rate,
                time_period=self._config.user_time_period,
            )
        return self._user_limiters[user_id]

    @staticmethod
    def format_cache(update: Update) -> Tuple[int, str, bytes]:
        _, user, message, _, callback_query = extract_data(update)
        if not (user and user.id):
            return None, None, None

        elif callback_query and callback_query.data:
            return user.id, f"callback:{user.id}", str(
                callback_query.data).encode()

        elif message and message.text:
            return user.id, f"message:{user.id}", str(
                message.text.lower()).encode()

        return None, None, None

    async def check_update(self, user_id: int, key: str, value: bytes) -> bool:
        user_limiter = self._get_user_limiter(user_id)
        try:
            await user_limiter.acquire()
        except ValueError as ve:
            expected_message = "Can't acquire more than the maximum capacity"
            if ve == expected_message:
                return False
            raise ValueError(ve)
        else:
            return self._updates.get(key, "") == value

    def add_update(self, key: str, value: bytes) -> None:
        self._updates[key] = value
