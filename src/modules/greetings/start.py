from __future__ import annotations

from typing import TYPE_CHECKING

from src.router import router
from src.utils import extract_data

if TYPE_CHECKING:
    from telegram import Update


@router.command("start")
async def start_command(update: Update, _):
    message = extract_data(update)[2]
    await message.reply_text(text="Hmm??")
