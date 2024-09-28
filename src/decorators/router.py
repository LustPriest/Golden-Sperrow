from typing import Optional, List, Tuple, Union, Pattern

from telegram.ext import filters, CallbackQueryHandler, CommandHandler, MessageHandler
from telegram.ext.filters import BaseFilter

from ..application import application


def command(
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
            ),
            group
        )
        logger.debug(
            'Loaded handler %s for function %s',
            command,
            callback.__name__
        )
        return callback
    return wrapper


def message(
    filters: Optional[BaseFilter] = None,
    block: Optional[bool] = True,
    group: Optional[int] = 0,
):
    async def wrapper(callback):
        await application.add_handler(MessageHandler(filters, callback, block), group)
        logger.debug(
            'Loaded filter pattern %s for function %s',
            pattern,
            callback.__name__
        )
        return callback
    return wrapper


def callback_query(
    pattern: Optional[
        Union[str, Pattern[str], Optional[bool]]
    ] = None,
    block: Optional[bool] = True,
    group: Optional[int] = 0,
):
    async def wrapper(callback):
        await application.add_handler(CallbackQueryHandler(pattern=pattern, callback=callback, block=block), group)
        logger.debug(
            'Loaded callbackquery handler with pattern %s for function %s',
            pattern,
            callback.__name__
        )
        return callback
    return wrapper
