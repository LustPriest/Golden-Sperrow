from __future__ import annotations

from typing import TYPE_CHECKING, Coroutine

from loguru import logger
from telegram.ext import BaseUpdateProcessor

from src.cache import UserSemaphore, UserUpdates

if TYPE_CHECKING:
    from telegram import Update

Semaphore = UserSemaphore()


class UpdateProcessor(BaseUpdateProcessor):

    async def initialize(self) -> None:
        await Semaphore.initialize(name=self.__class__.__name__)
        await UserUpdates.initialize(name=self.__class__.__name__)
        logger.debug(f"{self.__class__.__name__} Initialized")

    async def shutdown(self) -> None:
        await Semaphore.shutdown(name=self.__class__.__name__)
        await UserUpdates.shutdown(name=self.__class__.__name__)
        logger.debug(f"{self.__class__.__name__} Shutdown")

    async def do_process_update(self, update: Update,
                                coroutine: Coroutine) -> None:
        user_id, cache_key, cache_value = UserUpdates.format_cache(
            update=update)
        if user_id and cache_key and cache_value:
            if await UserUpdates.check_update(user_id=user_id,
                                              key=cache_key,
                                              value=cache_value):
                coroutine.close()
                return

            UserUpdates.add_update(key=cache_key, value=cache_value)

        if user_id is None:
            await coroutine
        else:
            semaphore = Semaphore.get(user_id=user_id)
            async with semaphore:
                await coroutine
