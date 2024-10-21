import discord
from discord import slash_command, Option, ApplicationContext
from discord.ext import commands

class start(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(start(bot))
