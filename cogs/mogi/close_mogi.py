import random

import discord
from discord.ext import commands, tasks

class close_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    

def setup(bot: commands.Bot):
    bot.add_cog(close_mogi(bot))
