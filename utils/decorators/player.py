from functools import wraps
from bson.int64 import Int64

from models.CustomMogiContext import MogiApplicationContext

from utils.data.data_manager import data_manager, archive_type
from utils.data.mogi_manager import mogi_manager


def with_player(
    query_varname: str = None,
    assert_in_mogi: bool = False,
    assert_not_in_mogi: bool = False,
    assert_not_suspended: bool = False,
):
    """
    Decorator that assigns the target player to `ctx.player` and performs additional checks if wanted.

    Arguments:
        **query_varname (str):** If the slash_command takes in a target player, it's variable name as string.\n
        If left empty, the user of the command will be the player in question.\n
        **assert_in_mogi (bool):** Whether to check if player is already in the current mogi\n
        **assert_not_in_mogi (bool):** Whether to check if player not in any mogi\n
        **assert_not_suspended (bool):** Whether to ensure the player may not be suspended\n
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: MogiApplicationContext, *args, **kwargs):
            # Define which player to operate on
            # kwargs.get(query_varname) is the player query the user provided to the slash_command
            # if not provided, choose the command user
            target_query: str | int | Int64 | None = (
                kwargs.get(query_varname, None) or ctx.user.id
            )

            # Fetch player record
            ctx.player = data_manager.find_player(
                query=target_query, archive=archive_type.INCLUDE
            )

            if not ctx.player:
                return await ctx.respond("Couldn't find Lounge profile.")

            # Make sure the player is in the mogi
            if assert_in_mogi:
                if not ctx.player in ctx.mogi.players:
                    return await ctx.respond("You're not in this mogi")

            # Make sure player is not already in a mogi (including in another channel)
            if assert_not_in_mogi:
                for mogi in mogi_manager.mogi_registry.values():
                    if ctx.player in mogi.players:
                        if mogi.channel_id == ctx.channel.id:
                            return await ctx.respond("You're already in this mogi")
                        return await ctx.respond(
                            f"You're already in a mogi in <#{mogi.channel_id}>"
                        )

            # If suspended
            if assert_not_suspended and ctx.player.suspended:
                return await ctx.respond("Temporarily unable to join mogis.")

            # Pass the player to the original function
            return await func(self, ctx, *args, **kwargs)

        return wrapper

    return decorator
