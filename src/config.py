import os


class ConfigError(Exception):
    pass


class ConfigManager:
    """Environment-based config manager"""

    @staticmethod
    def get(key: str, default: str = None) -> str:
        value = os.getenv(key.upper(), default)
        if value is None:
            raise ConfigError(f"Missing required config: {key}")
        return value

    @staticmethod
    def get_int(key: str, default: int = None) -> int:
        value = os.getenv(key.upper())
        if value is None:
            raise ConfigError(f"Missing required config: {key}")
        try:
            return int(value)
        except ValueError:
            raise ConfigError(f"Invalid integer for {key}: {value}")

    @staticmethod
    def get_bool(key: str, default: bool = None) -> bool:
        value = os.getenv(key.upper())
        if value is None:
            raise ConfigError(f"Missing required config: {key}")
        return value.lower() in ("1", "true", "yes", "on")

    @staticmethod
    def get_list(key: str,
                 separator: str = None,
                 maxsplit: int = -1,
                 default: list = None) -> list:
        if default is None:
            default = []
        value = os.getenv(key.upper())
        if value is None:
            raise ConfigError(f"Missing required config: {key}")
        return value.split(separator=separator, maxsplit=maxsplit)
