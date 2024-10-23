from discord import slash_command, SlashCommandGroup, Option, ApplicationContext
from discord.ext import commands, tasks


class calculations(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot


def setup(bot: commands.Bot):
    bot.add_cog(calculations(bot))
