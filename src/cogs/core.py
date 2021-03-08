from discord.ext import commands
from discord import Message, TextChannel, Embed
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

    @staticmethod
    def get_badge(level: int):
        if level < 10:
            return "", "User"
        elif level < 100:
            return "🔧", "Server Staff"
        else:
            return "🛠️", "Global Admin"

    @staticmethod
    def censor_embed(embed: Embed, filter: MessageFilter) -> Embed:
        if embed.description:
            result = filter(embed.description)
            embed.description = result.message
        return embed

    @staticmethod
    def create_embed(message: Message, badge: str) -> Embed:
        tcr = 0
        for role in message.author.roles:
            if role.colour:
                tcr = role.colour

        embed = Embed(
            description=message.content,
            colour=tcr,
            timestamp=message.created_at,
        )

        embed.set_author(
            name=f"{message.author} {badge}",
            icon_url=str(message.author.avatar_url),
        )

        embed.set_footer(
            text=str(message.author.id)
        )

        return embed

    def should_ignore(self, message: Message):
        if message.author.bot or not message.guild:
            return True
        if message.channel.id not in self.channel_mapping:
            return True
        for pref in ["!", "c!", "]"]:
            if message.content.lower().startswith(pref):
                return True
        return False

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

    async def _siblings(self, id: int):
        message = await self.bot.db.get_message(id)

        if (not message) or message.id == message.bcid:
            return []

        return (await self.bot.db.get_messages(message.bcid)) or []

    async def _msginfo(self, id: int) -> Embed:
        message = await self.bot.db.get_message(id)

        if (not message) or message.id == message.bcid:
            return Embed(description="No message found with that ID")

        siblings = await self.bot.db.get_messages(message.bcid)
        original = await self.bot.db.get_message(message.bcid)

        embed = Embed(
            title=f"Message Info - {id}",
            colour=0x87CEEB,
            description="",
        )

        guild = self.bot.get_guild(original.guild_id)
        channel = self.bot.get_channel(original.channel_id)
        author = self.bot.get_user(original.author_id)

        embed.description += f"Parent ID: {original.id}\n"
        embed.description += f"Siblings: {', '.join([str(m.id) for m in siblings if m.id not in (original.id, id)])}\n"
        embed.description += f"Guild: {original.guild_id} ({guild})\n"
        embed.description += f"Channel: {original.channel_id} ({channel})\n"
        embed.description += f"Author: {original.author_id} ({author})"

        return embed

    async def _reject(self, message: Message, reason: str, delete_after: int = 10, dm: bool = False):
        await message.delete(delay=delete_after)
        if dm:
            return await message.author.send(reason)
        await message.reply(reason, delete_after=delete_after)

    async def _send(self, bcid: int, channel: TextChannel, bypass: bool = False, **kwargs):
        if not bypass:
            ft = self.filters.get(channel.guild.id)
            if "embed" in kwargs and ft:
                kwargs["embed"] = self.censor_embed(kwargs["embed"], ft)

        message = await channel.send(**kwargs)

        await self.bot.db.create_message(message, bcid)

        logger.info(f"Successfully sent message to {channel.id} [BCID: {bcid}]")

    async def broadcast(self, msgid: int, channel: str, **kwargs):
        channels = self.channels.get(channel, [])

        for cid in channels:
            self.bot.loop.create_task(self._send(msgid, self.bot.get_channel(cid), **kwargs))

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if self.should_ignore(message): return

        user = await self.bot.db.get_user(message.author.id)

        if user.banned:
            return await self._reject(message, "You cannot send messages as you are banned from CrossChat.")

        badge, _ = self.get_badge(user.permissions)
        embed = self.create_embed(message, badge)

        gc = self.channel_mapping[message.channel.id]

        await self.bot.db.create_message(message, message.id)
        await self.broadcast(message.id, gc, embed=embed)
        await message.delete()

    @commands.command(name="info")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    async def info(self, ctx: commands.Context, message: int):
        """Get info about a message."""

        await ctx.reply(embed=await self._msginfo(message))


def setup(bot: Bot):
    bot.add_cog(Core(bot))
