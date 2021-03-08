from asyncio import get_event_loop
from asyncpg import create_pool
from os import getenv
from loguru import logger
from json import dumps, loads
from discord import Message as Msg
from collections import namedtuple
from datetime import datetime

Guild = namedtuple("Guild", ["id", "config", "created_at"])
User = namedtuple("User", ["id", "permissions", "banned", "created_at"])
Message = namedtuple("Message", ["id", "bcid", "guild_id", "channel_id", "author_id", "content", "deleted"])


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
        guilds = await self.fetch("SELECT * FROM Guilds;")

        gs = []
        for data in guilds:
            gs.append(Guild(data["id"], loads(data["config"]), data["created_at"]))

        return gs

    # User coros
    async def get_user(self, user_id: int):
        if user_id in self.users:
            return self.users[user_id]

        data = await self.fetchrow("SELECT * FROM Users WHERE id = $1;", user_id)

        if not data:
            return await self.create_user(user_id)

        user = User(data["id"], data["permissions"], data["banned"], data["created_at"])
        self.users[user_id] = user

        return user

    async def create_user(self, user_id: int):
        await self.execute("INSERT INTO Users (id) VALUES ($1);", user_id)
        self.users.pop(user_id, None)  # Shouldn't be needed, but I want to make sure

        return User(user_id, 0, False, datetime.utcnow())

    async def update_user_permissions(self, user_id: int, level: int):
        await self.execute("UPDATE Users SET permissions = $2 WHERE id = $1;", user_id, level)
        self.users.pop(user_id, None)  # Clear the cache

    # Message coros
    async def create_message(self, message: Msg, bcid: int):
        id = message.id
        guild_id = message.guild.id
        channel_id = message.channel.id
        author_id = message.author.id
        content = message.content

        await self.execute(
            "INSERT INTO Messages (id, bcid, guild_id, channel_id, author_id, content) VALUES ($1, $2, $3, $4, $5, $6);",
            id, bcid, guild_id, channel_id, author_id, content,
        )

    async def get_message(self, id: int):
        data = await self.fetchrow("SELECT * FROM Messages WHERE id = $1;", id)

        if not data:
            return None

        return Message(
            data["id"], data["bcid"], data["guild_id"], data["channel_id"], data["author_id"], data["content"], data["deleted"]
        )

    async def get_messages(self, bcid: int):
        messages = await self.fetch("SELECT * FROM Messages WHERE bcid = $1;", bcid)

        ms = []
        for data in messages:
            ms.append(Message(
                data["id"], data["bcid"], data["guild_id"], data["channel_id"], data["author_id"], data["content"], data["deleted"]
            ))
        return ms
