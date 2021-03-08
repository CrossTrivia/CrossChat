from discord.ext import commands
from discord import Intents
from aiohttp import ClientSession
from async_rediscache import RedisSession
from typing import Optional
from dotenv import load_dotenv
from loguru import logger
from traceback import format_exc
from os import getenv

from src.utils.database import Database


load_dotenv()


class Bot(commands.Bot):
    """A subclass of `commands.Bot` with additional features."""

    def __init__(self, *args, **kwargs):
        logger.info("Starting CrossChat...")
        intents = Intents.default()
        intents.members = True

        super().__init__(
            command_prefix="c!",
            intents=intents,
            *args,
            **kwargs,
        )

        self.http_session: Optional[ClientSession] = None
        self.redis_session: Optional[RedisSession] = None
        self.db = Database()

    def load_extensions(self, *exts):
        """Load a set of extensions."""
        for ext in exts:
            try:
                self.load_extension(ext)
                logger.info(f"Successfully loaded cog {ext}.")
            except Exception:
                logger.error(f"Failed to load cog: {ext}: {format_exc()}")

        logger.info("Cog loading complete.")

    async def login(self, *args, **kwargs) -> None:
        """Create the aiohttp ClientSession before logging in."""
        logger.info("Logging in to Discord...")

        self.http_session = ClientSession()

        logger.info("Creating redis session...")
        self.redis_session = RedisSession(address=getenv("REDIS_ADDR", "redis://localhost"))
        await self.redis_session.connect()
        logger.info("Redis session connected.")

        await super().login(*args, **kwargs)

    async def log(self, embed):
        channel = self.get_channel(int(getenv("LOGS")))

        await channel.send(embed=embed)
