from discord import slash_command
from discord.ext import commands
from pycord.multicog import subcommand

from models.CustomMogiContext import MogiApplicationContext

from utils.decorators.checks import (
    is_mogi_in_progress,
    is_mogi_manager,
)


class reset(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @subcommand(group="points")
    @slash_command(name="reset", description="Reset collected points")
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


def setup(bot: commands.Bot):
    bot.add_cog(reset(bot))
