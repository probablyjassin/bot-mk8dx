from discord import slash_command
from discord.utils import get, utcnow
from discord.ext import commands

from utils.decorators.player import with_player
from utils.command_helpers.server_region import REGIONS
from utils.command_helpers.checks import (
    is_mogi_not_in_progress,
)

from utils.data.mogi_manager import mogi_manager

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

import asyncio
import time, datetime


class participation(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.join_semaphore = asyncio.Semaphore(1)
        self.leave_semaphore = asyncio.Semaphore(1)

        self.last_join: dict[str, int] = {}

    @slash_command(name="join", description="Join this mogi")
    @is_mogi_not_in_progress()
    @with_player(assert_not_in_mogi=True, assert_not_suspended=True)
    async def join(self, ctx: MogiApplicationContext):
        async with self.join_semaphore:
            # check if mogi full
            if len(ctx.mogi.players) >= ctx.mogi.player_cap:
                return await ctx.respond("This mogi is full.")

            # add player and their role
            ctx.mogi.players.append(player)
            await ctx.user.add_roles(ctx.inmogi_role, reason="Joined mogi")
            await ctx.respond(
                f"{ctx.author.mention} has joined the mogi!\n{len(ctx.mogi.players)} players are in!"
            )

            self.last_join[str(ctx.author.id)] = time.time()

            # WIP: while transitioning: remind people to add a region role
            for role in [get(ctx.guild.roles, name=region) for region in REGIONS]:
                if role in ctx.user.roles:
                    return
            await ctx.send_followup(
                "It seems like you don't have a region role yet. Go to <#1128146332683612241> to grab one.",
                ephemeral=True,
            )

    @slash_command(name="leave", description="Leave this mogi")
    @is_mogi_not_in_progress()
    @with_player(assert_in_mogi=True, assert_not_suspended=True)
    async def leave(self, ctx: MogiApplicationContext):
        async with self.leave_semaphore:
            ctx.mogi.players = [
                player
                for player in ctx.mogi.players
                if player.discord_id != ctx.author.id
            ]
            if ctx.inmogi_role in ctx.user.roles:
                await ctx.user.remove_roles(ctx.inmogi_role, reason="Left mogi")

            if self.last_join.get(str(ctx.author.id), None):
                if time.time() - self.last_join[str(ctx.author.id)] < 5:
                    await ctx.send(f"<@{ctx.author.id}>, don't do that")
                    if discord_user := get(ctx.guild.members, id=ctx.author.id):
                        await discord_user.timeout(
                            until=utcnow() + datetime.timedelta(minutes=5),
                            reason="Spamming mogi commands",
                        )
                del self.last_join[str(ctx.author.id)]

            if len(ctx.mogi.players) == 0:
                mogi_manager.destroy_mogi(ctx.channel.id)
                return await ctx.respond("# This mogi has been closed.")
            await ctx.respond(
                f"{ctx.author.mention} has left the mogi!\n{len(ctx.mogi.players)} players are in!"
            )


def setup(bot: commands.Bot):
    bot.add_cog(participation(bot))
