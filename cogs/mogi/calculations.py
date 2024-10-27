import math

from discord import (
    SlashCommandGroup,
    ApplicationContext,
    ChannelType,
    Thread,
    File,
)
from discord.ext import commands

from models.MogiModel import Mogi
from utils.maths.mmr_algorithm import calculate_mmr
from utils.maths.placements import get_placements_from_scores
from utils.maths.table import create_table
from utils.maths.apply import apply_mmr

from utils.command_helpers.apply_update_roles import update_roles
from utils.command_helpers.wait_for import get_awaited_message
from utils.data.mogi_manager import get_mogi


class calculations(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    points = SlashCommandGroup(
        name="points", description="commands for mmr calculations"
    )

    @points.command(name="collect", description="Collect points from tablestring")
    async def collect(self, ctx: ApplicationContext):
        await ctx.response.defer()

        mogi: Mogi = get_mogi(ctx.channel.id)

        if not mogi:
            return await ctx.respond("No open Mogi in this channel.")
        if not mogi.isPlaying:
            return await ctx.respond("This mogi has not started yet.")
        if mogi.isFinished:
            return await ctx.respond("This mogi has already finished.")

        # Create a thread to collect points
        points_collection_thread: Thread = await ctx.channel.create_thread(
            name=f"collecting-points-{ctx.author.name}",
            type=ChannelType.public_thread,
        )
        await points_collection_thread.send(
            f"{ctx.author.mention}, send the tablestring from `/l context:tablestring` to collect points from it."
        )

        # Wait for the tablestring to be sent in the thread
        tablestring: str = await get_awaited_message(
            self.bot, ctx, points_collection_thread
        )

        # clean up by deleting the thread
        await points_collection_thread.delete()
        if not tablestring:
            return

        # Collect the points to the mogi
        try:
            mogi.collect_points(tablestring)
        except ValueError as e:
            return await ctx.respond("Invalid tablestring format.")

        # obtain the placements from the collected points
        placements = list(get_placements_from_scores(mogi.collected_points).values())

        # break down names and mmrs of all players
        all_player_mmrs = [player.mmr for player in mogi.players]

        # Calculate MMR results
        results = calculate_mmr(
            all_player_mmrs,
            placements,
            mogi.format,
        )

        # apply custom mmr scaling
        results = [
            math.ceil(rating * 1.2) if rating > 0 else rating for rating in results
        ]

        # store the results in the mogi, extended for every player
        for delta in results:
            mogi.mmr_results_by_group.extend([delta] * mogi.format)

        # Store the Placements in order of Players/Teams
        for place in placements:
            mogi.placements_by_group.extend([place] * mogi.format)

        if not len(mogi.mmr_results_by_group) == len(mogi.players):
            return await ctx.respond(
                "Something has gone seriously wrong, the amount of players and the MMR results don't add up. Use /debug to find the issue and contact a moderator."
            )

        print(f"All MMRs: {all_player_mmrs}")
        print(f"Summed Points: {mogi.collected_points}")
        print(f"Placements Points: {get_placements_from_scores(mogi.collected_points)}")
        print(f"MMR Changes: {mogi.mmr_results_by_group}")

        file = File(create_table(mogi), filename="table.png")
        await ctx.respond(content="# Results", file=file)

    @points.command(name="reset", description="Reset collected points")
    async def reset(self, ctx: ApplicationContext):
        await ctx.response.defer()

        mogi: Mogi = get_mogi(ctx.channel.id)

        if not mogi:
            return await ctx.respond("No open Mogi in this channel.")
        if not mogi.isPlaying:
            return await ctx.respond("This mogi has not started yet.")
        if not mogi.collected_points:
            return await ctx.respond("No points have been collected yet.")
        if mogi.isFinished:
            return await ctx.respond("This mogi has already finished.")

        mogi.collected_points.clear()
        mogi.placements_by_group.clear()
        mogi.mmr_results_by_group.clear()

        await ctx.respond("Points have been reset.")

    # TODO: permissions on all commands

    @points.command(name="apply", description="Apply MMR changes")
    async def apply(self, ctx: ApplicationContext):
        await ctx.response.defer()
        mogi: Mogi = get_mogi(ctx.channel.id)

        if not mogi:
            return await ctx.respond("No open Mogi in this channel.")
        if mogi.isVoting or not mogi.isPlaying:
            return await ctx.respond("This mogi has not started yet.")
        if not mogi.mmr_results_by_group:
            return await ctx.respond("No results to apply or already applied")
        if not len(mogi.mmr_results_by_group) == len(mogi.players):
            return await ctx.respond(
                "Something has gone seriously wrong, players and results don't add up. Use /debug to find the issue and contact a moderator."
            )

        await apply_mmr(mogi)
        await ctx.respond("Applied MMR changes ✅")
        await update_roles(ctx, mogi)


def setup(bot: commands.Bot):
    bot.add_cog(calculations(bot))
