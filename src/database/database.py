from typing import Optional

from beanie import init_beanie
from loguru import logger
from pymongo import AsyncMongoClient

from src.cache import UserSemaphore
from src.config import ConfigManager

from .models import Sudo


class Database:
    __slots__ = ("_client", "_semaphore")

    def __init__(self) -> None:
        DB_URL = ConfigManager.get("DB_URL")
        self._client = AsyncMongoClient(DB_URL)
        self._semaphore = UserSemaphore()

    async def initialize(self) -> None:
        await self._semaphore.initialize(name=self.__class__.__name__)
        await init_beanie(database=self._client.db_name,
                          document_models=[Sudo])
        await self._initialize_sudo()
        logger.debug(f"{self.__class__.__name__} Initialized")

    async def shutdown(self) -> None:
        await self._semaphore.shutdown(name=self.__class__.__name__)
        logger.debug(f"{self.__class__.__name__} Shutdown")

    async def _initialize_sudo(self) -> None:
        user_id = ConfigManager.get_int("OWNER_ID")
        if not await self.is_sudo(user_id=user_id):
            logger.debug(f"[{self.__class__.__name__}] Setting up `OWNER_ID`")
            await self.set_sudo(user_id=user_id)

    async def is_sudo(self, user_id: int) -> bool:
        sudo = await self.get_sudo(user_id=user_id)
        return sudo is not None

    async def get_sudo(self, user_id: int) -> Optional[Sudo]:
        return await Sudo.find({"user_id": user_id}).first_or_none()

    async def set_sudo(self, user_id: int) -> None:
        dbsemaphore = self._semaphore.get(user_id=user_id)
        async with dbsemaphore:
            if not await self.is_sudo(user_id=user_id):
                sudo = Sudo(user_id=user_id)
                await sudo.insert()

    async def remove_sudo(self, user_id: int) -> None:
        dbsemaphore = self._semaphore.get(user_id=user_id)
        async with dbsemaphore:
            if await self.is_sudo(user_id=user_id):
                sudo = await self.get_sudo(user_id=user_id)
                if sudo:
                    await sudo.delete()
