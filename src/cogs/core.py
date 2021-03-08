from discord.ext import commands
from collections import defaultdict
from async_rediscache import RedisCache
from loguru import logger

from src.internal.bot import Bot


class Core(commands.Cog):
    """Core functionality for CrossChat."""

    def __init__(self, bot: Bot):
        self.bot = bot

        self.redis = RedisCache(namespace="crosschat")

        self.bot.loop.run_until_complete(self.setup())

    async def setup(self):
        """Set up the bot ready for execution."""
        logger.info("Setting up core...")

        self.channel_mapping = {}
        self.channels = defaultdict(set)

        guilds = await self.bot.db.get_all_guilds()
        for guild in guilds:
            channels = guild.config.get('channels', {})

            for local, glob in channels.items():
                self.channel_mapping[local] = glob
                self.channels[glob].add(local)

        logger.info("Core setup complete.")


def setup(bot: Bot):
    bot.add_cog(Core(bot))
