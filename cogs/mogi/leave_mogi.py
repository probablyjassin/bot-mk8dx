from discord import slash_command
from discord.utils import get
from discord.ext import commands

from models.CustomMogiContext import MogiApplicationContext
from utils.command_helpers.checks import is_mogi_not_in_progress
from utils.data.mogi_manager import mogi_manager

import asyncio


class leave_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.leave_semaphore = asyncio.Semaphore(1)

    @slash_command(name="leave", description="Leave this mogi")
    @is_mogi_not_in_progress()
    async def leave(self, ctx: MogiApplicationContext):
        async with self.leave_semaphore:
            if not [
                player
                for player in ctx.mogi.players
                if player.discord_id == ctx.author.id
            ]:
                return await ctx.respond("You're not in this mogi.")

            ctx.mogi.players = [
                player
                for player in ctx.mogi.players
                if player.discord_id != ctx.author.id
            ]
            await ctx.user.remove_roles(ctx.inmogi_role)
            if len(ctx.mogi.players) == 0:
                mogi_manager.destroy_mogi(ctx.channel.id)
                return await ctx.respond("# This mogi has been closed.")
            await ctx.respond(
                f"{ctx.author.mention} has left the mogi!\n{len(ctx.mogi.players)} players are in!"
            )


def setup(bot: commands.Bot):
    bot.add_cog(leave_mogi(bot))
