import math, time
from discord import File

from models import MogiApplicationContext

from utils.maths.mmr_algorithm import calculate_mmr
from utils.maths.placements import get_placements_from_scores
from utils.maths.table import create_table

from config import FORMATS


async def process_tablestring(ctx: MogiApplicationContext, tablestring: str):
    ctx.mogi.finished_at = round(time.time())

    if not tablestring:
        await ctx.respond("No tablestring found")
        return False

    # Collect the points to the mogi
    try:
        ctx.mogi.collect_points(tablestring)
    except ValueError as e:
        await ctx.respond("Invalid tablestring format.")
        return False
    except KeyError as e:
        # Extract the username from the KeyError message
        username = str(e).strip("'")
        ctx.mogi.collected_points = []
        await ctx.respond(f"Missing player name in tablestring: `{username}`")
        return False

    # obtain the placements from the collected points
    placements = []
    for score in ctx.mogi.collected_points:
        placements.append(get_placements_from_scores(ctx.mogi.collected_points)[score])

    # break down names and mmrs of all players
    all_player_mmrs = [player.mmr for player in ctx.mogi.players]

    # Calculate MMR results
    results = calculate_mmr(
        all_player_mmrs,
        placements,
        ctx.mogi.format,
    )

    # apply custom mmr scaling
    results = [math.ceil(rating * 1.1) if rating > 0 else rating for rating in results]
    if ctx.mogi.is_mini:
        results = [math.floor(rating * 0.6) for rating in results]

    # store the results in the mogi, extended for every player
    for delta in results:
        ctx.mogi.mmr_results_by_group.extend([delta] * ctx.mogi.format)

    # Store the Placements in order of Players/Teams
    for place in placements:
        ctx.mogi.placements_by_group.extend([place] * ctx.mogi.format)

    if not len(ctx.mogi.mmr_results_by_group) == len(ctx.mogi.players):
        await ctx.respond(
            "Something has gone seriously wrong, the amount of players and the MMR results don't add up. Use /debug to find the issue and contact a moderator."
        )
        return False

    key_to_format = {
        int(format[0]) if format[0].isdigit() else 1: format for format in FORMATS
    }

    # Store the date of the results
    file = File(await create_table(ctx.mogi), filename="table.png")
    message = await ctx.results_channel.send(
        content=f"# Results - {time.strftime('%d.%m.%y')}\n"
        f"Duration: {int((ctx.mogi.finished_at - ctx.mogi.started_at) / 60)} minutes"
        f"{' | MINI MOGI' if ctx.mogi.is_mini else ' | ' + key_to_format[ctx.mogi.format]}",
        file=file,
    )

    await ctx.respond("Results got posted in the results channel.")

    ctx.mogi.table_message_id = message.id
    return True
