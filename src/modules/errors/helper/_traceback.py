from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from telegram.ext import ContextTypes


def get_traceback(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    context_tb = traceback.format_exception(None, context.error,
                                            context.error.__traceback__)
    if not context_tb or context_tb is None or context_tb == []:
        etype, value, tb = sys.exc_info()
        if not (etype and value and tb):
            formatted_exc = traceback.format_exc()
        else:
            formatted_exc = traceback.format_exception(etype, value, tb)
        return ("".join(formatted_exc)
                if isinstance(formatted_exc, list) else formatted_exc)
    else:
        return "".join(context_tb) if isinstance(context_tb,
                                                 list) else context_tb
