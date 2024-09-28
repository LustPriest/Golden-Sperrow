from typing import Optional, List, Tuple, Union, Pattern, Callable

from telegram.ext import filters, CallbackQueryHandler, CommandHandler, MessageHandler
from telegram.ext.filters import BaseFilter


class Handlers:

    def command(
        self,
        command: Union[List[str], Tuple[str], str],
        filters: Optional[BaseFilter] = None,
        block: Optional[bool] = True,
        has_args: Optional[Union[bool, int]] = None,
        group: Optional[int] = 0,
    ):
        async def wrapper(callback):
              await application.add_handler(
                        CommandHandler(
                            command,
                            callback,
                            filters,
                            block,
                            has_args
                        ), group
                    )
              logger.debug(
                    f"Loaded handler {command} for function {func.__name__}"
                )
            return callback 
        return wrapper

    def message(
        self,
        filters: Optional[BaseFilter] = None,
        block: Optional[bool] = True,
        group: Optional[int] = 0,
    ):
        async def wrapper(callback):
            await application.add_handler(MessageHandler(filters, callback, block), group)
            logger.debug(
                    f"Loaded filter pattern {pattern} for function {func.__name__}"
            )
            return callback
        return wrapper

    def callback_query(
        self,
        pattern: Optional[
            Union[str, Pattern[str], type, Callable[[object], Optional[bool]]]
        ] = None,
        block: Optional[bool] = True,
        group: Optional[int] = 0,
    ):
        async def wrapper(callback):
            await application.add_handler(CallbackQueryHandler(pattern=pattern, callback=callback, block=block), group)
            logger.debug(
                f"Loaded callbackquery handler with pattern {pattern} for function {func.__name__}"
            )
            return callback
        return wrapper
