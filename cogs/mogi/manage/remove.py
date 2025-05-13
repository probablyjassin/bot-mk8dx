from discord import slash_command, Option
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from pycord.multicog import subcommand

from utils.decorators.player import with_player
from utils.decorators.checks import (
    is_mogi_not_in_progress,
    is_mogi_manager,
)


class remove(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @subcommand(group="manage")
    @slash_command(name="remove", description="Remove a player from the current mogi")
    @is_mogi_manager()
    @is_mogi_not_in_progress()
    @with_player(query_varname="player", assert_in_mogi=True)
    async def remove(
        self,
        ctx: MogiApplicationContext,
        player: str = Option(
            str, name="player", description="The player to remove from the mogi."
        ),
    ):
        ctx.mogi.players.remove(ctx.player)

        # remove the role
        if ctx.player_discord and ctx.inmogi_role in ctx.player_discord.roles:
            await ctx.player_discord.remove_roles(
                ctx.inmogi_role, reason="Removed from Mogi"
            )

        await ctx.respond(
            f"<@{ctx.player.discord_id}> was removed from the mogi.",
        )


def setup(bot: commands.Bot):
    bot.add_cog(remove(bot))
