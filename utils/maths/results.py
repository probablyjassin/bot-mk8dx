from typing import TYPE_CHECKING

import math, time, asyncio
from discord import File

from .placements import get_placements_from_scores
from .mmr_algorithm import calculate_mmr
from .table import create_table

from config import FORMATS

if TYPE_CHECKING:
    from models.CustomMogiContext import MogiApplicationContext
    from models.PlayerModel import PlayerProfile


def collect_points(
    tablestring: str, teams: list[list["PlayerProfile"]]
) -> tuple[list[int], int]:
    """
    Collects and calculates points for players and teams from a given table string.\n
    Returns a tuple of 1. the scores and 2. the amount of DCs infered from the tablestring.
    """

    all_players: list["PlayerProfile"] = [player for team in teams for player in team]
    disconnections: int = 0
    all_points = {}

    try:
        for line in tablestring.split("\n"):
            line = line.replace("|", "+")
            sections = line.split()
            for player in all_players:
                if sections and sections[0] == player.name:
                    parts = [part.split("+") for part in line.split()]
                    points = sum(
                        [int(num) for part in parts for num in part if num.isdigit()]
                    )
                    all_points[player.name] = points
                    disconnections = (
                        len([num for part in parts for num in part if num.isdigit()])
                        - 1
                    )
    except Exception as e:
        print(e)

    team_points_list = []
    for team in teams:

        try:
            team_points = sum(all_points[player.name] for player in team)
        except KeyError as error:
            raise error

        team_points_list.append(team_points)

    return team_points_list, disconnections


async def calculate_results_from_tablestring(
    tablestring: str,
    players: list["PlayerProfile"],
    team_size: int,
    is_mini: bool = False,
) -> dict:
    """
    Calculates MMR results from a tablestring.

    Returns:
        - dict with keys:
            - collected_points: list[int]
            - disconnections: int
            - mmr_results: list[int]
            - placements: list[int]
            - finished_at: int
            - error: str (if any error occurred)
    """

    finished_at = round(time.time())

    if not tablestring:
        return {"error": "No tablestring found"}

    # Group players into teams
    teams = []
    for i in range(0, len(players), team_size):
        teams.append(players[i : i + team_size])

    # Collect the points
    try:
        collected_points, disconnections = collect_points(tablestring, teams)
    except ValueError:
        return {"error": "Invalid tablestring format."}
    except KeyError as e:
        username = str(e).strip("'")
        return {"error": f"Missing player name in tablestring: `{username}`"}

    # Obtain the placements from the collected points
    placements = []
    for score in collected_points:
        placements.append(get_placements_from_scores(collected_points)[score])

    # Break down MMRs of all players
    all_player_mmrs = [player.mmr for player in players]

    # Calculate MMR results
    mmr_deltas = calculate_mmr(
        all_player_mmrs,
        placements,
        team_size,
    )

    # Apply custom MMR scaling
    mmr_deltas = [
        math.ceil(rating * 1.1) if rating > 0 else rating for rating in mmr_deltas
    ]
    if is_mini:
        mmr_deltas = [math.floor(rating * 0.6) for rating in mmr_deltas]

    # Extend results for every player in each team
    mmr_results_by_player = []
    placements_by_player = []
    for delta in mmr_deltas:
        mmr_results_by_player.extend([delta] * team_size)
    for place in placements:
        placements_by_player.extend([place] * team_size)

    # Validate
    if len(mmr_results_by_player) != len(players):
        return {
            "error": "Something has gone seriously wrong, the amount of players and the MMR results don't add up."
        }

    return {
        "collected_points": collected_points,
        "disconnections": disconnections,
        "mmr_results": mmr_results_by_player,
        "placements": placements_by_player,
        "finished_at": finished_at,
    }


async def end_collect_tablestring_to_results(
    ctx: "MogiApplicationContext", tablestring: str
):
    """
    Wraps the abstracted calculate_results_from_tablestring function.
    """

    # Use the abstracted function
    results = await calculate_results_from_tablestring(
        tablestring=tablestring,
        players=ctx.mogi.players,
        team_size=ctx.mogi.format,
        is_mini=ctx.mogi.is_mini,
    )

    # Handle errors
    if "error" in results:
        await ctx.respond(results["error"])
        return False

    # Apply results to mogi
    ctx.mogi.finished_at = results["finished_at"]
    ctx.mogi.collected_points = results["collected_points"]
    ctx.mogi.disconnections = results["disconnections"]
    ctx.mogi.mmr_results_by_group = results["mmr_results"]
    ctx.mogi.placements_by_group = results["placements"]

    key_to_format = {
        int(format[0]) if format[0].isdigit() else 1: format for format in FORMATS
    }

    # Create and send the results table
    file = File(
        await asyncio.to_thread(
            create_table,
            names=[player.name for player in ctx.mogi.players],
            old_mmrs=[player.mmr for player in ctx.mogi.players],
            results=ctx.mogi.mmr_results_by_group,
            placements=ctx.mogi.placements_by_group,
            team_size=ctx.mogi.format,
        ),
        filename="table.png",
    )
    message = await ctx.results_channel.send(
        content=f"# Results - {time.strftime('%d.%m.%y')}\n"
        f"Duration: {int((ctx.mogi.finished_at - ctx.mogi.started_at) / 60)} minutes"
        f"{' | MINI MOGI' if ctx.mogi.is_mini else ' | ' + key_to_format[ctx.mogi.format]}",
        file=file,
    )

    await ctx.respond("Results got posted in the results channel.")

    ctx.mogi.table_message_id = message.id
    return True
