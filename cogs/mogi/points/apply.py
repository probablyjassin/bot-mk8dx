import asyncio

from discord import slash_command
from discord.ext import commands
from pycord.multicog import subcommand

from models.CustomMogiContext import MogiApplicationContext
from utils.data.mogi_manager import mogi_manager
from utils.maths.apply import apply_mmr

from utils.command_helpers.team_roles import remove_team_roles
from utils.command_helpers.apply_update_roles import update_roles
from utils.command_helpers.find_player import get_guild_member
from utils.decorators.checks import (
    is_mogi_in_progress,
    is_mogi_manager,
)


class apply(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.apply_semaphore = asyncio.Semaphore(1)

    @subcommand(group="points")
    @slash_command(name="apply", description="Apply MMR changes")
    @is_mogi_manager()
    @is_mogi_in_progress()
    async def apply(self, ctx: MogiApplicationContext):
        async with self.apply_semaphore:
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
            for player in ctx.mogi.players:
                user = await get_guild_member(ctx.guild, player.discord_id)
                if not user:
                    await ctx.send(
                        f"<@{player.discord_id}> not found, skipping role removal"
                    )
                    continue
                if ctx.inmogi_role in user.roles:
                    await user.remove_roles(ctx.inmogi_role, reason="Mogi finished")

            await remove_team_roles(ctx=ctx)
            mogi_manager.destroy_mogi(ctx.channel.id)
            return await ctx.respond("# This channel's Mogi is finished and closed.")


def setup(bot: commands.Bot):
    bot.add_cog(apply(bot))
