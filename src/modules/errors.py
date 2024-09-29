import traceback
import html
import random

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from telegram.constants import ChatType, ParseMode

from src.config import ConfigManager
from src.decorators import router
from src.utils import nixnet
from src.utils.logging import logger

class ErrorsDict(dict):
    """A custom dict to store errors and their count"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __contains__(self, error):
        error.identifier = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
        for e in self:
            if type(e) is type(error) and e.args == error.args:
                self[e] += 1
                return True
        self[error] = 0
        return False


errors = ErrorsDict()

@router.error()
async def error_callback(update: Update, context: CallbackContext):
    if not update: return

    e = html.escape(f'{context.error}')
    if update.effective_chat.type != ChatType.CHANNEL:
        try:
            await context.bot.send_message(update.effective_chat.id, 
            f'<b>Sorry I ran into an error!</b>\n<b>Error</b>: <code>{e}</code>\n<i>This incident has been logged. No further action is required.</i>',
            parse_mode=ParseMode.HTML)
        except BaseException as e:
            await logger.aexception(e)

    if context.error in errors: return
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = ''.join(tb_list)
    pretty_message = f'An exception was raised while handling an update\nUser: {update.effective_user.id if update.effective_user else update.effective_message.sender_chat.id}\nChat: {update.effective_chat.title if update.effective_chat else ""} {update.effective_chat.id if update.effective_chat else ""}\nCallback data: {update.callback_query.data if update.callback_query else "None"}\nMessage: {update.effective_message.text if update.effective_message else "No message"}\n\nFull Traceback: {tb}'
    paste_url = nixnet.upload_text(pretty_message)


    if paste_url := nixnet.upload_text(pretty_message):
        await context.bot.send_message(
            ConfigManager.get('general', 'LOGS_CHAT'),
            text=f'#{context.error.identifier}\n<b>Unhandled exception caught:</b>\n<code>{e}</code>',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("PrivateBin", url=paste_url)]]),
            parse_mode=ParseMode.HTML,
        )
    else:
        with open('error.txt', 'w+') as f:
            f.write(pretty_message)
        await context.bot.send_document(
            ConfigManager.get('general', 'LOGS_CHAT'),
            open('error.txt', 'rb'),
            caption=f'#{context.error.identifier}\n<b>Unhandled exception caught:</b>\n<code>{e}</code>',
            parse_mode=ParseMode.HTML,
        )
