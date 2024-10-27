from discord import ApplicationContext
from discord.errors import CheckFailure
from discord.ext import commands
from discord.utils import get

from utils.data.mogi_manager import mogi_registry
from models.MogiModel import Mogi


async def check(
    ctx: ApplicationContext,
    condition: bool,
    error_message: str = "You're not allowed to use this command.",
):
    if condition:
        return True
    else:
        await ctx.respond(error_message, ephemeral=True)
        return False


def is_mogi_manager():
    async def predicate(ctx: ApplicationContext):
        return await check(
            ctx=ctx,
            condition=(
                ctx.author.guild_permissions.is_superset(
                    get(ctx.guild.roles, name="Mogi Manager").permissions
                )
            ),
            error_message="You're not allowed to use this command.",
        )

    return commands.check(predicate)


def is_moderator():
    async def predicate(ctx: ApplicationContext):
        return await check(
            ctx=ctx,
            condition=(
                ctx.author.guild_permissions.is_superset(
                    get(ctx.guild.roles, name="Moderator").permissions
                )
            ),
            error_message="You're not allowed to use this command.",
        )

    return commands.check(predicate)


def is_admin():
    async def predicate(ctx: ApplicationContext):
        return await check(
            ctx=ctx,
            condition=(
                ctx.author.guild_permissions.is_superset(
                    get(ctx.guild.roles, name="Admin").permissions
                )
            ),
            error_message="You're not allowed to use this command.",
        )

    return commands.check(predicate)


def is_mogi_open():
    async def predicate(ctx: ApplicationContext):
        return await check(
            ctx=ctx,
            condition=(mogi_registry.get(ctx.channel.id) != None),
            error_message="No open Mogi in this channel.",
        )

    return commands.check(predicate)


def is_mogi_in_progress():
    async def predicate(ctx: ApplicationContext):
        mogi: Mogi = mogi_registry.get(ctx.channel.id)
        return await check(
            ctx=ctx,
            condition=(not mogi.isVoting)
            and (mogi.isPlaying)
            and (not mogi.isFinished),
            error_message="The mogi is either not in progress or has already finished calculations.",
        )

    return commands.check(predicate)
