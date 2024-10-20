import asyncio
from discord import slash_command, ApplicationContext
from discord.ext import commands
from utils.mogis import get_mogi
from utils.models import Mogi, MogiPlayer
from utils.database import db_players, db_archived

class join_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.join_semaphore = asyncio.Semaphore(1)

    @slash_command(name="join", description="Join this mogi")
    async def join_mogi(self, ctx: ApplicationContext):
        async with self.join_semaphore:
            mogi: Mogi = get_mogi(ctx.channel.id)
            if not mogi:
                await ctx.respond("There is no mogi open in this channel.")
            if ctx.author.id in mogi.players:
                await ctx.respond("You're already in this mogi.")
            else:
                player = await db_players.find_one({"discord_id": ctx.author.id})
                if not player:
                    archived_player = await db_players.find_one({"discord_id": ctx.author.id, "archived": True})
                    await ctx.respond("You're not registered for Lounge.")
                else:
                    mogi.players.append(MogiPlayer(discord_id=ctx.author.id))
                    await ctx.respond(f"{ctx.author.mention} has joined the mogi!\n{len(mogi.players)} players are in!")
                mogi.players.append(MogiPlayer(discord_id=ctx.author.id))
                await ctx.respond(f"{ctx.author.mention} has joined the mogi!\n{len(mogi.players)} players are in!")

def setup(bot: commands.Bot):
    bot.add_cog(join_mogi(bot))
