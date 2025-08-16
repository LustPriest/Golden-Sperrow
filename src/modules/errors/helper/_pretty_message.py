from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

from src.utils import extract_data

if TYPE_CHECKING:
    from telegram import CallbackQuery, Chat, Message, Update, User

PRETTY_MESSAGE: str = """An exception was raised while handling an update
User: {user_fullname} ({user_id}) - @{user_username}'
Chat: {chat_title} ({chat_id}) - @{chat_username}
Callback Query Data: {callback_data}
Message: {message_id} - {message_text}

Full Traceback:
{traceback}"""


def get_pretty_message(
    update: Update,
    traceback: str,
) -> str:
    chat, user, message, _, callback_query = extract_data(update)
    pretty_message_data: dict = {
        "user_fullname": getattr(user, "full_name", "Deleted Account"),
        "user_id": getattr(user, "id", "None"),
        "user_username": getattr(user, "username", "None"),
        "chat_title": getattr(chat, "title", "None"),
        "chat_id": getattr(chat, "id", "None"),
        "chat_username": getattr(chat, "username", "None"),
        "callback_data": getattr(callback_query, "data", "None"),
        "message_id": getattr(message, "id", "None"),
        "message_text": getattr(message, "text", "None"),
        "traceback": traceback,
    }
    return textwrap.dedent(PRETTY_MESSAGE.format(**pretty_message_data))
