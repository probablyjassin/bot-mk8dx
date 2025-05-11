import math
import time
import asyncio

from discord import (
    SlashCommandGroup,
    ChannelType,
    Thread,
    File,
    message_command,
    Message,
)
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.data.mogi_manager import mogi_manager

from utils.maths.mmr_algorithm import calculate_mmr
from utils.maths.placements import get_placements_from_scores
from utils.maths.table import create_table
from utils.maths.apply import apply_mmr

from cogs.mogi.calculations import calculations

from utils.command_helpers.team_roles import remove_team_roles
from utils.command_helpers.apply_update_roles import update_roles
from utils.command_helpers.wait_for import get_awaited_message
from utils.command_helpers.find_player import get_guild_member
from utils.decorators.checks import (
    is_mogi_in_progress,
    is_mogi_manager,
)


class collection(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.collect_semaphore = asyncio.Semaphore(1)

    async def process_tablestring(self, ctx: MogiApplicationContext, tablestring: str):
        if not tablestring:  #
            await ctx.respond("No tablestring found")
            return False

        # Collect the points to the mogi
        try:
            ctx.mogi.collect_points(tablestring)
        except ValueError as e:
            await ctx.respond("Invalid tablestring format.")
            return False

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
            await ctx.respond(
                "Something has gone seriously wrong, the amount of players and the MMR results don't add up. Use /debug to find the issue and contact a moderator."
            )
            return False

        # Store the date of the results
        file = File(await create_table(ctx.mogi), filename="table.png")
        message = await ctx.results_channel.send(
            content=f"# Results - {time.strftime('%d.%m.%y')}", file=file
        )

        await ctx.respond("Results got posted in the results channel.")

        ctx.mogi.table_message_id = message.id
        return True

    @calculations.points.command(
        name="collect", description="Collect points from tablestring"
    )
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def collect(self, ctx: MogiApplicationContext):
        async with self.collect_semaphore:
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

            # Process the tablestring
            await self.process_tablestring(ctx, tablestring)

    @message_command(name="Collect Points")
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def collect_points(self, ctx: MogiApplicationContext, message: Message):
        async with self.collect_semaphore:
            if ctx.mogi.collected_points:
                return await ctx.respond("Already collected points.")

            await ctx.response.defer()

            # Extract tablestring from message content
            tablestring = message.content

            # Process the tablestring
            await self.process_tablestring(ctx, tablestring)


def setup(bot: commands.Bot):
    bot.add_cog(collection(bot))
