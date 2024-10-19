import discord
from discord.ext import commands, tasks
from utils.mogis import mogi_registry

class debugging(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    

def setup(bot: commands.Bot):
    bot.add_cog(debugging(bot))
