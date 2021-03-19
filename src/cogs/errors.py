from discord import Embed
from discord.ext import commands
from discord.ext.commands import errors
from loguru import logger

from src.internal.bot import Bot


class Errors(commands.Cog):
    """Error handling functionality for CrossChat."""

    def __init__(self, bot: Bot):
        self.bot = bot

    def _get_error_embed(self, title: str, body: str) -> Embed:
        """Return an embed that contains the exception."""
        return Embed(
            title=title,
            colour=0xFF0000,
            description=body,
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, e: errors.CommandError):
        command = ctx.command

        if isinstance(command, errors.CommandNotFound):
            return
        elif isinstance(e, errors.MissingRequiredArgument):
            embed = self._get_error_embed("Missing required argument", e.param.name)
            await ctx.reply(embed=embed)
        elif isinstance(e, errors.TooManyArguments):
            embed = self._get_error_embed("Too many arguments", str(e))
            await ctx.reply(embed=embed)
        elif isinstance(e, errors.BadArgument):
            embed = self._get_error_embed("Bad argument", str(e))
            await ctx.reply(embed=embed)
        elif isinstance(e, errors.BadUnionArgument):
            embed = self._get_error_embed("Bad argument", f"{e}\n{e.errors[-1]}")
            await ctx.reply(embed=embed)
        elif isinstance(e, errors.ArgumentParsingError):
            embed = self._get_error_embed("Argument parsing error", str(e))
            await ctx.reply(embed=embed)
        elif isinstance(e, errors.MemberNotFound):
            embed = self._get_error_embed("Member not found", str(e))
            await ctx.reply(embed=embed)
        else:
            embed = self._get_error_embed(
                "Input error",
                "Something about your input seems off. Check the arguments and try again.",
            )
            await ctx.reply(embed=embed)

        logger.error(f"Error while executing command {command}: {e.__class__.__name__}")


def setup(bot: Bot):
    bot.add_cog(Errors(bot))
