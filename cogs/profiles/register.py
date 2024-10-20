import discord
from discord import slash_command
from discord.ext import commands

class register(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="register", description="Register yourself as a player")
    async def register(self, ctx: commands.Context):
        pass

def setup(bot: commands.Bot):
    bot.add_cog(register(bot))
