from discord import slash_command
from discord.ext import commands
from models import MogiApplicationContext
from pycord.multicog import subcommand


class guild_scores(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @subcommand(group="squads", independent=True)
    @slash_command(
        name="collect-results",
        description="",
    )
    async def collect(self, ctx: MogiApplicationContext):
        return await ctx.respond("meow")


def setup(bot: commands.Bot):
    bot.add_cog(guild_scores(bot))
