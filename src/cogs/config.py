from discord.ext import commands
from discord import TextChannel, Member
from loguru import logger
from os import getenv

from src.internal.bot import Bot
from src.utils.checks import level


def in_guild(guild: int):
    async def predicate(ctx: commands.Context):
        return ctx.guild and ctx.guild.id == guild

    return commands.check(predicate)


class Config(commands.Cog):
    """Config functionality for CrossChat."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="setup")
    @level(100)
    async def setup(self, ctx: commands.Context, channel: str = "general"):
        """Set up a channel for crosschat."""

        guild = await self.bot.db.get_guild(ctx.guild.id)

        config = guild.config

        if "channels" not in config:
            config["channels"] = {str(ctx.channel.id): channel}
        else:
            config["channels"][str(ctx.channel.id)] = channel

        await self.bot.db.update_guild(ctx.guild.id, config)
        await self.bot.cogs["Core"].setup()
        await ctx.reply(f"Successfully linked {ctx.channel.mention} to cc:#{channel}")

    @commands.command(name="unlink")
    @commands.check_any(level(100), commands.has_guild_permissions(manage_guild=True))
    async def unlink(self, ctx: commands.Context, channel: TextChannel = None):
        """Unlink a channel."""

        channel = channel or ctx.channel

        guild = await self.bot.db.get_guild(ctx.guild.id)

        config = guild.config

        if "channels" not in config:
            config["channels"] = {}
            return await ctx.reply(
                "This channel isn't linked to any CrossChat channel."
            )
        elif str(channel.id) in config["channels"]:
            old = config["channels"].pop(str(channel.id))
        else:
            return await ctx.reply(
                "This channel isn't linked to any CrossChat channel."
            )

        await self.bot.db.update_guild(ctx.guild.id, config)
        await self.bot.cogs["Core"].setup()
        await ctx.reply(f"Successfully unlinked {channel.mention} from cc:#{old}")

    @commands.command(name="spl")
    @level(100)
    async def set_perm_level(
        self, ctx: commands.Context, member: Member, level: int = 0
    ):
        """Set a user's permission level."""

        user = await self.bot.db.get_user(
            member.id
        )  # Make sure the user exists, not perfect

        await self.bot.db.update_user_permissions(member.id, level)
        await ctx.reply(f"Successfully set permission level for {member} to {level}")

    @commands.command(name="addmod")
    @level(50)
    @in_guild(int(getenv("GUILD")))
    async def add_mod(self, ctx: commands.Context, member: Member):
        """Add a moderator."""

        if ctx.author == member:
            return await ctx.send("You can't perform this action on yourself.")

        user = await self.bot.db.get_user(member.id)
        author = await self.bot.db.get_user(ctx.author.id)

        if user >= author:
            return await ctx.send(
                "You can't perform this action on someone with the same as or higher permission level than you."
            )

        await self.set_perm_level(ctx, member, 10)

    @commands.command(name="delmod")
    @level(50)
    @in_guild(int(getenv("GUILD")))
    async def del_mod(self, ctx: commands.Context, member: Member):
        """Remove a moderator."""

        if ctx.author == member:
            return await ctx.send("You can't perform this action on yourself.")

        user = await self.bot.db.get_user(member.id)
        author = await self.bot.db.get_user(ctx.author.id)

        if user >= author:
            return await ctx.send(
                "You can't perform this action on someone with the same as or higher permission level than you."
            )

        await self.set_perm_level(ctx, member, 0)


def setup(bot: Bot):
    bot.add_cog(Config(bot))
