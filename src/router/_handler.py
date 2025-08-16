from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Pattern, Union

from loguru import logger
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from src.filters import IS_BOT

if TYPE_CHECKING:
    from telegram.ext import Application
    from telegram.ext.filters import BaseFilter


class TelegramHandler:
    __slots__ = ("_application", )

    def __init__(self) -> None:
        self._application: Application = None

    async def initialize(self, application: Application) -> None:
        self._application = application
        logger.debug(f"{self.__class__.__name__} Initialized")

    async def shutdown(self) -> None:
        logger.debug(f"{self.__class__.__name__} Shutdown")

    def command(
        self,
        command: Union[str, List[str]],
        filters: Optional[BaseFilter] = None,
        block: Optional[bool] = True,
        has_args: Optional[Union[bool, int]] = None,
        group: Optional[int] = 0,
    ) -> Callable[[Any], None]:

        def decorator(callback: Callable) -> None:
            self._application.add_handler(
                handler=CommandHandler(
                    command=[command] if isinstance(command, str) else command,
                    callback=callback,
                    filters=filters & ~IS_BOT if filters else ~IS_BOT,
                    block=block,
                    has_args=has_args,
                ),
                group=group,
            )
            logger.debug(
                f"[COMMAND HANDLER] Loaded handler {command} for function {callback.__name__}"
            )
            return callback

        return decorator

    def message(
        self,
        filters: Optional[BaseFilter] = None,
        block: Optional[bool] = True,
        group: Optional[int] = 0,
    ) -> Callable[[Any], None]:

        def decorator(callback: Callable) -> None:
            self._application.add_handler(
                handler=MessageHandler(
                    filters=filters & ~IS_BOT if filters else ~IS_BOT,
                    callback=callback,
                    block=block,
                ),
                group=group,
            )
            logger.debug(
                f"[MESSAGE HANDLER] Loaded filter for function {callback.__name__}"
            )
            return callback

        return decorator

    def callback_query(
        self,
        pattern: Optional[Union[str, Pattern[str], Optional[bool]]] = None,
        block: Optional[bool] = True,
        group: Optional[int] = 0,
    ) -> Callable[[Any], None]:

        def decorator(callback: Callable) -> None:
            self._application.add_handler(
                handler=CallbackQueryHandler(callback=callback,
                                             pattern=pattern,
                                             block=block),
                group=group,
            )
            logger.debug(
                f"[CALLBACK HANDLER] Loaded callback_query handler for function {callback.__name__}"
            )
            return callback

        return decorator

    def error(self, block: Optional[bool] = True) -> Callable[[Any], None]:

        def decorator(callback: Callable) -> None:
            self._application.add_error_handler(callback=callback, block=block)
            logger.debug(
                f"[ERROR HANDLER] Loaded error handler function {callback.__name__}"
            )
            return callback

        return decorator
