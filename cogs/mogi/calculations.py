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

        points_collection_thread: Thread = await ctx.channel.create_thread(
            name=f"collecting-points-{ctx.author.name}",
            type=ChannelType.public_thread,
        )
        await points_collection_thread.send(
            f"{ctx.author.mention}, send the tablestring from `/l context:tablestring` to collect points from it."
        )

        tablestring: str = await get_awaited_message(
            self.bot, ctx, points_collection_thread
        )

        await points_collection_thread.delete()
        if not tablestring:
            return

        mogi.collect_points(tablestring)

        await ctx.respond(f"Points collected: {mogi.collected_points}")


def setup(bot: commands.Bot):
    bot.add_cog(calculations(bot))
