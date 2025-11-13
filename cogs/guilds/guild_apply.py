import asyncio

from discord import slash_command
from discord.ext import commands
from pycord.multicog import subcommand

from models import MogiApplicationContext
from utils.decorators import is_mogi_manager
from utils.data import guild_manager
from utils.maths.apply import apply_guild_mmr


class guild_apply(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.apply_semaphore = asyncio.Semaphore(1)

    @subcommand(group="squads", independent=True)
    @slash_command(
        name="apply-results",
        description="",
    )
    @is_mogi_manager()
    async def apply_results(self, ctx: MogiApplicationContext):
        async with self.apply_semaphore:
            await ctx.response.defer()

            playing_guilds = guild_manager.read_playing()

            if not playing_guilds:
                return await ctx.respond("No guild mogi in progress.")

            if not (guild_mogi_results := guild_manager.results):
                return await ctx.respond("No collected results to apply.")

            if len(guild_mogi_results) != len(playing_guilds):
                return await ctx.respond(
                    "Results don't add up with the guilds in the mogi."
                )

            apply_guild_mmr(playing_guilds, guild_mogi_results)
            guild_manager.clear_queue()

            await ctx.respond("# This guild mogi is finished and closed.")


def setup(bot: commands.Bot):
    bot.add_cog(guild_apply(bot))
