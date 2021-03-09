from os import getenv

from src.internal.bot import Bot

bot = Bot()

bot.load_extensions(
    "jishaku",
    "src.cogs.core",
    "src.cogs.config",
    "src.cogs.errors",
)

bot.run(getenv("TOKEN"))
