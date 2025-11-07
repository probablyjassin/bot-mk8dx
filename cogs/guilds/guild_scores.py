import asyncio

from discord import slash_command, Thread, ChannelType
from discord.ext import commands
from pycord.multicog import subcommand

from models import MogiApplicationContext
from utils.decorators import is_mogi_manager
from utils.command_helpers import get_awaited_message
from utils.data import guild_manager


class guild_scores(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.collect_semaphore = asyncio.Semaphore(1)

    @subcommand(group="squads", independent=True)
    @slash_command(
        name="collect-results",
        description="",
    )
    @is_mogi_manager()
    async def collect_results(self, ctx: MogiApplicationContext):
        async with self.collect_semaphore:
            await ctx.response.defer()

            queue = guild_manager.read_queue()

            # Create a thread to collect points
            result_collection_thread: Thread = await ctx.channel.create_thread(
                name=f"collecting-result-{ctx.author.name}",
                type=ChannelType.public_thread,
            )
            await result_collection_thread.send(
                f"{ctx.author.mention}, type out the positions each guild placed in, in their order in the queue.\n "
                "Example: Team A placed 3rd, Team B placed 2nd, Team C placed first. -> "
                "Type '321'\n"
                "## Guild Queue Order:\n"
                f"- {'\n - '.join(guild_name for guild_name in list(queue.keys()))}"
            )

            # Wait for the tablestring to be sent in the thread
            rank_str: str = await get_awaited_message(
                self.bot, ctx, result_collection_thread
            )

            # clean up by deleting the thread
            await result_collection_thread.delete()

            # Process the tablestring
            await ctx.respond("Work In Progress: " + rank_str)


def setup(bot: commands.Bot):
    bot.add_cog(guild_scores(bot))
