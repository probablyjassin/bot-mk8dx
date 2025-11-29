from discord import slash_command
from discord.ext import commands

from pycord.multicog import subcommand

from utils.decorators import is_admin
from models import MogiApplicationContext


class rollback(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @subcommand(group="manage", independent=True)
    @is_admin()
    @slash_command(
        name="rollback",
        description="Admin only: roll back the last mogi's results",
    )
    async def rollback(self, ctx: MogiApplicationContext):
        return await ctx.respond("meow")


def setup(bot: commands.Bot):
    bot.add_cog(rollback(bot))
