from discord import ApplicationContext
from discord.errors import CheckFailure
from discord.ext import commands
from discord.utils import get

from models.MogiModel import Mogi


@commands.Cog.listener()
async def on_application_command_error(ctx: ApplicationContext, error: Exception):
    if isinstance(error, CheckFailure):
        await ctx.respond(
            "You do not have the required permissions to use this command.",
            ephemeral=True,
        )


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


""" def is_mogi_open(mogi: Mogi):
    async def predicate(ctx: ApplicationContext):
        if mogi_status and ctx.author.guild_permissions.is_superset(
            get(ctx.guild.roles, name="Mogi Manager").permissions
        ):
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False

    return commands.check(predicate)
 """
