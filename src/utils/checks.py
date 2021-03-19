from discord.ext import commands


def level(l: int):
    async def predicate(ctx: commands.Context):
        user = await ctx.bot.db.get_user(ctx.author.id)

        return user.permissions >= l

    return commands.check(predicate)
