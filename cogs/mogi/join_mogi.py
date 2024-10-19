import random

import discord
from discord.ext import commands, tasks

class join_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    

def setup(bot: commands.Bot):
    bot.add_cog(join_mogi(bot))
