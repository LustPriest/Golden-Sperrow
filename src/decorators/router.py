from functools import wraps
from pyrate_limiter import Limiter, RequestRate, Duration, MemoryListBucket
from pyrate_limiter.exceptions import RateLimitException
import time
from typing import Optional, List, Tuple, Union, Pattern

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler
from telegram.ext.filters import BaseFilter, UpdateType

from src.application import application
from src.utils.caching import cache
from src.utils.logging import logger

rate = RequestRate(1, Duration.SECOND * 2)
bucket = MemoryListBucket()
limiter = Limiter(rate, bucket)


def rate_limit(messages_per_window: int, window_seconds: int):
    def decorator(callback):
        @wraps(callback)
        async def wrapper(update: Update, context: CallbackContext):
            user_id = f'{update.effective_user.id}'
            try:
                limiter.try_acquire(user_id)
            except RateLimitException:
                await logging.awarning(
                    'Rate limit exceeded for user %s. '
                    'Allowed %s updates in %s seconds.',
                    user_id, messages_per_window, window_seconds
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
    def wrapper(callback):
        if filters is not None: filters = ~UpdateType.EDITED & filters
        else: filters = ~UpdateType.EDITED
        application.add_handler(
            CommandHandler(
                command,
                callback,
                filters,
                block,
                has_args
            ),
            group
        )
        logger.info(
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
    def wrapper(callback):
        if filters is not None: filters = ~UpdateType.EDITED & filters
        else: filters = ~UpdateType.EDITED
        application.add_handler(MessageHandler(filters, callback, block), group)
        logger.info(
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
    def wrapper(callback):
        application.add_handler(CallbackQueryHandler(pattern=pattern, callback=callback, block=block), group)
        logger.info(
            'Loaded callbackquery handler with pattern %s for function %s',
            pattern,
            callback.__name__
        )
        return callback
    return wrapper


def error(
    block: Optional[bool] = True
):
    def wrapper(callback):
        application.add_error_handler(callback, block)
        logger.info(
            'Loaded error handler for function %s',
            callback.__name__
        )
        return callback
    return wrapper
