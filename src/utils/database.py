from asyncio import get_event_loop
from asyncpg import create_pool
from os import getenv
from loguru import logger
from json import dumps, loads
from collections import namedtuple

Guild = namedtuple("Guild", ["id", "config", "created_at"])
User = namedtuple("User", ["id", "permissions", "banned", "created_at"])


class Database:
    """A database interface for the bot to connect to Postgres."""

    def __init__(self):
        self.guilds = {}
        self.users = {}

        loop = get_event_loop()
        loop.run_until_complete(self.setup())

    async def setup(self):
        logger.info("Setting up database connections...")
        self.pool = await create_pool(
            host=getenv("DB_HOST", "127.0.0.1"),
            port=getenv("DB_PORT", 5432),
            database=getenv("DB_DATABASE", "crosschat"),
            user=getenv("DB_USER", "root"),
            password=getenv("DB_PASS", "password"),
        )
        logger.info("Database setup complete.")

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    # Guild Coros
    async def get_guild(self, guild_id: int):
        if guild_id in self.guilds:
            return self.guilds[guild_id]

        data = await self.fetchrow("SELECT * FROM Guilds WHERE id = $1;", guild_id)

        if not data:
            return None

        guild = Guild(data["id"], loads(data["config"]), data["created_at"])
        self.guilds[guild_id] = guild

        return guild

    async def create_guild(self, guild_id: int, config: dict = {}):
        await self.execute("INSERT INTO Guilds (id, config) VALUES ($1, $2);", guild_id, dumps(config))
        self.guilds.pop(guild_id, None)  # Shouldn't be needed, but I want to make sure

    async def update_guild(self, guild_id: int, config: dict):
        await self.execute("UPDATE Guilds SET config = $2 WHERE id = $1;", guild_id, dumps(config))
        self.guilds.pop(guild_id, None)  # Clear the cache

    async def get_all_guilds(self):
        return await self.fetch("SELECT * FROM Guilds;")

    # User coros
    async def get_user(self, user_id: int):
        if user_id in self.users:
            return self.users[user_id]

        data = await self.fetchrow("SELECT * FROM Users WHERE id = $1;", user_id)

        if not data:
            return None

        user = User(data["id"], data["permissions"], data["banned"], data["created_at"])
        self.users[user_id] = user

        return user

    async def create_user(self, user_id: int):
        await self.execute("INSERT INTO Users (id, messages) VALUES ($1, 1);", user_id)
        self.users.pop(user_id, None)  # Shouldn't be needed, but I want to make sure

    async def update_user_permissions(self, user_id: int, level: int):
        await self.execute("UPDATE Users SET permissions = $2 WHERE id = $1;", user_id, level)
        self.users.pop(user_id, None)  # Clear the cache
