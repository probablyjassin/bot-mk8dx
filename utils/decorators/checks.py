from enum import Enum

from discord import ApplicationContext, ChannelType
from discord.ext import commands


async def _check(
    ctx: ApplicationContext,
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


def _is_at_least_role(ctx: ApplicationContext, role: LoungeRole) -> bool:
    """
    ## Internal function for command checkers that checks if the user has a sufficient role in the hierarchy
    `ctx.get_lounge_role(lounge_role.value[0]) in ctx.author.roles and lounge_role.value[1] >= min_level`
    """
    min_level = role.value[1]
    for lounge_role in LoungeRole:
        if (
            ctx.get_lounge_role(lounge_role.value[0]) in ctx.author.roles
            and lounge_role.value[1] >= min_level
        ):
            return True
    return False


def is_mogi_manager():
    """
    ## Command checker that requires the user to be at least Mogi Manager
    `_is_at_least_role(ctx, LoungeRole.MOGI_MANAGER)`
    """

    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=_is_at_least_role(ctx, LoungeRole.MOGI_MANAGER),
            error_message="You're not allowed to use this command.",
        )

    return commands.check(predicate)


def is_moderator():
    """
    ## Command checker that requires the user to be at least Moderator
    `_is_at_least_role(ctx, LoungeRole.MODERATOR)`
    """

    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=_is_at_least_role(ctx, LoungeRole.MODERATOR),
            error_message=f"You're not allowed to use this command.",
        )

    return commands.check(predicate)


def is_admin():
    """
    ## Command checker that requires the user to be Admin
    `_is_at_least_role(ctx, LoungeRole.ADMIN)`
    """

    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=_is_at_least_role(ctx, LoungeRole.ADMIN),
            error_message="You're not allowed to use this command.",
        )

    return commands.check(predicate)


def is_mogi_open():
    """
    ## Command checker that requires a mogi to exist in the current channel
    `ctx.mogi != None`
    """

    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=(ctx.mogi != None),
            error_message="No open Mogi in this channel.",
        )

    return commands.check(predicate)


def is_in_mogi(except_admin=False):
    """
    ## Command checker that requires the user to be in the channel's mogi
    `ctx.author.id in [player.discord_id for player in ctx.mogi.players]`
    """

    async def predicate(ctx: MogiApplicationContext):
        if except_admin and _is_at_least_role(ctx, LoungeRole.ADMIN):
            return True
        return await _check(
            ctx=ctx,
            condition=(
                ctx.author.id in [player.discord_id for player in ctx.mogi.players]
            ),
            error_message="You're not in this mogi.",
        )

    return commands.check(predicate)


def is_mogi_not_full():
    """
    ## Command checker that requires the mogi to have spots left
    `len(ctx.mogi.players) < ctx.mogi.player_cap`
    """

    async def predicate(ctx: MogiApplicationContext):
        return await _check(
            ctx=ctx,
            condition=len(ctx.mogi.players) < ctx.mogi.player_cap,
            error_message="There aren't enough spots left in the mogi.",
        )

    return commands.check(predicate)


def is_mogi_in_progress():
    """
    ## Command checker that requires the channel's mogi to be in progress
    `ctx.mogi and (ctx.mogi.vote or (ctx.mogi.isPlaying) and (not ctx.mogi.isFinished))`
    """

    async def predicate(ctx: MogiApplicationContext):
        message = "The mogi is either not open, not in progress or already finished and is about to be closed."
        if not ctx.mogi:
            message = "There is no open mogi in this channel."
        elif not (ctx.mogi.vote or (ctx.mogi.isPlaying) and (not ctx.mogi.isFinished)):
            message = "The mogi is not in progress."

        return await _check(
            ctx=ctx,
            condition=ctx.mogi
            and (ctx.mogi.vote or (ctx.mogi.isPlaying) and (not ctx.mogi.isFinished)),
            error_message=message,
        )

    return commands.check(predicate)


def is_mogi_not_in_progress():
    """
    ## Command checker that requires the channel's mogi not to be in progress
    `ctx.mogi and (not ctx.mogi.vote and (not ctx.mogi.isPlaying) or (ctx.mogi.isFinished))`
    """

    async def predicate(ctx: MogiApplicationContext):
        message = "The mogi is either not open, still in progress or hasn't finished calculations yet."
        if not ctx.mogi:
            message = "There is no open mogi in this channel."
        elif ctx.mogi.vote:
            message = "You can't join or leave while a vote is going on."
        elif ctx.mogi.collected_points:
            message = "The points are still being worked on. The mogi will close on it's own when it's done."
        elif ctx.mogi.isPlaying:
            message = "You can't join or leave while the mogi is in progress."

        return await _check(
            ctx=ctx,
            condition=ctx.mogi
            and (
                not ctx.mogi.vote and (not ctx.mogi.isPlaying) or (ctx.mogi.isFinished)
            ),
            error_message=message,
        )

    return commands.check(predicate)
