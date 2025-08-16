import asyncio
from contextlib import suppress
from dataclasses import dataclass
from typing import Callable, Coroutine, Optional, Tuple, Union

from aiolimiter import AsyncLimiter
from cachetools import LRUCache
from loguru import logger
from telegram._utils.types import JSONDict, ODVInput
from telegram.error import RetryAfter
from telegram.ext._baseratelimiter import BaseRateLimiter


@dataclass(frozen=True, slots=True)
class RateLimitConfig:
    max_retries: int = 3
    max_rate: int = 30
    time_period: int = 1
    retry_padding: float = 0.1

    group_max_rate: int = 20
    group_time_period: int = 60

    user_max_rate: int = 1
    user_time_period: int = 1

    group_cache_size: int = 256
    user_cache_size: int = 512

    valid_methods: frozenset[str] = frozenset({
        "sendMessage",
        "sendPhoto",
        "sendDocument",
        "editMessage",
        "editMessageText",
        "editMessageCaption",
        "editMessageMedia",
        "editMessageReplyMarkup",
        "answerCallbackQuery",
    })


class AIORateLimiter(BaseRateLimiter[int]):
    __slots__ = (
        "_config",
        "_base_limiter",
        "_group_limiters",
        "_user_limiters",
        "_retry_after_event",
    )

    def __init__(self) -> None:
        cfg = RateLimitConfig()
        self._config = cfg
        self._base_limiter: AsyncLimiter = AsyncLimiter(
            max_rate=cfg.max_rate,
            time_period=cfg.time_period,
        )
        self._group_limiters: LRUCache[Union[str, int],
                                       AsyncLimiter] = LRUCache(
                                           maxsize=cfg.group_cache_size)
        self._user_limiters: LRUCache[Union[str, int],
                                      AsyncLimiter] = LRUCache(
                                          maxsize=cfg.user_cache_size)
        self._retry_after_event = asyncio.Event()
        self._retry_after_event.set()

    async def initialize(self) -> None:
        logger.debug(f"{self.__class__.__name__} Initialized")

    async def shutdown(self) -> None:
        self._group_limiters.clear()
        self._user_limiters.clear()
        logger.debug(f"{self.__class__.__name__} Shutdown")

    def _get_group_limiter(self, chat_id: Union[str, int]) -> AsyncLimiter:
        if chat_id not in self._group_limiters:
            self._group_limiters[chat_id] = AsyncLimiter(
                max_rate=self._config.group_max_rate,
                time_period=self._config.group_time_period,
            )
        return self._group_limiters[chat_id]

    def _get_user_limiter(self, chat_id: Union[str, int]) -> AsyncLimiter:
        if chat_id not in self._user_limiters:
            self._user_limiters[chat_id] = AsyncLimiter(
                max_rate=self._config.user_max_rate,
                time_period=self._config.user_time_period,
            )
        return self._user_limiters[chat_id]

    async def _run_request(
        self,
        chat_id: Union[str, int],
        callback: Callable[..., Coroutine[None, None, Union[bool, JSONDict,
                                                            list[JSONDict]]]],
        args: Tuple[str, JSONDict],
        kwargs: dict[str, ODVInput[float]],
    ) -> Union[bool, JSONDict, list[JSONDict]]:

        async def inner() -> Union[bool, JSONDict, list[JSONDict]]:
            await self._retry_after_event.wait()
            return await callback(*args, **kwargs)

        base_context = self._base_limiter
        chat_context = (self._get_group_limiter(chat_id)
                        if str(chat_id).startswith("-100") else
                        self._get_user_limiter(chat_id))

        async with chat_context, base_context:
            return await inner()

    async def process_request(
        self,
        callback: Callable[..., Coroutine[None, None, Union[bool, JSONDict,
                                                            list[JSONDict]]]],
        args: Tuple[str, JSONDict],
        kwargs: dict[str, ODVInput[float]],
        endpoint: str,
        data: JSONDict,
        rate_limit_args: Optional[int],
    ) -> Union[bool, JSONDict, list[JSONDict]]:
        chat_id = data.get("chat_id", None)
        if chat_id is None or endpoint not in self._config.valid_methods:
            logger.debug(f"Skipping endpoint={endpoint} for chat_id={chat_id}")
            return await callback(*args, **kwargs)

        with suppress(ValueError, TypeError):
            chat_id = int(chat_id)

        max_retries = (self._config.max_retries
                       if rate_limit_args is None else rate_limit_args)
        for attempt in range(max_retries + 1):
            try:
                return await self._run_request(
                    chat_id=chat_id,
                    callback=callback,
                    args=args,
                    kwargs=kwargs,
                )
            except RetryAfter as exc:
                if attempt == max_retries:
                    logger.exception(
                        f"Rate limit hit after maximum of {max_retries} retries",
                        exc_info=exc,
                    )
                    raise

                retry_seconds = (exc.retry_after.total_seconds() if hasattr(
                    exc.retry_after, "total_seconds") else
                    exc.retry_after) + self._config.retry_padding

                logger.debug(
                    f"Rate limit hit for chat_id={chat_id} on endpoint '{endpoint}'."
                    f"Retrying after {retry_seconds:.2f} seconds")

                self._retry_after_event.clear()
                await asyncio.sleep(retry_seconds)
            finally:
                self._retry_after_event.set()

        return None
