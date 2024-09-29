from typing import Optional, List, Tuple, Union, Pattern

from telegram.ext import filters, CallbackQueryHandler, CommandHandler, MessageHandler
from telegram.ext.filters import BaseFilter

from ..application import application
from ..utils.logging import logger


def command(
    command: Union[List[str], Tuple[str], str],
    filters: Optional[BaseFilter] = None,
    block: Optional[bool] = True,
    has_args: Optional[Union[bool, int]] = None,
    group: Optional[int] = 0
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
        await logger.adebug(
            'Loaded handler %s for function %s',
            command,
            callback.__name__
        )
        return callback
    return wrapper


def message(
    filters: Optional[BaseFilter] = None,
    block: Optional[bool] = True,
    group: Optional[int] = 0
):
    async def wrapper(callback):
        await application.add_handler(MessageHandler(filters, callback, block), group)
        await logger.adebug(
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
    group: Optional[int] = 0
):
    async def wrapper(callback):
        await application.add_handler(CallbackQueryHandler(pattern=pattern, callback=callback, block=block), group)
        await logger.adebug(
            'Loaded callbackquery handler with pattern %s for function %s',
            pattern,
            callback.__name__
        )
        return callback
    return wrapper


def error(
    block: Optional[bool] = True
):
    async def wrapper(callback):
        await application.add_error_handler(callback, block)
        await logger.adebug(
            'Loaded error handler for function %s',
            callback.__name__
        )
        return callback
    return wrapper
