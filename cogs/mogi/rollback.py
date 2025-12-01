import time, asyncio, math

from discord import slash_command, File
from discord.ext import commands

from pycord.multicog import subcommand

from utils.decorators import is_admin
from utils.command_helpers import create_embed, confirmation, get_awaited_message
from utils.maths import (
    get_placements_from_scores,
    create_table,
    calculate_mmr,
    calculate_results_from_tablestring,
)

from models import MogiApplicationContext, MogiHistoryData

from services.mogis import get_latest_mogi
from services.players import find_player_profiles_by_ids

from config import FORMATS

# TODO: overhaul the actual mogi collect points function(s) to standardize them to do this as well.


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
        await ctx.defer()

        latest_mogi: MogiHistoryData | None = await get_latest_mogi()
        if not latest_mogi:
            return await ctx.respond("Couldn't find a latest mogi in the database.")

        all_players = await find_player_profiles_by_ids(latest_mogi.player_ids)
        latest_team_size = max(latest_mogi.format, 1)

        last_mogi_embed = create_embed(
            title="Latest mogi:",
            description="You are trying to revert the following mogi:",
            fields={
                "Started at:": f"<t:{latest_mogi.started_at}>",
                "Finished at:": f"<t:{latest_mogi.finished_at}>",
                "Players:": "\n".join(
                    f"<@{player}>" for player in latest_mogi.player_ids
                ),
                "MMR changes (in player order):": "\n".join(
                    [str(score) for score in latest_mogi.results]
                ),
            },
        )

        erase_mogi_fully: bool = True

        if await confirmation(
            ctx=ctx,
            text="# React ✅ to overwrite the mogi with new fixed scores\n# OR ❌ to erase it completely!",
            user_id=ctx.user.id,
            embed=last_mogi_embed,
        ):
            erase_mogi_fully = False

            # Ask user to input the new table string
            await ctx.send(
                "Please send the corrected table string in this channel.\n"
                "You have 60 seconds to respond."
            )

            tablestring = await get_awaited_message(
                bot=self.bot, ctx=ctx, target_channel=ctx.channel
            )

            if not tablestring:
                return await ctx.respond(
                    "No table string provided. Rollback cancelled."
                )

            results = calculate_results_from_tablestring(
                tablestring=tablestring,
                players=all_players,
                team_size=latest_team_size,
                is_mini=latest_mogi.format == 0,
            )

            if "error" in results:
                return await ctx.respond(results["error"])

            key_to_format = {
                int(format[0]) if format[0].isdigit() else 1: format
                for format in FORMATS
            }

            # Create the results table
            file = File(
                await asyncio.to_thread(
                    create_table,
                    names=[player.name for player in all_players],
                    old_mmrs=[
                        player.mmr - latest_mogi.results[i]
                        for i, player in enumerate(all_players)
                    ],
                    results=results["mmr_results_by_player"],
                    placements=results["placements_by_player"],
                    team_size=latest_team_size,
                ),
                filename="table.png",
            )

            await ctx.respond(
                content=f"# Rollback - New Results\n"
                f"Original duration: {int((latest_mogi.finished_at - latest_mogi.started_at) / 60)} minutes\n"
                f"Format: {key_to_format.get(latest_team_size, 'Unknown')}",
                file=file,
            )

            # TODO: Update the database with new results

        else:
            # TODO: erase completely
            await ctx.respond("This is not implemented yet.")

        return await ctx.respond("WIP")


def setup(bot: commands.Bot):
    bot.add_cog(rollback(bot))
