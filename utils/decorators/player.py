from functools import wraps

from models.CustomMogiContext import MogiApplicationContext
from utils.command_helpers.find_player import get_guild_member

from database.types import archive_type
from utils.data import mogi_manager
from services.players import find_player_profile


def with_player(
    query_varname: str | None = None,
    assert_in_mogi: bool = False,
    assert_not_in_mogi: bool = False,
    assert_not_suspended: bool = False,
):
    """
    Decorator that passes the target player variables to the slash_command and performs additional checks if wanted.
    Passes:
        `ctx.player`: the Lounge profile of the player in question
        `ctx.player_member`: the discord member object of the corresponding player

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

            query: str | int = (
                kwargs.get(query_varname) if kwargs.get(query_varname) else ctx.user.id
            )

            # Fetch player record and assign discord user as well
            ctx.player = await find_player_profile(query, archive=archive_type.INCLUDE)

            if not ctx.player:
                return await ctx.respond(
                    f"Couldn't find {'that' if query_varname else 'your'} Lounge profile."
                )

            ctx.player_discord = await get_guild_member(
                ctx.guild, ctx.player.discord_id
            )

            # Make sure the player is in the mogi
            if assert_in_mogi:
                if not ctx.player in ctx.mogi.players:
                    return await ctx.respond(
                        f"{'Player' if query_varname else 'You\'re'} not in this mogi",
                        ephemeral=True,
                    )

            # Make sure player is not already in a mogi (including in another channel)
            if assert_not_in_mogi:
                for mogi in mogi_manager.read_registry().values():
                    if ctx.player in mogi.players:
                        if mogi.channel_id == ctx.channel.id:
                            return await ctx.respond(
                                f"{'Player' if query_varname else 'You\'re'} already in this mogi"
                            )
                        return await ctx.respond(
                            f"{'Player' if query_varname else 'You\'re'} already in a mogi in <#{mogi.channel_id}>"
                        )

            # If suspended
            if assert_not_suspended and ctx.player.suspended:
                return await ctx.respond(
                    f"{'Player' if query_varname else 'You\'re'} temporarily unable to join mogis."
                )

            # Pass the player to the original function
            return await func(self, ctx, *args, **kwargs)

        return wrapper

    return decorator
