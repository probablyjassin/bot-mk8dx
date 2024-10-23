from discord import ApplicationContext
from discord.ext import commands
from discord.utils import get


def is_mogi_manager():
    async def predicate(ctx: ApplicationContext):
        if ctx.author.guild_permissions.is_superset(
            get(ctx.guild.roles, name="Mogi Manager").permissions
        ):
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False

    return commands.check(predicate)


def is_moderator():
    async def predicate(ctx: ApplicationContext):
        if ctx.author.guild_permissions.is_superset(
            get(ctx.guild.roles, name="Moderator").permissions
        ):
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False

    return commands.check(predicate)


def is_admin():
    async def predicate(ctx: ApplicationContext):
        if ctx.author.guild_permissions.is_superset(
            get(ctx.guild.roles, name="Admin").permissions
        ):
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False

    return commands.check(predicate)
