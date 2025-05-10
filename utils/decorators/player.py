from functools import wraps

from models.PlayerModel import PlayerProfile
from models.CustomMogiContext import MogiApplicationContext

from utils.data.data_manager import data_manager, archive_type
from utils.data.mogi_manager import mogi_manager


def with_player(assert_not_in_mogi: bool = True, assert_not_suspended: bool = True):
    """
    Decorator that checks if the player exists in database and adds them to the function parameters.

    Arguments:
        check_in_mogi (bool): Whether to check if player is already in the current mogi
        check_other_mogis (bool): Whether to check if player is in another mogi channel

    Handles:
    - Player already in this mogi check
    - Player in another mogi check
    - Player existence in database check
    - Player suspension check

    Adds 'player' parameter to the wrapped function if all checks pass
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: MogiApplicationContext, *args, **kwargs):
            # Check if player is already in a mogi (including in another channel)
            if assert_not_in_mogi:
                for mogi in mogi_manager.mogi_registry.values():
                    for player in mogi.players:
                        if player.discord_id == ctx.author.id:
                            if mogi.channel_id == ctx.channel.id:
                                return await ctx.respond("You're already in this mogi.")
                            return await ctx.respond(
                                f"You're already in a mogi in <#{mogi.channel_id}>"
                            )

            # Fetch player record
            if player_entry := data_manager.find_player(
                query=ctx.author.id,
                archive=archive_type.INCLUDE,
            ):
                pass
            else:
                return await ctx.respond("You're not registered for Lounge.")

            # Assign Player object
            player = PlayerProfile(**player_entry)

            # If suspended
            if assert_not_suspended and player.suspended:
                return await ctx.respond("You're temporarily unable to join mogis.")

            # Pass the player to the original function
            return await func(self, ctx, player=player, *args, **kwargs)

        return wrapper

    return decorator
