from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, CallbackQueryHandler

from ..decorators import router


@router.command('start', pass_args=True)
@rate_limit(1, 2)
async def start(update: Update, context: CallbackContext):
    await update.effective_message.reply_text('Hmmm?')
