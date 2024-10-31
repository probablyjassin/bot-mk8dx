from discord.ext import commands
from discord.utils import get

from models.CustomMogiContext import MogiApplicationContext


async def check(
    ctx: MogiApplicationContext,
    condition: bool,
    error_message: str = "You're not allowed to use this command.",
):
    if condition:
        return True
    else:
        await ctx.respond(error_message, ephemeral=True)
        return False


def is_mogi_manager():
    async def predicate(ctx: MogiApplicationContext):
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
    async def predicate(ctx: MogiApplicationContext):
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
    async def predicate(ctx: MogiApplicationContext):
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
    async def predicate(ctx: MogiApplicationContext):
        return await check(
            ctx=ctx,
            condition=(ctx.mogi != None),
            error_message="No open Mogi in this channel.",
        )

    return commands.check(predicate)


def is_mogi_in_progress():
    async def predicate(ctx: MogiApplicationContext):
        return await check(
            ctx=ctx,
            condition=(ctx.mogi != None)
            and ctx.mogi.isVoting
            or (ctx.mogi.isPlaying)
            and (not ctx.mogi.isFinished),
            error_message="The mogi is either not in progress or has already finished calculations.",
        )

    return commands.check(predicate)


# BUG: this doesnt work when the mogi doesnt exist
def is_mogi_not_in_progress():
    async def predicate(ctx: MogiApplicationContext):
        return await check(
            ctx=ctx,
            condition=ctx.mogi
            and not ctx.mogi.isVoting
            and (not ctx.mogi.isPlaying)
            or (ctx.mogi.isFinished),
            error_message="The mogi is either not in progress or has already finished calculations.",
        )

    return commands.check(predicate)
