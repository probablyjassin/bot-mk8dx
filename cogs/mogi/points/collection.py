import asyncio

from discord import (
    ChannelType,
    Thread,
    message_command,
    Message,
    slash_command
)
from discord.ext import commands
from pycord.multicog import subcommand

from models.CustomMogiContext import MogiApplicationContext
from utils.maths.results import process_tablestring
from utils.command_helpers.wait_for import get_awaited_message
from utils.decorators.checks import (
    is_mogi_in_progress,
    is_mogi_manager,
)

class collection(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.collect_semaphore = asyncio.Semaphore(1)

    @slash_command(name="collect_points")
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
            await process_tablestring(ctx, tablestring)

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
            await process_tablestring(ctx, tablestring)


def setup(bot: commands.Bot):
    bot.add_cog(collection(bot))
