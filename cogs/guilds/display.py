from discord import slash_command, Option, Attachment
from discord.ext import commands

from models import MogiApplicationContext, Guild

from utils.decorators.checks import (
    is_admin,
)


class display(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(
        name="guild",
        description="View your guild or a guild of your choice",
    )
    @is_admin()
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
    bot.add_cog(display(bot))
