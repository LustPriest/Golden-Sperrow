from . import health_checker
from .bot import Bot

if __name__ == "__main__":
    health_checker.check()

    bot = Bot()
    bot.run()
