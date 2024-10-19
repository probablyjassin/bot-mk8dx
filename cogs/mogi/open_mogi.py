import random
import discord
from discord import slash_command, ApplicationContext
from discord.ext import commands, tasks
from utils.mogis import create_mogi

class open_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="open", description="Open a mogi")
    async def open_mogi(self, ctx: ApplicationContext):
        try:
            create_mogi(ctx.channel.id)
            await ctx.respond("New Mogi open!")
        except:
            await ctx.respond("A Mogi for this channel is already open.")

def setup(bot: commands.Bot):
    bot.add_cog(open_mogi(bot))
