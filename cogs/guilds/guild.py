from discord import slash_command, Option
from discord.ext import commands

from models import MogiApplicationContext, Guild

from utils.decorators import (
    is_admin,
)


class guild(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="guild",
        description="View your guild or a guild of your choice",
    )
    async def guild(
        self,
        ctx: MogiApplicationContext,
        guild: str = Option(
            str,
            "Name",
            required=False,
        ),
    ):

        return await ctx.respond("meow")


def setup(bot: commands.Bot):
    bot.add_cog(guild(bot))
