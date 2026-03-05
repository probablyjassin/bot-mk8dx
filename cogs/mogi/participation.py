import asyncio, json, time

from discord import slash_command
from discord.utils import get
from discord.ext import commands

from models import MogiApplicationContext

from utils.data import mogi_manager
from utils.decorators import with_player, is_mogi_not_in_progress
from utils.command_helpers import REGIONS


class participation(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.join_semaphore = asyncio.Semaphore(1)
        self.leave_semaphore = asyncio.Semaphore(1)

    @slash_command(name="join", description="Join this mogi")
    @is_mogi_not_in_progress()
    @with_player(assert_not_in_mogi=True, assert_not_suspended=True)
    async def join(self, ctx: MogiApplicationContext):
        async with self.join_semaphore:
            # check if mogi full
            if len(ctx.mogi.players) >= ctx.mogi.player_cap:
                return await ctx.respond("This mogi is full.")

            # add player and their role
            ctx.mogi.players.append(ctx.player)
            await ctx.user.add_roles(ctx.inmogi_role, reason="Joined mogi")
            in_mogi = len(ctx.mogi.players)
            await ctx.respond(
                f"{ctx.author.mention} has joined the mogi!\n{len(ctx.mogi.players)} {'player is' if in_mogi == 1 else 'players are'} in!"
            )

            # note down joined time
            with open("state/joined_times.json", "r+", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
                data[str(ctx.author.id)] = round(time.time())
                f.seek(0)
                json.dump(data, f)

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

            if len(ctx.mogi.players) == 0:
                mogi_manager.destroy_mogi(ctx.channel.id)
                return await ctx.respond("# This mogi has been closed.")
            in_mogi = len(ctx.mogi.players)
            await ctx.respond(
                f"{ctx.author.mention} has left the mogi!\n{in_mogi} {'player is' if in_mogi == 1 else 'players are'} in!"
            )


def setup(bot: commands.Bot):
    bot.add_cog(participation(bot))
