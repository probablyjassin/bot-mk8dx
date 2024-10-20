import discord
from discord import Option, ApplicationContext
from discord.ext import commands
from discord.utils import get

def is_allowed_server(server_id: int):
    return server_id in [1084911987626094654, 1056713663714693241]

def is_mogi_manager():
    async def predicate(ctx: ApplicationContext):
        if is_allowed_server(ctx.guild_id) and (ctx.user.guild_permissions.administrator or get(ctx.guild.roles, name="Mogi Manager") in ctx.user.roles):
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False
    return commands.check(predicate)

def is_admin():
    async def predicate(ctx: ApplicationContext):
        if is_allowed_server(ctx.guild_id) and ctx.user.guild_permissions.administrator:
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False
    return commands.check(predicate)

def is_moderator():
    async def predicate(ctx: ApplicationContext):
        if is_allowed_server(ctx.guild_id) and (ctx.user.guild_permissions.administrator or get(ctx.guild.roles, name="Moderator") in ctx.user.roles):
            return True
        else:
            await ctx.respond("You're not allowed to use this command.", ephemeral=True)
            return False
    return commands.check(predicate)

def is_lounge_information_channel():
    async def predicate(ctx: ApplicationContext):
        if ctx.channel_id in [1181312934803144724]:
            return True
        else:
            await ctx.respond("This is only usable in #lounge-information", ephemeral=True)
            return False
    return commands.check(predicate)