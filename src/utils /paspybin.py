from paspybin import Paspybin
from paspybin.exceptions import PaspybinBadAPIRequestError

from src.config import ConfigManager

PASTEBIN_API_DEV_KEY = ConfigManager.get('general', 'PASTEBIN_API_DEV_KEY')

async def paste(content: str) -> str:
    async with Paspybin(PASTEBIN_API_DEV_KEY) as paspybin:
        return await paspybin.pastes.create_paste(content)
