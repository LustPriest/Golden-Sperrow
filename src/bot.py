import asyncio

from telegram import LinkPreviewOptions, constants
from telegram.ext import Application, Defaults

from .config import ConfigManager
from .database import db
from .ext import AIORateLimiter, UpdateProcessor
from .modules import ModuleLoader
from .router import router


class Bot:
    __slots__ = ("_application", )

    def __init__(self) -> None:
        self._application = (Application.builder().defaults(
            self._get_defaults()).concurrent_updates(
                self._get_update_processor()).rate_limiter(
                    self._get_rate_limiter()).update_queue(
                        self._get_update_queue()).post_init(
                            self.initialize).post_stop(self.shutdown).token(
                                ConfigManager.get("TOKEN")).build())

    @staticmethod
    def _get_defaults() -> "Defaults":
        defaults = Defaults(
            parse_mode=constants.ParseMode.HTML,
            disable_notification=True,
            allow_sending_without_reply=True,
            block=True,
            link_preview_options=LinkPreviewOptions(is_disabled=True),
            do_quote=True,
        )
        return defaults

    @staticmethod
    def _get_update_processor() -> "UpdateProcessor":
        update_processor = UpdateProcessor(256)
        return update_processor

    @staticmethod
    def _get_rate_limiter() -> "AIORateLimiter":
        rate_limiter = AIORateLimiter()
        return rate_limiter

    @staticmethod
    def _get_update_queue() -> "asyncio.Queue":
        update_queue = asyncio.Queue()
        return update_queue

    @staticmethod
    def _get_allowed_updates() -> list["constants.UpdateType"]:
        allowed_updates = [
            constants.UpdateType.MESSAGE,
            constants.UpdateType.CALLBACK_QUERY,
        ]
        return allowed_updates

    @staticmethod
    async def initialize(application: "Application") -> None:
        await db.initialize()
        await router.initialize(application)

        loader = ModuleLoader()
        loader.load_all()

    def run(self) -> None:
        allowed_updates = self._get_allowed_updates()
        return self._application.run_polling(
            allowed_updates=allowed_updates,
            drop_pending_updates=True,
        )

    @staticmethod
    async def shutdown(application: "Application") -> None:
        pass
