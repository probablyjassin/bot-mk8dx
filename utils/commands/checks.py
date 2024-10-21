from discord import ApplicationContext
from discord.ext import commands
from discord.utils import get
from utils.objects import (
    get_mogi_manager_role,
    get_moderator_role,
    get_admin_role,
)


def is_mogi_manager():
    async def predicate(ctx: ApplicationContext):
        if ctx.author.guild_permissions.is_superset(
            (await get_mogi_manager_role()).permissions
        ):
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False

    return commands.check(predicate)


def is_moderator():
    async def predicate(ctx: ApplicationContext):
        if ctx.author.guild_permissions.is_superset(
            (await get_moderator_role()).permissions
        ):
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False

    return commands.check(predicate)


def is_admin():
    async def predicate(ctx: ApplicationContext):
        if ctx.author.guild_permissions.is_superset(
            (await get_admin_role()).permissions
        ):
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False

    return commands.check(predicate)
