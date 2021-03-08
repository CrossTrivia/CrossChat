from discord.ext import commands
from discord import Message, TextChannel
from collections import defaultdict
from async_rediscache import RedisCache
from loguru import logger

from src.internal.bot import Bot
from src.utils.filter import MessageFilter


class Core(commands.Cog):
    """Core functionality for CrossChat."""

    def __init__(self, bot: Bot):
        self.bot = bot

        self.redis = RedisCache(namespace="crosschat")
        self.filters = {}

        self.bot.loop.run_until_complete(self.setup())

    def init_filter(self, guild_id: int, words: list):
        self.filters[guild_id] = MessageFilter(words)

    async def setup(self):
        """Set up the bot ready for execution."""
        logger.info("Setting up core...")

        self.channel_mapping = {}
        self.channels = defaultdict(set)

        guilds = await self.bot.db.get_all_guilds()
        for guild in guilds:
            channels = guild.config.get('channels', {})

            for local, glob in channels.items():
                local = int(local)
                self.channel_mapping[local] = glob
                self.channels[glob].add(local)

            self.init_filter(guild.id, guild.config.get("words", []))

        logger.info("Core setup complete.")

    async def _send(self, bcid: int, channel: TextChannel, bypass: bool = False, **kwargs):
        message = await channel.send(**kwargs)

        await self.bot.db.create_message(message, bcid)

        logger.info(f"Successfully sent message to {channel.id} [BCID: {bcid}]")

    async def broadcast(self, message: Message, channel: str, **kwargs):
        channels = self.channels.get(channel, [])

        for cid in channels:
            self.bot.loop.create_task(self._send(message.id, self.bot.get_channel(cid), **kwargs))


def setup(bot: Bot):
    bot.add_cog(Core(bot))
