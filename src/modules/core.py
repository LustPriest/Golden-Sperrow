from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from types import ModuleType


class ModuleLoader:
    """Discovers, loads, and registers modules and their handlers."""

    def __init__(self) -> None:
        """Initializes the ModuleLoader."""
        self.modules: dict[str, dict[str, list[str]]] = {}
        self.parent_path: Path = Path(__file__).parent
        self.loaded_modules: set[str] = set()

    def discover_modules(self) -> None:
        """Discovers modules (directories containing Python files) in the parent directory."""
        logger.debug("Discovering modules...")

        for entry in self.parent_path.iterdir():
            if entry.is_dir() and entry.exists():
                module_name = entry.name
                if module_name == "helper":
                    logger.debug(f"Skipping helper module `{module_name}`")
                    continue
                elif module_name.startswith("_") or module_name.endswith("_"):
                    logger.debug(f"Skipping module `{module_name}`")
                    continue
                handlers = [
                    f"{module_name}.{file.stem}" for file in entry.glob("*.py")
                    if not file.name.startswith("_")
                ]
                if handlers:
                    self.modules[module_name] = {"handlers": handlers}
                    logger.debug(
                        f"Discovered module: {module_name} with handlers: {handlers}"
                    )
                else:
                    logger.warning(
                        f"Module `{module_name}` has no handlers. Skipping.")

    def load_module(self, module_name: str, handlers: list[str]) -> bool:
        """Loads a specific module.

        Args:
            module_name: The name of the module to load.
            handlers: A list of handler names within the module.

        Returns:
            True if the module was loaded successfully, False otherwise.
        """
        if module_name in self.loaded_modules:
            logger.warning(f"Module `{module_name}` already loaded. Skipping.")
            return True

        logger.debug(f"Loading module: {module_name}")
        success = True

        for handler_path in handlers:
            try:
                component: ModuleType = import_module(f".{handler_path}",
                                                      "src.modules")
                logger.debug(f"Imported component: {component.__name__}")
            except (ModuleNotFoundError, AttributeError, TypeError):
                logger.exception(f"Error loading handler: {handler_path}")
                success = False
                continue

        if success:
            self.loaded_modules.add(module_name)
            logger.debug(f"Module loaded successfully: {module_name}")
            return True
        else:
            logger.warning(f"Module `{module_name}` loaded with errors.")
            return False

    def load_all(self) -> None:
        """Loads all discovered modules."""
        logger.debug("Loading all modules...")

        self.discover_modules()

        loaded_count = 0
        for module_name, module_info in self.modules.items():
            if self.load_module(module_name, module_info["handlers"]):
                loaded_count += 1

        logger.info(f"Loaded {loaded_count} of {len(self.modules)} modules")
        if self.modules:
            logger.info(f"Loaded modules: {self.loaded_modules}")
        else:
            logger.info("No modules found to load.")
