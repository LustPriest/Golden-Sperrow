from telegram.ext import Application
from .config import ConfigManager

application = Application.builder().token(ConfigManager.get('telegram', 'TOKEN')).build()
