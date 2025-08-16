from paspybin import Paspybin
from paspybin.exceptions import PaspybinBadAPIRequestError

from src.config import ConfigManager


async def paspybin(content: str) -> str:
    try:
        async with Paspybin(
                ConfigManager.get("PASTEBIN_API_DEV_KEY")) as paspy:
            return await paspy.pastes.create_paste(content)
    except PaspybinBadAPIRequestError:
        return None
