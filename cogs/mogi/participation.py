from discord import slash_command
from discord.utils import get, utcnow
from discord.ext import commands

from utils.command_helpers.checks import is_mogi_not_in_progress

from utils.data.mogi_manager import mogi_manager
from utils.data.database import db_players, db_archived

from models.CustomMogiContext import MogiApplicationContext
from models.PlayerModel import PlayerProfile

from bson.int64 import Int64
import asyncio
import time, datetime


class participation(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.join_semaphore = asyncio.Semaphore(1)
        self.leave_semaphore = asyncio.Semaphore(1)

        self.last_join: dict[int, int] = {}

    @slash_command(name="join", description="Join this mogi")
    @is_mogi_not_in_progress()
    async def join(self, ctx: MogiApplicationContext):
        async with self.join_semaphore:
            # check if player already in mogi
            if [
                player
                for player in ctx.mogi.players
                if player.discord_id == ctx.author.id
            ]:
                return await ctx.respond("You're already in this mogi.")
            # check if mogi full
            if len(ctx.mogi.players) >= ctx.mogi.player_cap:
                return await ctx.respond("This mogi is full.")

            # fetch player record
            player_entry = db_players.find_one({"discord_id": Int64(ctx.author.id)})
            # if not found
            if not player_entry:
                if db_archived.find_one({"discord_id": Int64(ctx.author.id)}):
                    return await ctx.respond(
                        "You're in Lounge but archived. Contact a mod to get unarchived."
                    )
                return await ctx.respond("You're not registered for Lounge.")

            # assign Player object
            player: PlayerProfile = PlayerProfile(**player_entry)

            # if suspended
            if player.suspended:
                return await ctx.respond(
                    "You're temporarily inable to join mogis.", ephemeral=True
                )

            ctx.mogi.players.append(player)
            await ctx.user.add_roles(ctx.inmogi_role)
            await ctx.respond(
                f"{ctx.author.mention} has joined the mogi!\n{len(ctx.mogi.players)} players are in!"
            )

            self.last_join[ctx.author.id] = time.time()

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

            if user_id := self.last_join.get(ctx.author.id):
                if time.time() - self.last_join[ctx.author.id] < 5:
                    await ctx.send(f"<@{user_id}>, don't do that")
                    if discord_user := get(ctx.guild.members, id=user_id):
                        await discord_user.timeout(
                            until=utcnow() + datetime.timedelta(minutes=2),
                            reason="Spamming mogi commands",
                        )
            del self.last_join[ctx.author.id]


def setup(bot: commands.Bot):
    bot.add_cog(participation(bot))
