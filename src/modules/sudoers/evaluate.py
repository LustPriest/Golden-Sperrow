from __future__ import annotations

import asyncio
import html
import sys
import textwrap
import traceback
from typing import TYPE_CHECKING, Any

import aiofiles
from meval import meval
from telegram.ext import ContextTypes

from src.decorators import is_sudo
from src.router import router
from src.utils import delete_if_exists, extract_data

if TYPE_CHECKING:
    from telegram import Update


def _namespaces(update, context) -> dict:
    (chat, user, message, reply_to_message,
     callback_query) = extract_data(update)
    return {
        "update": update,
        "context": context,
        "bot": context.bot,
        "user": user,
        "chat": chat,
        "message": message,
        "reply_to_message": reply_to_message,
        "callback_query": callback_query,
    }


def _cleanup_code(code: str) -> str:
    if code.startswith("```") and code.endswith("```"):
        return "\n".join(code.split("\n")[1:-1])
    return code.strip("` \n")


async def _evaluate_expression(expression: str, namespaces: dict) -> Any:
    task = asyncio.create_task(
        meval(expression, globals(), **locals(), **namespaces))
    return await task


async def _handle_output(message, output: Any, code: str) -> None:
    if output is None:
        await message.reply_text("No output.")
        return

    output_str = str(output)
    filename = "evaluate.txt"
    try:
        async with aiofiles.open(filename, "w", encoding="utf-8") as f:
            await f.write(textwrap.dedent(output_str))
        await message.reply_document(
            document=filename, caption=f"<code>{html.escape(code)}</code>")
    finally:
        delete_if_exists(filename)


@router.command("eval")
@is_sudo
async def eval_command(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    message = extract_data(update)[2]

    _code = message.text.split(maxsplit=1)
    if len(_code) < 2:
        await message.reply_text("No expression provided.")
        return

    namespaces = _namespaces(update, context)
    code = _cleanup_code(_code[-1])

    try:
        output = await _evaluate_expression(code, namespaces)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        if not (etype and value and tb):
            _formatted_exc = traceback.format_exc()
        else:
            _formatted_exc = traceback.format_exception(etype, value, tb)

        formatted_exc = ("".join(_formatted_exc) if isinstance(
            _formatted_exc, list) else _formatted_exc)
        output = f"{e}\n\n{formatted_exc}"

    await _handle_output(message, output, code)
