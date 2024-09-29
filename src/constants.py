import os
from pathlib import Path

BOT_ROOT_PATH: Path = Path(__file__).parent.parent.parent

XDG_CONFIG_HOME: str = str(Path.home() / ".config")
DEFAULT_CONFIG_PATH: str = f"{XDG_CONFIG_HOME}/configuration.toml"

DEFAULT_CONFIG_TEMPLATE: dict[str, dict[str, str | bool | int] | dict[str, list[str] | str]] = {
    "telegram": {
        "TOKEN": "",
        "SUDOERS": ["123"],
        "LOGS_CHAT": "-123",
        "BACKUPS_CHAT": "-123",
    },
    "general": {
        "PASTEBIN_API_DEV_KEY": "",
    },
}

MESSAGE_LENGTH_LIMIT: int = 4096
