import asyncio
from discord import slash_command, ApplicationContext
from discord.ext import commands, tasks
from utils.mogis import get_mogi, close_mogi
from utils.models import Mogi, PlayerProfile

class list_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.leave_semaphore = asyncio.Semaphore(1)

    @slash_command(name="leave", description="Leave this mogi")
    async def join_mogi(self, ctx: ApplicationContext):
        async with self.leave_semaphore:
            mogi: Mogi = get_mogi(ctx.channel.id)
            if not mogi:
                await ctx.respond("There is no mogi open in this channel.")
            if not [player for player in mogi.players if player.discord_id == ctx.author.id]:
                await ctx.respond("You're not in this mogi.")
            if mogi.isPlaying or mogi.isVoting:
                await ctx.respond("This mogi has already started.")

            else:
                mogi.players = [player for player in mogi.players if player.discord_id != ctx.author.id]
                if len(mogi.players) == 0:
                    close_mogi(ctx.channel.id)
                    return await ctx.respond("This mogi has been closed.")
                await ctx.respond(f"{ctx.author.mention} has left the mogi!\n{len(mogi.players)} players are in!")

def setup(bot: commands.Bot):
    bot.add_cog(list_mogi(bot))
