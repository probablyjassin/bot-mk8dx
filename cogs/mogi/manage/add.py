from discord import Option, slash_command
from discord.ext import commands

from models import MogiApplicationContext
from pycord.multicog import subcommand

from utils.command_helpers import player_name_autocomplete
from utils.decorators import (
    is_mogi_not_in_progress,
    is_mogi_not_full,
    is_moderator,
    with_player,
)


class add(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @subcommand(group="manage", independent=True)
    @slash_command(name="add", description="Add a player to the current mogi")
    @is_moderator()
    @is_mogi_not_in_progress()
    @is_mogi_not_full()
    @with_player(
        query_varname="player", assert_not_in_mogi=True, assert_not_suspended=True
    )
    async def add_player(
        self,
        ctx: MogiApplicationContext,
        player: str = Option(
            str,
            name="player",
            description="username | @ mention | discord_id",
            autocomplete=player_name_autocomplete,
        ),
    ):
        # Add to mogi and add roles
        ctx.mogi.players.append(ctx.player)
        if ctx.player_discord and ctx.inmogi_role not in ctx.player_discord.roles:
            await ctx.player_discord.add_roles(ctx.inmogi_role, reason="Added to Mogi")

        await ctx.respond(
            f"<@{ctx.player.discord_id}> joined the mogi! (against their will)"
        )


def setup(bot: commands.Bot):
    bot.add_cog(add(bot))
