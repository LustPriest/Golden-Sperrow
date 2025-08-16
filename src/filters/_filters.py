from __future__ import annotations

from typing import TYPE_CHECKING

from telegram.ext.filters import MessageFilter

if TYPE_CHECKING:
    from telegram import Message


class _IS_BOT(MessageFilter):
    __slots__ = ()

    def filter(self, message: Message) -> bool:
        user = message.from_user
        return getattr(user, "is_bot", False)


IS_BOT = _IS_BOT(name="filters.IS_BOT")
