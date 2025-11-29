from discord import slash_command
from discord.ext import commands

from pycord.multicog import subcommand

from utils.decorators import is_admin
from utils.command_helpers import create_embed

from models import MogiApplicationContext, MogiHistoryData

from services.mogis import get_latest_mogi
from services.players import find_player_profiles_by_ids


class rollback(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @subcommand(group="manage", independent=True)
    @is_admin()
    @slash_command(
        name="rollback",
        description="Admin only: roll back the last mogi's results",
    )
    async def rollback(self, ctx: MogiApplicationContext):

        latest_mogi: MogiHistoryData | None = await get_latest_mogi()
        if not latest_mogi:
            return await ctx.respond("Couldn't find a latest mogi in the database.")

        latest_mogi.started_at

        all_players = await find_player_profiles_by_ids(latest_mogi.player_ids)

        last_mogi_embed = create_embed(
            title="Latest mogi:",
            description="You are trying to revert the following mogi:",
            fields={
                "Started at:" f"<t:{latest_mogi.started_at}>",
                "Finished at:" f"<t:{latest_mogi.finished_at}>",
                "Players:"
                "\n".join(f"<@{player}>" for player in latest_mogi.player_ids),
                "MMR changes (in player order):" "\n".join(latest_mogi.results),
            },
        )

        return await ctx.respond(embed=last_mogi_embed)


def setup(bot: commands.Bot):
    bot.add_cog(rollback(bot))
