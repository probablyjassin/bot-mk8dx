from discord import ChannelType
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from enum import Enum


async def _check(
    ctx: MogiApplicationContext,
    condition: bool,
    error_message: str = "You're not allowed to use this command.",
):
    if not ctx.channel.type == ChannelType.private and condition:
        return True
    else:
        await ctx.respond(error_message, ephemeral=True)
        return False


class LoungeRole(Enum):
    ADMIN = ("Admin", 3)
    MODERATOR = ("Moderator", 2)
    MOGI_MANAGER = ("Mogi Manager", 1)


def _is_at_least_role(ctx: MogiApplicationContext, role: LoungeRole) -> bool:
    min_level = role.value[1]
    for lounge_role in LoungeRole:
        if (
            ctx.get_lounge_role(lounge_role.value[0]) in ctx.author.roles
            and lounge_role.value[1] >= min_level
        ):
            return True
    return False


def is_mogi_manager():
    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=_is_at_least_role(ctx, LoungeRole.MOGI_MANAGER),
            error_message="You're not allowed to use this command.",
        )

    return commands.check(predicate)


def is_moderator():
    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=_is_at_least_role(ctx, LoungeRole.MODERATOR),
            error_message=f"You're not allowed to use this command. Debug Your Top Role:{ctx.author.top_role}",
        )

    return commands.check(predicate)


def is_admin():
    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=_is_at_least_role(ctx, LoungeRole.ADMIN),
            error_message="You're not allowed to use this command.",
        )

    return commands.check(predicate)


def is_mogi_open():
    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=(ctx.mogi != None),
            error_message="No open Mogi in this channel.",
        )

    return commands.check(predicate)


def is_in_mogi():
    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=(
                ctx.author.id in [player.discord_id for player in ctx.mogi.players]
            ),
            error_message="You're not in this mogi.",
        )

    return commands.check(predicate)


def is_mogi_in_progress():
    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=ctx.mogi
            and (
                ctx.mogi.isVoting or (ctx.mogi.isPlaying) and (not ctx.mogi.isFinished)
            ),
            error_message="The mogi is either not in progress or has already finished calculations.",
        )

    return commands.check(predicate)


def is_mogi_not_in_progress():
    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=ctx.mogi
            and (
                not ctx.mogi.isVoting
                and (not ctx.mogi.isPlaying)
                or (ctx.mogi.isFinished)
            ),
            error_message="The mogi is either not in progress or has already finished calculations.",
        )

    return commands.check(predicate)
