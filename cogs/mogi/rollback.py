import time, asyncio, math

from discord import slash_command, File
from discord.ext import commands

from pycord.multicog import subcommand

from utils.decorators import is_admin
from utils.command_helpers import create_embed, confirmation, get_awaited_message
from utils.maths import get_placements_from_scores, create_table, calculate_mmr

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
            await ctx.respond(
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

            # Collect the points from the tablestring
            all_points = {}
            try:
                # get points per player like in mogi.collect_points()
                for line in tablestring.split("\n"):
                    line = line.replace("|", "+")
                    sections = line.split()
                    for player in all_players:
                        if sections and sections[0] == player.name:
                            parts = [part.split("+") for part in line.split()]
                            points = sum(
                                [
                                    int(num)
                                    for part in parts
                                    for num in part
                                    if num.isdigit()
                                ]
                            )
                            all_points[player.name] = points

                # Verify all players are in the tablestring
                if len(all_points) != len(all_players):
                    missing_players = [
                        p.name for p in all_players if p.name not in all_points
                    ]
                    await ctx.respond(
                        f"Missing players in tablestring: {', '.join(missing_players)}"
                    )
                    return

            except ValueError as e:
                return await ctx.respond("Invalid tablestring format.")
            except KeyError as e:
                # Extract the username from the KeyError message
                username = str(e).strip("'")
                return await ctx.respond(
                    f"Missing player name in tablestring: `{username}`"
                )

            # Group players into teams based on format and calc points
            team_size = latest_mogi.format
            team_points_list = []

            if team_size == 1:
                for player in all_players:
                    try:
                        team_points_list.append(all_points[player.name])
                    except KeyError as error:
                        await ctx.respond(
                            f"Failed to find points for player: {player.name}"
                        )
                        return
            else:
                # if teams group players by team size
                num_teams = len(all_players) // team_size
                for team_idx in range(num_teams):
                    team = all_players[
                        team_idx * team_size : (team_idx + 1) * team_size
                    ]
                    try:
                        team_points = sum(all_points[player.name] for player in team)
                        team_points_list.append(team_points)
                    except KeyError as error:
                        await ctx.respond(
                            f"Failed to find points for a player in team {team_idx + 1}"
                        )
                        return

            # obtain the placements from the collected points
            placements = []
            for score in team_points_list:
                placements.append(get_placements_from_scores(team_points_list)[score])

            # break down names and mmrs of all players
            all_player_mmrs = [player.mmr for player in all_players]

            # Calculate MMR results
            results = calculate_mmr(
                all_player_mmrs,
                placements,
                team_size,
            )

            # apply custom mmr scaling
            results = [
                math.ceil(rating * 1.1) if rating > 0 else rating for rating in results
            ]
            # TODO: mini-mogi scaling (format == 0)

            # store the results extended for every player
            mmr_results_by_player = []
            for delta in results:
                mmr_results_by_player.extend([delta] * team_size)

            # Store the Placements in order of Players
            placements_by_player = []
            for place in placements:
                placements_by_player.extend([place] * team_size)

            if not len(mmr_results_by_player) == len(all_players):
                await ctx.respond(
                    "Something has gone seriously wrong, the amount of players and the MMR results don't add up."
                )
                return

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
                    results=mmr_results_by_player,
                    placements=placements_by_player,
                    team_size=team_size,
                ),
                filename="table.png",
            )

            await ctx.respond(
                content=f"# Rollback - New Results\n"
                f"Original duration: {int((latest_mogi.finished_at - latest_mogi.started_at) / 60)} minutes\n"
                f"Format: {key_to_format.get(team_size, 'Unknown')}",
                file=file,
            )

            # TODO: Update the database with new results

        else:
            # TODO: erase completely
            await ctx.respond("This is not implemented yet.")

        return await ctx.respond("WIP")


def setup(bot: commands.Bot):
    bot.add_cog(rollback(bot))
