import asyncio

from discord import (
    slash_command,
    SlashCommandGroup,
    Option,
    ApplicationContext,
    ChannelType,
    Thread,
)
from discord.ext import commands, tasks

from models.MogiModel import Mogi
from utils.command_helpers.wait_for import get_awaited_message
from utils.data.mogi_manager import get_mogi


class calculations(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="points", description="Collect points from tablestring")
    async def points(self, ctx: ApplicationContext):
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

        team_points_list = []
        for team in mogi.teams:
            team_points = sum(mogi.collected_points[player.name] for player in team)
            team_points_list.append(team_points)

        await ctx.respond(f"Team Points: {team_points_list}")


def setup(bot: commands.Bot):
    bot.add_cog(calculations(bot))
