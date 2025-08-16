import html
import random
import time
from collections import OrderedDict

import aiofiles
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatType
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from src.config import ConfigManager
from src.router import router
from src.utils import delete_if_exists, extract_data, paspybin

from .helper import get_pretty_message, get_traceback


class ErrorsDict(OrderedDict):
    """ErrorsDict with size-based LRU auto-expiry"""

    def __init__(self, max_size: int = 100):
        super().__init__()
        self.max_size = max_size

    def __contains__(self, error):
        for e in self:
            if type(e) is type(error) and e.args == error.args:
                self[e]["count"] += 1
                self.move_to_end(e)
                return True

        error.identifier = "".join(
            random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=4))
        self[error] = {"count": 0, "time": time.time()}
        if len(self) > self.max_size:
            self.popitem(last=False)

        return False


errors = ErrorsDict()
ERROR_FILE = "error.txt"


@router.error()
async def error_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update:
        return

    chat = extract_data(update)[0]
    e = html.escape(str(context.error))

    if chat and chat.type != ChatType.CHANNEL:
        try:
            await context.bot.send_message(
                chat.id,
                text=(f"<b>Sorry I ran into an error!</b>\n<b>Error</b>: <code>{e}</code>\n"
                      "<i>This incident has been logged. No further action is required.</i>"
                      ),
            )
        except BadRequest as br:
            expected_message = "enough rights to send"
            if expected_message not in br:
                raise BadRequest(br)

    if context.error in errors:
        return
    traceback = get_traceback(context)
    pretty_message = get_pretty_message(update, traceback)
    title = f"#{context.error.identifier}\n<b>Unhandled exception caught:</b>\n<code>{e}</code>"
    logs_chat = ConfigManager.get("LOGS_CHAT")

    if paste_key := await paspybin(pretty_message):
        paste_url = f"pastebin.com/{paste_key}"
        await context.bot.send_message(
            logs_chat,
            text=title,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("PrivateBin", url=paste_url)]]),
        )
    else:
        async with aiofiles.open(ERROR_FILE, "w") as f:
            await f.write(pretty_message)
        await context.bot.send_document(
            logs_chat,
            document=ERROR_FILE,
            caption=title,
        )
        delete_if_exists(ERROR_FILE)
