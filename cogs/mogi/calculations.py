import math

from discord import SlashCommandGroup, ChannelType, Thread, File
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.data.mogi_manager import mogi_manager

from utils.maths.mmr_algorithm import calculate_mmr
from utils.maths.placements import get_placements_from_scores
from utils.maths.table import create_table
from utils.maths.apply import apply_mmr

from utils.command_helpers.checks import (
    is_mogi_in_progress,
    is_mogi_manager,
)
from utils.command_helpers.confirm import confirmation
from utils.command_helpers.apply_update_roles import update_roles
from utils.command_helpers.wait_for import get_awaited_message


class calculations(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    points = SlashCommandGroup(
        name="points", description="commands for mmr calculations"
    )

    @points.command(name="collect", description="Collect points from tablestring")
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def collect(self, ctx: MogiApplicationContext):
        if ctx.mogi.collected_points:
            return await ctx.respond("Already collected points.")

        await ctx.response.defer()

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
            ctx.mogi.collect_points(tablestring)
        except ValueError as e:
            return await ctx.respond("Invalid tablestring format.")

        # obtain the placements from the collected points
        placements = []
        for score in ctx.mogi.collected_points:
            placements.append(
                get_placements_from_scores(ctx.mogi.collected_points)[score]
            )

        # break down names and mmrs of all players
        all_player_mmrs = [player.mmr for player in ctx.mogi.players]

        # Calculate MMR results
        results = calculate_mmr(
            all_player_mmrs,
            placements,
            ctx.mogi.format,
        )

        # apply custom mmr scaling
        results = [
            math.ceil(rating * 1.2) if rating > 0 else rating for rating in results
        ]

        # store the results in the mogi, extended for every player
        for delta in results:
            ctx.mogi.mmr_results_by_group.extend([delta] * ctx.mogi.format)

        # Store the Placements in order of Players/Teams
        for place in placements:
            ctx.mogi.placements_by_group.extend([place] * ctx.mogi.format)

        if not len(ctx.mogi.mmr_results_by_group) == len(ctx.mogi.players):
            return await ctx.respond(
                "Something has gone seriously wrong, the amount of players and the MMR results don't add up. Use /debug to find the issue and contact a moderator."
            )

        file = File(create_table(ctx.mogi), filename="table.png")
        message = await ctx.respond(content="# Results", file=file)

        ctx.mogi.table_message_id = message.id

    @points.command(name="reset", description="Reset collected points")
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def reset(self, ctx: MogiApplicationContext):
        await ctx.response.defer()

        if not ctx.mogi.collected_points:
            return await ctx.respond("No points have been collected yet.")

        ctx.mogi.collected_points.clear()
        ctx.mogi.placements_by_group.clear()
        ctx.mogi.mmr_results_by_group.clear()
        try:
            await (await ctx.channel.fetch_message(ctx.mogi.table_message_id)).delete()
        except Exception:
            pass

        await ctx.respond("Points have been reset.")

    @points.command(name="apply", description="Apply MMR changes")
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def apply(self, ctx: MogiApplicationContext):
        await ctx.response.defer()

        if not ctx.mogi.mmr_results_by_group:
            return await ctx.respond("No results to apply or already applied")

        if not len(ctx.mogi.mmr_results_by_group) == len(ctx.mogi.players):
            return await ctx.respond(
                "Something has gone seriously wrong, players and results don't add up. Use /debug to find the issue and contact a moderator."
            )

        await apply_mmr(ctx.mogi)
        await ctx.send("Applied MMR changes ✅")
        await update_roles(ctx, ctx.mogi)
        ctx.mogi.finish()

        if await confirmation(
            ctx,
            "{}, the mogi is ready to be closed. Would you like to?".format(
                ctx.author.mention
            ),
        ):
            mogi_manager.destroy_mogi(ctx.channel.id)
            return await ctx.respond("# This channel's Mogi is finished and closed.")
        await ctx.respond("Held mogi open.")


def setup(bot: commands.Bot):
    bot.add_cog(calculations(bot))
