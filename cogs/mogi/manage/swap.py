from discord import slash_command, Option
from discord.ext import commands

from models import MogiApplicationContext, PlayerProfile
from pycord.multicog import subcommand

from utils.maths import recurse_replace
from utils.decorators import (
    is_mogi_open,
    is_admin,
)


class swap(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @subcommand(group="manage")
    @slash_command(
        name="swap",
        description="Swap two players in the mogi with one another (for teams)",
    )
    @is_admin()
    @is_mogi_open()
    async def swap(
        self,
        ctx: MogiApplicationContext,
        player1: str = Option(str, name="player1", description="first player"),
        player2: str = Option(str, name="player2", description="second player"),
    ):
        return await ctx.respond("This command is out of order.")
        """ first_player: PlayerProfile | str = await find(player1) or player1
        second_player: PlayerProfile | str = await find(player2) or player2
        for player in [first_player, second_player]:
            if isinstance(player, str):
                return await ctx.respond(f"{player} not found")
            if player not in ctx.mogi.players:
                return await ctx.send(f"<@{player.discord_id}> not in the mogi")

        ctx.mogi.players = recurse_replace(
            ctx.mogi.players, first_player, second_player
        )
        ctx.mogi.players = recurse_replace(
            ctx.mogi.players, second_player, first_player
        )
        ctx.mogi.players = recurse_replace(
            ctx.mogi.players, first_player, second_player
        )
        ctx.mogi.teams = recurse_replace(ctx.mogi.teams, second_player, first_player)

        await ctx.respond(f"Swapped {first_player.name} with {second_player.name}")

 """


def setup(bot: commands.Bot):
    bot.add_cog(swap(bot))
