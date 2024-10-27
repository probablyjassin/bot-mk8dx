from discord import SlashCommandGroup, ApplicationContext
from discord.ext import commands

from utils.data.mogi_manager import create_mogi


class sub_manager(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    replacement = SlashCommandGroup(
        name="replacement", description="Substitute a player"
    )

    @replacement.command(name="sub")
    async def sub(self, ctx: ApplicationContext):
        pass

    @replacement.command(name="unsub")
    async def sub(self, ctx: ApplicationContext):
        pass


def setup(bot: commands.Bot):
    bot.add_cog(sub_manager(bot))
