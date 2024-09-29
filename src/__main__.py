import importlib
from src.modules import ALL_MODULES

IMPORTED = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module('src.modules.' + module_name)
    if imported_module.__name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__name__.lower()] = imported_module

if __name__ == '__main__':
    application.run_polling(drop_pending_updates=True)
