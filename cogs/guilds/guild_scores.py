import asyncio, time

from discord import slash_command, Thread, ChannelType, File
from discord.ext import commands
from pycord.multicog import subcommand

from models import MogiApplicationContext
from utils.decorators import is_mogi_manager
from utils.command_helpers import get_awaited_message
from utils.data import guild_manager, data_manager
from utils.maths.results import calculate_mmr
from utils.maths.table import create_table


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

            queue = guild_manager.read_playing()

            if not queue:
                return await ctx.respond("No guild mogi in progress.")

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
                f"- {'\n - '.join(guild_name for guild_name in queue)}"
            )

            # Wait for the tablestring to be sent in the thread
            rank_str: str = await get_awaited_message(
                self.bot, ctx, result_collection_thread
            )

            # clean up by deleting the thread
            await result_collection_thread.delete()

            if not rank_str.isnumeric():
                return await ctx.respond("The result needs to be strictly numeric!")
            if len(rank_str) != len(queue):
                return await ctx.respond(
                    "The lenght of the results provided don't match the amount of guilds playing."
                )

            ranks: list[int] = [int(placement) for placement in rank_str]

            playing_guild_objects = [
                data_manager.Guilds.find(queue[i]) for i in range(len(queue))
            ]

            results = calculate_mmr(
                [guild.mmr for guild in playing_guild_objects],
                ranks,
                1,
            )

            file = File(
                await create_table(
                    names=queue,
                    old_mmrs=[guild.mmr for guild in playing_guild_objects],
                    results=results,
                    placements=ranks,
                    team_size=1,
                ),
                filename="table.png",
            )
            message = await ctx.results_channel.send(
                content=f"# Guild Mogi Results - {time.strftime('%d.%m.%y')}",
                file=file,
            )

            await ctx.respond(message)


def setup(bot: commands.Bot):
    bot.add_cog(guild_scores(bot))
