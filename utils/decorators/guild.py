from functools import wraps
from bson.int64 import Int64

from models.CustomMogiContext import MogiApplicationContext
from utils.data import data_manager


def with_guild(
    query_varname: str | None = None,
    assert_is_owner: bool = False,
):
    """
    Decorator that passes the target lounge guild variables to the slash_command and performs additional checks if wanted.
    Passes:
        `ctx.lounge_guild`: the Lounge Guild of the player in question

    Arguments:
        **query_varname (str):** If the slash_command takes in a target player, it's variable name as string.\n
        If left empty, the user of the command will be the player in question.\n
        **assert_is_owner (bool):** Whether to check if player is the first entry in the list of guild members (aka the founder/owner)\n
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: MogiApplicationContext, *args, **kwargs):
            # Define which guild to operate on
            # kwargs.get(query_varname) is the guild query the user provided to the slash_command
            # if not provided, choose the command user's guild if applicable

            query: str | int | None = (
                kwargs.get(query_varname) if kwargs.get(query_varname) else ctx.user.id
            )

            # Fetch guild record
            ctx.lounge_guild = data_manager.Guilds.find(
                query=query if query else ctx.user.id
            )

            if not ctx.lounge_guild:
                return await ctx.respond(
                    f"Couldn't find {'that' if query_varname else 'your'} Guild profile."
                )

            # Make sure the player is the guild first member/founder/owner
            if assert_is_owner:
                if not ctx.lounge_guild.player_ids[0] == Int64(ctx.user.id):
                    return await ctx.respond(
                        f"Only <@{ctx.lounge_guild.player_ids[0]}> may administer in this guild"
                    )

            # Pass the player to the original function
            return await func(self, ctx, *args, **kwargs)

        return wrapper

    return decorator
