from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from telegram import CallbackQuery, Chat, Message, User


def _get_chat(update) -> Optional[Chat]:
    return getattr(update, "effective_chat", None)


def _get_user(update) -> Optional[User]:
    return getattr(update, "effective_user", None)


def _get_message(update) -> Optional[Message]:
    return getattr(update, "effective_message", None)


def _get_reply_to_message(update) -> Optional[Message]:
    message = _get_message(update)
    return getattr(message, "reply_to_message", None)


def _get_callback_query(update) -> Optional[CallbackQuery]:
    return getattr(update, "callback_query", None)


def extract_data(update) -> Tuple[Chat, User, Message, CallbackQuery]:
    return (
        _get_chat(update),
        _get_user(update),
        _get_message(update),
        _get_reply_to_message(update),
        _get_callback_query(update),
    )
