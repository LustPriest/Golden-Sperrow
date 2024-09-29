from functools import wraps
from typing import Optional, List, Tuple, Union, Pattern

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler
from telegram.ext.filters import BaseFilter, UpdateType

from src.application import application
from src.utils.cache import cache
from src.utils.logging import logger


def rate_limit(messages_per_window: int, window_seconds: int):
    def decorator(callback):
        @wraps(callback)
        async def wrapper(update: Update, context: CallbackContext):
            key = f'{update.effective_user.id}'
            try:
                await cache.rate_limit(key, limit=messages_per_window, period=window_seconds)
            except cache.RateLimitError:
                await logging.ainfo(
                    'Rate limit exceeded for user %s. '
                    'Allowed %s updates in %s seconds.',
                    key, messages_per_window, window_seconds
                )
                return
            return await callback(update, context)
        return wrapper
    return decorator


def command(
    command: Union[List[str], Tuple[str], str],
    filters: Optional[BaseFilter] = None,
    block: Optional[bool] = True,
    has_args: Optional[Union[bool, int]] = None,
    group: Optional[int] = 0
):
    async def wrapper(callback):
        if filters is not None: filters = ~UpdateType.EDITED & filters
        else: filters = ~UpdateType.EDITED
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
        if filters is not None: filters = ~UpdateType.EDITED & filters
        else: filters = ~UpdateType.EDITED
        await application.add_handler(MessageHandler(filters, callback, block), group)
        await logger.adebug(
            'Loaded filter pattern for function %s',
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
